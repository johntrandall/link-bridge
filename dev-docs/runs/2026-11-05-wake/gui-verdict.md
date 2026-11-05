---
verdict: pass
sha: 287aaf8ac8b7dd48087f8ffc36e9ac3e6f5c6b23
looked_by: designer
looked_at: "/wake#link-bridge/lead-designer and /wake#../etc, served from the branch on 127.0.0.1:5498, rendered by headless Chrome at 700x520"
screenshot: dev-docs/runs/2026-11-05-wake/wake-page.png
---
# GUI look: the /wake page (0.1.15)

Release mode is instant (deterministic system, no gate between landing and the human's view), so the lead designer's own look writes this verdict, marked `looked_by: designer` (watchbill:lead-designer, the GUI verdict rule).

Looked at first on d2799ad at 17:44 and again on the tip 287aaf8 at 18:3x EST (the page's files changed after the security verdict: onmac.js ignores a second click and hides the button after a wake, bridge.css dims a disabled button; the load state is unchanged, below), headless Chrome (`/Applications/Google Chrome.app`), dark scheme:

- `/wake#link-bridge/lead-designer` (`wake-page.png`): title "Wake a watchbill seat"; the question "Wake the lead-designer of link-bridge? The Mac runs:"; the exact command `watchbill resume link-bridge --seat lead-designer` in monospace; one button "Wake it on the Mac"; the note saying nothing happens until the button is pressed, what resume refuses, and that there is no scheme form. Nothing fired on load (the server log shows only the GET).
- `/wake#../etc` (`wake-page-refused.png`): "The system name is not a watchbill slug." and no button.

Pass: the page says what the click will run before it runs anything, and a refused fragment shows no button.

The click state (button dimmed while the Mac answers, hidden after a 200 wake) was not screenshotted: headless Chrome's screenshot takes no click; the cold verifier checked that behaviour in the code (security-verdict.md, finding 3) and the two-clicks test checks the server side.
