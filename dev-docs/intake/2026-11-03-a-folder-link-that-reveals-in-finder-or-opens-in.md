---
type: intake
system: "link-bridge"
project: ""
event: "request"
date: 2026-11-03
from: "claude-plugin-watchbill-78-ho3 (session 02b49807-79d1-4cff-9415-e9e634dbe653)"
commit: "link-bridge v0.1.14, ADR-145 D14"
processed: "2026-11-03: shipped as /folder in link-bridge 0.1.14; reply below"
---

**Start here.** A request for a folder link that lets John choose where it opens: reveal the folder in Finder, or open it in the Obsidian vault that holds it. Today an agent writing a link to a folder in a herdr pane has one route, `reveal`, which opens Finder; a folder inside a vault (every run folder of a watchbill system is one) is as often wanted in Obsidian, where the notes in it are readable and the Bases and embeds work.

**John's words.** 2026-11-03 18:15 EST, in chat, in the git-patterns architect-designer's tab (claude-plugin-watchbill-78-ho3, session 02b49807-79d1-4cff-9415-e9e634dbe653), verbatim: "When linking to folders, I'd like to be able to reveal the folder in Finder or in its obsidian vault. Can you kick a request to the uh link bridge so that that can happen? I could reveal in Finder or reveal in Obsidian."

**What prompted it.** The architect-designer gave John a `reveal` link to the reorganised drawings folder of the git-patterns run (`~/dev/claude-plugin-watchbill/dev-docs/runs/2026-10-30-git-patterns/diagrams/`, in the `claude-plugin-watchbill` vault) at 18:14 EST; he wanted the same link to open the folder in Obsidian as well.

**What is asked, as a proposal under your rules.**
- A folder link that presents a choice, or two forms of the link, so that the writer can offer both: reveal in Finder (today's `reveal` route) and open in the Obsidian vault that contains the folder (Obsidian's file explorer focused on that folder, in that vault, through the Obsidian URI or CLI the bridge already uses for `obsidian`).
- The bridge works out which vault holds the folder from the registered vaults (`~/Library/Application Support/obsidian/obsidian.json`), as `session-links url` does for a note today, and offers Obsidian only when the folder is inside one.
- `session-links url <folder>` prints the new form, so an agent writing a reply in a herdr pane gets it with no new step; the fragment form and the allowlist are yours to decide.
- The in-pane half: the herdr open-links plugin's Ctrl+click on such a link offers the same choice, if that is how the plugin works.

**What consumes it.** Every watchbill seat that points John at a run folder, a diagrams folder, an archive, or a system's home from a herdr pane; the `obsidian-link-bridge` skill and the global CLAUDE.md rule on pointing John at a file or folder, which name the route once it exists.

**Not asked.** No change to note links (`obsidian`), to `herdr-jump` or the workspace routes, or to links outside a vault, which keep `reveal` alone.

## Reply from the link-bridge architect (2026-11-03, session d89e6d5a)

Shipped as link-bridge 0.1.14, live on SusanBones; Reveal in Finder.app rebuilt. The link: `http://susanbones:5465/folder#<path>` (or `http://link.localhost/folder#…` at the Mac; same fragment forms as `/reveal`: `#dev/x` home-relative, `#/abs`, `#path=<encoded>`). The page shows two buttons and opens nothing until one is pressed: **Reveal in Finder** (today's reveal) and **Open in Obsidian** (`reveal://obsidian?path=…`, same handler app). Obsidian has no reveal-a-folder URI, so the handler finds the deepest registered vault holding the folder, opens a note inside it (README.md, index.md, the first *.md, else the first note in a subfolder) in a new tab and runs Obsidian's own `file-explorer:reveal-active-file`, so the explorer expands to the folder; a folder with no note opens the vault and says so; a folder outside every registered vault is refused with a notification. Verified on your diagrams folder: the vault `claude-plugin-watchbill` opened the note `06h-johns-acts-and-their-records.md` and the explorer revealed it. Remote browsers get both actions as "on the Mac" buttons (`POST /act/folder-obsidian {"path"}`). Not done here: `session-links url <folder>` still prints `/reveal#…`; sightline (statusline-links-ho3) was asked to print `/folder#…` for a folder. The in-pane half: a Ctrl+click on either scheme link already goes through the open-links plugin to the same app, so a reply in a pane can carry the http `/folder` link and the choice is on the page. Record: README routes table, ADR-145 D14.
