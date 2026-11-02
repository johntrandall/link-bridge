"""Run: python3 -I -m unittest discover -s test -p 'test_registered.py'
Starts the server on a scratch port with a temporary actions.toml naming one dummy command, and
exercises every gate of a registered action: unknown name, header, token, value shape, the run,
and the /routes listing. Nothing real is touched: the dummy command only echoes its arguments."""
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.error
import urllib.request

BIN = os.path.join(os.path.dirname(__file__), "..", "bin", "link-bridge")
PORT = 5498
TOKEN = "t" * 48


def post(path, body, token=TOKEN, header=True, login=None):
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}{path}", data=json.dumps(body).encode(),
                                 method="POST", headers={"Content-Type": "application/json"})
    if header:
        req.add_header("X-Link-Bridge", "1")
    if token is not None:
        req.add_header("X-Link-Bridge-Token", token)
    if login is not None:
        req.add_header("Tailscale-User-Login", login)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        raw = e.read() or b"{}"
        try:
            return e.code, json.loads(raw)
        except ValueError:
            return e.code, {}


class Registered(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        echo = os.path.join(cls.tmp, "echo_args.py")
        with open(echo, "w") as f:
            f.write("import sys\n"
                    "args = sys.argv[1:]\n"
                    "if 'boom' in args: sys.exit('refused: boom')\n"
                    "print(' | '.join(args))\n")
        cfg = os.path.join(cls.tmp, "actions.toml")
        with open(cfg, "w") as f:
            f.write(f'[actions.echo]\nargv = ["{sys.executable}", "-I", "{echo}"]\n'
                    f'params = ["date", "check"]\ntoken = "{TOKEN}"\ntimeout = 10\nrate_per_minute = 100\n'
                    f'[actions.phone]\nargv = ["{sys.executable}", "-I", "{echo}"]\nparams = ["x"]\n'
                    f'token = "{TOKEN}"\nallow_logins = ["me@github"]\nrate_per_minute = 100\n'
                    f'[actions.local]\nargv = ["{sys.executable}", "-I", "{echo}"]\nparams = ["x"]\n'
                    f'token = "{TOKEN}"\nallow_logins = ["me@github"]\nallow_loopback = true\n'
                    f'[actions.slow]\nargv = ["{sys.executable}", "-I", "{echo}"]\nparams = ["x"]\n'
                    f'token = "{TOKEN}"\nrate_per_minute = 2\n'
                    '[actions.broken]\nargv = ["relative/path"]\nparams = []\ntoken = "short"\n')
        env = {**os.environ, "LINK_BRIDGE_ACTIONS": cfg}
        cls.proc = subprocess.Popen([sys.executable, "-I", BIN, "serve", "--port", str(PORT)],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
        for _ in range(50):
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{PORT}/healthz", timeout=1); break
            except Exception:  # noqa: BLE001
                time.sleep(0.1)

    @classmethod
    def tearDownClass(cls):
        cls.proc.terminate(); cls.proc.wait(timeout=5)

    def test_routes_lists_only_well_formed_registrations(self):
        with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/routes", timeout=5) as r:
            d = json.loads(r.read())
        self.assertEqual(d["registered"], ["echo", "local", "phone", "slow"])

    def test_unknown_name_is_405_and_gates_run_in_order(self):
        self.assertEqual(post("/act/nope", {})[0], 405)
        self.assertEqual(post("/act/broken", {})[0], 405)
        self.assertEqual(post("/act/echo", {"date": "d", "check": "c"}, header=False)[0], 403)
        self.assertEqual(post("/act/echo", {"date": "d", "check": "c"}, token=None)[0], 403)
        self.assertEqual(post("/act/echo", {"date": "d", "check": "c"}, token="x" * 48)[0], 403)

    def test_values_are_gated(self):
        self.assertEqual(post("/act/echo", {"date": "d"})[0], 400)
        self.assertEqual(post("/act/echo", {"date": "d", "check": "a\nb"})[0], 400)
        self.assertEqual(post("/act/echo", {"date": "d", "check": "--help"})[0], 400)
        self.assertEqual(post("/act/echo", {"date": "d", "check": "x" * 129})[0], 400)
        self.assertEqual(post("/act/echo", {"date": 5, "check": "c"})[0], 400)

    def test_run_passes_named_values_as_separate_arguments(self):
        code, d = post("/act/echo", {"date": "2026-11-02", "check": "pills; rm -rf /"})
        self.assertEqual(code, 200)
        self.assertEqual(d["output"], "--date | 2026-11-02 | --check | pills; rm -rf /")

    def test_nonzero_exit_is_400_with_the_refusal(self):
        code, d = post("/act/echo", {"date": "boom", "check": "c"})
        self.assertEqual(code, 400)
        self.assertIn("refused: boom", d["error"])
        self.assertEqual(d["exit"], 1)

    def test_allow_logins_admits_only_the_named_tailscale_login(self):
        # Serve sets this header for untagged tailnet devices and strips client copies; the test
        # plays Serve by setting it on loopback.
        self.assertEqual(post("/act/phone", {"x": "1"}, login="me@github")[0], 200)
        self.assertEqual(post("/act/phone", {"x": "1"}, login="other@github")[0], 403)
        self.assertEqual(post("/act/phone", {"x": "1"})[0], 403)             # loopback, no header
        self.assertEqual(post("/act/local", {"x": "1"})[0], 200)             # allow_loopback
        self.assertEqual(post("/act/local", {"x": "1"}, login="other@github")[0], 403)

    def test_rate_limit_per_action(self):
        self.assertEqual(post("/act/slow", {"x": "1"})[0], 200)
        self.assertEqual(post("/act/slow", {"x": "1"})[0], 200)
        self.assertEqual(post("/act/slow", {"x": "1"})[0], 429)
        self.assertEqual(post("/act/echo", {"date": "d", "check": "c"})[0], 200)   # other buckets untouched

    def test_content_length_is_bounded_before_any_read(self):
        import http.client
        for bad in ("-1", "5000", "x"):
            c = http.client.HTTPConnection("127.0.0.1", PORT, timeout=10)
            c.putrequest("POST", "/act/echo", skip_accept_encoding=True)
            c.putheader("X-Link-Bridge", "1"); c.putheader("X-Link-Bridge-Token", TOKEN)
            c.putheader("Content-Type", "application/json"); c.putheader("Content-Length", bad)
            c.endheaders()
            r = c.getresponse(); body = json.loads(r.read() or b"{}"); c.close()
            self.assertEqual(r.status, 400, bad)
            self.assertIn("Content-Length", body.get("error", ""))


if __name__ == "__main__":
    unittest.main()
