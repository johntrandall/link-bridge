#!/usr/bin/env python3
"""Open a folder in the Obsidian vault that holds it: the explorer expanded to that folder.

Run by the "Reveal in Finder" applet for reveal://obsidian?path=<folder> (0.1.14; the applet
decodes the link with reveal_decode.py first, so the path here is absolute, existing, and not
inside a bundle). Obsidian has no "reveal this folder" URI, so the handler does what a person does:

1. find the deepest registered vault (~/Library/Application Support/obsidian/obsidian.json)
   whose root contains the folder; a folder outside every vault is refused (exit 2);
2. pick a note inside the folder to open: README.md, then index.md, then the first *.md by name,
   then the first note in any subfolder; a folder with none opens the vault alone (exit 3 after
   opening, so the applet can say so);
3. `obsidian vault=<name> open path=<note> newtab`, then `command id=file-explorer:reveal-active-file`
   (the Obsidian CLI at /Applications/Obsidian.app/Contents/MacOS/obsidian; the vault opens if it
   was closed), then bring Obsidian forward.

A file given instead of a folder opens that file and reveals it. `--dry-run` prints the plan and
runs nothing. Log: ~/Library/Logs/reveal-in-finder.log (the applet writes it).
"""
import json
import os
import subprocess
import sys

REGISTRY = os.environ.get("OBSIDIAN_REGISTRY") or os.path.expanduser("~/Library/Application Support/obsidian/obsidian.json")
OBSIDIAN = os.environ.get("OBSIDIAN_BIN") or "/Applications/Obsidian.app/Contents/MacOS/obsidian"


def vault_for(path, registry=REGISTRY):
    """(vault name, vault root) for the deepest registered vault containing path, or None."""
    try:
        with open(registry, encoding="utf-8") as f:
            vaults = json.load(f).get("vaults") or {}
    except (OSError, ValueError, AttributeError):
        return None
    target = os.path.normpath(path)
    best = None
    for rec in vaults.values():
        root = rec.get("path") if isinstance(rec, dict) else None
        if not isinstance(root, str) or not root:
            continue
        root = os.path.normpath(root)
        if target == root or target.startswith(root.rstrip("/") + "/"):
            if best is None or len(root) > len(best):
                best = root
    return (os.path.basename(best), best) if best else None


def pick_note(folder):
    """A vault-relative-ready absolute path of the note to open for a folder, or None."""
    if os.path.isfile(folder):
        return folder
    try:
        names = sorted(os.listdir(folder))
    except OSError:
        return None
    for name in ("README.md", "index.md", "_index.md"):
        if name in names:
            return os.path.join(folder, name)
    notes = [n for n in names if n.lower().endswith(".md") and not n.startswith(".")]
    if notes:
        return os.path.join(folder, notes[0])
    for name in names:
        sub = os.path.join(folder, name)
        if os.path.isdir(sub) and not name.startswith("."):
            found = pick_note(sub)
            if found:
                return found
    return None


def plan(path, registry=REGISTRY):
    """{"vault", "root", "note" (vault-relative or None), "folder"} or None when outside every vault."""
    found = vault_for(path, registry)
    if not found:
        return None
    name, root = found
    note = pick_note(path)
    rel = os.path.relpath(note, root) if note else None
    return {"vault": name, "root": root, "note": rel, "folder": os.path.relpath(path, root) if path != root else "."}


def run(p):
    """Carry out a plan; returns 0 (note revealed) or 3 (vault opened, nothing to reveal)."""
    def cli(*args):
        subprocess.run([OBSIDIAN, f"vault={p['vault']}", *args], capture_output=True, text=True, timeout=30)
    if os.path.exists(OBSIDIAN) and p["note"]:
        cli("open", f"path={p['note']}", "newtab")
        cli("command", "id=file-explorer:reveal-active-file")
        code = 0
    else:
        import urllib.parse
        q = "vault=" + urllib.parse.quote(p["vault"], safe="")
        if p["note"]:
            q += "&file=" + urllib.parse.quote(p["note"][:-3] if p["note"].endswith(".md") else p["note"], safe="")
        subprocess.run(["/usr/bin/open", "obsidian://open?" + q], capture_output=True, timeout=10)
        if os.path.exists(OBSIDIAN):
            cli("command", "id=file-explorer:open")
        code = 0 if p["note"] else 3
    subprocess.run(["/usr/bin/open", "-a", "Obsidian"], capture_output=True, timeout=10)
    return code


def main(argv):
    dry = "--dry-run" in argv
    args = [a for a in argv[1:] if a != "--dry-run"]
    if len(args) != 1:
        print("usage: reveal_obsidian.py [--dry-run] <absolute path>", file=sys.stderr)
        return 2
    p = plan(args[0])
    if p is None:
        print("not inside a registered Obsidian vault", file=sys.stderr)
        return 2
    print(json.dumps(p))
    if dry:
        return 0 if p["note"] else 3
    return run(p)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
