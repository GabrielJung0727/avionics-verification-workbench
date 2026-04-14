# DO-330 tool classification (DRAFT)

> Learning-grade classification. No certification credit is claimed. The
> table below maps every in-house tool to its hypothetical DO-330 use
> category and TQL — what *would* apply if any of these tools were ever
> used to claim credit during a real airborne software certification.

## Use categories (DO-330 §FAQ D-1, D-2, D-3)
- **Criterion 1**: tool output is part of the airborne software (so a
  tool error could insert an error into airborne software)
- **Criterion 2**: tool automates verification activity *and* output is
  used to claim credit *and* could fail to detect an error
- **Criterion 3**: tool reduces, automates, or eliminates a process *and*
  output is used to claim credit

## TQL summary (§T-1)
- Criterion 1 + DAL A/B/C → **TQL-1/2/3**
- Criterion 2 + DAL A/B/C → **TQL-4/5/5**
- Criterion 3 + DAL A/B/C → **TQL-5/5/5**

## Tool inventory

| Tool path | Use criterion (assumed) | TQL (assumed if used for credit) | Notes |
|---|---|---|---|
| `tools/sim_py/avx_sim/*` (runtime) | — | — | Not airborne; never embedded |
| `tools/runner/runner.py` | Crit 2 | TQL-5 | Verification automation; claim only after Phase C reviewer-confirmed |
| `tools/coverage_reporter/` | Crit 2 | TQL-5 | Structural coverage reporting |
| `tools/sim_py/avx_sim/mcdc.py` | Crit 2 | TQL-5 | MC/DC analyzer; designated decisions only |
| `tools/fault_injector/` | Crit 2 | TQL-5 | Fault campaign automation |
| `tools/evidence_bundler/` | Crit 3 | TQL-5 | Process automation (CM-side) |
| `tools/data_foundation/` | Crit 3 | TQL-5 | Process automation (data lineage) |
| `tools/intelligence/registry/` | Crit 3 | TQL-5 | Process automation (model lifecycle) |
| `tools/intelligence/predictors/escape_predictor` | Crit 3 (advisory) | TQL-5 if credit claimed; **N/A** today | Currently advisory only |
| `tools/intelligence/predictors/engine_anomaly` | Crit 3 (advisory) | TQL-5 if credit claimed; **N/A** today | Currently advisory only |
| `tools/intelligence/predictors/trace_gap_intel` | Crit 3 (advisory) | TQL-5 if credit claimed; **N/A** today | Rule-based; no credit |
| `tools/ai_assistant/*` | none (DRAFT outputs) | **N/A** | All outputs labelled DRAFT, never used for credit |
| `scripts/run_verification.py` | Crit 2 (orchestrator) | TQL-5 | Orchestration of qualified tools |
| `scripts/replay_bundle.py` | Crit 3 | TQL-5 | CM verification of evidence bundles |

## Tool Operational Requirements (sample, escape predictor)
1. Predictor SHALL output `(p_escape ∈ [0,1], advice ∈ {"run early",
   "lower priority", "review"})`.
2. Predictor SHALL include the `_draft` marker in every output.
3. Predictor SHALL NOT modify the campaign queue; reordering is the
   reviewer's action.
4. Predictor SHALL refuse to load if `meta.json::frozen` is `false`.
5. Registry SHALL refuse to register a model whose
   `dataset.split_strategy` equals `"random"`.

## Known limitations (must appear in any qualification packet)
- Synthetic training data; no real flight data
- Single-channel feature extraction for engine anomaly
- Rule-based trace gap intel
- No formal independence between training and verification tooling — both
  built by the same engineer

## Re-qualification trigger
Any of:
- TQL classification changes (e.g. tool starts being used for credit)
- DO-330 issue update
- DAL of consumed evidence changes
- Underlying ML library (`sklearn`) major-version bump
