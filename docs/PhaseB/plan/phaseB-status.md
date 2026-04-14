# Phase B — Status Snapshot (2026-04-14)

## Module map
| Component | File | Notes |
|---|---|---|
| Local model registry | `tools/intelligence/registry/registry.py` | meta + dataset + metrics + model_card + assurance_stub per version |
| Fault sweep generator | `tools/intelligence/data/fault_sweep.py` | 600 deterministic synthetic campaigns + 7% label noise |
| Non-random splits | `tools/intelligence/data/splits.py` | `split_by_key`, `split_by_date` (random forbidden) |
| Escape predictor (v0) | `tools/intelligence/predictors/escape_predictor.py` | sklearn GradientBoostingClassifier |
| Engine anomaly (v0) | `tools/intelligence/predictors/engine_anomaly.py` | sklearn IsolationForest over 12 window features |
| Trace gap intel (v0) | `tools/intelligence/predictors/trace_gap_intel.py` | rule-based baseline + ML interface |
| Trainer | `scripts/train_intelligence.py` | trains all 3, registers, dumps `intelligence-summary.json` |
| Orchestrator integration | `scripts/run_verification.py` | runs trainer after Phase A ingest |
| Tests | `tests/python/test_phase_b.py` (9) | sweep determinism, splits, train/score, registry discipline |

## Local run
```
Ran 122 tests in 3.285s — OK

=== Phase B intelligence ===
  fault_escape_predictor     v0.1.0   dir=evidence/registry/fault_escape_predictor/v0.1.0
  engine_anomaly_detector    v0.1.0   dir=evidence/registry/engine_anomaly_detector/v0.1.0
  trace_gap_intel            v0.1.0   dir=evidence/registry/trace_gap_intel/v0.1.0
```

### Headline metrics
| Model | Metric | v0.1.0 value |
|---|---|---|
| fault_escape_predictor | AUC (holdout=seed_7, noise=7%) | **0.993** |
| fault_escape_predictor | F1 / precision / recall | 0.92 / 0.89 / 0.96 |
| engine_anomaly_detector | detection_rate (anomalous tail) | **0.51** |
| engine_anomaly_detector | false_alarm_rate (clean) | 0.05 |
| trace_gap_intel | precision_at_3 / MRR | **1.0** / 1.0 |

> Numbers are honest: synthetic data is deterministic with controlled noise.
> The point of v0 is to ship the **pipeline + assurance metadata story** so
> that real Databricks/MLflow data swaps in without code change.

## Registry layout (per model version)
```
evidence/registry/<model>/<version>/
├── model.pkl           binary artifact
├── meta.json           name/version/git_sha/frozen=true/approval_state/intended_use/out_of_scope
├── dataset.json        dataset_version + dataset_hash + n_train/n_holdout + split_strategy + split_key
├── metrics.json        per-model holdout metrics + _draft=true
├── model_card.json     human-readable card with DRAFT banner
└── assurance_stub.md   Phase C extension hook (intended-use / OOS / pedigree / fallback / override)
```

## Discipline checks (enforced in tests)
- [x] `frozen=true` baked in
- [x] `approval_state="auto-generated"` initial
- [x] DRAFT banner in stub + meta + every prediction output
- [x] dataset_hash + label_version present
- [x] split_strategy ≠ "random" (test verifies seed-based split is honoured)
- [x] `out_of_scope` lists "control loop", "online learning", "automatic decisions"

## Exit Criteria
- [x] Local registry with full metadata bundle
- [x] dataset_hash + label_version + approval_state in every entry
- [x] Escape predictor v0 trained & registered (sklearn GBC)
- [x] Engine anomaly v0 trained & registered (Isolation Forest)
- [x] Trace gap intel v0 (rule-based baseline + ML interface)
- [x] Non-random split enforced (`bench-seed` strategy)
- [x] Orchestrator includes Phase B in evidence report
- [x] DRAFT banner on all outputs

## Carry-over to Phase C
- Each `assurance_stub.md` is the seed for a full assurance case
- failure modes / fallback / human override / change impact sections are
  pre-allocated; Phase C fills them with reviewer-confirmed content
- approval_state state machine is in place — Phase C adds the reviewer flow
