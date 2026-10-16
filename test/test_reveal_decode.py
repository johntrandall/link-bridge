"""Run: python3 -I -m unittest discover -s test -p 'test_reveal_decode.py'"""
import os
import sys
import tempfile
import unittest
import urllib.parse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "handler"))
import reveal_decode as rd  # noqa: E402


def link(path, **extra):
    q = "path=" + urllib.parse.quote(path, safe="")
    for k, v in extra.items():
        q += "&" + k + "=" + urllib.parse.quote(v, safe="")
    return "reveal://reveal?" + q


class RevealDecode(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="reveal-")
        self.note = os.path.join(self.tmp, "n o t e + café.md")
        open(self.note, "w").close()
        self.app = os.path.join(self.tmp, "Thing.app", "Contents")
        os.makedirs(self.app)
        open(os.path.join(self.app, "Info.plist"), "w").close()

    def test_existing_file_and_directory(self):
        self.assertEqual(rd.decode(link(self.note)), os.path.realpath(self.note))
        self.assertEqual(rd.decode(link(self.tmp)), os.path.realpath(self.tmp))

    def test_bundle_itself_ok_but_not_its_innards(self):
        bundle = os.path.dirname(self.app)
        self.assertEqual(rd.decode(link(bundle)), os.path.realpath(bundle))
        self.assertIsNone(rd.decode(link(os.path.join(self.app, "Info.plist"))))

    def test_refusals(self):
        self.assertIsNone(rd.decode("reveal://reveal?path=absent-in-home-9f1"))  # relative, missing
        self.assertIsNone(rd.decode(link(os.path.join(self.tmp, "absent"))))   # missing
        self.assertIsNone(rd.decode(link(self.note, open="1")))                # extra parameter
        self.assertIsNone(rd.decode("reveal://reveal?path=" + urllib.parse.quote(self.note, safe="") + "&path=%2Ftmp"))
        self.assertIsNone(rd.decode("reveal://open?path=%2Ftmp"))              # wrong host
        self.assertIsNone(rd.decode("file:///tmp"))                            # wrong scheme
        self.assertIsNone(rd.decode(link(self.tmp + "/\n")))                   # control char
        self.assertIsNone(rd.decode("reveal://reveal"))                        # no parameter
        self.assertIsNone(rd.decode("reveal://reveal?path="))                  # empty

    def test_relative_path_is_under_home(self):
        caches = os.path.join(rd.HOME, "Library", "Caches")
        if not os.path.isdir(caches):
            self.skipTest("no ~/Library/Caches to make a home-relative folder in")
        d = tempfile.mkdtemp(prefix="reveal-rel-", dir=caches)
        try:
            rel = os.path.relpath(d, rd.HOME)
            self.assertEqual(rd.decode("reveal://reveal?path=" + urllib.parse.quote(rel, safe="/")), os.path.realpath(d))
            self.assertEqual(rd.decode("reveal://reveal?path=" + urllib.parse.quote("~/" + rel, safe="/")), os.path.realpath(d))
        finally:
            os.rmdir(d)

    def test_symlink_is_resolved_before_checks(self):
        ln = os.path.join(self.tmp, "ln.plist")
        os.symlink(os.path.join(self.app, "Info.plist"), ln)
        self.assertIsNone(rd.decode(link(ln)))


if __name__ == "__main__":
    unittest.main()
