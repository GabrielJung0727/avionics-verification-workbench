# Assurance case — engine_anomaly_detector

## 1. Identity
```
model_name:    engine_anomaly_detector
version:       v0.1.0
case_owner:    Verification Engineering (DRAFT)
last_reviewed: 2026-04-14
state:         auto-generated
```

## 2. Top claim (G1)
The engine_anomaly_detector v0.1.0 is safe to use as an **advisory channel**
that flags engine telemetry windows for human inspection — it never
authorizes a maintenance, grounding, or in-flight action.

## 3. Context
- **C1** Operational environment: post-run analytics on `telemetry_event`
  Silver rows. Output is consumed by the verification dashboard and the
  Phase C reviewer flow only.
- **C2** Upstream: Phase A `telemetry_event` table (parsed bus_recording).
- **C3** Downstream: a flag in the assurance report; never a maintenance
  ticket, never a grounding decision.
- **C4** DAL allocation: **N/A** — model is offline analytics.
- **C5** Data sources: `engine-stream-2026-04-14-v1` (clean training stream
  + held-out anomalous stream with EGT runaway in the second half).
- **C6** User population: verification + maintenance review board (advisory
  only).

## 4. Assumptions (falsifiable)
- **A1** Window features (mean / std / first-difference of N1, N2, EGT, FF
  over an 8-tick window) are sufficient for the anomaly classes we care
  about (EGT runaway, hot-start, hung-start).
- **A2** Clean training stream is representative of nominal operation.
- **A3** Maintenance team always treats output as "**inspection
  candidate**", not "fault confirmed".
- **A4** No online learning. Re-training requires explicit Phase C
  re-review.

## 5. Strategy (S1)
G1 decomposes into:
- G1.1 — false-alarm rate is bounded
- G1.2 — detection rate on the held-out anomaly is reported honestly
- G1.3 — output is unambiguously advisory
- G1.4 — model never replaces deterministic engine I/F latch logic

## 6. Sub-goals + evidence

### G1.1 Bounded false-alarm rate
Evidence:
- **Sn1.1.1** `metrics.json` reports `false_alarm_rate=0.05` on training
  windows (matches `contamination=0.05` configuration)
- **Sn1.1.2** Test `TestEngineAnomaly::test_train_score` enforces
  `false_alarm_rate < 0.20`

### G1.2 Honest holdout
Evidence:
- **Sn1.2.1** Holdout = second half of the anomalous stream (clear time
  split, not random)
- **Sn1.2.2** `detection_rate=0.51` reported honestly — moderate signal
  matches the synthetic injection severity
- **Sn1.2.3** `dataset.json` records `split_strategy=time`, `split_key=
  second-half-anomalous`

### G1.3 Advisory output
Evidence:
- **Sn1.3.1** `score_engine_window()` returns `{decision, advice, _draft}`
- **Sn1.3.2** `decision` enum: `preventive_alert | early_warning |
  inspection_candidate | nominal` — none of these strings are imperative
- **Sn1.3.3** `advice` string explicitly says "advisory only"

### G1.4 Deterministic primacy
Evidence:
- **Sn1.4.1** Engine I/F latch logic in
  `tools/sim_py/avx_sim/modules/engine.py` runs unchanged with or without
  this model — the model only produces an after-the-fact score
- **Sn1.4.2** No code path in `run_verification.py` consults the model
  before a campaign is graded

## 7. Failure modes
- **F1** Concept drift: real engines have richer dynamics than the
  4-channel synthetic stream. Mitigation: retrain on real
  `telemetry_event` once enough nominal hours are logged.
- **F2** Adversarial sensor noise: an attacker injecting a slow drift
  could stay under the `score_samples` threshold. Mitigation: this is an
  offline analytics tool, not a real-time guard.
- **F3** Window boundary sensitivity: anomalies shorter than the 8-tick
  window may be smoothed out. Mitigation: future v0.2 should expose
  multiple window sizes.

## 8. Fallback behavior
If the model artifact is missing or the registry refuses to load it,
verification reports include the deterministic `EngineExceed` events from
`avx_sim.modules.engine` exactly as they did before Phase B.
The model adds nothing the runtime depends on.

## 9. Human override path
- A reviewer can mark any flagged window as `false_alarm` in the
  `human_review` Silver table.
- A board-approved override demotes the model state to
  `reviewer-confirmed` until the next training cycle reaches the
  required precision target.

## 10. Change impact
- `dataset_hash` change → state reset
- `_make_engine_streams` parameters changed → state reset
- Window size or contamination changed → state reset

## 11. Standards mapping
- **DO-178C** — N/A (analytics tool, not airborne software)
- **ARP4754A** — N/A
- **ARP4761A** — Could *inform* future FHA discussion of
  observability/diagnosability. Not a substitute for the FHA itself.
- **DO-330** — Potential TQL-5 if ever used for certification credit;
  currently used only for human review prioritization.
- **EASA AI Concept Paper** — Level 1A (offline analytics, no operational
  authority).

## 12. Reviewer log
| Reviewer | Role | Date | State after | Notes |
|---|---|---|---|---|
| _ | _ | _ | auto-generated | Initial draft generated by `train_intelligence.py` |
