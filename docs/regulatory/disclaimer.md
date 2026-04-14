# Master Disclaimer

> **This repository is a learning and portfolio artefact. Nothing inside
> it is certification evidence, nothing here has been reviewed by a DER /
> AR / EASA expert, and no DAL / IDAL / TQL rating is substantiated.**

## What is and isn't claimed

| ✓ Claimed | ✗ NOT claimed |
|---|---|
| Engineering fluency with the documents listed under [`README.md`](README.md) | Substantiated certification credit |
| A code-anchored study path through the lifecycle | A replacement for an SOI / SOI3 audit |
| Demonstrative DAL, TQL, AI-level *hypotheses* | Authoritative ratings |
| A pattern that *could* map to certified work after substantial rework | Production-ready airborne software |

## Specifically NOT in scope
- Real **FHA / PSSA / SSA** (FC-01..12 are learning-grade hypotheses)
- Real **environmental qualification** (DO-160G — see [do160g.md](do160g.md))
- Real **airborne electronic hardware** (DO-254 — see [do254.md](do254.md))
- Real **DAL allocation** (Phase B/C/D `out_of_scope` declarations are honest about this)
- Real **TQL allocation** (Phase C TQL hypotheses are illustrative only)
- Real **AI authority allocation** — by Phase D design, AI never closes a control loop here

## Use rules for anyone reading this repo
- Treat every output marked `_draft` as draft.
- Treat every `approval_state` value as a sketch of what a real workflow
  would track, not as proof a real reviewer signed anything.
- The `assurance_stub.md` files seeded under each model in
  `evidence/registry/<model>/<version>/` are **stubs**, not assurance cases.
- The `assurance case` markdown under `docs/PhaseC/cases/` is a
  **GSN-lite educational exercise**, not a deliverable for a project.

## If you are a reviewer wanting to verify how the disclaimer is enforced
- Phase B registry: every `meta.json` ships with `frozen=true`,
  `approval_state="auto-generated"`, and `out_of_scope` listing
  control-loop use, online learning, and unsupervised authority transfer.
- Phase C linter: refuses any case missing required sections.
- Phase D loader: refuses Advisory+ modes below `board-approved`,
  refuses any in-place training call.
- Phase A drift gate: refuses to ingest a verification report whose
  schema has silently changed.

## Contact
This is a personal portfolio. Open an issue for technical questions,
corrections, or a real-world reality check.
