#!/bin/sh
set -eu
[ -L "$HOME/.local/bin/link-bridge" ] && rm "$HOME/.local/bin/link-bridge" && echo "Removed ~/.local/bin/link-bridge"
echo "Handler app: move ~/Applications/Reveal in Finder.app to the Trash if you no longer want reveal:// links."
