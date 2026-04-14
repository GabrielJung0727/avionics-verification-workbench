# EASA AI Concept Paper (Issue 2, 2024) — Summary + Project Response

> Public summary based on EASA's published Concept Paper (Issue 2,
> 2024). This memo is a learning interpretation, not legal advice.

## What EASA's paper says (in plain words)

### Levels of AI use
- **Level 1A** — Human Augmentation (the human is in full control; AI
  only assists)
- **Level 1B** — Human Cognitive Assistance in Decision and Action
- **Level 2A** — Human/AI Cooperation
- **Level 2B** — Human/AI Collaboration
- **Level 3** — More autonomous AI — **scope of a future paper, not in
  the current acceptance envelope**

### Allowed lifecycle
- **Offline-trained models** that are **frozen** at certification time
- Online learning is **out of scope** of the current paper
- Reinforcement learning in operational control is **out of scope**

### Trust-building blocks (W-shaped lifecycle)
1. AI/ML constituent specification
2. Data management
3. Learning process management
4. Learning process verification
5. Trained model description
6. Inference model verification
7. Independent data and learning verification
8. AI safety risk assessment
9. AI explainability
10. AI assurance / cross-cutting

## Where this repo answers each block

| EASA building block | Repo evidence |
|---|---|
| AI/ML specification | Each model's `model_card.json` + `assurance_stub.md` + Phase C `cases/*.md` |
| Data management | Phase A `tools/data_foundation` (Bronze/Silver/Gold + dataset contract + drift gate) |
| Learning process management | `scripts/train_intelligence.py` (deterministic, seeded) + non-random splits |
| Learning process verification | Phase B `metrics.json` + holdout discipline (`split_by_key`) |
| Trained model description | `model_card.json` + `dataset.json` per registered version |
| Inference model verification | Phase B unit tests + Phase D shadow harness disagreement stats |
| Independent verification | Phase C reviewer ≠ author rule (`PromotionError` if violated) |
| Safety risk assessment | `docs/M1/certification/safety.md` + Phase C cases §7 (Failure modes) |
| Explainability | rule-based components are inherently explainable; ML uses simple sklearn classifiers; Phase C cases §6 cite evidence |
| AI assurance / cross-cutting | Phase D runtime assurance shell + Shadow→Advisory→LimitedSupervised |

## Where this repo currently lands on the level scale
- **Level 1A** for trace gap intelligence and escape predictor (advisory
  to verification engineer)
- **Level 1A** for engine anomaly (advisory to maintenance reviewer)
- Phase D Shadow runs are deliberately **below operational use** —
  observation only

## Hard line that maps to "out of scope" of the EASA paper
- `model.fit()` / `partial_fit()` raise `OnlineLearningAttempt` at the
  Phase D loader (no online learning)
- No reinforcement learning in any module
- Loader refuses Advisory+ modes below `board-approved` (no operational
  use of an unreviewed model)

## What we cannot demonstrate locally
- Independence between AI development and AI verification (single engineer)
- Real safety risk assessment (FC-01..12 are illustrative)
- Real explainability evidence (sklearn GBC feature importances are not
  certified explanations)

## Reference
- EASA Concept Paper *First usable guidance for Level 1 & 2 machine
  learning applications*, Issue 2 (2024). See EASA AI roadmap publications.
