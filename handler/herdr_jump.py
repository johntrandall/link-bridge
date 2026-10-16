#!/usr/bin/env python3
"""Resolve a herdr-jump://session/<claude-session-uuid> link and focus that session's herdr tab.

Run by the "Jump to Session" applet (the Launch Services handler for the herdr-jump scheme), so
a link clicked in a browser, for example the /herdr-jump page of this bridge opened from a
Claude Code status line, lands on the right herdr tab. The same resolution lives in the
johntrandall.open-links herdr plugin for Ctrl+click inside a pane; keep the two in step.

Resolution:
1. `herdr agent list` names every live agent pane's Claude session id and tab id. A match is
   focused with `herdr tab focus <tab_id>`, which also switches the focused workspace.
2. Not live: a /clear keeps a user-given session name but mints a new id, so the old id is
   looked up in ~/.claude/sessions/*.json; when that record has nameSource "user", the live
   pane whose own record carries the same name is focused instead.
3. Otherwise nothing is focused; a herdr notification says the session is gone.

After a focus the terminal app hosting herdr is brought to the front (default Terminal; set
LINK_BRIDGE_TERMINAL_APP for iTerm2, Ghostty, ...), because the click came from a browser.

The link is untrusted input: the uuid must match strictly, and nothing from the URL ever reaches
a shell. Log: ~/Library/Logs/jump-to-session.log
"""
import datetime
import glob
import json
import os
import re
import subprocess
import sys

UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
LINK = re.compile(r"herdr-jump://session/([0-9a-fA-F-]{36})/?")
HERDR = os.environ.get("HERDR_BIN_PATH") or "/opt/homebrew/bin/herdr"
SESSIONS = os.path.expanduser("~/.claude/sessions")
LOG = os.path.expanduser("~/Library/Logs/jump-to-session.log")
TERMINAL_APP = os.environ.get("LINK_BRIDGE_TERMINAL_APP", "Terminal")


def log(msg):
    try:
        with open(LOG, "a") as f:
            f.write(f"{datetime.datetime.now():%Y-%m-%dT%H:%M:%S} {msg}\n")
    except OSError:
        pass


def herdr(*args):
    out = subprocess.run([HERDR, *args], capture_output=True, text=True, timeout=20)
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip() or out.stdout.strip() or f"herdr {' '.join(args)} failed")
    return out.stdout


def notify(title, body):
    try:
        herdr("notification", "show", title, "--body", body)
    except Exception as e:  # noqa: BLE001
        log(f"notify failed: {e}")


def parse_session_url(url):
    """The session uuid in a herdr-jump://session/<uuid> link, lower-cased, or None."""
    # fullmatch, not match + "$": "$" also matches before a trailing newline.
    m = LINK.fullmatch(url or "")
    if not m:
        return None
    uuid = m.group(1).lower()
    return uuid if UUID.fullmatch(uuid) else None


def session_records():
    records = {}
    for path in glob.glob(os.path.join(SESSIONS, "*.json")):
        try:
            with open(path) as f:
                rec = json.load(f)
        except (OSError, ValueError):
            continue
        if isinstance(rec, dict) and rec.get("sessionId"):
            records[rec["sessionId"]] = rec
    return records


def live_agents():
    data = json.loads(herdr("agent", "list"))
    agents = data.get("result", data).get("agents", [])
    return [((a.get("agent_session") or {}).get("value"), a.get("tab_id")) for a in agents]


def focus(tab_id):
    herdr("tab", "focus", tab_id)
    # The click came from a browser; bring the terminal that hosts herdr forward.
    if subprocess.run(["/usr/bin/pgrep", "-xq", TERMINAL_APP], capture_output=True).returncode == 0:
        subprocess.run(["/usr/bin/open", "-a", TERMINAL_APP], capture_output=True)


def main(argv):
    url = argv[1] if len(argv) > 1 else os.environ.get("HERDR_PLUGIN_CLICKED_URL", "")
    uuid = parse_session_url(url)
    if not uuid:
        log(f"refused {url!r}")
        return 3
    agents = live_agents()
    for sid, tab_id in agents:
        if sid == uuid and tab_id:
            focus(tab_id)
            log(f"focused {tab_id} for {uuid}")
            return 0
    records = session_records()
    wanted = records.get(uuid)
    if wanted and wanted.get("nameSource") == "user" and wanted.get("name"):
        name = wanted["name"]
        for sid, tab_id in agents:
            rec = records.get(sid)
            if rec and rec.get("nameSource") == "user" and rec.get("name") == name and tab_id:
                focus(tab_id)
                log(f"focused {tab_id} for {uuid} via name {name!r} -> {sid}")
                return 0
        notify("Session gone", f"{name} ({uuid[:8]}) is not in any live herdr pane")
    else:
        notify("Session gone", f"{uuid[:8]} is not in any live herdr pane")
    log(f"not found {uuid}")
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Exception as e:  # noqa: BLE001
        log(f"error {e}")
        notify("Jump to Session failed", str(e)[:120])
        sys.exit(1)
