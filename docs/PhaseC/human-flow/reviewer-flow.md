# Human-in-the-loop reviewer flow

## State machine
```
┌──────────────────┐  promote(reviewer-confirmed)  ┌──────────────────────┐
│ auto-generated   │ ────────────────────────────► │ reviewer-confirmed   │
└────────┬─────────┘                               └─────────┬────────────┘
         │  change_impact_reset                              │ promote(board-approved)
         │  (dataset_hash / git_sha / etc)                   ▼
         │                                         ┌──────────────────────┐
         │  ◄─────────────────────────────────────│ board-approved       │
         │                       any reset trigger └──────────────────────┘
         ▼
   (back to auto-generated)
```

## Roles
- **author** — creates the model, runs `train_intelligence.py`, drafts the
  assurance case
- **reviewer** — independent of author; signs the case to move state from
  `auto-generated` → `reviewer-confirmed`
- **board** — V&V lead + safety lead; signs once a model is intended to
  influence any quantitative decision (even advisory) → `board-approved`

## Promotion rules
- `auto-generated` → `reviewer-confirmed`
  - Reviewer ≠ author
  - All assurance lint checks pass
  - Reviewer has read the assurance case AND the registry meta + dataset
- `reviewer-confirmed` → `board-approved`
  - 2+ board signatures
  - At least one prior `reviewer-confirmed` cycle was consumed in
    production without escape
- Any state → `auto-generated`
  - On any change_impact reset (see §10 of each case)

## Where it's recorded
- `evidence/registry/<model>/<version>/meta.json::approval_state`
- `human_review` Silver row written by the governance tool, with
  `(reviewer_role, adjudication, rationale, state)`

## Override
- Any reviewer can write a row with `disagreement=1` and `adjudication=
  "rejected"`. State is forced back to `auto-generated`.
