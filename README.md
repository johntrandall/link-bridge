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
brew services start link-bridge      # http://localhost:5465, keeps running across logins
link-bridge install-handler          # ~/Applications/Reveal in Finder.app, the reveal:// handler
brew install obsidian-vault-setup && obsidian-vault-setup install-finder-button   # optional: /vault-setup links
link-bridge doctor
```

Without Homebrew: `git clone https://github.com/johntrandall/link-bridge && cd link-bridge && ./install.sh`
puts `link-bridge` on your PATH; run `link-bridge serve` from a LaunchAgent of your own.

```bash
link-bridge url ~/notes/Plan.md
# http://localhost:5465/reveal#notes/Plan.md
link-bridge url --vault-setup ~/dev/project
# http://localhost:5465/vault-setup#dev/project
```

| Route | Forwards to | What happens |
|---|---|---|
| `/obsidian#vault=…&filepath=…&openmode=tab` | `obsidian://advanced-uri?…` or `obsidian://open?…` | opens a note in Obsidian ("open a note" parameters only) |
| `/reveal#notes/Plan.md` | `reveal://reveal?path=…` | selects the file or folder in a Finder window; never opens it |
| `/vault-setup#dev/project` | `obsidian-vault-setup://open?path=…` | opens the Obsidian vault at the folder's git root, or creates it; needs [obsidian-vault-setup](https://github.com/johntrandall/obsidian-vault-setup) and its handler app |

`/reveal` and `/vault-setup` take the path two ways. The **short form** is the bare fragment:
`#notes/Plan.md` is relative to your home folder, `#/Volumes/x/y` is absolute, and only `/` is left
unencoded (`#a%20b/c`). It exists for places that show the whole URL, such as a terminal status line,
where `#path=%2FUsers%2Fme%2Fnotes%2FPlan.md` cost 35 columns of noise per row. The **long form**,
`#path=<percent-encoded path>`, still works. Relative paths are joined onto the home folder by the
handlers, which know it; the pages only check shape.

`/obsidian` is the [obsidian-link-bridge](https://github.com/johntrandall/obsidian-link-bridge) page,
unchanged. `/reveal` is new and needs a small handler app on the Mac, because browsers refuse to
navigate from https to `file:` at all.

## The reveal handler

`handler/install.sh` builds `~/Applications/Reveal in Finder.app` with `osacompile` and registers
the `reveal` URL scheme. On a link it runs `handler/reveal_decode.py`, which accepts only
`reveal://reveal?path=<absolute path>` where the path exists and is not inside an application or
plug-in bundle, then runs `open -R <path>`. Anything else is refused, logged to
`~/Library/Logs/reveal-in-finder.log` and announced with a notification.

```sh
sh handler/install.sh
open 'reveal://reveal?path=%2FUsers%2Fme'      # a Finder window with your home folder selected
```

Why reveal and not open: once a scheme is registered, any page or app can emit a link to it. A
reveal can show you where a file is; it cannot run it. You double-click if you want it opened.

## Running it locally

The local server is the normal way to run it: loopback only, no network needed, nothing hosted.

```sh
brew services start link-bridge      # launchd keeps it up across logins; log: ~/Library/Logs/link-bridge.log
link-bridge serve --port 5465        # or run it in the foreground yourself
link-bridge doctor                   # server answering? handler installed?
```

Port 5465 spells LINK on a phone keypad; `--port` or `LINK_BRIDGE_PORT` picks another. The links
to hand out are `http://localhost:5465/reveal#…`, `/vault-setup#…` and `/obsidian#…`. Every
click stays on the machine, which is why `/reveal` and `/vault-setup` can exist at all: their
handler apps are on this Mac.

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
node --test test/                                                  # page logic (obsidian.js, reveal.js)
python3 -I -m unittest discover -s test -p 'test_reveal_decode.py'  # handler decoder
```

## License

MIT
