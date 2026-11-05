---
type: brief
run: 2026-11-05-wake
branch: build/wake
seat: link-bridge-architect (lead designer, session 445976e7-4722-4c05-a388-c40659b43ff9), building alone
security: review
gui: review
launched_by: 445976e7-4722-4c05-a388-c40659b43ff9 · accountable: 445976e7-4722-4c05-a388-c40659b43ff9 · principal: human
---
# Build: /wake, a route that wakes an asleep watchbill seat (link-bridge 0.1.15)

## Start here
link-bridge is the local link bridge on this Mac: a small Python server (`bin/link-bridge serve`, Homebrew service, `http://link.localhost` through a Caddy front door) that serves pages turning an `http(s)` link into an app link (`obsidian://`, `reveal://`, `herdr-jump://`) or into an action the bridge performs on the Mac (`POST /act/<name>`, header `X-Link-Bridge: 1`). This run adds one route and one action.

**Asked by:** watchbill's lead designer, intake note `dev-docs/intake/2026-11-05-a-route-that-wakes-a-watchbill-seat-from-seats-m.md` (commit 1fd0066). Watchbill 0.10.95 writes `_seats.md` in the cross-system queue vault: a table of every lead designer and steward, live, asleep or dormant, with the shell command that wakes it (`watchbill resume <system> --seat <seat>`). In Obsidian that command is dead text; the route makes the row one click (watchbill's design D12 §8, `~/dev/claude-plugin-watchbill/dev-docs/design/12-sleep-and-wake.md`).

**Approved by John:** 2026-11-05 17:10, in chat (AskUserQuestion, "Yes, build it as proposed"), recorded in `dev-docs/decisions.md`. Asked rather than built on the 2026-10-16 listen-mode grant because this is the first bridge action that starts an agent (a Claude Code session) from a link.

## What was built (commit d2799ad on `build/wake`)
- `public/wake.html`, `public/wake.js`: `/wake#<system>/<seat>` (seat defaults to `lead-designer`) or `#system=…&seat=…`. The page shows the exact command and one button, **Wake it on the Mac**, which POSTs `/act/wake {"system","seat"}` through `onmac.js` (same-origin, `X-Link-Bridge: 1`). On the Mac and off it alike: nothing happens on load, there is no `herdr-jump://` scheme form on purpose (a registered scheme fires from any page or app with no page in between).
- `bin/link-bridge`: route `/wake`, action `/act/wake` → `run_wake`: both names must match `[a-z0-9][a-z0-9._-]{0,63}` (so no leading dash, no shell), fixed argv `[~/.local/bin/watchbill or $WATCHBILL_BIN_PATH, "resume", system, "--seat", seat]`, PATH widened for the brew service (`~/.local/bin`, `/opt/homebrew/bin`), timeout 120 s. 200 with watchbill's line; 409 when watchbill refuses (exit 1: unknown system, nothing of that name asleep, live seat; exit 3: hard line); 501 when watchbill is not installed; 504 on timeout. VERSION 0.1.15; `/routes` lists both.
- `test/wake.test.js` (fragment parsing), `test/test_actions.py::test_wake_refusals` (400s, a 409-or-501 for an unknown system, `/routes`).
- README: route table row, interface-stability line, tests line. `packaging/homebrew/link-bridge.rb`: tag v0.1.15 (sha256 is filled at release).
- `~/dev/herdr-open-links` (the roster's second repository): untouched, because the route has no scheme form; herdr opens `http://link.localhost/wake#…` itself.

## Trust boundary (why `security: review`)
A listener on loopback and the tailnet (Tailscale Serve) now runs a command that spawns a Claude Code session, on a POST that carries no token. The gates are the ones every `/act/` action has: the custom header (a cross-origin page cannot send it without a CORS preflight the server never answers), a 4 KiB body, no shell, and watchbill's own refusals. The cold verifier judges whether that is enough for an action that starts an agent, and names file and line for anything it is not.

## Gate
No `tests/run-all.sh` here; the suites are `node --test test/` and `python3 -I -m unittest discover -s test -p 'test_*.py'` (README "Tests"). Both green on d2799ad (37 node tests, 40 python tests; the first draft of this line said 46, the verifier counted 40).

## After the first security verdict (FAIL on 8b3736d, `security-verdict.md`)
Fixed in the next commit: a Host allowlist on every `POST /act/…` (finding 2, DNS rebinding) with a test; a non-blocking lock plus a 60 s per-seat cooldown in `run_wake` and a button that disables itself on the first click (finding 5) with a two-concurrent-clicks test on a sleeping fake watchbill; `re.ASCII` on the slug grammar (finding 1) with Kelvin-sign and İ tests; the README security model paragraph and the 504/400 codes in the interface line (finding 7); timeout 300 s and the caller's login logged (recommended).
