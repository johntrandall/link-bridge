---
type: brief
seat: link-bridge-verify-wake (a cold verifier session, agent watchbill:verifier, model Opus)
reports_to: link-bridge-architect (lead designer, session 445976e7-4722-4c05-a388-c40659b43ff9)
written_by: link-bridge-architect, 2026-11-05 evening
branch: build/wake
track_changes: ignore
---
# Cold verdict on link-bridge 0.1.15 (`build/wake`): security and PASS

## Start here
You are a cold verifier of the link-bridge system (`~/dev/link-bridge`; read `build-brief.md` beside this file first: it says what was built and why). You did not build the branch and you will not land it. Two things are yours, in this order, and nothing else: a **security verdict** on the new action, and, after the lead designer commits that verdict, the trailer-only **PASS commit** `watchbill land` requires. Model: Opus (the security verifier is Opus and cold, watchbill:lead-designer). Do not load Engram.

Work from your own worktree of the tip the lead names in its spawn message: `git -C ~/dev/link-bridge worktree add <your scratchpad>/lb-verify-wake --detach <tip>`. Never write in `~/dev/link-bridge` (the primary checkout) or `~/dev/link-bridge-wake` (the lead's worktree). Never start the bridge on port 5465 (the live service) or 80; a scratch port above 5490 is fine, and kill only the PID you started.

## 1. Security review (file and line for everything you say)
The change crosses a trust boundary: `POST /act/wake` on a listener reachable on loopback and, through Tailscale Serve, on the tailnet runs `watchbill resume <system> --seat <seat>`, which spawns a Claude Code session, and the request carries no token. Read `bin/link-bridge` (`run_wake`, `do_POST`, `ACTIONS`, `HEADERS`), `public/wake.js`, `public/wake.html`, `public/onmac.js`, and the README's "Security model" and the `/wake` row. Judge at least:
1. Argument safety: can anything in the body reach a shell, become an option to watchbill (a leading dash), or exceed the slug grammar? Is `.lower()` applied after the check harmless?
2. The request gates: the `X-Link-Bridge` header as the CORS gate (is a preflight really never answered: no `do_OPTIONS`?), the 4 KiB body, `Content-Type` not required (is that a problem here?), no GET with side effects, the page's CSP (`connect-src 'self'`, `form-action 'none'`).
3. The page: does anything fire on load or on `hashchange` without a click (`wake.js` `render`)? Is the command shown exactly what the server runs?
4. Reachability: on the tailnet, any device of John's can press the button; an untagged device's `Tailscale-User-Login` is not checked for this action (it is for registered actions). Say whether that is acceptable for an action that starts an agent, given that `watchbill resume` refuses everything but an asleep seat of a registered system and the seat then runs in John's own herdr. If you think a token or `allow_logins` is needed, say so as a FAIL with the reason; if the existing policy (the same gates as `/act/herdr-jump`) is enough, say why in one paragraph.
5. The subprocess: the widened PATH (`TOOL_PATH`), `env` inheritance, the 120 s timeout, what `watchbill resume` itself refuses (`~/.local/bin/watchbill`, `cmd_resume`: an unknown system, nothing asleep, `herdr` unreachable, a hard-line session). Can a repeated click spawn twice? (After a wake the seat is live, so the second resume refuses: check the reasoning holds in `watchbill_sleep.asleep_rows`.)
6. Both suites green in your worktree: `node --test test/` and `python3 -I -m unittest discover -s test -p 'test_*.py'`; `/routes` on a scratch port lists `/wake` and `/act/wake`; `POST /act/wake {"system":"no-such-system-7f3a"}` with the header answers 409 and without it 403.
7. The README row and the interface-stability line describe what the code does (status codes, forms, the no-scheme reason); `VERSION` and the formula tag say 0.1.15; `~/dev/herdr-open-links` is unchanged and the brief says why.

Write your verdict as a message to `link-bridge-architect` (SendMessage), formatted as the file `security-verdict.md` to commit, exactly this shape (the lead commits it on the branch unchanged):

```
---
verdict: pass            # or fail
sha: <the tip you checked, full 40 characters>
verifier: <your session id>
---
# Security verdict: /wake and POST /act/wake (link-bridge 0.1.15)
<one paragraph per numbered check above, with file:line; a FAIL names the line and the fix>
```

## 2. The PASS commit (only after the lead's reply)
The lead commits `dev-docs/runs/2026-11-05-wake/security-verdict.md` on `build/wake` and messages you the new tip. Then, in your worktree: `git checkout --detach <new tip>`, run both suites once more, and make one **empty** commit (`git commit --allow-empty`) whose message is your one-paragraph verdict with the decisive lines, ending in exactly these trailers (your own session id; the hook `commit-msg 0.14` runs in this repository):

```
Watchbill-Event: verified
Watchbill-Rule: <the new tip, full 40 characters>
Claude-Session-Id: <your session id>
Resume: claude --resume <your session id>
```

Then move the branch onto it without touching the lead's worktree: `git -C ~/dev/link-bridge update-ref refs/heads/build/wake <your commit> <the new tip>`. A FAIL at this stage is the same commit with `Watchbill-Event: verify-failed` and the failing check named. Message the lead the commit SHA, remove your worktree (`git -C ~/dev/link-bridge worktree remove <path>`), and exit (`herdr-lifecycle capture-check`, then `herdr-lifecycle exit`).

## Rules
One crew at a time on this machine; do the checks yourself. Never `pkill -f` by pattern; kill only the PID you started. Do not edit any file of the repository: your only writes are the message, the empty commit, and the branch ref move the lead asked for. If the tip moves before your PASS, check the new tip (the lead's message names it) and name that one.
