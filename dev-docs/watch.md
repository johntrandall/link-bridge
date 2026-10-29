# watch.md — what the link-bridge architect watches while dormant

Shape: software project (`watchbill systems`: link-bridge, doorbell architect, intake `dev-docs/intake/`). Roster since 2026-10-29: this repo and `~/dev/herdr-open-links` (the herdr plugin, the pane-side entry point; README "What this system owns").
Architect: the session labelled `🌙 link-bridge …` in herdr (Claude name `link-bridge-architect` from the
next relaunch; `d89e6d5a` until then).

## Probes (run on waking, and by the bounded watch below)

| Probe | Command | Pass |
|---|---|---|
| Local bridge + front door + handlers + plugin, on this Mac | `sh ~/admin-technical/setup/macos/local-front-door/probe.sh` | prints `OK …`, exit 0 |
| Installed vs released | `brew outdated link-bridge`; `gh release view --repo johntrandall/link-bridge` | installed = latest tag |
| Tests on main | `node --test test/ && python3 -I -m unittest discover -s test -p 'test_*.py'` | all pass |
| Handler logs | `tail ~/Library/Logs/{reveal-in-finder,jump-to-session}.log` | no `refused` bursts, no `error` |
| Consumers | sightline rows resolve `http://link.localhost` (status line shows no "install link-bridge" row) | as expected |
| Plugin enabled and in step | `herdr plugin list --plugin johntrandall.open-links --json` (enabled, 4 link handlers, `source.kind` local at `~/dev/herdr-open-links`); every `herdr-jump://` form the handler app accepts (`session/`, `workspace/`, `workspace/label/`, `owner/`) has a matching branch in `herdr-open-links/herdr-jump.py`; `git -C ~/dev/herdr-open-links status -sb` clean and pushed | enabled, 4 handlers, forms match, clean |

## Scheduled probe (John, 2026-10-16: "put yourself in watch mode")

A session cron runs the first probe every 30 minutes (`13,43 * * * *`), last result in
`~/.local/state/link-bridge-watch/last.txt`, contract in admin-technical
`setup/macos/local-front-door/README.md` "Watch". Exit: seven clean days including one SusanBones
reboot or re-login survived, or John's word; deadline 2026-10-23 17:55 EDT. This is the dormant
shape's rule (watchbill 0.6.1): the seat itself does nothing on a schedule, the probes its watch.md
names run silently and wake it only on a failure. After the deadline the remaining probes above are
checked on waking.

## How John is told

- A failed probe during the bounded watch: one PushNotification plus a short message, once per distinct
  failure; silence while clean.
- A request from another agent: handled in listen-mode (negotiate, council if needed, ship within the
  standing autonomy in `dev-docs/decisions.md`); John hears about it only when it falls outside those bounds
  or changes a consumer contract he cares about.
- Outcome of the bounded watch: written into the admin-technical README "Watch" section at its end.
