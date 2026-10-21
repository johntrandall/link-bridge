"""Run: python3 -I -m unittest discover -s test -p 'test_herdr_jump.py'"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "handler"))
import herdr_jump as hj  # noqa: E402

U = "d89e6d5a-8330-4b20-8650-cc1697929329"


class ParseSessionUrl(unittest.TestCase):
    def test_accepts_exactly_one_uuid(self):
        self.assertEqual(hj.parse_session_url(f"herdr-jump://session/{U}"), U)
        self.assertEqual(hj.parse_session_url(f"herdr-jump://session/{U}/"), U)
        self.assertEqual(hj.parse_session_url(f"herdr-jump://session/{U.upper()}"), U)

    def test_refuses_everything_else(self):
        for bad in ("", "herdr-jump://session/", "herdr-jump://session/../etc",
                    f"herdr-jump://session/{U}?x=1", f"herdr-jump://session/{U}&a",
                    f"herdr-jump://pane/{U}", f"reveal://session/{U}",
                    "herdr-jump://session/" + "z" * 36, f"herdr-jump://session/{U} ; rm -rf /",
                    f"herdr-jump://session/{U}\n"):
            self.assertIsNone(hj.parse_session_url(bad), bad)


class ParseWorkspaceUrl(unittest.TestCase):
    def test_id_form(self):
        self.assertEqual(hj.parse_workspace_url("herdr-jump://workspace/wBK"), ("id", "wBK"))
        self.assertEqual(hj.parse_workspace_url("herdr-jump://workspace/w7P/"), ("id", "w7P"))

    def test_label_form_decodes(self):
        self.assertEqual(hj.parse_workspace_url("herdr-jump://workspace/label/s-svc%20link-bridge"),
                         ("label", "s-svc link-bridge"))
        self.assertEqual(hj.parse_workspace_url("herdr-jump://workspace/label/%F0%9F%8C%99%20x"), ("label", "🌙 x"))

    def test_refuses_everything_else(self):
        for bad in ("", "herdr-jump://workspace/", "herdr-jump://workspace/BK", "herdr-jump://workspace/w",
                    "herdr-jump://workspace/w123456789", "herdr-jump://workspace/wBK?x=1",
                    "herdr-jump://workspace/wBK\n", "herdr-jump://workspace/label/", "herdr-jump://workspace/label/a%0Ab",
                    "herdr-jump://workspace/label/" + "x" * 81, "herdr-jump://workspace/label/%ff",
                    "herdr-jump://workspace/label/a/b", f"herdr-jump://workspace/{U}", "reveal://workspace/wBK"):
            self.assertIsNone(hj.parse_workspace_url(bad), bad)

    def test_session_links_are_not_workspace_links(self):
        self.assertIsNone(hj.parse_workspace_url(f"herdr-jump://session/{U}"))
        self.assertIsNone(hj.parse_session_url("herdr-jump://workspace/wBK"))


class LabelMatching(unittest.TestCase):
    def test_glyphs_and_case_are_ignored(self):
        self.assertEqual(hj.label_key("🌙 📦 s-svc link-bridge"), "s-svc link-bridge")
        self.assertEqual(hj.label_key("? 🔁 a-on readme"), "a-on readme")
        self.assertEqual(hj.label_key("↪ JOB automation → ho2"), "job automation → ho2")
        self.assertTrue(hj.label_matches("🌙 📦 s-svc link-bridge", "S-SVC Link-Bridge"))
        self.assertTrue(hj.label_matches("🌙 📦 s-svc link-bridge", "🌙 📦 s-svc link-bridge"))
        self.assertFalse(hj.label_matches("🌙 📦 s-svc link-bridge", "link-bridge"))
        self.assertEqual(hj.label_key("🌙"), "")
        self.assertFalse(hj.label_matches("🌙", "📦"))


if __name__ == "__main__":
    unittest.main()
