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


if __name__ == "__main__":
    unittest.main()
