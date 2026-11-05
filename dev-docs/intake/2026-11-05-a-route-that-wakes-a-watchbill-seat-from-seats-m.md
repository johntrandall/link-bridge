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
processed: "2026-11-05: shipped in link-bridge 0.1.15 (landed adbc77a, tag v0.1.15; John approved the shape 17:10 in chat): /wake#<system>/<seat>, a page with one button that POSTs /act/wake and runs watchbill resume; reply below"                  # the receiving seat writes: "YYYY-MM-DD: <what became of it>"
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

## Reply (link-bridge, 2026-11-05)

Shipped in link-bridge 0.1.15 (`adbc77a`, tag `v0.1.15`, tap formula updated, installed on SusanBones). The shape:

- **Link:** `http://link.localhost/wake#<system>/<seat>` (seat defaults to `lead-designer`; a session name such as `outreach-steward-ho3` is a seat too) or `#system=…&seat=…`. Off the Mac, the same path on the tailnet names (`http://susanbones.flicker-duckbill.ts.net:5465/wake#…`) and the https bridge form. Both names are slugs `[a-z0-9][a-z0-9._-]{0,63}`.
- **What happens:** the page shows the exact command, `watchbill resume <system> --seat <seat>`, and one button, **Wake it on the Mac**. Nothing runs until it is pressed; the button then POSTs `/act/wake {"system","seat"}` and the bridge runs that fixed argv. 200 carries watchbill's own line (`woke … as session …`); 409 carries watchbill's refusal (unknown system, nothing of that name asleep, live seat, hard line) or the bridge's (a wake already running on the Mac; the same seat woken within the last 60 s); 501 when watchbill is not installed; 504 after 300 s.
- **No `herdr-jump://` form, on purpose:** this is the only bridge action that starts an agent, so there is no scheme another page or app could emit; the open-links plugin is unchanged (herdr opens the http link itself).
- **Security (cold Opus verdict, `dev-docs/runs/2026-11-05-wake/security-verdict.md`):** the usual header gate plus, new in 0.1.15 for every `POST /act/…`, a Host allowlist against DNS rebinding, and the wake lock and cooldown above.
- **Consumer check:** `GET /routes` lists `/wake` and `/act/wake` from 0.1.15.

One finding for watchbill (the verifier's item 5): nothing in watchbill serialises a bridge wake with the board daemon's own wake of the same seat inside the spawn window; the bridge holds its own lock, but a lock in `cmd_resume` / `wake()` would close the race on watchbill's side.
