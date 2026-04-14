# Assurance case — fault_escape_predictor

## 1. Identity
```
model_name:    fault_escape_predictor
version:       v0.1.0
case_owner:    Verification Engineering (DRAFT)
last_reviewed: 2026-04-14
state:         auto-generated
```

## 2. Top claim (G1)
The fault_escape_predictor v0.1.0 is safe to use as an **advisory** input to
the verification team's campaign-prioritization workflow, provided the
assumptions in §4 hold and the human override path in §9 remains
unrestricted.

## 3. Context
- **C1** Operational environment: verification engineering desktop / CI
  pipeline. Model output is consumed by `tools/runner` and the verification
  dashboard, never by the runtime simulator.
- **C2** Upstream: Phase A `fault_injection_case` Silver table.
- **C3** Downstream: campaign ordering for the next CI nightly run.
- **C4** DAL allocation: **N/A** — model never lives on an aircraft and
  never closes a control loop.
- **C5** Data sources: synthetic fault sweep `sweep-2026-04-14-v1`
  (label noise 7% to model real-world labelling drift).
- **C6** User population: verification engineers with the authority to
  reorder, defer, or waive campaigns.

## 4. Assumptions (falsifiable)
- **A1** Synthetic fault sweep covers the parameter ranges that real
  campaigns will exercise (delay_us ≤ 200 ms, drop_every_n ≤ 10,
  n1 ≤ 110%, dual_fault_us ≤ 200 ms).
- **A2** Label oracle (`_classify`) reflects the deterministic semantics of
  `tools/fault_injector/campaign.py` `run_campaign`.
- **A3** Verification engineers always have the authority to override the
  model's ordering — no automated gate blocks human reordering.
- **A4** Model is retrained from scratch on every dataset_hash change; no
  online learning at any point.

## 5. Strategy (S1)
G1 decomposes into four sub-goals:
- G1.1 — predictor outputs are reproducible from the registered artifact
- G1.2 — predictor performance was measured on a non-random holdout
- G1.3 — every prediction surfaces with the DRAFT marker
- G1.4 — failure of the predictor degrades to the deterministic baseline

## 6. Sub-goals + evidence

### G1.1 Reproducibility
Evidence:
- **Sn1.1.1** registry entry `evidence/registry/fault_escape_predictor/v0.1.0/`
- **Sn1.1.2** `dataset.json` records `dataset_hash` over the training matrix
- **Sn1.1.3** `meta.json` records `training_seed=42` and `frozen=true`
- **Sn1.1.4** unit test `tests/python/test_phase_b.py::TestEscapePredictor`

### G1.2 Honest holdout
Evidence:
- **Sn1.2.1** `tools/intelligence/data/splits.py` `split_by_key` (random forbidden)
- **Sn1.2.2** holdout key `seed_7` ≠ training seeds; balanced labels
- **Sn1.2.3** AUC=0.993, F1=0.92 reported in `metrics.json` (with 7% label noise)
- **Sn1.2.4** integration test `TestRegistry::test_register_and_load`

### G1.3 DRAFT marker
Evidence:
- **Sn1.3.1** `score_escape()` returns `{"_draft": "...", "advice": ...}`
- **Sn1.3.2** registry `assurance_stub.md` carries DRAFT banner
- **Sn1.3.3** orchestrator wraps every Phase B output with the same banner

### G1.4 Safe degradation
Evidence:
- **Sn1.4.1** `tools/runner/runner.py` runs entire campaign suite with or
  without the predictor — predictor only reorders, never gates
- **Sn1.4.2** `scripts/run_verification.py` returns a non-zero exit code if
  Phase A drift gate fails *before* Phase B runs, so a stale model can
  never be silently used

## 7. Failure modes
- **F1** Distribution shift: real campaigns drift outside the synthetic
  sweep envelope → silently low recall. Mitigation: re-train on real
  Silver data once Databricks sweep produces ≥1k labelled rows.
- **F2** Label oracle drift: if `_classify` rules diverge from
  `run_campaign` semantics, training labels become stale.
  Mitigation: dataset_version bump + Phase C re-review trigger.
- **F3** Class imbalance on production data: synthetic data is roughly
  1:5 escape:non-escape; real ratios may differ. Mitigation: evaluate AUC
  per family, not just global, before promoting state.

## 8. Fallback behavior
If the predictor file is missing or the registry refuses to load it, the
verification runner runs every campaign in declared order. No campaign is
ever *skipped* due to a low predicted probability — only **reordered**.
This guarantee is enforced by `tools/runner/runner.py::run_all` operating
on the full discovered set.

## 9. Human override path
- The verification engineer sees the predicted ranking but submits the
  final campaign order via PR.
- Override is recorded in git history; the orchestrator does not write to
  `human_review` automatically — that table is reserved for explicit
  reviewer adjudication tracked by Phase C governance tools.

## 10. Change impact
The case becomes **stale** (state forced back to `auto-generated`) on any
of:
- `dataset_hash` change in `dataset.json`
- `git_sha` change in `meta.json` for this model
- `_classify` rules in `tools/intelligence/data/fault_sweep.py` modified
- new fault type added to `tools/fault_injector/campaign.py`

Phase C governance tool `change_impact.py` enforces this.

## 11. Standards mapping
- **DO-178C** — verification of software → tooling support; not part of
  airborne software. The model itself is not flight software.
- **ARP4754A** — N/A (no aircraft-level allocation).
- **ARP4761A** — N/A (no FHA item allocates to this model).
- **DO-330** — fault_escape_predictor + sklearn together would be a
  potential **TQL-5** verification tool *if* used to claim
  certification credit. Currently used only for prioritization; no credit
  claimed. See `docs/PhaseC/tool-qualification/`.
- **EASA AI Concept Paper** — Level 1A/1B (offline-trained advisory tool,
  no operational impact, frozen-after-training).

## 12. Reviewer log
| Reviewer | Role | Date | State after | Notes |
|---|---|---|---|---|
| _ | _ | _ | auto-generated | Initial draft generated by `train_intelligence.py` |
