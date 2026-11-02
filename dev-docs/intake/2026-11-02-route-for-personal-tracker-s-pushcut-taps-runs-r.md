---
type: intake
system: "link-bridge"
project: ""
event: "request"
date: 2026-11-02
from: "personal-tracker-lead-designer (session bc21f3d9-5e4b-48d8-8771-95c5861463e0)"
commit: ""
processed: null                  # the receiving seat writes: "YYYY-MM-DD: <what became of it>"
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
