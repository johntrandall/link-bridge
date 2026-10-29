#!/usr/bin/env python3
"""Resolve a herdr-jump:// link: focus a Claude session's herdr tab, or focus a herdr workspace.

    herdr-jump://session/<claude-session-uuid>      -> `herdr tab focus <tab>` (the session's pane)
    herdr-jump://workspace/<workspace id>           -> `herdr workspace focus <id>`   (0.1.8)
    herdr-jump://workspace/label/<url-encoded label> -> the workspace whose tab-bar label matches,
                                                        lifecycle glyphs in front ignored, case-insensitive
    herdr-jump://owner/<claude-session-uuid>        -> the tab of whoever holds that session's SEAT now,
                                                        per `herdr-lifecycle owner <uuid> --json` (0.1.11)

Run by the "Jump to Session" applet (the Launch Services handler for the herdr-jump scheme), so
a link clicked in a browser, for example the /herdr-jump page of this bridge opened from a
Claude Code status line, lands on the right herdr tab. The same resolution lives in the
johntrandall.open-links herdr plugin for Ctrl+click inside a pane; keep the two in step.

Resolution:
1. `herdr agent list` names every live agent pane's Claude session id and tab id. A match is
   focused with `herdr tab focus <tab_id>`, which also switches the focused workspace.
2. Not live (0.1.9, asked by watchbill for its decision cards): the seat's current owner. The
   id's Claude name comes from herdr-lifecycle's role file (~/.local/state/herdr-lifecycle/
   roles/<sid>.json), its handoff ledger, or ~/.claude/sessions; `herdr-lifecycle siblings
   --all --json` then names the live members of that name's handoff chain (<base>, <base>-ho2,
   ...), and the highest -hoN that is live is focused, else any live member (the historian).
3. Still nothing: a /clear keeps a user-given session name but mints a new id, so the old id is
   looked up in ~/.claude/sessions/*.json; when that record has nameSource "user", the live
   pane whose own record carries the same name is focused instead.
4. Otherwise nothing is focused; a herdr notification says the session is gone.

`herdr_jump.py --resolve <url>` prints what would be focused and why, without focusing.

After a focus the terminal app hosting herdr is brought to the front (default Terminal; set
LINK_BRIDGE_TERMINAL_APP for iTerm2, Ghostty, ...), because the click came from a browser.

The link is untrusted input: the uuid and the workspace id must match strictly, a label is only ever
compared to `herdr workspace list` output, and nothing from the URL ever reaches a shell.
Log: ~/Library/Logs/jump-to-session.log
"""
import datetime
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.parse

UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
LINK = re.compile(r"herdr-jump://session/([0-9a-fA-F-]{36})/?")
OWNER_LINK = re.compile(r"herdr-jump://owner/([0-9a-fA-F-]{36})/?")
WORKSPACE_ID = re.compile(r"w[A-Za-z0-9]{1,8}")
WORKSPACE_LINK = re.compile(r"herdr-jump://workspace/(w[A-Za-z0-9]{1,8})/?")
WORKSPACE_LABEL_LINK = re.compile(r"herdr-jump://workspace/label/([^/?#]{1,400})/?")
LABEL_MAX = 80
HERDR = os.environ.get("HERDR_BIN_PATH") or "/opt/homebrew/bin/herdr"
SESSIONS = os.path.expanduser("~/.claude/sessions")
LIFECYCLE_STATE = os.environ.get("HERDR_LIFECYCLE_LEDGER_DIR") or os.path.expanduser("~/.local/state/herdr-lifecycle")
HERDR_LIFECYCLE = os.environ.get("HERDR_LIFECYCLE_BIN") or shutil.which("herdr-lifecycle") or os.path.expanduser("~/.local/bin/herdr-lifecycle")
HO_SUFFIX = re.compile(r"-ho(\d+)$")
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


def parse_owner_url(url):
    """The session uuid in a herdr-jump://owner/<uuid> link, lower-cased, or None."""
    m = OWNER_LINK.fullmatch(url or "")
    if not m:
        return None
    uuid = m.group(1).lower()
    return uuid if UUID.fullmatch(uuid) else None


def seat_owner(uuid):
    """`herdr-lifecycle owner <uuid> --json` as a dict (keys session_id, name, how, live, ...),
    or None when the tool is missing or its output is not JSON. Exit 3 (nobody) still returns
    the dict, with live false and session_id null."""
    try:
        out = subprocess.run([HERDR_LIFECYCLE, "owner", uuid, "--json"],
                             capture_output=True, text=True, timeout=15)
        data = json.loads(out.stdout) if out.stdout.strip() else None
        return data if isinstance(data, dict) else None
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def resolve_owner(uuid, agents, records):
    """(tab_id, reason) for the live holder of a session's seat, or (None, why)."""
    info = seat_owner(uuid)
    if info is None:
        return None, "herdr-lifecycle owner is not available on this Mac"
    owner_sid, name, how = info.get("session_id"), info.get("name") or "", info.get("how") or ""
    if not info.get("live") or not owner_sid:
        return None, how or f"nobody holds {name or uuid[:8]}'s seat"
    tabs = {sid: tab_id for sid, tab_id in agents if sid and tab_id}
    if owner_sid in tabs:
        return tabs[owner_sid], f"seat owner {name} ({how})"
    found = resolve_session(owner_sid, agents, records)
    if found:
        return found[0], f"seat owner {name} ({how}), via {found[1]}"
    return None, f"{name} holds the seat ({how}) but has no herdr pane"


def parse_workspace_url(url):
    """("id", <workspace id>) or ("label", <label text>) for a herdr-jump://workspace/… link, else None."""
    m = WORKSPACE_LINK.fullmatch(url or "")
    if m:
        return ("id", m.group(1))
    m = WORKSPACE_LABEL_LINK.fullmatch(url or "")
    if not m:
        return None
    try:
        label = urllib.parse.unquote(m.group(1), errors="strict")
    except UnicodeDecodeError:
        return None
    if not label or len(label) > LABEL_MAX or any(ord(c) < 0x20 or ord(c) == 0x7F for c in label):
        return None
    return ("label", label)


def label_key(label):
    """A workspace label with its leading lifecycle/category glyph tokens dropped, case-folded:
    "🌙 📦 s-svc link-bridge" -> "s-svc link-bridge". A token counts as a glyph when it has no
    ASCII letter or digit, so "? 🔁 a-on readme" also reduces to "a-on readme"."""
    words = str(label or "").split()
    while words and not re.search(r"[A-Za-z0-9]", words[0]):
        words.pop(0)
    return " ".join(words).casefold()


def label_matches(label, wanted):
    key = label_key(wanted)
    return label == wanted or (bool(key) and label_key(label) == key)


def workspaces():
    data = json.loads(herdr("workspace", "list"))
    return data.get("result", data).get("workspaces", [])


def find_workspace(kind, value):
    """The workspace id for an id or label, or None. An exact label wins over a glyph-stripped match."""
    rows = workspaces()
    if kind == "id":
        return next((w["workspace_id"] for w in rows if w.get("workspace_id") == value), None)
    exact = [w for w in rows if w.get("label") == value]
    loose = exact or [w for w in rows if label_matches(w.get("label", ""), value)]
    return loose[0]["workspace_id"] if loose else None


def focus_workspace(workspace_id):
    herdr("workspace", "focus", workspace_id)
    if subprocess.run(["/usr/bin/pgrep", "-xq", TERMINAL_APP], capture_output=True).returncode == 0:
        subprocess.run(["/usr/bin/open", "-a", TERMINAL_APP], capture_output=True)


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


def chain_base(name):
    """"x-ho3" -> "x"; "x" -> "x"."""
    return HO_SUFFIX.sub("", name or "")


def ho_number(name):
    """"x-ho3" -> 3; "x" -> 0 (the origin of a chain)."""
    m = HO_SUFFIX.search(name or "")
    return int(m.group(1)) if m else 0


def name_for_session(uuid, records=None):
    """The Claude name of a session id, live or exited: herdr-lifecycle's role file, then its
    handoff ledger (spawn/adopt rows carry session_id+name, handoff/relieve rows origin and
    receiver), then the ~/.claude/sessions record. None when nothing names it."""
    try:
        with open(os.path.join(LIFECYCLE_STATE, "roles", f"{uuid}.json")) as f:
            name = json.load(f).get("name")
        if name:
            return name
    except (OSError, ValueError, AttributeError):
        pass
    try:
        with open(os.path.join(LIFECYCLE_STATE, "handoffs.jsonl")) as f:
            for line in f:
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                if row.get("session_id") == uuid and row.get("name"):
                    return row["name"]
                if row.get("origin_sid") == uuid and row.get("origin_name"):
                    return row["origin_name"]
                if row.get("receiver_sid") == uuid and row.get("receiver_name"):
                    return row["receiver_name"]
    except OSError:
        pass
    rec = (records or {}).get(uuid) or {}
    return rec.get("name") or None


def siblings():
    """{"sessions": [...], "chains": {base: [live member names]}} from herdr-lifecycle, or None."""
    try:
        out = subprocess.run([HERDR_LIFECYCLE, "siblings", "--all", "--json"],
                             capture_output=True, text=True, timeout=15)
        return json.loads(out.stdout) if out.returncode == 0 else None
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def pick_owner(name, chains, sessions):
    """(session_id, owner_name, reason) of the live session that now holds `name`'s seat:
    the highest -hoN of its handoff chain that is live, else any live chain member (the
    historian), else a live session with the same name (/clear). None when nothing is live.
    Pure: `chains` and `sessions` are herdr-lifecycle siblings output."""
    live = {}
    for row in sessions or []:
        cname, sid = row.get("claude_name"), row.get("session_id")
        if cname and sid and (cname not in live or ho_number(cname) > ho_number(live[cname])):
            live[cname] = sid
    base = chain_base(name)
    members = set((chains or {}).get(base) or []) | {base, name}
    members |= {n for n in live if chain_base(n) == base}
    ranked = sorted((n for n in members if n in live), key=ho_number, reverse=True)
    if not ranked:
        return None
    owner = ranked[0]
    if owner == name:
        return live[owner], owner, "same name is live"
    if ho_number(owner) > ho_number(name):
        return live[owner], owner, f"{name} handed off; {owner} owns the seat"
    return live[owner], owner, f"{name} is gone; {owner} is the live member of its chain"


def live_agents():
    data = json.loads(herdr("agent", "list"))
    agents = data.get("result", data).get("agents", [])
    return [((a.get("agent_session") or {}).get("value"), a.get("tab_id")) for a in agents]


def focus(tab_id):
    herdr("tab", "focus", tab_id)
    # The click came from a browser; bring the terminal that hosts herdr forward.
    if subprocess.run(["/usr/bin/pgrep", "-xq", TERMINAL_APP], capture_output=True).returncode == 0:
        subprocess.run(["/usr/bin/open", "-a", TERMINAL_APP], capture_output=True)


def resolve_session(uuid, agents, records):
    """(tab_id, reason) for a session uuid: its own live pane, the current owner of its seat
    (herdr-lifecycle chain), or a live pane with the same user-given name. None when gone."""
    tabs = {sid: tab_id for sid, tab_id in agents if sid and tab_id}
    if uuid in tabs:
        return tabs[uuid], "live"
    name = name_for_session(uuid, records)
    if name:
        sib = siblings()
        if sib:
            owner = pick_owner(name, sib.get("chains"), sib.get("sessions"))
            if owner and owner[0] in tabs:
                return tabs[owner[0]], f"via herdr-lifecycle: {owner[2]} ({owner[0][:8]})"
    wanted = records.get(uuid)
    if wanted and wanted.get("nameSource") == "user" and wanted.get("name"):
        for sid, tab_id in agents:
            rec = records.get(sid)
            if rec and rec.get("nameSource") == "user" and rec.get("name") == wanted["name"] and tab_id:
                return tab_id, f"via name {wanted['name']!r} -> {sid[:8]}"
    return None


def main(argv):
    dry = len(argv) > 1 and argv[1] == "--resolve"
    if dry:
        argv = argv[1:]
    url = argv[1] if len(argv) > 1 else os.environ.get("HERDR_PLUGIN_CLICKED_URL", "")
    wanted_ws = parse_workspace_url(url)
    if wanted_ws:
        kind, value = wanted_ws
        workspace_id = find_workspace(kind, value)
        if dry:
            print(f"{workspace_id or 'none'} workspace {kind}={value!r}")
            return 0 if workspace_id else 1
        if not workspace_id:
            notify("Workspace gone", f"no herdr workspace with {kind} {value[:40]!r}")
            log(f"workspace not found {kind}={value!r}")
            return 1
        focus_workspace(workspace_id)
        log(f"focused workspace {workspace_id} for {kind}={value!r}")
        return 0
    owner_of = parse_owner_url(url)
    if owner_of:
        tab_id, reason = resolve_owner(owner_of, live_agents(), session_records())
        if dry:
            print(f"{tab_id or 'none'} {reason}")
            return 0 if tab_id else 1
        if not tab_id:
            notify("Nobody holds that seat", reason[:120])
            log(f"owner not found for {owner_of}: {reason}")
            return 1
        focus(tab_id)
        log(f"focused {tab_id} for owner of {owner_of} ({reason})")
        return 0
    uuid = parse_session_url(url)
    if not uuid:
        log(f"refused {url!r}")
        return 3
    agents = live_agents()
    records = session_records()
    found = resolve_session(uuid, agents, records)
    if found:
        tab_id, reason = found
        if dry:
            print(f"{tab_id} {reason}")
            return 0
        focus(tab_id)
        log(f"focused {tab_id} for {uuid} ({reason})")
        return 0
    name = name_for_session(uuid, records)
    who = f"{name} ({uuid[:8]})" if name else uuid[:8]
    if dry:
        print(f"none: {who} is not in any live herdr pane and its seat has no live owner")
        return 1
    notify("Session gone", f"{who} is not in any live herdr pane, and its seat has no live owner")
    log(f"not found {uuid} ({who})")
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Exception as e:  # noqa: BLE001
        log(f"error {e}")
        notify("Jump to Session failed", str(e)[:120])
        sys.exit(1)
