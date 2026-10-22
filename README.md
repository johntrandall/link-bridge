# link-bridge

Tiny web pages that turn a web link into an app link, for places that only make `http(s)` links
clickable: a terminal status line, Google Calendar, chat and ticket tools. Served from your own Mac
(`brew services`, loopback only, works offline) or from any static host. The target travels in the
URL fragment, which browsers never send, so no server ever sees a note or file name.

Successor of [obsidian-link-bridge](https://github.com/johntrandall/obsidian-link-bridge), whose `/obsidian`
page is included here unchanged; that repository is deprecated in favour of this one.

## Install

```bash
brew tap johntrandall/tap
brew install link-bridge
brew services start link-bridge      # http://127.0.0.1:5465, keeps running across logins
link-bridge install-handler          # ~/Applications: Reveal in Finder.app (reveal://), Jump to Session.app (herdr-jump://)
brew install obsidian-vault-setup && obsidian-vault-setup install-finder-button   # optional: /vault-setup links
link-bridge doctor
```

Without Homebrew: `git clone https://github.com/johntrandall/link-bridge && cd link-bridge && ./install.sh`
links `link-bridge` into `~/.local/bin` (make sure that is on your PATH); run `link-bridge serve` from a LaunchAgent of your own.

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
| `/herdr-jump#<session uuid>` | `herdr-jump://session/<uuid>` | focuses the [herdr](https://herdr.dev) tab holding that Claude Code session (handler: Jump to Session.app, below; inside a herdr pane the [open-links](https://github.com/johntrandall/herdr-open-links) plugin handles the Ctrl+click directly). The page accepts one UUID (`#<uuid>` or `#session=<uuid>`) and nothing else |
| `/herdr-workspace#<workspace id>` | `herdr-jump://workspace/<id>` | focuses one herdr **workspace** (0.1.8; same handler app and plugin as `/herdr-jump`; `herdr workspace focus`). Forms: `#<id>` or `#id=<id>` (a herdr id such as `wBK`), or `#label=<url-encoded tab-bar label>`, which the handler matches ignoring the lifecycle glyphs in front and case, so it survives a herdr restart that renumbers ids |

`/reveal` and `/vault-setup` take the path two ways. The **short form** is the bare fragment:
`#notes/Plan.md` is relative to your home folder, `#/Volumes/x/y` is absolute, and only `/` is left
unencoded (`#a%20b/c`). It exists for places that show the whole URL, such as a terminal status line,
where `#path=%2FUsers%2Fme%2Fnotes%2FPlan.md` cost 35 columns of noise per row. The **long form**,
`#path=<percent-encoded path>`, still works. Relative paths are joined onto the home folder by the
handlers, which know it; the pages only check shape.

`/obsidian` is the [obsidian-link-bridge](https://github.com/johntrandall/obsidian-link-bridge) page,
unchanged. `/reveal` is new and needs a small handler app on the Mac, because browsers refuse to
navigate from https to `file:` at all.

## The handler apps

Browsers hand a custom scheme to whatever app registered it with Launch Services, so each local
action is a tiny AppleScript applet in `~/Applications`, built by `link-bridge install-handler`
(`handler/install.sh`) with `osacompile`. Each one runs a small Python gate inside its own bundle
before acting, logs to `~/Library/Logs/`, and shows a notification when it refuses a link.

**Reveal in Finder.app** (`reveal://`): `handler/reveal_decode.py` accepts only
`reveal://reveal?path=<path>` where the path exists (relative means under your home folder) and is
not inside an application or plug-in bundle, then runs `open -R <path>`. Why reveal and not open:
once a scheme is registered, any page or app can emit a link to it. A reveal can show you where a
file is; it cannot run it. You double-click if you want it opened.

**Jump to Session.app** (`herdr-jump://`): `handler/herdr_jump.py` accepts exactly one Claude Code
session UUID, asks `herdr agent list` which live pane holds it, runs `herdr tab focus` (which also
switches workspace) and brings the terminal forward (`LINK_BRIDGE_TERMINAL_APP`, default Terminal).
Since 0.1.8 the same app also takes `herdr-jump://workspace/<id>` and `herdr-jump://workspace/label/<label>`
(from `/herdr-workspace`), looks the workspace up in `herdr workspace list` (an exact label first, then the
label with its leading glyph tokens dropped, case-insensitively) and runs `herdr workspace focus <id>`.
Since 0.1.9, when the id is no longer live the app focuses the **current owner of that session's seat**
(asked by watchbill for its decision cards): the id's Claude name comes from herdr-lifecycle's role file or
handoff ledger (`~/.local/state/herdr-lifecycle`), `herdr-lifecycle siblings --all --json` names the live
members of that name's handoff chain (`<base>`, `<base>-ho2`, …), and the highest live `-hoN` is focused, else
any live member (the historian). `handler/herdr_jump.py --resolve <url>` prints what would be focused and why
without focusing. If the id is no longer live but its `~/.claude/sessions` record carries a user-given name (a `/clear`
keeps the name and mints a new id), the live pane with that name is focused instead; otherwise a herdr
notification says "Session gone" and nothing is focused. Nothing from the link ever reaches a shell.

```sh
link-bridge install-handler
open 'reveal://reveal?path=%2FUsers%2Fme'                    # a Finder window with your home folder selected
open 'herdr-jump://session/<claude session uuid>'             # that session's herdr tab comes to the front
open 'herdr-jump://workspace/wBK'                               # that herdr workspace comes to the front (0.1.8)
open 'herdr-jump://workspace/label/s-svc%20link-bridge'          # the same, by tab-bar label (glyphs and case ignored)
```

Chrome asks once per site and scheme whether it may open the app; tick "Always allow" for your
bridge host. Logs: `~/Library/Logs/reveal-in-finder.log`, `~/Library/Logs/jump-to-session.log`.

## Running it locally

The local server is the normal way to run it: loopback only, no network needed, nothing hosted.

```sh
brew services start link-bridge      # launchd keeps it up across logins; log: ~/Library/Logs/link-bridge.log
link-bridge serve --port 5465        # or run it in the foreground yourself
link-bridge doctor                   # server answering? handler installed?
```

Port 5465 spells LINK on a phone keypad; `--port` or `LINK_BRIDGE_PORT` picks another. `GET /healthz`
answers `link-bridge <version>`, directly and through the front door, so a status line can tell the
bridge from anything else that might sit on a port. The links
to hand out are `http://127.0.0.1:5465/reveal#…`, `/vault-setup#…` and `/obsidian#…` (`link-bridge url` prints them). Every
click stays on the machine, which is why `/reveal` and `/vault-setup` can exist at all: their
handler apps are on this Mac.

### Dropping the port: a local front door (optional)

`:5465` in every link is noise if you read these links all day. macOS lets only root bind port
80, so the clean way to lose the port is a small reverse proxy on 80 that routes by name and
leaves link-bridge running unprivileged on 5465. With [Caddy](https://caddyserver.com):

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

A ready-made kit is in [`frontdoor/`](frontdoor/) and runs with `brew install caddy &&
link-bridge install-front-door`: that Caddyfile, a LaunchDaemon plist with a full
`ServiceDescription`, and an installer that validates the config, copies it root-owned, adds the
hosts lines, bootstraps the daemon and verifies that only loopback listens. Or by hand:
run Caddy as root from a LaunchDaemon of your own (not `sudo brew services`, which leaves
root-owned files in the Homebrew prefix), add `127.0.0.1 link.localhost` and `::1 link.localhost`
to `/etc/hosts` for Safari and command-line tools (Chrome resolves `*.localhost` by itself), and
check with `sudo lsof -nP -iTCP:80 -sTCP:LISTEN` (root's listener is invisible to an unprivileged `lsof`; `netstat -an -p tcp | grep '\.80 '` also works) that only loopback addresses listen. From then on
`link-bridge url` prints `http://link.localhost/reveal#…` and `link-bridge doctor` reports
`front door: ok`. Set `LINK_BRIDGE_NAME` if you choose another name. A second local web app later
gets its own name in the same Caddyfile instead of a port.

## Running it remotely (Cloudflare Workers)

When a link has to work from a phone or another machine, for example in a calendar event, the
same `public/` folder deploys unchanged to Cloudflare Workers as static assets (`wrangler.jsonc`,
`_headers` carries the CSP). The server never sees the target: it travels in the URL fragment.

```sh
npm install -g wrangler              # or: brew install wrangler
cp deploy.env.example deploy.env     # git-ignored
$EDITOR deploy.env                   # CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_API_TOKEN, BRIDGE_DOMAIN
./deploy.sh                          # runs the tests, then `wrangler deploy --domain $BRIDGE_DOMAIN`
```

`BRIDGE_DOMAIN` must be a hostname in a zone on that Cloudflare account; Cloudflare creates the
DNS record. The API token needs the "Edit Cloudflare Workers" template plus Zone access to that
zone. Values in `deploy.env` may be 1Password secret references (`op://vault/item/field`);
`deploy.sh` then runs the deploy through `op run` so the secrets never land in a file. On a public
host only `/obsidian` is useful to everyone: `/reveal` and `/vault-setup` still need the handler
apps on the Mac that opens the link, and a phone has no Finder.

Both can run at once: local links for what you read on the Mac, the public host for what you read
elsewhere.

## From a phone or tablet (Moshi, a remote browser)

Serve the bridge over your tailnet as well as loopback (the policy pattern: upstream stays on
`127.0.0.1`, Tailscale Serve fronts it with HTTPS):

```sh
tailscale serve --bg --https=5465 http://127.0.0.1:5465   # https://<mac>.<tailnet>.ts.net:5465
```

Then `https://<mac>.<tailnet>.ts.net:5465/obsidian#vault=Notes&file=Plan` opens the note in
Obsidian on the device that opened the link (an iPad, if that vault is on it), and `/reveal` and
`/herdr-jump` show an **On the Mac** button instead of trying a scheme the device cannot handle:
the page POSTs `/act/reveal {"path"}`, `/act/herdr-jump {"session"}` or `/act/herdr-workspace {"workspace"}` / `{"label"}` (header `X-Link-Bridge: 1`)
and the bridge performs the action on the Mac through the same gates as the handler apps. The
header makes any cross-origin attempt a CORS preflight the server never answers. A terminal app
that cannot tap links (Moshi today) still needs the URL copied into a browser.

## Interface stability

Other tools depend on these; treat them as a contract and tell the consumers before changing or
renaming any of them (today: the Claude Code status line, [sightline](https://github.com/johntrandall/claude-statusline),
owned by the `statusline-architect` herdr session on John's Macs):

- `GET /healthz` → `200`, body starting `link-bridge` (then a space and the version)
- the routes `/obsidian#…`, `/reveal#…`, `/vault-setup#…`, `/herdr-jump#…`, `/herdr-workspace#…` (0.1.8+), and the
  actions `POST /act/reveal`, `POST /act/herdr-jump` (0.1.7+), `POST /act/herdr-workspace` (0.1.8+); `/herdr-jump` resolves an exited session to its seat's live owner (0.1.9+); `/obsidian` accepts any
  combination of Obsidian's `open` parameters (`vault`, `file`, `path`, plus `paneType`), `vault=` alone
  included (0.1.5+), or the Advanced URI set when `filepath=` is present, and refuses every other key
- the short home-relative fragment form (`#notes/Plan.md`, `#/abs/path`) beside `#path=…`
- the install command a consumer shows when the bridge is not running:
  `brew install johntrandall/tap/link-bridge && brew services start link-bridge && link-bridge install-handler`

A new page that wants a status-line row goes to the status-line owner, not straight into sightline.

## Requesting a change (for agents and people)

Message the link-bridge owner session (the herdr tab labelled `📡 link-bridge watch …`, Claude
address `d89e6d5a` until a successor is named) with: the surface that will show the link, the
scheme or action wanted, and who clicks it. The owner negotiates scope, may convene a short council
of expert subagents for anything that touches the security model, agrees a plan with you in writing,
implements it, cuts a release and bumps the tap, and tells the consumers listed under *Interface
stability*. New routes follow the existing shape: a fragment that never reaches a server, an
explicit allowlist on the page, and a handler app that re-checks on the Mac and can only reveal,
open or focus, never run.

## Security model

Once you tick a browser's "Always allow" for a bridge host, any link to that host opens the app
without a prompt, so a link someone else crafts must not be able to do more than open. Each page
therefore forwards only a fixed set of parameters and refuses anything else: `/obsidian` the
"open a note" parameters (Advanced URI can also run commands and write files via `commandid`,
`data`, `mode`, …; those are refused), `/reveal` and `/vault-setup` a single path. Beyond the
page, each handler app re-checks the link on the Mac (`reveal_decode.py`; obsidian-vault-setup's
`url --decode`): the path must exist, a reveal never opens anything, a vault-setup path must be
under your home folder. The pages load nothing from other sites and ship with a strict Content
Security Policy, `Referrer-Policy: no-referrer`, `X-Frame-Options: DENY` and `X-Robots-Tag:
noindex`.

What the bridge cannot hide: the app that shows the link sees the whole link. Google Calendar
stores it in the event, and its click-through redirect passes the full URL, fragment included,
through Google.

## Prior art, and why yet another one

The `/obsidian` page began life as [obsidian-link-bridge](https://github.com/johntrandall/obsidian-link-bridge),
itself yet another Obsidian link bridge. Others got there first, and they are worth a look:

- [obsid.net](https://obsid.net) ([source](https://github.com/jdevalk/obsid.net)): a redirect service, also
  self-hostable as a Cloudflare Worker, that turns `vault` and `file` query parameters into `obsidian://open` links.
- [Ibraheem-Khalil/obsidian-link-bridge](https://github.com/Ibraheem-Khalil/obsidian-link-bridge) (2025): a
  one-page redirect that reads `vault` and `file` from the query string and opens `obsidian://open`.
- [SvenAkk/obsidian-link-bridge](https://github.com/SvenAkk/obsidian-link-bridge): a static page on GitHub Pages
  that carries a note path and line in the URL fragment and opens it with Advanced URI.

Why another one: the two GitHub bridges carry no license, and without one nobody may legally copy, modify or
redistribute their code. obsid.net is MIT-licensed (stated on its site) and self-hostable, but it reads the note
from the query string in server code and only produces `obsidian://open` links. This project keeps the target out
of every request, runs no server code on a public host, supports Advanced URI, runs locally with nothing hosted at
all, reaches beyond Obsidian (Finder, vault setup), and is **MIT-licensed** (see [LICENSE](LICENSE)): fork it,
change it, ship it.

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
node --test test/                                         # page logic (obsidian, reveal, vault-setup, herdr-jump, herdr-workspace)
python3 -I -m unittest discover -s test -p 'test_*.py'    # handler gates (reveal_decode, herdr_jump)
```

## License

MIT
