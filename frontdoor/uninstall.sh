#!/bin/sh
# Remove the local front door: daemon, config, and the /etc/hosts lines install.sh added.
set -eu
cd "$(dirname "$0")"
LABEL=com.link-bridge.front-door
sudo launchctl bootout "system/$LABEL" 2>/dev/null || true
sudo rm -f "/Library/LaunchDaemons/$LABEL.plist"
sudo rm -rf /usr/local/etc/link-bridge-front-door
for name in $(sed -nE 's/^http:\/\/([a-z0-9.-]+) \{$/\1/p' Caddyfile); do
  sudo sed -i '' -E "/^(127\.0\.0\.1|::1)[[:space:]]+$name([[:space:]]|$)/d" /etc/hosts
done
echo "removed $LABEL; /etc/hosts entries for the front-door names deleted"
