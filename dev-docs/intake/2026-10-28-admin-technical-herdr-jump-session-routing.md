---
type: intake
system: "link-bridge"
project: ""
event: "defect"
date: 2026-10-28
from: "admin-technical session (claude4 account), session 2ee7e45f-1f5c-419f-a43c-d9ee488fcd7c"
commit: "link-bridge 0.1.9 (route present); sightline claude-statusline f09e956"
processed: "2026-10-29: fixed in sightline b61af05 (statusline-links-ho3); link-bridge confirms the route forms; verified live"
---

## Start here

This is a defect report from John's admin-technical infrastructure session. Its subject is the `session-links url` command, which turns a link into a clickable form for a reply read in a herdr pane. John tried to open a herdr session by link and got a Finder window instead.

Terms used below. **herdr** is the terminal multiplexer John works in. A **herdr tab** holds one Claude Code session. **`herdr-jump://session/<uuid>`** is the custom link that focuses that tab. **`/herdr-jump#<uuid>`** is the link-bridge web route that accepts the same UUID. **sightline** is the status-line system in `~/dev/claude-statusline`. Its function `bridge_form` (in `sightline/links.py`) builds the clickable form, and `session-links url` calls it.

## What happened

John asked for a herdr session to be opened from a link. The agent ran `session-links url "herdr-jump://session/c521bade-f669-4312-a56e-96dcf159e28c"`. The command printed:

`http://susanbones:5465/reveal#admin-technical/herdr-jump%3A/session/c521bade-f669-4312-a56e-96dcf159e28c`

That is a `/reveal` link. Opening it reveals a path in Finder. It does not focus the herdr tab.

Expected output: `http://susanbones:5465/herdr-jump#c521bade-f669-4312-a56e-96dcf159e28c`. The bridge answers that route with HTTP 200 (checked 2026-10-28, bridge version 0.1.9). So the route works, and the conversion is the fault.

John's words, verbatim, in chat: "the link-bridge links aren't working. We don't want to 'reveal in finder', we want to open in herdr."

## Cause (verified by reading the code, not by a changed-variable test)

In `sightline/links.py`, `bridge_form` (around line 718) handles three input kinds: `http(s)://`, `obsidian://` and `obsidian-vault-setup://`, and everything else. `herdr-jump://` matches none of them. It falls through to the last branch, which builds `file://` plus the absolute path. Then `bridge_url` maps that to `/reveal`. Nothing in `sightline` or in `session-links` knows the `herdr-jump` route.

## What is wanted

1. **sightline (`bridge_form`):** a branch for `herdr-jump://session/<uuid>` that returns the bridged `/herdr-jump#<uuid>` form, and one for `herdr-jump://workspace/<id>` or `herdr-jump://workspace/label/<label>` that returns `/herdr-workspace#…`. Both must return the link-bridge form when a bridge answers, and `None` otherwise, so the caller prints the right error.
2. **link-bridge:** confirm that the route forms in the README (`/herdr-jump#<uuid>`, `/herdr-workspace#…`) are the ones sightline should emit, and say so in the reply. No handler change is expected.
3. **Test:** a case in sightline's tests for each `herdr-jump://` form, so this does not regress.

The fix belongs in sightline. This note is also filed there, as a separate intake note, so the sightline steward sees it.

## Who clicks it, and when

John clicks it from a reply in a herdr pane, and from iPad over Moshi. He wants it to bring the herdr tab forward. He has asked for this routing twice (2026-10-17, 2026-10-19: "use link-bridge"), so the lack of it is the reason this is a defect and not a feature request.

## Requested reply

Name the commit that ships the fix, and the output of `session-links url "herdr-jump://session/c521bade-f669-4312-a56e-96dcf159e28c"` after the fix. Mark this note `processed` when the fix is live on the Mac.

## Reply from the link-bridge architect (2026-10-29 12:10 EDT, session d89e6d5a)

Confirmed: the forms sightline should emit are exactly the README ones, `/herdr-jump#<uuid>` and `/herdr-workspace#<id>` or `#label=<url-encoded label>`, and since 0.1.11 also `/herdr-owner#<uuid>`. No link-bridge handler change was needed. The fix landed in sightline as commit b61af05 ("links: herdr-jump:// links bridge to /herdr-jump and /herdr-workspace"), by statusline-links-ho3. Verified on this Mac on 2026-10-29: `session-links url "herdr-jump://session/c521bade-f669-4312-a56e-96dcf159e28c"` prints `http://susanbones:5465/herdr-jump#c521bade-f669-4312-a56e-96dcf159e28c`, and the workspace form prints `http://susanbones:5465/herdr-workspace#wBK`. The `herdr-jump://owner/` form is not yet in sightline's `bridge_form`; a notice went to statusline-links-ho3 with this reply.
