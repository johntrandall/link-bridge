# link-bridge

Tiny web pages that turn a web link into an app link, for places that only make `http(s)` links clickable: a terminal status line, Google Calendar, chat and ticket tools. Served from your own Mac (`brew services`, loopback only, works offline) or from any static host. The target travels in the URL fragment, which browsers never send, so no server ever sees a note or file name.

Successor of [obsidian-link-bridge](https://github.com/johntrandall/obsidian-link-bridge), whose `/obsidian` page is included here unchanged; that repository is deprecated in favour of this one.

## Install

```bash
brew tap johntrandall/tap
brew install link-bridge
brew services start link-bridge      # http://127.0.0.1:5465, keeps running across logins
link-bridge install-handler          # ~/Applications: Reveal in Finder.app (reveal://), Jump to Session.app (herdr-jump://)
brew install obsidian-vault-setup && obsidian-vault-setup install-finder-button   # optional: /vault-setup links
link-bridge doctor
```

Without Homebrew: `git clone https://github.com/johntrandall/link-bridge && cd link-bridge && ./install.sh` links `link-bridge` into `~/.local/bin` (make sure that is on your PATH); run `link-bridge serve` from a LaunchAgent of your own.

```bash
link-bridge url ~/notes/Plan.md
# http://127.0.0.1:5465/reveal#notes/Plan.md   (http://link.localhost/… once the front door below is installed)
link-bridge url --vault-setup ~/dev/project
# http://127.0.0.1:5465/vault-setup#dev/project
```

| Route | Forwards to | What happens |
|---|---|---|
| `/obsidian#vault=…&filepath=…&openmode=tab` | `obsidian://advanced-uri?…` or `obsidian://open?…` | opens a note in Obsidian ("open a note" parameters only); `#vault=…` alone opens that vault |
| `/reveal#notes/Plan.md` | `reveal://reveal?path=…` | selects the file or folder in a Finder window; never opens it |
| `/vault-setup#dev/project` | `obsidian-vault-setup://open?path=…` | opens the Obsidian vault at the folder's git root, or creates it; needs [obsidian-vault-setup](https://github.com/johntrandall/obsidian-vault-setup) and its handler app |
| `/folder#<path>` | `reveal://reveal?path=…` **or** `reveal://obsidian?path=…` | a folder (or file) the reader chooses where to open (0.1.14; John 2026-11-03: "reveal the folder in Finder or in its obsidian vault"): two buttons, **Reveal in Finder** (as `/reveal`) and **Open in Obsidian** (the handler finds the registered vault that holds the folder, opens a note inside it, README first, and runs Obsidian's "reveal active file in navigation" so the explorer expands to the folder; a folder outside every vault is refused with a notification). Same fragment forms as `/reveal`. Nothing opens until a button is pressed |
| `/herdr-jump#<session uuid>` | `herdr-jump://session/<uuid>` | focuses the [herdr](https://herdr.dev) tab holding that Claude Code session (handler: Jump to Session.app, below; inside a herdr pane the [open-links](https://github.com/johntrandall/herdr-open-links) plugin handles the Ctrl+click directly). The page accepts one UUID (`#<uuid>` or `#session=<uuid>`) and nothing else |
| `/herdr-owner#<session uuid>` | `herdr-jump://owner/<uuid>` | focuses the herdr tab of **whoever holds that session's seat now** (0.1.11; asked by watchbill for its decision cards, John 2026-10-29): the handler asks `herdr-lifecycle owner <uuid> --json` (watchbill ≥ 0.10.76) and focuses the `session_id` it returns when `live`, else shows "Nobody holds that seat". Differs from `/herdr-jump`, which goes to the session itself while it is live, even a historian. Forms `#<uuid>` or `#session=<uuid>` |
| `/herdr-workspace#<workspace id>` | `herdr-jump://workspace/<id>` | focuses one herdr **workspace** (0.1.8; same handler app and plugin as `/herdr-jump`; `herdr workspace focus`). Forms: `#<id>` or `#id=<id>` (a herdr id such as `wBK`), or `#label=<url-encoded tab-bar label>`, which the handler matches ignoring the lifecycle glyphs in front and case, so it survives a herdr restart that renumbers ids |
| `/wake#<system>/<seat>` | `POST /act/wake` (no scheme form, on purpose) | wakes an asleep watchbill seat (0.1.15; asked by watchbill 0.10.95 for the `Wake with` column of its `_seats.md`, John 2026-11-05): the page shows the exact command, `watchbill resume <system> --seat <seat>`, and runs it on the Mac only when its one button is pressed, on the Mac and from an iPad alike. watchbill refuses an unknown system, a seat that is not asleep (live included), and a session past its hard line, and spawns the seat in its own herdr workspace. Forms: `#<system>/<seat>` (seat defaults to `lead-designer`) or `#system=…&seat=…`; both names are slugs. The only bridge action that starts an agent, so it has no `herdr-jump://` form: a registered scheme fires from any page or app with no page in between |

`/reveal` and `/vault-setup` take the path two ways. The **short form** is the bare fragment: `#notes/Plan.md` is relative to your home folder, `#/Volumes/x/y` is absolute, and only `/` is left unencoded (`#a%20b/c`). It exists for places that show the whole URL, such as a terminal status line, where `#path=%2FUsers%2Fme%2Fnotes%2FPlan.md` cost 35 columns of noise per row. The **long form**, `#path=<percent-encoded path>`, still works. Relative paths are joined onto the home folder by the handlers, which know it; the pages only check shape.

`/obsidian` is the [obsidian-link-bridge](https://github.com/johntrandall/obsidian-link-bridge) page, unchanged. `/reveal` is new and needs a small handler app on the Mac, because browsers refuse to navigate from https to `file:` at all.

## The handler apps

Browsers hand a custom scheme to whatever app registered it with Launch Services, so each local action is a tiny AppleScript applet in `~/Applications`, built by `link-bridge install-handler` (`handler/install.sh`) with `osacompile`. Each one runs a small Python gate inside its own bundle before acting, logs to `~/Library/Logs/`, and shows a notification when it refuses a link.

**Reveal in Finder.app** (`reveal://`): `handler/reveal_decode.py` accepts only `reveal://reveal?path=<path>` where the path exists (relative means under your home folder) and is not inside an application or plug-in bundle, then runs `open -R <path>`. Since 0.1.14 the same app takes `reveal://obsidian?path=<folder>` (from `/folder`): `handler/reveal_obsidian.py` finds the deepest registered vault containing the folder (`~/Library/Application Support/obsidian/obsidian.json`), picks a note in it (README.md, index.md, the first `*.md`, else the first note in a subfolder), runs `obsidian vault=<v> open path=<note> newtab` then `command id=file-explorer:reveal-active-file` (the Obsidian CLI), and brings Obsidian forward; a folder with no note opens the vault alone and says so; a folder outside every vault is refused. `--dry-run` prints the plan. Why reveal and not open: once a scheme is registered, any page or app can emit a link to it. A reveal can show you where a file is; it cannot run it. You double-click if you want it opened.

**Jump to Session.app** (`herdr-jump://`): `handler/herdr_jump.py` accepts exactly one Claude Code session UUID, asks `herdr agent list` which live pane holds it, runs `herdr tab focus` (which also switches workspace) and brings the terminal forward (`LINK_BRIDGE_TERMINAL_APP`, default Terminal). Since 0.1.8 the same app also takes `herdr-jump://workspace/<id>` and `herdr-jump://workspace/label/<label>` (from `/herdr-workspace`), looks the workspace up in `herdr workspace list` (an exact label first, then the label with its leading glyph tokens dropped, case-insensitively) and runs `herdr workspace focus <id>`. Since 0.1.9, when the id is no longer live the app focuses the **current owner of that session's seat** (asked by watchbill for its decision cards): the id's Claude name comes from herdr-lifecycle's role file or handoff ledger (`~/.local/state/herdr-lifecycle`), `herdr-lifecycle siblings --all --json` names the live members of that name's handoff chain (`<base>`, `<base>-ho2`, …), and the highest live `-hoN` is focused, else any live member (the historian). `handler/herdr_jump.py --resolve <url>` prints what would be focused and why without focusing. If the id is no longer live but its `~/.claude/sessions` record carries a user-given name (a `/clear` keeps the name and mints a new id), the live pane with that name is focused instead; otherwise a herdr notification says "Session gone" and nothing is focused. Nothing from the link ever reaches a shell.

```sh
link-bridge install-handler
open 'reveal://reveal?path=%2FUsers%2Fme'                    # a Finder window with your home folder selected
open 'herdr-jump://session/<claude session uuid>'             # that session's herdr tab comes to the front
open 'herdr-jump://workspace/wBK'                               # that herdr workspace comes to the front (0.1.8)
open 'herdr-jump://workspace/label/s-svc%20link-bridge'          # the same, by tab-bar label (glyphs and case ignored)
open 'herdr-jump://owner/<claude session uuid>'                 # the tab of whoever holds that session's seat now (0.1.11)
```

Chrome asks once per site and scheme whether it may open the app; tick "Always allow" for your bridge host. Logs: `~/Library/Logs/reveal-in-finder.log`, `~/Library/Logs/jump-to-session.log`.

## Running it locally

The local server is the normal way to run it: loopback only, no network needed, nothing hosted.

```sh
brew services start link-bridge      # launchd keeps it up across logins; log: ~/Library/Logs/link-bridge.log
link-bridge serve --port 5465        # or run it in the foreground yourself
link-bridge doctor                   # server answering? handler installed?
```

Port 5465 spells LINK on a phone keypad; `--port` or `LINK_BRIDGE_PORT` picks another. `GET /healthz` answers `link-bridge <version>`, directly and through the front door, so a status line can tell the bridge from anything else that might sit on a port. The links to hand out are `http://127.0.0.1:5465/reveal#…`, `/vault-setup#…` and `/obsidian#…` (`link-bridge url` prints them). Every click stays on the machine, which is why `/reveal` and `/vault-setup` can exist at all: their handler apps are on this Mac.

### Dropping the port: a local front door (optional)

`:5465` in every link is noise if you read these links all day. macOS lets only root bind port 80, so the clean way to lose the port is a small reverse proxy on 80 that routes by name and leaves link-bridge running unprivileged on 5465. With [Caddy](https://caddyserver.com):

```
# Caddyfile
{
	default_bind 127.0.0.1 ::1    # loopback only: /reveal and /vault-setup act on THIS Mac
	admin off
	auto_https off
}
http://link.localhost {
	reverse_proxy 127.0.0.1:5465
}
```

A ready-made kit is in [`frontdoor/`](frontdoor/) and runs with `brew install caddy && link-bridge install-front-door`: that Caddyfile, a LaunchDaemon plist with a full `ServiceDescription`, and an installer that validates the config, copies it root-owned, adds the hosts lines, bootstraps the daemon and verifies that only loopback listens. Or by hand: run Caddy as root from a LaunchDaemon of your own (not `sudo brew services`, which leaves root-owned files in the Homebrew prefix), add `127.0.0.1 link.localhost` and `::1 link.localhost` to `/etc/hosts` for Safari and command-line tools (Chrome resolves `*.localhost` by itself), and check with `sudo lsof -nP -iTCP:80 -sTCP:LISTEN` (root's listener is invisible to an unprivileged `lsof`; `netstat -an -p tcp | grep '\.80 '` also works) that only loopback addresses listen. From then on `link-bridge url` prints `http://link.localhost/reveal#…` and `link-bridge doctor` reports `front door: ok`. Set `LINK_BRIDGE_NAME` if you choose another name. A second local web app later gets its own name in the same Caddyfile instead of a port.

## Running it remotely (Cloudflare Workers)

When a link has to work from a phone or another machine, for example in a calendar event, the same `public/` folder deploys unchanged to Cloudflare Workers as static assets (`wrangler.jsonc`, `_headers` carries the CSP). The server never sees the target: it travels in the URL fragment.

```sh
npm install -g wrangler              # or: brew install wrangler
cp deploy.env.example deploy.env     # git-ignored
$EDITOR deploy.env                   # CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_API_TOKEN, BRIDGE_DOMAIN
./deploy.sh                          # runs the tests, then `wrangler deploy --domain $BRIDGE_DOMAIN`
```

`BRIDGE_DOMAIN` must be a hostname in a zone on that Cloudflare account; Cloudflare creates the DNS record. The API token needs the "Edit Cloudflare Workers" template plus Zone access to that zone. Values in `deploy.env` may be 1Password secret references (`op://vault/item/field`); `deploy.sh` then runs the deploy through `op run` so the secrets never land in a file. On a public host only `/obsidian` is useful to everyone: `/reveal` and `/vault-setup` still need the handler apps on the Mac that opens the link, and a phone has no Finder.

Both can run at once: local links for what you read on the Mac, the public host for what you read elsewhere.

## From a phone or tablet (Moshi, a remote browser)

Serve the bridge over your tailnet as well as loopback (the policy pattern: upstream stays on `127.0.0.1`, Tailscale Serve fronts it with HTTPS):

```sh
tailscale serve --bg --https=5465 http://127.0.0.1:5465   # https://<mac>.<tailnet>.ts.net:5465
```

Then `https://<mac>.<tailnet>.ts.net:5465/obsidian#vault=Notes&file=Plan` opens the note in Obsidian on the device that opened the link (an iPad, if that vault is on it), and `/reveal` and `/herdr-jump` show an **On the Mac** button instead of trying a scheme the device cannot handle: the page POSTs `/act/reveal {"path"}`, `/act/herdr-jump {"session"}` or `/act/herdr-workspace {"workspace"}` / `{"label"}` (header `X-Link-Bridge: 1`) and the bridge performs the action on the Mac through the same gates as the handler apps. The header makes any cross-origin attempt a CORS preflight the server never answers. A terminal app that cannot tap links (Moshi today) still needs the URL copied into a browser.

## Registered actions (0.1.12): a command the bridge runs for one caller

Since 0.1.12 the operator of a Mac may register a command the bridge runs on `POST /act/<name>`, for a caller that can make an HTTP request but cannot run anything on the Mac (first case: personal-tracker's Pushcut buttons on John's iPhone, which record one tap each; intake `dev-docs/intake/2026-11-02-route-for-personal-tracker-s-pushcut-taps-runs-r.md`). The request supplies named **values** only; the command line is fixed in `~/.config/link-bridge/actions.toml` (`$LINK_BRIDGE_ACTIONS` overrides; mode 0600; never committed), which only the operator writes:

```toml
[actions.personal-tracker-tap]
argv = ["/opt/homebrew/opt/python@3.14/bin/python3.14", "-E", "-s", "/Users/me/dev/personal-tracker/scripts/record_tap.py"]
params = ["date", "check", "button"]      # each becomes --<param> <value>, in this order; all required
token = "<48 hex chars>"                  # `link-bridge token` prints a fresh one
timeout = 20                              # seconds, optional (default 20)
cwd = "/Users/me/dev/personal-tracker"    # optional
allow_logins = ["me@github"]              # optional (0.1.13): only these Tailscale logins may call it
allow_loopback = false                    # optional: with allow_logins, also admit calls made on this Mac
rate_per_minute = 10                      # optional (0.1.13): per action; 429 beyond it
```

The call: `POST http://<bridge host>/act/personal-tracker-tap` with headers `X-Link-Bridge: 1`, `X-Link-Bridge-Token: <token>`, `Content-Type: application/json`, body `{"date": "2026-11-02", "check": "pills", "button": "Doing it now"}`. The bridge answers `200 {"ok": true, "output": "<stdout>"}`, `400` with the command's refusal (`{"exit": n, "error": "<stderr>"}`) or with the value that was refused, `403` for a missing header or wrong token, `405` for a name that is not registered, `504` on timeout. Pushcut's notification actions carry a method, headers and a body (`urlBackgroundOptions`: `httpMethod`, `httpHeader`, `httpBody`, `httpContentType`), so the phone can make this call in the background.

**Gates, every call:** the `X-Link-Bridge` header (a page on another origin cannot send it without a CORS preflight this server never answers); the per-action token, compared in constant time; with `allow_logins`, the caller's Tailscale identity (`Tailscale-User-Login`, which Tailscale Serve sets for traffic from an untagged tailnet device and strips from the client's own headers; loopback callers and tagged devices carry none, so they are refused unless `allow_loopback`); the per-action rate limit; a `Content-Length` checked against 0..4096 before anything is read, and a socket timeout; each value a non-empty string of at most 128 characters with no control characters and no leading dash (so a value can never become an option); the body at most 4 KiB and a JSON object; the argv fixed and absolute, nothing from the request reaching a shell; a timeout; a minimal environment; and the listener's reach, loopback and the tailnet only. A registration that is not well formed (relative argv, bad name, short token) is skipped and named on stderr, never run. `GET /routes` lists registered names under `registered`.

**HTTPS for callers that should fail on an impostor:** the same bridge is also served as `https://<mac>.<tailnet>.ts.net:5466` (Tailscale Serve, certificate from Tailscale; registered in admin-technical's Services-Inventory), so a caller such as a phone can hold an HTTPS URL and refuse a host that cannot present the certificate. The plain `http://<mac>:5465` form stays for the status line, where width matters and the links only open pages. A token that rides in a phone notification is still a secret that leaves the Mac; `allow_logins` makes it one factor of two, and rotation is one edit of the config file (the bridge rereads it on every call) plus the caller's copy.

**Why not a GET with a query string**, which is what the first requester proposed: a GET with side effects is reachable from any page a tailnet device visits (an `<img>` is enough), and its query lands in logs; the POST gates above cost the caller nothing.

## Interface stability

Other tools depend on these; treat them as a contract and tell the consumers before changing or renaming any of them (today: the Claude Code status line, [sightline](https://github.com/johntrandall/claude-statusline), owned by the `statusline-architect` herdr session on John's Macs):

- `GET /healthz` → `200`, body starting `link-bridge` (then a space and the version)
- the routes `/obsidian#…`, `/reveal#…`, `/vault-setup#…`, `/herdr-jump#…`, `/herdr-workspace#…` (0.1.8+), and the actions `POST /act/reveal`, `POST /act/herdr-jump` (0.1.7+), `POST /act/herdr-workspace` (0.1.8+); `/herdr-jump` resolves an exited session to its seat's live owner (0.1.9+); `/herdr-owner#…` and `POST /act/herdr-owner {"session"}` focus the seat's current holder even while the asker is live (0.1.11+); `/folder#<path>` with its two buttons and `POST /act/folder-obsidian {"path"}` (0.1.14+); `/wake#<system>/<seat>` and `POST /act/wake {"system","seat"}` (0.1.15+; 409 when watchbill refuses or a wake is already running or was run for that seat within a minute, 501 when watchbill is not installed, 504 on the 300 s timeout, 400 for a name that is not a slug or any other watchbill exit); every `POST /act/…` answers 403 to a Host that is not one of this bridge's names (0.1.15+); `GET /routes` returns `{"version","routes","actions","registered"}` so a consumer can check which routes this bridge has (0.1.11+; `registered` since 0.1.12); `POST /act/<name>` for an operator-registered action, gated by `X-Link-Bridge: 1` and `X-Link-Bridge-Token` (0.1.12+), plus `allow_logins` and a rate limit (0.1.13+); `/obsidian` accepts any combination of Obsidian's `open` parameters (`vault`, `file`, `path`, plus `paneType`), `vault=` alone included (0.1.5+), or the Advanced URI set when `filepath=` is present, and refuses every other key
- the short home-relative fragment form (`#notes/Plan.md`, `#/abs/path`) beside `#path=…`
- the install command a consumer shows when the bridge is not running:
  `brew install johntrandall/tap/link-bridge && brew services start link-bridge && link-bridge install-handler`

A new page that wants a status-line row goes to the status-line owner, not straight into sightline.

## What this system owns (roster)

Since 2026-10-29 (John: "approved", relayed by infra-account-watch-orch; link-bridge intake `dev-docs/intake/2026-10-29-adopt-herdr-open-links.md`) the link-bridge system owns two repositories, because they are two entry points to one feature and every route change touches both:

| Repository | What it is | Entry point |
|---|---|---|
| `~/dev/link-bridge` (this repo; GitHub `johntrandall/link-bridge`, mirror `umbridge` `dev/link-bridge`, tap `johntrandall/tap/link-bridge`) | the pages, the local server, the handler apps (Reveal in Finder, Jump to Session), the front-door kit | a link clicked in a browser, a status line, a card, or any app that opens http(s) |
| `~/dev/herdr-open-links` (GitHub `johntrandall/herdr-open-links`, mirror `umbridge` `dev/herdr-open-links`; linked into herdr with `herdr plugin link`) | the herdr plugin whose `[[link_handlers]]` make `obsidian://`, `file://`, `reveal://` and `herdr-jump://` links work on Ctrl+click inside a pane | a link clicked inside a herdr pane |

**One route, two entry points, one change.** A new or changed `herdr-jump://` form, scheme, or allowlist lands in both repos in the same release, and the plugin's resolution (`herdr-jump.py`) stays in step with the handler app's (`handler/herdr_jump.py`): same inputs, same resolution order, same refusals. The plugin version is bumped with the bridge's, and `dev-docs/watch.md` probes both. Requests for either go through this system's intake; there is no separate plugin owner.

## Requesting a change (for agents and people)

Message the link-bridge architect (the herdr tab labelled `🌙 link-bridge …`, Claude address `d89e6d5a` until a successor is named; or drop a note in `dev-docs/intake/` and ring the doorbell, `watchbill systems`) with: the surface that will show the link, the scheme or action wanted, and who clicks it. The owner negotiates scope, may convene a short council of expert subagents for anything that touches the security model, agrees a plan with you in writing, implements it, cuts a release and bumps the tap, and tells the consumers listed under *Interface stability*. New routes follow the existing shape: a fragment that never reaches a server, an explicit allowlist on the page, and a handler app that re-checks on the Mac and can only reveal, open or focus, never run.

## Security model

Once you tick a browser's "Always allow" for a bridge host, any link to that host opens the app without a prompt, so a link someone else crafts must not be able to do more than open. Each page therefore forwards only a fixed set of parameters and refuses anything else: `/obsidian` the "open a note" parameters (Advanced URI can also run commands and write files via `commandid`, `data`, `mode`, …; those are refused), `/reveal` and `/vault-setup` a single path. Beyond the page, each handler app re-checks the link on the Mac (`reveal_decode.py`; obsidian-vault-setup's `url --decode`): the path must exist, a reveal never opens anything, a vault-setup path must be under your home folder. The pages load nothing from other sites and ship with a strict Content Security Policy, `Referrer-Policy: no-referrer`, `X-Frame-Options: DENY` and `X-Robots-Tag: noindex`.

What the bridge cannot hide: the app that shows the link sees the whole link. Google Calendar stores it in the event, and its click-through redirect passes the full URL, fragment included, through Google.

**Registered actions are the first exception to "never run"** (0.1.12), and the exception is narrow: the bridge runs only a command line the operator wrote into a mode-0600 config file on the Mac, with the request contributing named values that pass the gates above (no shell, no options, no control characters, a token, the header, the tailnet). A request can make the registered command run with values it validates itself; it cannot choose the command.

**`/act/wake` is the second exception, and the only built-in one that starts an agent** (0.1.15). It runs one fixed command, `watchbill resume <system> --seat <seat>`, with the request contributing two ASCII slugs (`[a-z0-9][a-z0-9._-]{0,63}` each: no shell, no leading dash, nothing else). Its gates, checked cold by the run's security verifier (`dev-docs/runs/2026-11-05-wake/security-verdict.md`): the page runs nothing on load and has no `herdr-jump://` form, so the only way in is its button or a same-origin POST; the `X-Link-Bridge` header (a cross-origin page cannot send it without a preflight the server never answers); a **Host allowlist** on every `POST /act/…`, so a page on an attacker's name that rebinds to 127.0.0.1 is refused with 403 (the front-door name, `localhost`, `127.0.0.1`, `::1`, this Mac's hostname, its `.local` and `<host>.<tailnet>.ts.net` names, plus `$LINK_BRIDGE_HOSTS`; a refused Host is logged); one wake at a time on the Mac and one per seat per minute (409 otherwise), and the page disables its button once pressed, so a double click cannot resume one conversation twice; a 300 s timeout, longer than watchbill's own spawn budget; and watchbill's refusals, which decide everything else: an unknown system, a seat that is not asleep (live included), a session past its hard line. No token: on the tailnet any device of John's can press it, as it can press `/act/herdr-jump`, and the worst it can do is start a seat early at a cost in credits, with a first prompt watchbill fixes (the caller's Tailscale login, or loopback, is logged on each wake).

## Prior art, and why yet another one

The `/obsidian` page began life as [obsidian-link-bridge](https://github.com/johntrandall/obsidian-link-bridge),
itself yet another Obsidian link bridge. Others got there first, and they are worth a look:

- [obsid.net](https://obsid.net) ([source](https://github.com/jdevalk/obsid.net)): a redirect service, also self-hostable as a Cloudflare Worker, that turns `vault` and `file` query parameters into `obsidian://open` links.
- [Ibraheem-Khalil/obsidian-link-bridge](https://github.com/Ibraheem-Khalil/obsidian-link-bridge) (2025): a one-page redirect that reads `vault` and `file` from the query string and opens `obsidian://open`.
- [SvenAkk/obsidian-link-bridge](https://github.com/SvenAkk/obsidian-link-bridge): a static page on GitHub Pages that carries a note path and line in the URL fragment and opens it with Advanced URI.

Why another one: the two GitHub bridges carry no license, and without one nobody may legally copy, modify or redistribute their code. obsid.net is MIT-licensed (stated on its site) and self-hostable, but it reads the note from the query string in server code and only produces `obsidian://open` links. This project keeps the target out of every request, runs no server code on a public host, supports Advanced URI, runs locally with nothing hosted at all, reaches beyond Obsidian (Finder, vault setup), and is **MIT-licensed** (see [LICENSE](LICENSE)): fork it, change it, ship it.

As far as we can tell (checked 2026-10-15), the Obsidian page is also the most complete of the four:

| | obsid.net | Ibraheem-Khalil | SvenAkk | link-bridge |
|---|---|---|---|---|
| Runs on your own domain | Yes (self-host the Worker), or use obsid.net | Yes | Yes (GitHub Pages) | Yes, or on your own Mac with no domain at all |
| Note name never sent to the server | No (query string) | No (query string) | Yes (fragment) | Yes (fragment) |
| Any vault | Yes | Yes | No (vault fixed in the code) | Yes |
| Built-in `obsidian://open` | Yes | Yes | No | Yes |
| [Advanced URI](https://github.com/Vinzent03/obsidian-advanced-uri) (new tab, heading, block, line) | No | No | Line only | Yes |
| Only ever opens notes | Yes (fixed parameters) | Yes (fixed parameters) | Yes (fixed parameters) | Yes (explicit allowlist) |
| Runs no server code | No (Worker reads the query) | Yes | Yes | Yes |
| Deploy kit | Cloudflare Worker (`wrangler`) | No | GitHub Pages | Homebrew (local), Cloudflare Workers, any static host |
| Files and folders, vault creation | No | No | No | Yes (`/reveal`, `/vault-setup`) |
| License | MIT (stated on obsid.net; no LICENSE file in the repo) | None | None | MIT |

## Tests

```sh
node --test test/                                         # page logic (obsidian, reveal, vault-setup, herdr-jump, herdr-workspace, folder, wake)
python3 -I -m unittest discover -s test -p 'test_*.py'    # handler gates (reveal_decode, herdr_jump)
```

## License

MIT

## Handoffs

| Date | Origin (name, session id) | Receiver (name, session id) | Scope | Historian exited |
|---|---|---|---|---|
| 2026-11-03 | admin-technical-e5 (link-bridge architect), d89e6d5a-8330-4b20-8650-cc1697929329 | link-bridge-architect, (see dev-docs/handoffs/2026-11-03-link-bridge-architect.md) | seat | no |

2026-11-03: the origin session built the bridge from 0.1.0 to 0.1.14 (routes obsidian, reveal, vault-setup, herdr-jump, herdr-workspace, herdr-owner, folder; registered actions; front door; tailnet HTTP and HTTPS; the open-links plugin), ran the 7-day watch (closed 10-22, met), and handed the seat off at its context limit; briefing in dev-docs/handoffs/. Left for the receiver: the obsidian-link-bridge skill and the CLAUDE.md link rule should name /folder once sightline's session-links url prints it.
