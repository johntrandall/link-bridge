# Decisions (link-bridge)

Decisions for the human and the standing grants he has made. One line per item, newest first.

- 2026-10-16 18:05 John, standing autonomy (listen-mode): "if other agents come to you with their needs for
  functionality in Linkbridge, you can negotiate with them, launch a council of experts, agree upon a plan,
  implement it, and publish it." Bounds kept by the architect: update existing installs and extend what exists;
  no new root installs, no disruptive change, no edits inside another agent's repo; interface changes go to the
  consumers first (README "Interface stability"); credentials and new hosts still ask John.
- 2026-10-16 John: "caddy as the front door, but this belongs to the link-bridge" (port-free local links).
- 2026-10-16 John: "do reveal" (reveal:// = select in Finder, never open); scheme name reveal, not finder.
- 2026-10-16 John: local server, brew-installable, `brew services start`; decommission the Cloudflare copy that
  served the Mac (the public obsidian host stays for the phone and calendar).

## 2026-10-29 — Adopt herdr-open-links into this system

**Decided** (John, 2026-10-29 ~15:25 EDT, "approved", said in the infra-account-watch-orch session and relayed by its intake note; the architect treats a relay as a lead and recorded it here so John can reverse it with a word): the link-bridge system owns `~/dev/herdr-open-links` as well as this repo. One route, two entry points (browser → pages and handler apps; pane → plugin), one change per release; the plugin's `herdr-jump.py` stays in step with `handler/herdr_jump.py`. Documentation only: no code changed, the plugin was already kept in step (0.1.1 ↔ 0.1.8, 0.1.2 ↔ 0.1.9, 0.1.3 ↔ 0.1.11). Added an `umbridge` mirror (`dev/herdr-open-links`) and the on-prem manifest row; `watch.md` gains a plugin probe; README gains the roster.

