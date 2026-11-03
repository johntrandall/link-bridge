# Task: link-bridge architect, dormant listen-mode seat (handoff from session d89e6d5a, 2026-11-03 18:23 EST)

## Start here
You are the architect of the watchbill system **link-bridge** (home ~/dev/link-bridge; also ~/dev/herdr-open-links since 2026-10-29). The seat is dormant: it wakes for intake notes in dev-docs/intake/, messages, and John; it ships changes under John's standing autonomy (dev-docs/decisions.md, 2026-10-16 18:05) and tells him when a change touches a security promise or a consumer contract. The origin session (d89e6d5a, derived name admin-technical-e5, tab "🌙 link-bridge …" in workspace wBK) ran out of context on 2026-11-03 after shipping 0.1.14. Read README.md first (routes table, "What this system owns", "Interface stability", "Registered actions", "Security model", "Requesting a change"), then dev-docs/watch.md and dev-docs/decisions.md, then the intake notes (all processed).

## Take over from the origin (first, before any work)
- Cards: none. Anchors: none beyond the cwd. Tasks: none open in any task list.
- Run `herdr-lifecycle appoint link-bridge-architect --seat architect --system link-bridge --approved "John 2026-10-16: you can negotiate with them, launch a council of experts, agree upon a plan, implement it, and publish it"` if the ledger does not already show you as the seat, then `herdr-lifecycle relieve` per the two-party relief in skills/steward/references/handoff.md. Set your tab label to "🌙 link-bridge · listen-mode".
- Then message the origin "adopted".

## Historians in this chain
- admin-technical-e5 (link-bridge architect) — d89e6d5a-8330-4b20-8650-cc1697929329 (oldest; this handoff)

## Why, what was rejected, what the human cares about
- John's rules of record are in ADR-145 (~/admin-technical/ADRs/ADR-145-Link-Bridge-And-Reveal-Scheme.md, D1–D14) and the README. Every route: fragment never reaches the server, explicit allowlist on the page, handler re-checks on the Mac; reveal never opens; link.localhost front door; tailnet HTTP on susanbones:5465 for the status line, HTTPS on :5466 for callers that must fail on an impostor (D13a).
- Registered actions (D13, 0.1.12–0.1.13) are the one exception to "never run": operator-written ~/.config/link-bridge/actions.toml (0600), POST with X-Link-Bridge + per-action token, allow_logins on Tailscale-User-Login, rate limit, Content-Length bound. John was told it amends a security promise and offered a veto ("no registered actions"); he has not answered. First registration: personal-tracker-tap (allow_logins johntrandall@github; tests from this tagged Mac get 403, the positive test is John's phone).
- Rejected: a GET-with-query route (side-effecting GET reachable from any page, query in logs); creating a watchbill decision board on a relay (John reserved boards for his own word; AUTO-SHIP column reads "no" until he says "make the board"); unpinning python@3.14 (python-toolchain project; use `brew install --ignore-dependencies johntrandall/tap/link-bridge` to upgrade; run `link-bridge install-handler` after, never before).
- Release discipline: gate every step on its exit code (`git commit … || exit 1`, check `git log -1` before tagging); v0.1.10 was mis-tagged by a hook-refused commit and withdrawn (memory feedback-tag-only-after-the-commit-succeeds). markdown-unwrap fix README.md before committing. Tap: ~/dev/homebrew-tap/Formula/link-bridge.rb (pull --ff-only first), sha by python urllib, never curl.
- Consumers: sightline (statusline-links-ho3; session-links url; bridge_host tailnet on SusanBones), watchbill (decision cards carry /herdr-jump and /herdr-owner links; watchbill-rules-release, watchbill-architect-hoN), personal-tracker (Pushcut taps), callimachus. Interface notices go to statusline-links-ho3 citing README "Interface stability".
- Open for John (unanswered, do not nag more than once per message): the 10-22 closeout approval block of the origin (moot now), a Stop hook that blocks obsidian:// links in herdr replies (origin recommended yes; not built), the registered-actions veto, "make the board", restart-in-place for stale hooks (now yours to keep current: `watchbill stale-hooks`).

## The work (state as of 2026-11-03 18:23 EST)
- Live on SusanBones: link-bridge 0.1.14 (brew service, front door :80, tailnet http :5465, https :5466), Reveal in Finder.app and Jump to Session.app rebuilt, herdr-open-links 0.1.3 linked. All repos clean and pushed (origin GitHub + umbridge mirrors; admin-technical pushed to umbridge).
- Just shipped (0.1.14): /folder chooser page (Finder or Obsidian), reveal://obsidian?path= via handler/reveal_obsidian.py, POST /act/folder-obsidian. Asked sightline to make `session-links url <directory>` print /folder#…; await their reply, then update the obsidian-link-bridge skill (~/.claude/skills/obsidian-link-bridge/SKILL.md) and the global CLAUDE.md link rule to name /folder for folders in herdr replies (the 10-29 intake from claude-plugin-watchbill-78-ho3 asked for that).
- Tests: `node --test test/` (33) and `python3 -I -m unittest discover -s test -p 'test_*.py'` (36) all pass at 9bde9e4 (tag v0.1.14).
- Gotchas: python3 -I implies -P (breaks sibling imports; use -E -s for scripts with their own modules); `reveal_obsidian.py --dry-run <folder>` and `handler/herdr_jump.py --resolve <url>` test without side effects; this Mac is a tagged tailnet node (no identity header); Engram (umbridge) was unreachable on 2026-11-02/03, memory went to ~/.claude/projects/-Users-johnrandall-admin-technical/memory/.
- Public Cloudflare host (obsidian-link-bridge.johnrandall.com) still serves 0.1.7 pages; deploy.sh needs the 1Password Workers token (ask John before).

## Completion
1. There is no end state: the seat stays dormant. Each intake: answer in the note (processed line + reply), ship, cut a release, tell consumers.
2. On your own handoff: section 2 of watchbill:handoff-session, copy this historian list with yourself added.
3. Before self-shutdown: `herdr-lifecycle closed`, then message each historian it prints.
