---
type: intake
system: "link-bridge"
project: ""
event: "request"
date: 2026-10-29
from: "watchbill-rules-release (session 4262baa8-0929-40d8-836e-8221aa83de00)"
commit: ""
processed: null                  # the receiving seat writes: "YYYY-MM-DD: <what became of it>"
---

**Start here.** This is a request from the watchbill plugin (its rules seat, `watchbill-rules-release`, on the word of its architect `watchbill-architect-ho8`, 2026-10-29) for one new link-bridge route. Watchbill's decision cards are read in Obsidian, where only http links work, so their links go through link-bridge. Each card will carry two links at the top. One is "talk to the agent that wrote this", which today's `/herdr-jump#<session>` route serves. The other is "talk to the seat that holds it now", which no route serves today.

**Terms.**
- **Seat**: a role in a watchbill system (architect, steward, rules seat, and so on), held by one Claude session at a time.
- **Handoff chain**: when a session hands its seat to a successor, the successor is named `<name>-ho2`, then `-ho3`, and so on. The earlier sessions become *historians*, which often stay open, live, answering only questions about the past.
- **`herdr-lifecycle owner <session-id> --json`**: a read-only command (watchbill 0.10.76, no herdr needed) that says who owns a session's work now. That is the session itself while it is live and not relieved; else the head of its relieve chain when live; else the receiver of its unrelieved handoff when live; else the highest live `-hoN` of its name; else the live doorbell seat of its system. With none, exit 3. Its JSON carries `session_id` (the owner's), `name`, `how`, `live` and `asked`.

**The problem.** `/herdr-jump#<session>` runs herdr-open-links' `herdr-jump.py`, which focuses the given session's own tab whenever that session is live. It falls back to the highest live `-hoN` of the chain only when the session is gone. A historian that is still open therefore catches the click, which is the case the human named.

**The human's words** (John, 2026-10-29 09:53, on watchbill's TALK TO card, verbatim): "I think this information is better put on the card itself as a call out on the top of each card on the board. Click here to talk to the agent that wrote this and click here to talk to the seat that wrote this in case the seat has rolled on and the agent that originally wrote it has become a historian. I don't think that we need this in the CLI at the system level."

**The request.** A route that resolves the seat's owner at click time:
- `http://link.localhost/herdr-owner#<claude-session-uuid>` (the name is yours to choose; tell us what you pick).
- The route runs `herdr-lifecycle owner <uuid> --json` and focuses the tab of the `session_id` it returns, the way `/herdr-jump` focuses a session (`herdr-jump://session/<owner sid>`).
- On exit 3, or when `live` is false, it shows the same "nobody holds it" notice `/herdr-jump` shows when it finds nothing.
- A `/healthz` or consumer-contract line naming the route, so watchbill can tell when it is installed.

**What watchbill does meanwhile.** From 0.10.78, the second link points at `/herdr-jump#<owner sid>`, with the owner resolved by `herdr-lifecycle owner` when the card is written. It can go stale between writes; `watchbill decisions your-move` refreshes it. Once your route lands, watchbill switches the second link to it, and a `your-move` refresh rewrites every card.

**Also wanted, outside link-bridge (not filed there):** herdr-open-links (`~/dev/herdr-open-links`, the owner of `herdr-jump.py`) is not a registered watchbill system, so no note went there. If your route needs a `herdr-jump://owner/<uuid>` form in `herdr-jump.py`, watchbill's architect is the one to raise it.
