-- "Reveal in Finder" — URL handler for reveal://reveal?path=<percent-encoded absolute path>.
-- Selects the file or folder in a Finder window (`open -R`). It never opens, launches or runs
-- anything, so a link from a web page, a chat message or a terminal status line can do no more
-- than show you where something is. Since 0.1.14 it also takes reveal://obsidian?path=<folder>:
-- the folder is shown in the Obsidian vault that holds it (reveal_obsidian.py: open a note in
-- the folder, then Obsidian's own "reveal active file in navigation"); a folder outside every
-- registered vault is refused with a notification.
--
-- The link is decoded and checked by reveal_decode.py inside this bundle (tested in test/):
-- scheme and host must match, the only parameter is path=, the path must be absolute and exist,
-- and it may not point inside an application or plug-in bundle. A refused link prints nothing.
-- Built by handler/install.sh with osacompile, which also registers the URL scheme.
-- Log: ~/Library/Logs/reveal-in-finder.log

on open location theURL
	set targetPath to ""
	set decoder to POSIX path of (path to resource "reveal_decode.py")
	try
		set targetPath to do shell script "/usr/bin/python3 -I " & quoted form of decoder & " " & quoted form of theURL
	end try
	if targetPath is "" then
		do shell script "printf '%s refused %s\\n' \"$(date '+%Y-%m-%dT%H:%M:%S')\" " & quoted form of theURL & " >> \"$HOME/Library/Logs/reveal-in-finder.log\""
		display notification "Refused: " & theURL with title "Reveal in Finder"
		return
	end if
	if theURL starts with "reveal://obsidian?" then
		set revealer to POSIX path of (path to resource "reveal_obsidian.py")
		set outcome to "0"
		try
			do shell script "/usr/bin/python3 -I " & quoted form of revealer & " " & quoted form of targetPath & " >/dev/null 2>&1"
		on error errMsg number errNum
			set outcome to errNum as string
		end try
		do shell script "printf '%s obsidian %s exit %s\\n' \"$(date '+%Y-%m-%dT%H:%M:%S')\" " & quoted form of targetPath & " " & quoted form of outcome & " >> \"$HOME/Library/Logs/reveal-in-finder.log\""
		if outcome is "2" then
			display notification "Not inside a registered Obsidian vault: " & targetPath with title "Reveal in Finder"
		else if outcome is "3" then
			display notification "No note in that folder; the vault is open" with title "Reveal in Finder"
		end if
		return
	end if
	do shell script "printf '%s reveal %s\\n' \"$(date '+%Y-%m-%dT%H:%M:%S')\" " & quoted form of targetPath & " >> \"$HOME/Library/Logs/reveal-in-finder.log\"; /usr/bin/open -R " & quoted form of targetPath
end open location

on run
	display notification "This app only handles reveal:// links (reveal and obsidian)." with title "Reveal in Finder"
end run
