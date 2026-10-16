-- "Reveal in Finder" — URL handler for reveal://reveal?path=<percent-encoded absolute path>.
-- Selects the file or folder in a Finder window (`open -R`). It never opens, launches or runs
-- anything, so a link from a web page, a chat message or a terminal status line can do no more
-- than show you where something is.
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
	do shell script "printf '%s reveal %s\\n' \"$(date '+%Y-%m-%dT%H:%M:%S')\" " & quoted form of targetPath & " >> \"$HOME/Library/Logs/reveal-in-finder.log\"; /usr/bin/open -R " & quoted form of targetPath
end open location

on run
	display notification "This app only handles reveal:// links." with title "Reveal in Finder"
end run
