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


class ParseOwnerUrl(unittest.TestCase):
    def test_accepts_exactly_one_uuid(self):
        self.assertEqual(hj.parse_owner_url(f"herdr-jump://owner/{U}"), U)
        self.assertEqual(hj.parse_owner_url(f"herdr-jump://owner/{U.upper()}/"), U)

    def test_refuses_everything_else(self):
        for bad in ("", "herdr-jump://owner/", f"herdr-jump://owner/{U}?x=1", f"herdr-jump://session/{U}",
                    "herdr-jump://owner/" + "z" * 36, f"herdr-jump://owner/{U}\n", f"herdr-jump://owner/{U}/../x"):
            self.assertIsNone(hj.parse_owner_url(bad), bad)
        self.assertIsNone(hj.parse_session_url(f"herdr-jump://owner/{U}"))
        self.assertIsNone(hj.parse_workspace_url(f"herdr-jump://owner/{U}"))


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


class ChainOwner(unittest.TestCase):
    """pick_owner over herdr-lifecycle siblings output: who holds the seat of an exited session."""
    SESSIONS = [
        {"claude_name": "statusline-links-ho3", "session_id": "39b3a7c4-0000-4000-8000-000000000003"},
        {"claude_name": "resume-steward-ho2", "session_id": "aaaaaaaa-0000-4000-8000-000000000002"},
        {"claude_name": "resume-steward", "session_id": "aaaaaaaa-0000-4000-8000-000000000001"},
        {"claude_name": "lonely", "session_id": "bbbbbbbb-0000-4000-8000-000000000001"},
    ]
    CHAINS = {"statusline-links": ["statusline-links-ho3"], "resume-steward": ["resume-steward", "resume-steward-ho2"]}

    def test_names(self):
        self.assertEqual(hj.chain_base("x-ho12"), "x")
        self.assertEqual(hj.chain_base("x"), "x")
        self.assertEqual(hj.ho_number("x-ho12"), 12)
        self.assertEqual(hj.ho_number("x"), 0)
        self.assertEqual(hj.chain_base("x-ho2-ho3"), "x-ho2")

    def test_exited_origin_goes_to_the_highest_live_successor(self):
        sid, owner, _ = hj.pick_owner("statusline-links-ho2", self.CHAINS, self.SESSIONS)
        self.assertEqual((sid[-1], owner), ("3", "statusline-links-ho3"))
        sid, owner, _ = hj.pick_owner("statusline-links", self.CHAINS, self.SESSIONS)
        self.assertEqual(owner, "statusline-links-ho3")

    def test_live_origin_still_yields_the_owner_not_the_historian(self):
        sid, owner, reason = hj.pick_owner("resume-steward", self.CHAINS, self.SESSIONS)
        self.assertEqual(owner, "resume-steward-ho2")
        self.assertIn("owns the seat", reason)

    def test_same_name_live_is_the_clear_case(self):
        sid, owner, reason = hj.pick_owner("lonely", {}, self.SESSIONS)
        self.assertEqual((owner, reason), ("lonely", "same name is live"))

    def test_chain_members_found_without_a_chains_entry(self):
        sid, owner, _ = hj.pick_owner("resume-steward-ho1", None, self.SESSIONS)
        self.assertEqual(owner, "resume-steward-ho2")

    def test_nothing_live(self):
        self.assertIsNone(hj.pick_owner("ghost-ho4", {"ghost": []}, self.SESSIONS))
        self.assertIsNone(hj.pick_owner("ghost", None, []))


if __name__ == "__main__":
    unittest.main()
