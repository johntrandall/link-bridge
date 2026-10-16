#!/bin/sh
# Install or update the local front door (Caddy on 127.0.0.1:80 as a root LaunchDaemon).
# Run as your own user from this directory; it calls sudo where root is unavoidable.
# Idempotent: re-run after editing the Caddyfile or adding a name.
set -eu
cd "$(dirname "$0")"
LABEL=com.link-bridge.front-door
CONF_DIR=/usr/local/etc/link-bridge-front-door
PLIST=/Library/LaunchDaemons/$LABEL.plist
CADDY=/opt/homebrew/opt/caddy/bin/caddy

[ -x "$CADDY" ] || { echo "install: $CADDY missing; brew install caddy" >&2; exit 1; }
"$CADDY" validate --config Caddyfile --adapter caddyfile >/dev/null
plutil -lint "$LABEL.plist" >/dev/null

echo "== config -> $CONF_DIR (root-owned: a root process must not read a user-writable config)"
sudo install -d -m 0755 -o root -g wheel "$CONF_DIR"
sudo install -m 0644 -o root -g wheel Caddyfile "$CONF_DIR/Caddyfile"

echo "== /etc/hosts: one loopback line per name in the Caddyfile (Safari and CLI tools; Chrome needs none)"
# Fleet policy 49 allows any hostname on 127.0.0.1 / ::1; it rejects other addresses.
for name in $(sed -nE 's/^http:\/\/([a-z0-9.-]+) \{$/\1/p' Caddyfile); do
  for addr in 127.0.0.1 ::1; do
    if ! grep -qE "^$addr[[:space:]]+$name([[:space:]]|$)" /etc/hosts; then
      printf '%s\t%s\n' "$addr" "$name" | sudo tee -a /etc/hosts >/dev/null
      echo "   added $addr $name"
    fi
  done
done

echo "== LaunchDaemon $PLIST"
sudo install -m 0644 -o root -g wheel "$LABEL.plist" "$PLIST"
if sudo launchctl print "system/$LABEL" >/dev/null 2>&1; then
  sudo launchctl bootout "system/$LABEL" || true
  sleep 1
fi
sudo launchctl bootstrap system "$PLIST"
sleep 2

echo "== verify: loopback-only listeners on :80"
lsof -nP -iTCP:80 -sTCP:LISTEN | awk 'NR>1 {print "   " $1, $2, $9}'
if lsof -nP -iTCP:80 -sTCP:LISTEN | awk 'NR>1 {print $9}' | grep -vqE '^(127\.0\.0\.1|\[::1\]):80$'; then
  echo "install: a :80 listener is NOT on loopback; check default_bind in the Caddyfile" >&2; exit 1
fi
for name in $(sed -nE 's/^http:\/\/([a-z0-9.-]+) \{$/\1/p' Caddyfile); do
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 "http://$name/" || true)
  echo "   http://$name/ -> $code"
done
echo "done. Log: /Library/Logs/link-bridge-front-door.log"
