# frontdoor: drop the port with Caddy on 127.0.0.1:80

`http://link.localhost/reveal#notes/Plan.md` instead of `http://127.0.0.1:5465/…`. Caddy routes by
hostname on port 80 and proxies to link-bridge, which keeps running unprivileged on 5465. Only root may
bind 80 on macOS, so Caddy runs as a root LaunchDaemon; everything binds loopback only.

```sh
brew install caddy
sh install.sh        # sudo prompts inside: config, /etc/hosts lines, LaunchDaemon, loopback check
link-bridge doctor   # front door: ok (200 http://link.localhost/reveal)
```

| File | Installed to |
|---|---|
| `Caddyfile` | `/usr/local/etc/link-bridge-front-door/Caddyfile` (root-owned: a root process must not read a user-writable config) |
| `com.link-bridge.front-door.plist` | `/Library/LaunchDaemons/` (the `ServiceDescription` inside explains the why and the ops) |
| `install.sh` / `uninstall.sh` | run from here as your own user |

Not `sudo brew services start caddy`: that leaves root-owned files under the Homebrew prefix and
breaks later non-root `brew upgrade` and `cleanup`. The Caddy binary stays brew-managed; only the
service is this plist. macOS does not resolve `*.localhost` on its own (Chrome does), so the installer
adds `127.0.0.1 link.localhost` and `::1 link.localhost` to `/etc/hosts` for Safari and command-line
tools. Another local web app later gets its own `http://<name>.localhost { reverse_proxy … }` block;
re-run `install.sh`.
