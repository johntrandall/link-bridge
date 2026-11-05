---
verdict: pass
sha: d2799ad
looked_by: designer
looked_at: "/wake#link-bridge/lead-designer and /wake#../etc, served from the branch on 127.0.0.1:5498, rendered by headless Chrome at 700x520"
screenshot: dev-docs/runs/2026-11-05-wake/wake-page.png
---
# GUI look: the /wake page (0.1.15)

Release mode is instant (deterministic system, no gate between landing and the human's view), so the lead designer's own look writes this verdict, marked `looked_by: designer` (watchbill:lead-designer, the GUI verdict rule).

Looked at, 2026-11-05 17:44 EST, headless Chrome (`/Applications/Google Chrome.app`), dark scheme:

- `/wake#link-bridge/lead-designer` (`wake-page.png`): title "Wake a watchbill seat"; the question "Wake the lead-designer of link-bridge? The Mac runs:"; the exact command `watchbill resume link-bridge --seat lead-designer` in monospace; one button "Wake it on the Mac"; the note saying nothing happens until the button is pressed, what resume refuses, and that there is no scheme form. Nothing fired on load (the server log shows only the GET).
- `/wake#../etc` (`wake-page-refused.png`): "The system name is not a watchbill slug." and no button.

Pass: the page says what the click will run before it runs anything, and a refused fragment shows no button.
