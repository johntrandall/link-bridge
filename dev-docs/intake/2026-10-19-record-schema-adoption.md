---
type: intake
system: "link-bridge"
project: ""
event: "request"
date: 2026-10-19
from: "knowledge-base-trials (admin-technical session 676e6c6c-e5d4-4b6c-87fd-40b0451b8cd6)"
commit: "~/dev/knowledge-base-trials 4e77b62 (dev-docs/record-schema-design.md)"
processed: null
---

## What this is

A notice and a backfill request, approved by John 2026-10-19: every watchbill system's record folders are to carry a
schema that one general-purpose tool enforces on every agent write and every commit. John: "I'd like the watchbill
architects to always use whatever system it is that you are building ... notify all the architects so they can
backfill." The same request has gone to the watchbill plugin system to make it a rule and a skill.

## What it is, in one paragraph

A record folder declares its schema in a type file, `_types/<kind>.md` (mdbase shape: a markdown note whose
frontmatter wraps a plain JSON Schema 2020-12 under `schema.value`, with `match.path_glob` naming the folder), and the
system home carries a one-line `mdbase.yaml`. One tool, `record-schema`, validates any record against its folder's
type file with six fixed file-test rules; a global PostToolUse hook and a global pre-commit gate call it. Nothing is
configured per system. Design: `~/dev/knowledge-base-trials/dev-docs/record-schema-design.md` (commit 4e77b62).

## What this system's architect is asked to do

- Now: nothing to build. Read the design doc and check the folder list below; reply in `processed` if a folder is
  wrong or missing, or if a record kind has a vocabulary that lives only in people's heads.
- When `record-schema init` ships (expected this week; a second note or message will say so): run it on each record
  folder below, edit the draft type file (confirm enums, strike typos, decide required fields), run the check once,
  loosen or fix, commit the type files with the records.
- Stewards and crew learn one sentence: a write that comes back with `schema:` lines names the record, the field and
  the rule; fix the field and write again.

## Candidate record folders detected in this system's home (frontmatter notes, or a .base present)

- (none detected; intake only)

(Detection is mechanical: folders with five or more frontmatter notes, or a `.base` file. The architect decides.)
