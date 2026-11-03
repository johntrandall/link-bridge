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


class ObsidianHost(unittest.TestCase):
    def test_obsidian_host_decodes_like_reveal(self):
        home = os.path.expanduser("~")
        self.assertEqual(rd.decode("reveal://obsidian?path=" + urllib.parse.quote(home, safe="")), os.path.realpath(home))
        self.assertEqual(rd.host("reveal://obsidian?path=x"), "obsidian")
        self.assertEqual(rd.host("reveal://reveal?path=x"), "reveal")
        self.assertIsNone(rd.decode("reveal://finder?path=" + urllib.parse.quote(home, safe="")))
        self.assertIsNone(rd.host("reveal://finder?path=x"))


class RevealObsidianPlan(unittest.TestCase):
    def setUp(self):
        import json as _json
        import reveal_obsidian as ro
        self.ro = ro
        self.tmp = tempfile.mkdtemp()
        self.vault = os.path.join(self.tmp, "myvault"); os.makedirs(os.path.join(self.vault, "runs", "r1", "sub"))
        os.makedirs(os.path.join(self.vault, "empty"))
        open(os.path.join(self.vault, "runs", "r1", "zeta.md"), "w").close()
        open(os.path.join(self.vault, "runs", "r1", "alpha.md"), "w").close()
        open(os.path.join(self.vault, "runs", "r1", "sub", "deep.md"), "w").close()
        os.makedirs(os.path.join(self.vault, "runs", "r2", "sub")); open(os.path.join(self.vault, "runs", "r2", "sub", "only.md"), "w").close()
        os.makedirs(os.path.join(self.vault, "runs", "r3")); open(os.path.join(self.vault, "runs", "r3", "README.md"), "w").close()
        open(os.path.join(self.vault, "runs", "r3", "aaa.md"), "w").close()
        self.registry = os.path.join(self.tmp, "obsidian.json")
        with open(self.registry, "w") as f:
            _json.dump({"vaults": {"a": {"path": self.vault}, "b": {"path": self.tmp}}}, f)

    def test_deepest_vault_and_note_choice(self):
        p = self.ro.plan(os.path.join(self.vault, "runs", "r1"), self.registry)
        self.assertEqual((p["vault"], p["note"], p["folder"]), ("myvault", "runs/r1/alpha.md", "runs/r1"))
        self.assertEqual(self.ro.plan(os.path.join(self.vault, "runs", "r3"), self.registry)["note"], "runs/r3/README.md")
        self.assertEqual(self.ro.plan(os.path.join(self.vault, "runs", "r2"), self.registry)["note"], "runs/r2/sub/only.md")
        self.assertIsNone(self.ro.plan(os.path.join(self.vault, "empty"), self.registry)["note"])
        self.assertEqual(self.ro.plan(os.path.join(self.vault, "runs", "r1", "zeta.md"), self.registry)["note"], "runs/r1/zeta.md")
        self.assertEqual(self.ro.plan(self.vault, self.registry)["folder"], ".")

    def test_outside_every_vault(self):
        self.assertIsNone(self.ro.plan("/", self.registry))
        self.assertIsNone(self.ro.plan(self.tmp + "x", self.registry))


if __name__ == "__main__":
    unittest.main()
