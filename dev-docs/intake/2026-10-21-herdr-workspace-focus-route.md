---
type: intake
system: "link-bridge"
project: ""
event: "request"
date: 2026-10-21
from: "callimachus (architect callimachus-architect-ho2, session 3c187f2a-5768-49c1-9d8a-8b75a805ff69)"
commit: "link-bridge v0.1.8"
processed: 2026-10-21
---

## What this is

A request for a new route: a web link that brings one **herdr workspace** to the front. It would sit beside `/herdr-jump#<session uuid>`, which focuses one session's tab.

John asked for it on 2026-10-21 at about 13:45 EDT, in chat with callimachus-architect-ho2, verbatim: "Each 'decision card' should include a link to focus on that particular agent in herder. And antother link to focus just on the workspace in herdr." The agent link exists (`/herdr-jump`). The workspace link does not.

herdr has the verb: `herdr workspace focus` ("Focus a workspace").

Suggested form: `/herdr-workspace#<workspace label or id>` → `herdr-jump://workspace/<id>`, handled by Jump to Session.app. Allowlist it like the session route.

Workspace ids may not be stable across herdr restarts. If they aren't, resolve a system name (from `watchbill systems`) to its home workspace at click time, as the agent link does from a session id.

## Why it is this system's

link-bridge owns the web-link-to-Mac-action routes and their handlers. The consumer is watchbill's decision cards (watchbill intake 2026-10-21-renames-designer-operations-steward-and-card-links.md).

## Reply from the link-bridge architect (2026-10-21 13:50 EDT, session d89e6d5a)

Shipped as link-bridge 0.1.8 (tag v0.1.8, tap bumped, running on SusanBones) and herdr-open-links 0.1.1 (relinked).

- Route: `/herdr-workspace#<id>` → `herdr-jump://workspace/<id>` → `herdr workspace focus <id>`. Also `#id=<id>`.
- Label form: `/herdr-workspace#label=<url-encoded tab-bar label>` → `herdr-jump://workspace/label/<label>`. The handler matches an exact label first, then the label with its leading glyph tokens dropped, case-insensitively (`🌙 📦 s-svc link-bridge` matches `s-svc link-bridge`). Use this form on a card that may outlive a herdr restart; ids are not promised stable.
- Remote browsers (iPad): the page shows "Focus on the Mac" and POSTs `/act/herdr-workspace {"workspace": id}` or `{"label": text}` with `X-Link-Bridge: 1`, like `/act/herdr-jump`.
- Host: the same one the status line uses, so on SusanBones `http://susanbones:5465/herdr-workspace#label=…`; `session-links url` does not build this form yet (its argument is a note or a path), so build it directly.
- Not done: resolving a watchbill system name to its home workspace. The label form covers it when the card knows the workspace label; if watchbill wants `#system=<name>`, send a second note with where the name→workspace mapping lives.
- Verified: id, exact label and glyph-stripped label each focused the focused workspace (no visible change) with exit 0; a missing id exits 1 with a herdr notification; a malformed link exits 3; 27 page tests and 18 handler/action tests pass.
