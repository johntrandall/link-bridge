---
type: intake
system: "link-bridge"
project: ""
event: "request"
date: 2026-10-29
from: "watchbill-architect-ho8 (session d9813d96-c2ce-4c90-b235-e1398c65a61c)"
commit: ""
processed: null                  # the receiving seat writes: "YYYY-MM-DD: <what became of it>"
---

## What this is

Watchbill 0.10.79's `watchbill systems list --switches` shows an AUTO-SHIP column: a system's standing autonomy (watchbill design D9 §6), read from a decision card in the system's own board whose `question` contains "ship updates without" and whose answer is yes. John asked for it to be turned on where it should be. John, 2026-10-29 15:29:25, in the watchbill architect's tab (watchbill-architect-ho8), verbatim: "I see that the release auto ship is off for most projects Launch an agent to take a look at them all and figure out which ones it should be on for and then just turn those on."

A reader assessed all 21 deterministic systems: `~/dev/claude-plugin-watchbill/dev-docs/runs/2026-10-29-auto-ship/assessment.md` (watchbill ec0364ad). It recommends this system: **on**: John's standing grant of 2026-10-16 18:05 (your dev-docs/decisions.md line 6) already covers it, and 0.1.7 to 0.1.11 shipped under it; the listing cannot see it because no card's question names "ship updates without".

This is a relay of John's words from outside your system: record what your own rules allow. If they need his yes in your own tab, ask him there; he expects a few one-line confirmations.

## Why it is this system's

The card lives in this system's board, and only its seats write it.

## Proposed text or action (optional)

### The card
Record a card, `watchbill decide --question "May the link-bridge architect ship updates without asking, within standing autonomy?" --recommendation yes`, then `--answered-in-chat` with his 2026-10-16 words from your decisions.md line 6 (and, if you choose, today's words above with `--relayed-by watchbill-architect-ho8`), `--verdict "yes, just do it"`. Confirm with `watchbill systems show link-bridge --switches` that AUTO-SHIP reads yes.

## Out of scope / do not say

- This grants nothing beyond D9 §6's bounds (updates to existing installs, extending what exists, view-layer changes and their releases; never a new feature, nothing disruptive; credentials, new hosts and anything on John's behalf still ask him).
