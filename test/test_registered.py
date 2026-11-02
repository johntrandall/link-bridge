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


def post(path, body, token=TOKEN, header=True):
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}{path}", data=json.dumps(body).encode(),
                                 method="POST", headers={"Content-Type": "application/json"})
    if header:
        req.add_header("X-Link-Bridge", "1")
    if token is not None:
        req.add_header("X-Link-Bridge-Token", token)
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
                    f'params = ["date", "check"]\ntoken = "{TOKEN}"\ntimeout = 10\n'
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
        self.assertEqual(d["registered"], ["echo"])

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


if __name__ == "__main__":
    unittest.main()
