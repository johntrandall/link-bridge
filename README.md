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

## Serving it elsewhere (optional)

The local server is the normal way to run it. The same `public/` folder also deploys unchanged to
Cloudflare Workers as static assets (`wrangler.jsonc`, `deploy.sh`, `_headers` for the CSP) when a
link has to work from a phone or another machine, for example in a calendar event. Note that
`/reveal` is only useful where the handler app is installed, so on a public host it mostly serves
`/obsidian`.

## Tests

```sh
node --test test/                                                  # page logic (obsidian.js, reveal.js)
python3 -I -m unittest discover -s test -p 'test_reveal_decode.py'  # handler decoder
```

## License

MIT
