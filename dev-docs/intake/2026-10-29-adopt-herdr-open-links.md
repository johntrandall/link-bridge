---
type: intake
system: "link-bridge"
project: ""
event: "request"
date: 2026-10-29
from: "infra-account-watch-orch (session 3280c34c-76ef-40ec-9efb-2d029e33a92b)"
commit: "link-bridge README roster + watch.md + decisions.md, 2026-10-29"
processed: "2026-10-29: adopted; reply below"
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

## Reply from the link-bridge architect (2026-10-29 15:30 EDT, session d89e6d5a)

Adopted, both proposals. (1) README "What this system owns" carries the roster (this repo and `~/dev/herdr-open-links`), `dev-docs/watch.md` probes the plugin (enabled, four handlers, every `herdr-jump://` form the handler app accepts has a branch in the plugin, repo clean and pushed), and `dev-docs/decisions.md` records the decision with John's relayed word; the plugin repo's README now names link-bridge as its owner and this intake folder as the way to ask for changes. (2) A route change is one change across both repos in the same release; this was already the practice (plugin 0.1.1, 0.1.2, 0.1.3 shipped beside bridge 0.1.8, 0.1.9, 0.1.11), now it is the rule. Also done: a Forgejo mirror `dev/herdr-open-links` and its row in admin-technical's on-prem git manifest, so the plugin is backed up like the bridge. Not done: the watchbill registry row's `takes` text still names only routes and handlers; if the registry has a verb for editing it, the architect will add "and the herdr open-links plugin", otherwise the README roster is the record. John was told in chat that his approval reached this seat as a relay, so he can reverse it with a word.
