"""Run: python3 -I -m unittest discover -s test -p 'test_actions.py'
Starts the server on a scratch port and exercises the /act endpoints' gates. It never reveals a
real file or focuses a real tab: only refusal paths and a session id that no herdr pane holds."""
import json
import os
import subprocess
import sys
import time
import unittest
import urllib.error
import urllib.request

BIN = os.path.join(os.path.dirname(__file__), "..", "bin", "link-bridge")
PORT = 5499


def post(path, body, header=True):
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}{path}", data=json.dumps(body).encode(),
                                 method="POST", headers={"Content-Type": "application/json"})
    if header:
        req.add_header("X-Link-Bridge", "1")
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        raw = e.read() or b"{}"
        try:
            return e.code, json.loads(raw)
        except ValueError:          # http.server's own error pages are HTML (405)
            return e.code, {}


class Actions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proc = subprocess.Popen([sys.executable, "-I", BIN, "serve", "--port", str(PORT)],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(50):
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{PORT}/healthz", timeout=1); break
            except Exception:  # noqa: BLE001
                time.sleep(0.1)

    @classmethod
    def tearDownClass(cls):
        cls.proc.terminate(); cls.proc.wait(timeout=5)

    def test_header_required(self):
        code, body = post("/act/reveal", {"path": "/tmp"}, header=False)
        self.assertEqual(code, 403)

    def test_unknown_action_is_405(self):
        code, _ = post("/act/launch", {"x": 1})
        self.assertEqual(code, 405)

    def test_bad_session_400_and_missing_session_404(self):
        self.assertEqual(post("/act/herdr-jump", {"session": "../etc"})[0], 400)
        self.assertEqual(post("/act/herdr-jump", {"session": "00000000-0000-4000-8000-000000000000"})[0], 404)

    def test_owner_400_and_missing_404(self):
        self.assertEqual(post("/act/herdr-owner", {"session": "../etc"})[0], 400)
        self.assertEqual(post("/act/herdr-owner", {"session": "00000000-0000-4000-8000-000000000000"})[0], 404)

    def test_routes_lists_the_contract(self):
        import json as _json, urllib.request as _u
        with _u.urlopen(f"http://127.0.0.1:{PORT}/routes", timeout=5) as r:
            d = _json.loads(r.read())
        self.assertIn("/herdr-owner", d["routes"])
        self.assertIn("/act/herdr-owner", d["actions"])
        self.assertTrue(d["version"])

    def test_workspace_400_and_missing_404(self):
        self.assertEqual(post("/act/herdr-workspace", {})[0], 400)
        self.assertEqual(post("/act/herdr-workspace", {"workspace": "../etc"})[0], 400)
        self.assertEqual(post("/act/herdr-workspace", {"label": "a\nb"})[0], 400)
        self.assertEqual(post("/act/herdr-workspace", {"workspace": "wZZZZZZZ"})[0], 404)
        self.assertEqual(post("/act/herdr-workspace", {"label": "no such workspace label 7f3a"})[0], 404)

    def test_reveal_refusals(self):
        self.assertEqual(post("/act/reveal", {"path": ""})[0], 400)
        self.assertEqual(post("/act/reveal", {"path": "/definitely/not/here"})[0], 404)
        self.assertEqual(post("/act/reveal", {"path": "/tmp/a\nb"})[0], 400)

    def test_foreign_host_is_403(self):
        # DNS rebinding: a page on an attacker's name that resolves here sends its own Host.
        req = urllib.request.Request(f"http://127.0.0.1:{PORT}/act/herdr-jump", data=b'{"session":"x"}', method="POST",
                                     headers={"Content-Type": "application/json", "X-Link-Bridge": "1", "Host": "evil.example:5465"})
        with self.assertRaises(urllib.error.HTTPError) as cm:
            urllib.request.urlopen(req, timeout=10)
        self.assertEqual(cm.exception.code, 403)
        self.assertIn("Host", json.loads(cm.exception.read())["error"])

    def test_wake_refusals(self):
        # Bad names never reach watchbill (400); a well-formed name reaches `watchbill resume`, which
        # refuses an unknown system (409), or the bridge says watchbill is not installed here (501).
        self.assertEqual(post("/act/wake", {"system": "", "seat": "steward"})[0], 400)
        self.assertEqual(post("/act/wake", {"system": "../etc", "seat": "steward"})[0], 400)
        self.assertEqual(post("/act/wake", {"system": "watchbill", "seat": "--dry-run"})[0], 400)
        self.assertEqual(post("/act/wake", {"system": "watchbill", "seat": "a b"})[0], 400)
        self.assertEqual(post("/act/wake", {"system": "x" * 65})[0], 400)
        self.assertEqual(post("/act/wake", {"system": "\u212aelvin"})[0], 400)       # KELVIN SIGN: not ASCII, not a slug
        self.assertEqual(post("/act/wake", {"system": "\u0130" * 64})[0], 400)
        code, body = post("/act/wake", {"system": "no-such-system-7f3a", "seat": "lead-designer"})
        self.assertIn(code, (409, 501))
        self.assertFalse(body["ok"])
        with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/routes", timeout=5) as r:
            d = json.loads(r.read())
        self.assertIn("/wake", d["routes"])
        self.assertIn("/act/wake", d["actions"])

    def test_healthz_and_csp(self):
        with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/reveal", timeout=5) as r:
            self.assertIn("connect-src 'self'", r.headers.get("Content-Security-Policy", ""))


class WakeSerialised(unittest.TestCase):
    """A fake watchbill that sleeps: two concurrent wakes get one 200 and one 409, a repeat inside the cooldown 409."""
    PORT = 5497

    @classmethod
    def setUpClass(cls):
        import tempfile
        cls.tmp = tempfile.mkdtemp()
        fake = os.path.join(cls.tmp, "watchbill")
        with open(fake, "w") as f:
            f.write("#!/bin/sh\nsleep 2\necho woke $2 $4\n")
        os.chmod(fake, 0o755)
        cls.proc = subprocess.Popen([sys.executable, "-I", BIN, "serve", "--port", str(cls.PORT)],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                    env={**os.environ, "WATCHBILL_BIN_PATH": fake})
        for _ in range(50):
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{cls.PORT}/healthz", timeout=1); break
            except Exception:  # noqa: BLE001
                time.sleep(0.1)

    @classmethod
    def tearDownClass(cls):
        cls.proc.terminate(); cls.proc.wait(timeout=5)
        import shutil; shutil.rmtree(cls.tmp, ignore_errors=True)

    def _post(self, body):
        req = urllib.request.Request(f"http://127.0.0.1:{self.PORT}/act/wake", data=json.dumps(body).encode(), method="POST",
                                     headers={"Content-Type": "application/json", "X-Link-Bridge": "1"})
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read() or b"{}")

    def test_two_clicks_one_wake(self):
        import threading
        results = []
        ts = [threading.Thread(target=lambda: results.append(self._post({"system": "demo", "seat": "steward"}))) for _ in range(2)]
        for t in ts: t.start()
        for t in ts: t.join()
        self.assertEqual(sorted(c for c, _ in results), [200, 409])
        ok = next(b for c, b in results if c == 200)
        self.assertEqual(ok["output"], "woke demo steward")
        # the cooldown: the same seat again within a minute is refused, another seat is not
        self.assertEqual(self._post({"system": "demo", "seat": "steward"})[0], 409)
        self.assertEqual(self._post({"system": "demo", "seat": "lead-designer"})[0], 200)


if __name__ == "__main__":
    unittest.main()
