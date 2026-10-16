#!/bin/sh
# Build and register the URL-scheme handler apps in ~/Applications:
#   "Reveal in Finder.app"  handles reveal://reveal?path=<path>        (select a file or folder in Finder)
#   "Jump to Session.app"   handles herdr-jump://session/<uuid>        (focus that Claude session's herdr tab)
# Re-run after editing an AppleScript or a resolver; each app is rebuilt in place.
set -eu
cd "$(dirname "$0")"
LSREGISTER=/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister
PB=/usr/libexec/PlistBuddy

python3 -I -m unittest discover -s ../test -p 'test_*.py' >/dev/null
mkdir -p "$HOME/Applications"

# build_applet <app name> <bundle id> <scheme> <applescript> <icon or -> <resource files...>
build_applet() {
  app="$HOME/Applications/$1.app"; bundle="$2"; scheme="$3"; script="$4"; icon="$5"; shift 5
  osacompile -o "$app" "$script"
  for res in "$@"; do cp "$res" "$app/Contents/Resources/"; done
  if [ "$icon" != "-" ] && [ -f "$icon" ]; then
    cp "$icon" "$app/Contents/Resources/applet.icns" && touch "$app"
  fi
  plist="$app/Contents/Info.plist"
  $PB -c "Delete :CFBundleURLTypes" "$plist" 2>/dev/null || true
  $PB -c "Add :CFBundleURLTypes array" "$plist"
  $PB -c "Add :CFBundleURLTypes:0 dict" "$plist"
  $PB -c "Add :CFBundleURLTypes:0:CFBundleURLName string $scheme" "$plist"
  $PB -c "Add :CFBundleURLTypes:0:CFBundleURLSchemes array" "$plist"
  $PB -c "Add :CFBundleURLTypes:0:CFBundleURLSchemes:0 string $scheme" "$plist"
  # osacompile writes no bundle id; Launch Services keys scheme claims on one.
  $PB -c "Set :CFBundleIdentifier $bundle" "$plist" 2>/dev/null || $PB -c "Add :CFBundleIdentifier string $bundle" "$plist"
  # Background-only: no Dock icon flash on every click.
  $PB -c "Set :LSUIElement true" "$plist" 2>/dev/null || $PB -c "Add :LSUIElement bool true" "$plist"
  [ -x "$LSREGISTER" ] && "$LSREGISTER" -f "$app"
  echo "Built $app; handles $scheme://"
}

build_applet "Reveal in Finder" com.johnrandall.reveal-in-finder reveal reveal-in-finder.applescript \
  /System/Library/CoreServices/Finder.app/Contents/Resources/Finder.icns reveal_decode.py
build_applet "Jump to Session" com.johnrandall.jump-to-session herdr-jump jump-to-session.applescript \
  /System/Applications/Utilities/Terminal.app/Contents/Resources/Terminal.icns herdr_jump.py

echo "Try:  open 'reveal://reveal?path=%2FUsers%2F$(id -un)'"
echo "      open 'herdr-jump://session/<claude session uuid>'   (needs herdr running)"
