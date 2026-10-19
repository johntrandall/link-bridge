---
type: intake
system: "link-bridge"
project: ""
event: "release"
date: 2026-10-19
from: "knowledge-base-trials (admin-technical session 676e6c6c-e5d4-4b6c-87fd-40b0451b8cd6)"
commit: "~/dev/record-schema 6f5a1ca"
processed: null
---

## What this is

`record-schema init` has shipped (release, 2026-10-19). This is the second note promised in
`dev-docs/intake/2026-10-19-record-schema-adoption.md`: the backfill can start. Design: `~/dev/knowledge-base-trials/dev-docs/record-schema-design.md`
(4e77b62). Tool: `~/dev/record-schema` (commit 6f5a1ca), on PATH as `record-schema`.

## What the architect does (once per record folder, about ten minutes each)

```
printf 'spec_version: "0.3.0"\n' > <system home>/mdbase.yaml      # once per system, if absent
record-schema init <system home>/<folder>                           # writes _types/<folder>.md, never overwrites
$EDITOR <system home>/_types/<folder>.md                            # confirm enums, strike typos, set required, narrow the glob
record-schema check <system home>/<folder>/*.md                     # 0 diagnostics, or loosen / fix
git add mdbase.yaml _types/<folder>.md && git commit                # with the records
```

`init` reads the records, the folder's `_*template*.md` comments (`key: v  # a | b | c` becomes an enum) and the
sibling `.base` (column names and order). It marks fields missing from some records with `x-present-in` and lists
files in the folder that have no frontmatter, so a glob can exclude them. Verified today on job-hunt companies
(542 records), jobs (212), events (44), trackers (24) and an intake folder: each validates against its own draft
with zero diagnostics once non-record documents are excluded.

## What is not there yet

The two adapters that enforce automatically, the global PostToolUse hook and the global pre-commit command, land
next; until then `record-schema check` is run by hand. Both engines agree on YAML 1.2 core: `20:00`, `off`, `yes`
are strings. A one-item-list-or-null field is `type: [array, "null"]`.

Reply in `processed` with the commit that lands your type files, or with what blocked you.
