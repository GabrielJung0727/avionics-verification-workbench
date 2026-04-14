# FAA Roadmap for Artificial Intelligence Safety Assurance (v1) — Summary + Project Response

> Public summary based on the FAA's AI Roadmap (v1). This memo is a
> learning interpretation, not legal advice.

## What the FAA roadmap says (in plain words)

### Core distinction
- **Learned AI** — model is trained then frozen; behaviour fixed at
  deployment. Treated like other complex software with additional
  assurance for the training data + verification chain.
- **Learning AI** — model continues to update after deployment. **Not
  recommended for operational use today**; the assurance pathway is
  immature.

### Recommended approach
- **Incremental adoption** — start in non-safety-critical roles, add
  authority only as evidence accumulates
- **Runtime assurance** — pair the AI with a deterministic monitor that
  bounds its outputs and engages a fallback when needed
- **Explainability and traceability** are emphasised
- **Independence** between AI design and AI verification

## Where this repo answers it

| FAA roadmap concern | Repo evidence |
|---|---|
| Learned vs learning split | Phase D `loader.py` raises `OnlineLearningAttempt` on `fit` / `partial_fit`; every `meta.json` ships `frozen=true` |
| Incremental adoption | Phase D `Mode` enum: Shadow → Advisory → LimitedSupervised; loader refuses Advisory+ below `board-approved` |
| Runtime assurance | `tools/intelligence/runtime/assurance_shell.py` — range / rate / authority / watchdog; deterministic `fallback_provider` always wired |
| Independence (process) | Phase C `approval.py` blocks self-review (`PromotionError` if reviewer == author) |
| Traceability | Phase A `tools/data_foundation` + `lineage.py` — every Silver row reachable by `run_id` |
| Explainability | Rule-based components are inspectable; ML uses simple sklearn models; assurance case §6 lists evidence pointers |
| Lifecycle data | FAA Order 8110.49A informed Phase A schema (every artefact has an `artifact_index` row) |

## Phase D mode ladder mapped to FAA staging
| Phase D mode | FAA position | Repo enforcement |
|---|---|---|
| Shadow | Observation only — pre-deployment evidence gathering | `ShadowMode.consume` writes to log only |
| Advisory | Operational visibility but no automatic action | `AdvisoryMode` parks output in an `AckQueue` |
| LimitedSupervised | Acted upon only after explicit operator ack, low-criticality service | `LimitedSupervisedMode.apply_if_acked` filters by `allowed_consumer_keys` |

## Hard line
- No primary FCC authority transfer to any AI component
- Deterministic safety shell always has primary authority
- Override path is required for every Phase D mode
- Anything claiming flight-control AI today is **not what this roadmap recommends**

## What we cannot demonstrate locally
- Real fleet-scale operational evidence (we have only synthetic + simulator data)
- Real independence between AI design and AI verification (single engineer)
- A real runtime monitor that has been validated against an aircraft
  certification basis

## Reference
- FAA *Roadmap for Artificial Intelligence Safety Assurance*, Version I.
  Published by the FAA Aircraft Certification Service.
