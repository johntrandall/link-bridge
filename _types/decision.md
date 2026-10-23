---
kind: mdbase.type
name: decision
version: 1
match:
  path_glob: "dev-docs/substantive/*.md"
schema:
  dialect: json-schema-2020-12
  value:
    type: object
    additionalProperties: false
    required: [type, kind, system, question, status, asked_by, asked_at]
    properties:
      type: { const: decision }
      kind: { enum: [decision, approval, discussion] }
      weight: { enum: [quick, big, null] }
      asks: { enum: [approval, null] }
      system: { type: string, minLength: 1 }
      title: { type: [string, "null"], maxLength: 60 }
      question: { type: string, minLength: 1 }
      options: { type: [array, "null"], items: { type: string } }
      recommendation: { type: [string, "null"] }
      unblocks: { type: [string, "null"] }
      asked_by: { type: string, minLength: 1 }
      asked_at: { type: string, minLength: 1 }
      asked_via: { enum: [chat, ask-user-question, board, track-changes] }
      status: { enum: [draft, open, provisional, answered, applied, withdrawn] }
      applied_at: { type: [string, "null"] }
      applied_how: { type: [string, "null"] }
      undo: { type: [string, "null"] }
      source: { type: [string, "null"] }
      recorded_where: { type: [string, "null"] }
      relayed_by: { type: [string, "null"] }
      spawned: { type: [string, "null"] }
      subject: { type: [string, "null"] }
      subject_fingerprint: { type: [string, "null"] }
      _human_verdict: { type: [string, "null"] }
      human_verdict: { type: [string, "null"] }
      human_note: { type: [string, "null"] }
      human_words: { type: [string, "null"] }
      snooze_until: { type: [string, "null"] }
      previous_verdict: { type: [string, "null"] }
      moved_at: { type: [string, "null"] }
      moved_by: { type: [string, "null"] }
      working_by: { type: [string, "null"] }
      waiting_on: { type: [string, "null"] }
      revisit_when: { type: [string, "null"] }
      revisit_of: { type: [string, "null"] }
      revisits: { type: [array, "null"], items: { type: string } }
      review_marks: { type: [array, "null"], items: { type: string } }
x-watchbill:
  awaiting_human: { field: status, values: [open, provisional] }
---
# decision (substantive)

One substantive decision for the human, tied to no item (ADR-0001): a file in `dev-docs/substantive/`, the `_substantive.base` kanban as the view, `human_*` fields the human's alone. Shipped by the watchbill plugin (`watchbill systems init`); `watchbill decide` writes these records.

`_human_verdict` is a lane (0.10.50, `references/decisions.md`, "The lanes"): the human's (`snoozed`, `yes`, `no`, `revise substance`, `revise presentation`, `later`, `talk`, or one of the card's own `options`) or the agent's (`to review`, `new`, `returning`, `agent drafting`, `agent working`, `agent waiting`, `agent scheduled`, `processed`), so the schema takes any string and `watchbill decide` checks a verdict against the card's options. An agent writes the field only through the `watchbill decide` verbs, which keep the human's verdict in `previous_verdict`. A system that adds properties of its own keeps them across `systems init --refresh-bases`. The key was `human_verdict` before 0.10.50; the schema still allows it for one release, `watchbill` reads it as `_human_verdict`, and `--refresh-bases` renames it on every card. `weight` is `quick` or `big` (0.10.50): a big card (a document under Track Changes review, a design or ADR approval, or one the seat marks big with `decide --weight big`) is presented in `to review`, a quick one in `new` and then `returning`; his drag between `new` and `to review` sets it. `snooze_until` is the human's: an ISO date he may type on a snoozed card, on which `watchbill decisions sweep` brings it back as returning.
