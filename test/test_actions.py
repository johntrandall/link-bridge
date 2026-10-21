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

    def test_healthz_and_csp(self):
        with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/reveal", timeout=5) as r:
            self.assertIn("connect-src 'self'", r.headers.get("Content-Security-Policy", ""))


if __name__ == "__main__":
    unittest.main()
