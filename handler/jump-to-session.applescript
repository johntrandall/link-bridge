-- "Jump to Session" — URL handler for herdr-jump://session/<claude-session-uuid>.
-- Focuses the herdr tab that holds that Claude session (herdr_jump.py inside this bundle does
-- the resolution: `herdr agent list` -> `herdr tab focus`), then brings the terminal forward.
-- The URL goes to the script as a single quoted argument; nothing from it is interpolated into
-- the shell, and the script refuses anything that is not exactly one session uuid.
-- Built by handler/install.sh with osacompile, which also registers the URL scheme.
-- Log: ~/Library/Logs/jump-to-session.log

on open location theURL
	set resolver to POSIX path of (path to resource "herdr_jump.py")
	do shell script "HERDR_BIN_PATH=/opt/homebrew/bin/herdr /usr/bin/python3 -I " & quoted form of resolver & " " & quoted form of theURL & " >/dev/null 2>&1 &"
end open location

on run
	display notification "This app only handles herdr-jump:// links." with title "Jump to Session"
end run
