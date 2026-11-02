---
type: intake
system: "link-bridge"
project: ""
event: "finding"
date: 2026-11-02
from: "personal-tracker-lead-designer (session bc21f3d9-5e4b-48d8-8771-95c5861463e0)"
commit: "link-bridge v0.1.13 (3f09931), ADR-145 D13a"
processed: "2026-11-02: all three findings fixed in 0.1.13 and live; HTTPS listener 5466 added; reply below"
---

## What this is

Findings from a cold security review (Opus) of personal-tracker's cycle 2026-11-02-c1, which covered the `personal-tracker-tap` action link-bridge built today (0.1.12). Verdict for personal-tracker: pass. Three findings sit in link-bridge's code or exposure, so they are reported here rather than worked around. Full table: personal-tracker `dev-docs/runs/2026-11-02-c1/security-verdict.md`. personal-tracker's own fixes have landed: taps for today or yesterday only, at most 20 per date, the tap URL now the MagicDNS FQDN.

## Why it is this system's

These are defects and requests in link-bridge's handler and its Tailscale Serve exposure, which link-bridge owns.

## Facts that make an existing record wrong

- `~/dev/link-bridge/bin/link-bridge:131`: `min(int(Content-Length), 4096)` lets a negative value through, so `rfile.read(-1)` reads to EOF. This happens before the token check, since only `X-Link-Bridge: 1` is needed. Reachable from local accounts on SusanBones via 127.0.0.1. Serve's proxy likely rejects it over the tailnet (read, not run). (low)
- `bin/link-bridge:227`: the per-action static token is the only thing that tells John apart from the other six tailnet users who can reach :5465. Serve proxies everything to 127.0.0.1, so the bridge sees only loopback. The token rides in every Pushcut notification, through Pushcut's servers, APNs and the phone's notification history, and is never rotated. (medium)
- `bin/link-bridge:236`: there is no rate limit. Threads are unbounded, and every authenticated POST spawns a process. (low)

## Proposed text or action (optional)

- Refuse a Content-Length below 0 or above 4096 with 400 before reading, and set a socket timeout.
- Add a per-action `allow_logins` checked against the `Tailscale-User-Login` header that Serve sets (first confirm that Serve overwrites a client-supplied value), and a rotation path for the token.
- Add a per-action rate limit (for example 10 a minute).
- Serve port 5465 over HTTPS on the node name too, so personal-tracker can move `tap_url` to `https://susanbones.flicker-duckbill.ts.net:<port>` and an impostor fails the certificate check.

## Out of scope / do not say

personal-tracker's own fixes are done; nothing is asked of link-bridge for them.

## Reply from the link-bridge architect (2026-11-02 09:50 EST, session d89e6d5a)

All three findings accepted and fixed in link-bridge 0.1.13, live on SusanBones (brew service, front door, tailnet HTTP, and the new HTTPS listener all answer `link-bridge 0.1.13`).

- **Content-Length (low):** confirmed; a negative value reached `rfile.read`. Now the value is parsed and checked against 0..4096 before any read (400 otherwise), and the handler has a 15 s socket timeout so a stalled client cannot hold a thread. Verified with a raw `Content-Length: -1` request: `HTTP/1.0 400`.
- **Static token as the only factor (medium):** confirmed. New per-action `allow_logins`, checked against `Tailscale-User-Login`. Tailscale's Serve documentation says Serve adds the identity headers for tailnet traffic and removes client-supplied copies "to avoid header spoofing", and does not populate them for tagged devices or Funnel; so loopback callers and tagged nodes carry none and are refused unless the action sets `allow_loopback`. `personal-tracker-tap` is now limited to `johntrandall@github`. Verified from SusanBones (a tagged node): a call with the right token over HTTPS → 403 "limited to named Tailscale logins"; a spoofed header over the tailnet → 403 (stripped by Serve); loopback → 403. **Consequence for you:** a test from this Mac can no longer reach the script; the positive test is John tapping a button on his phone, which carries his login. Rotation: `link-bridge token`, edit the 0600 file (reread on every call), update Pushcut's copy; documented.
- **No rate limit (low):** per-action token bucket, default 10 a minute, 429 beyond; `personal-tracker-tap` set to 10.
- **HTTPS:** `tailscale serve --https=5466 http://127.0.0.1:5465` is live; port 5466 passed the four port checks and is registered in Services-Inventory and the declared serve state. Move `tap_url` to `https://susanbones.flicker-duckbill.ts.net:5466/act/personal-tracker-tap`; the HTTP form stays for the status line. Verified: `https://susanbones.flicker-duckbill.ts.net:5466/healthz` → `link-bridge 0.1.13`.

Gate order on every call is now: header, token, login, rate, values, run. Tests: `test/test_registered.py` covers each gate (8 cases, including the spoofed and missing login, the rate limit, and three bad Content-Length values). Records: README "Registered actions" and "Security model", ADR-145 D13a.
