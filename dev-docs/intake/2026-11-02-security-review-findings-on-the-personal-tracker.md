---
type: intake
system: "link-bridge"
project: ""
event: "finding"
date: 2026-11-02
from: "personal-tracker-lead-designer (session bc21f3d9-5e4b-48d8-8771-95c5861463e0)"
commit: ""
processed: null                  # the receiving seat writes: "YYYY-MM-DD: <what became of it>"
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
