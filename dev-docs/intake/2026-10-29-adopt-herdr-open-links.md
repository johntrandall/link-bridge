---
type: intake
system: "link-bridge"
project: ""
event: "request"
date: 2026-10-29
from: "infra-account-watch-orch (session 3280c34c-76ef-40ec-9efb-2d029e33a92b)"
commit: ""
processed: null                  # the receiving seat writes: "YYYY-MM-DD: <what became of it>"
---

## Start here

This is a request for the `link-bridge` system to take ownership of `herdr-open-links` (`~/dev/herdr-open-links`, a locally linked herdr plugin, version 0.1.3, no owner today). It comes from the infrastructure orchestrator `infra-account-watch-orch` (session 3280c34c-76ef-40ec-9efb-2d029e33a92b, admin-technical), which surveyed John's herdr tooling on 2026-10-29. John approved the proposal in that session's chat on 2026-10-29 at about 15:25 EDT with one word: "approved", in answer to a layout giving open-links to link-bridge.

**Terms.** *open-links* is the herdr plugin whose `[[link_handlers]]` make `obsidian://`, `file://`, `reveal://` and `herdr-jump://` links work on Ctrl+click inside a herdr pane. Clicked in a browser or another app, the same links go to link-bridge's pages and its `Jump to Session.app` handler.

## Why this system

- The two are halves of one feature: one route, two entry points. open-links' last three commits are "parity with link-bridge 0.1.8 / 0.1.9 / 0.1.10" (`/herdr-workspace`, the owner chain, `/herdr-owner`). Every route change already touches both repos, and only one of them has an owner.
- open-links resolves seats through watchbill's `herdr-lifecycle owner` chain, the same interface link-bridge's `/herdr-owner` uses.

## What is asked (proposals; your rules decide)

1. Adopt `herdr-open-links` into this system: README roster, owners, and a `watch.md` probe (plugin enabled in `herdr plugin list`, version in step with the routes).
2. Treat a route change as one change across both repos, so their behaviour stays the same whether a link is clicked in a pane or in a browser.
