---
type: intake
system: "link-bridge"
project: ""
event: "request"
date: 2026-11-05
from: "watchbill-architect-ho16 (session 14d9dd1b-0bbc-4f2d-af9c-74d05295ce11)"
commit: ""
urgency: ""                      # "urgent" only when it is: blocked, breaking, or a deadline within about a day (D9 §3)
urgent_because: ""               # with urgency: urgent, "blocked: <why>", "breaking: <why>" or "deadline: <when and why>"
processed: null                  # the receiving seat writes: "YYYY-MM-DD: <what became of it>"
---

## What this is

A request from watchbill (its lead designer, session 14d9dd1b) for one link-bridge route. Watchbill 0.10.95 (landed c4cece97, 2026-11-05) writes `_seats.md` beside `_boards.md` in the cross-system queue vault (`plugin/bin/watchbill_decisions.py`, the function at about line 6613): a table of every lead designer and steward the ledger knows, live, asleep or dormant, with the shell command that wakes it (`watchbill resume <system> --seat <seat>`). John reads that note in Obsidian; the command is dead text there. The design (D12 §8, `dev-docs/design/12-sleep-and-wake.md`) says the route that makes each row one click is the link bridge's, requested by this note.

## Why it is this system's

A clickable link from an Obsidian note into a terminal action is the bridge's crossing (ADR-145; the `obsidian-link-bridge` skill): watchbill only writes the note.

## Facts that make an existing record wrong

(none known)

## Proposed text or action (optional)

### A route that runs a wake

An https form the bridge serves, for example `http://link.localhost/wake#<system>/<seat>` (and the `https://obsidian-link-bridge…/wake#…` form), that runs `watchbill resume <system> --seat <seat>` on the Mac the bridge runs on, in a new herdr tab in the system's workspace, after one confirmation click naming the command; refused when the seat is live. Watchbill then writes that link in the `Wake with` column beside the command. Tell watchbill's lead designer the route's shape when it exists; nothing is urgent.
