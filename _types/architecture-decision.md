---
kind: mdbase.type
name: architecture-decision
version: 1
match:
  path_glob: "dev-docs/decisions/ADR-*.md"
schema:
  dialect: json-schema-2020-12
  value:
    type: object
    additionalProperties: false
    required: [number, title, status, proposed_by, proposed_at]
    properties:
      number: { type: integer, minimum: 1 }
      title: { type: string, minLength: 1 }
      system: { type: [string, "null"] }
      status: { enum: [proposed, accepted, implemented, superseded] }
      proposed_by: { type: string, minLength: 1 }
      proposed_at: { type: string, minLength: 1 }
      accepted_at: { type: [string, "null"] }
      accepted_how: { type: [string, "null"] }
      supersedes: { type: [string, "null"] }
      superseded_by: { type: [string, "null"] }
      from_decision: { type: [string, "null"] }
      said_in: { type: [string, "null"] }
      spawned: { type: [string, "null"] }
      implemented_at: { type: [string, "null"] }
      implemented_how: { type: [string, "null"] }
      migrated_from: { type: [string, "null"] }
x-watchbill:
  awaiting_human: { field: status, values: [proposed] }
---
# architecture-decision (ADR)

An architecture decision record in `dev-docs/decisions/`, `status: proposed` until the human accepts it (ADR-0001), `accepted` once he has, `implemented` once the work landed, `superseded` when a later ADR replaces it; `_decisions.base` is the view. `watchbill land --approved ADR-NNNN` sets `implemented`, `implemented_at` (the landing's time) and `implemented_how` (the landing SHA) on an accepted ADR, so no agent types them. The other keys: `system` (the registry name, 0.10.41: both boards filter on it, so a system's ADRs stay its own through the cross-system queue vault; `watchbill systems init --refresh-bases` stamps it on ADRs that lack it), `supersedes` / `superseded_by` (ADR numbers as strings), `from_decision` (the substantive decision it came from), `said_in` (where the human said it), `spawned` (what it spawned), `migrated_from` (where a migrated record came from). Shipped by the watchbill plugin (`watchbill systems init`); the key set was agreed with the consumer architects on 2026-10-20 (cycle 2026-10-20-queued).
