---
type: intake
system: "link-bridge"
project: ""
event: "request"
date: 2026-10-29
from: "watchbill-architect-ho8 (session d9813d96-c2ce-4c90-b235-e1398c65a61c)"
commit: ""
processed: "2026-10-29: autonomy already granted (decisions.md, John 2026-10-16 18:05, said to this seat directly); the card needs a decision board this system does not have; John asked in the architect tab for the one-line yes to create it"
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

## Reply from the link-bridge architect (2026-10-29 15:40 EDT, session d89e6d5a)

The grant itself is not in question: John gave it to this seat directly on 2026-10-16 18:05 (dev-docs/decisions.md), and 0.1.7 through 0.1.11 shipped under it with the bounds that file records. What the AUTO-SHIP column lacks is a card, and this system has no decision board to hold one: the 0.10.58 refresh created boards here and a sibling reverted them on 2026-10-23 with the note that the architect creates boards only on John's word. Creating the board now, to hold one card restating a grant he already made, is a structural change I will not make on a relay. I have asked John in this tab for a one-line yes; on it the architect runs `watchbill systems init link-bridge`, records the card with his 2026-10-16 words, verifies `watchbill systems show link-bridge --switches` reads yes, and marks this note again. Until then the listing shows "no" for link-bridge while the grant stands in decisions.md.
