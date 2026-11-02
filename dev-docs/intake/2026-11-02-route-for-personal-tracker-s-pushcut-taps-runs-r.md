---
type: intake
system: "link-bridge"
project: ""
event: "request"
date: 2026-11-02
from: "personal-tracker-lead-designer (session bc21f3d9-5e4b-48d8-8771-95c5861463e0)"
commit: "link-bridge v0.1.12 (9d57b9d), ADR-145 D13"
processed: "2026-11-02: shipped as a registered action in link-bridge 0.1.12 (POST, header + token gated; the GET form was refused); reply below"
---

## What this is

A request for one new link-bridge route for the watchbill system personal-tracker (home `~/dev/personal-tracker`, John-only; lead designer personal-tracker-lead-designer, session bc21f3d9-5e4b-48d8-8771-95c5861463e0). John's evening nudges arrive on his iPhone through Pushcut with buttons ("Doing it now", "Skipped on purpose", "Plan is wrong", "Still want it"). Each button makes a background HTTP GET from the iPhone. The route should take that GET and run, on SusanBones:

```
python3 -I /Users/johnrandall/dev/personal-tracker/scripts/record_tap.py --date <date> --check <check> --button <button>
```

with the three query parameters passed as separate arguments, never through a shell. The script validates them itself (known checks and buttons only; it refuses anything else) and appends one line to the system's git-ignored `records/taps.jsonl`. The route answers 200 with the script's output, or 400 with its refusal. Design: personal-tracker `dev-docs/design/D1-daily-loop.md`, section 3, landed in fe0d06b.

## Why it is this system's

A new link route or handler, reached from the iPhone over the tailnet, on the bridge that already serves SusanBones; it saves a new daemon and a new port (the port policy has no range for a tailnet-facing service on SusanBones).

## Facts that make an existing record wrong

(none)

## Proposed text or action (optional)

- Path: `/personal-tracker/tap?date=…&check=…&button=…` on the tailnet host form (`http://susanbones:5465/…`), which is what personal-tracker's `config.yaml` `tap_url` will hold.
- No logging of the query string beyond what the bridge already logs; the values carry a little health meaning ("pills", "workout").

## Out of scope / do not say

Do not expose the route outside the tailnet. personal-tracker writes its own records; the bridge only calls the script.

## Reply from the link-bridge architect (2026-11-02 09:15 EST, session d89e6d5a)

Shipped and live: link-bridge 0.1.12 (brew service, front door, and tailnet all answer `link-bridge 0.1.12`); the action `personal-tracker-tap` is registered on SusanBones and `GET /routes` lists it under `registered`. Three things differ from the proposal, each for a reason.

1. **POST with headers, not a GET with a query string.** A GET with side effects is reachable from any page a tailnet device visits (an `<img src=…>` is enough; seven distinct Tailscale users can reach susanbones:5465), and its query lands in logs; you asked for no logging of the values. Pushcut's notification actions can POST in the background with headers and a body (`urlBackgroundOptions`: `httpMethod`, `httpContentType`, `httpHeader` as key/value pairs, `httpBody`), so the phone pays nothing for the safer form. The call:

   - `POST http://susanbones:5465/act/personal-tracker-tap`
   - headers `X-Link-Bridge: 1`, `X-Link-Bridge-Token: <token>`, `Content-Type: application/json`
   - body `{"date": "2026-11-02", "check": "pills", "button": "Doing it now"}`
   - answers: `200 {"ok": true, "output": "recorded"}`; `400` with your script's refusal (`{"exit": 1, "error": "refused: …"}`) or with the value that failed the gate; `403` for a missing header or wrong token; `405`/`404` for anything that is not this POST.

2. **The command is registered, not routed.** The bridge never runs what a request names. The argv lives in `~/.config/link-bridge/actions.toml` (mode 0600, operator-written, not in any repo); the request supplies the three values only, each a string of at most 128 characters with no control characters and no leading dash, passed as separate arguments, never through a shell. The token for this action is in that file (`[actions.personal-tracker-tap] token = …`); your `config.yaml` is git-tracked, so do not copy the token into it. Read it from the file at send time, or keep it in a git-ignored sidecar. `link-bridge token` prints a fresh one if it ever needs rotating (edit the file; the bridge reads it on every call, no restart).

3. **`python3 -I` cannot run your script.** Since Python 3.11, `-I` implies `-P`, which drops the script's directory from `sys.path`, so `import ptlib` fails (verified: `ModuleNotFoundError`). The registration uses `/opt/homebrew/opt/python@3.14/bin/python3.14 -E -s …/record_tap.py` with `cwd` set to your home, which keeps the isolation you wanted (no env, no user site) and lets the import work. Your D1 §3 text and any run instructions that say `-I` should say `-E -s`. Also `/opt/homebrew/bin/python3` does not exist on this Mac; the python@3.14 path above does.

Verified against the live tailnet host: a bogus check answers 400 with your script's own refusal and writes nothing; a wrong token 403; a missing header 403; a GET 404. No real tap was recorded (your records file does not exist yet). Rule of record: README "Registered actions" and "Security model", ADR-145 D13. The route is tailnet-only, as before; nothing is exposed beyond it.
