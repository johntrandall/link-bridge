#!/bin/sh
# Build and register "~/Applications/Reveal in Finder.app", the handler for reveal:// links.
# Re-run after editing the AppleScript or the decoder; it rebuilds in place.
set -eu
cd "$(dirname "$0")"
APP="$HOME/Applications/Reveal in Finder.app"
BUNDLE_ID="com.johnrandall.reveal-in-finder"
SCHEME="reveal"
LSREGISTER=/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister

python3 -I -m unittest discover -s ../test -p 'test_reveal_decode.py' >/dev/null
mkdir -p "$HOME/Applications"
osacompile -o "$APP" reveal-in-finder.applescript
cp reveal_decode.py "$APP/Contents/Resources/reveal_decode.py"
# Finder's own icon, so the "open this app?" prompt is recognisable.
ICON=/System/Library/CoreServices/Finder.app/Contents/Resources/Finder.icns
[ -f "$ICON" ] && cp "$ICON" "$APP/Contents/Resources/applet.icns" && touch "$APP"

PLIST="$APP/Contents/Info.plist"
PB=/usr/libexec/PlistBuddy
$PB -c "Delete :CFBundleURLTypes" "$PLIST" 2>/dev/null || true
$PB -c "Add :CFBundleURLTypes array" "$PLIST"
$PB -c "Add :CFBundleURLTypes:0 dict" "$PLIST"
$PB -c "Add :CFBundleURLTypes:0:CFBundleURLName string $SCHEME" "$PLIST"
$PB -c "Add :CFBundleURLTypes:0:CFBundleURLSchemes array" "$PLIST"
$PB -c "Add :CFBundleURLTypes:0:CFBundleURLSchemes:0 string $SCHEME" "$PLIST"
# osacompile writes no bundle id; Launch Services keys scheme claims on one.
$PB -c "Set :CFBundleIdentifier $BUNDLE_ID" "$PLIST" 2>/dev/null || $PB -c "Add :CFBundleIdentifier string $BUNDLE_ID" "$PLIST"
# Background-only: no Dock icon flash on every click.
$PB -c "Set :LSUIElement true" "$PLIST" 2>/dev/null || $PB -c "Add :LSUIElement bool true" "$PLIST"
[ -x "$LSREGISTER" ] && "$LSREGISTER" -f "$APP"
echo "Built $APP; handles $SCHEME://reveal?path=<percent-encoded absolute path>"
echo "Try:  open 'reveal://reveal?path=%2FUsers%2F$(id -un)'"
