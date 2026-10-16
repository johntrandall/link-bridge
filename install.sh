#!/bin/sh
# Non-Homebrew install: put `link-bridge` on PATH (symlink, so `git pull` updates it).
set -eu
cd "$(dirname "$0")"
mkdir -p "$HOME/.local/bin"
ln -sfn "$PWD/bin/link-bridge" "$HOME/.local/bin/link-bridge"
echo "Linked ~/.local/bin/link-bridge -> $PWD/bin/link-bridge"
echo "Next: link-bridge install-handler ; link-bridge serve   (or start it from a LaunchAgent)"
