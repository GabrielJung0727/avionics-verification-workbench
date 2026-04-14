# 5-Minute Demo Script v2 (Phase A–D included)

> v1 lived at `docs/M6/demo/demo-script.md`. v2 adds Phase A lakehouse
> dashboard scenes and the Phase D shadow run. Total target: 5 minutes.

## Setup (off-camera)
- Terminal in repo root
- Browser tab on the SQL output of Phase A Gold views (or static screenshot)
- `evidence/` already populated from a recent run

## Script

### 0:00 — Hook (15 s)
> *"Most avionics side-projects re-implement a control law. This one does the
> opposite: it treats the boring-but-career-defining work — verification,
> traceability, evidence, assurance cases — as the product."*

Show: `README.md` top of file (badges + tagline).

### 0:15 — One run, end to end (60 s)
```
$ python scripts/run_verification.py
```
Narrate as it scrolls:
> *"6 requirement-based test cases pass, 3 fault campaigns,
> 100% MC/DC on the two designated decisions, 6/6 human-factors
> findings, 4 HIL-lite runs."*

When it stops, point at:
- *"Evidence bundle is built and re-verified by sha256."*
- *"Phase A drift gate ran — schema is stable."*
- *"Phase A lakehouse ingest — 13 outcomes, 3 campaigns, 88 telemetry events."*
- *"Phase B trained 3 frozen learned components and registered them."*
- *"Phase C lint passed every assurance case."*
- *"Phase D shadow run — engine anomaly model observed against the
  deterministic engine I/F. AI never touched control."*

### 1:15 — Phase A: lakehouse (45 s)
```
$ python scripts/ingest_evidence.py gold | head -40
```
Show:
- `weekly_escape_rate` row
- `req_pass_rate` rows

> *"Same SQL runs against Databricks SQL, BigQuery, or Athena — the
> contract is the lakehouse, not the SQLite file."*

### 2:00 — Phase B: frozen models (45 s)
Open `evidence/registry/fault_escape_predictor/v0.1.0/`:
- `meta.json` — `frozen=true`, `approval_state="auto-generated"`,
  `intended_use`, `out_of_scope` (list)
- `dataset.json` — `dataset_hash`, `split_strategy="bench-seed"`
- `metrics.json` — `auc=0.99`, `recall`, `precision`

> *"Every model ships with the metadata needed to re-train, audit, and
> register elsewhere. Swap the registry for MLflow and the artifact moves
> unchanged."*

### 2:45 — Phase C: assurance + workflow (60 s)
Open `docs/PhaseC/cases/escape-predictor.md`:
- §1 Identity (state machine)
- §2 Top claim
- §7 Failure modes
- §8 Fallback behavior
- §9 Human override path

> *"This is not a model card. This is the document a reviewer reads to
> decide whether the model is safe to use in this context. Linter
> enforces every required section."*

Then show `tools/intelligence/governance/approval.py`:
> *"Reviewer ≠ author. Self-promotion raises `PromotionError`. Every
> state change is logged."*

### 3:45 — Phase D: bounded operational AI (60 s)
```
$ python scripts/run_shadow.py
```
Narrate:
> *"Shadow mode. The engine anomaly model runs against the deterministic
> engine I/F. Agreement rate, fallback rate, violation counts are
> recorded. The deterministic pipeline is unchanged — the AI never
> closes a control loop."*

Then `tools/intelligence/runtime/loader.py`:
> *"`model.fit()` raises `OnlineLearningAttempt`. Below `board-approved`
> the loader refuses Advisory and LimitedSupervised modes. Phase C
> invalidations propagate here."*

### 4:45 — The differentiator (15 s)
> *"This is not an AI flight controller. It's a certification-aligned
> avionics verification intelligence platform. AI lives in the
> assurance layer; deterministic safety shell always has primary
> authority. That's exactly what EASA Level 1·2 and the FAA AI Roadmap
> currently accept — and it's the only path the regulator currently
> recognizes."*

End.

## Visual artifacts to keep ready
- README hero (top of file)
- `evidence/lakehouse/silver/catalog.sqlite` Gold view query screenshot
- `evidence/registry/<model>/<version>/` directory listing
- One assurance case opened to §9 (Human override path)
- `evidence/phaseD-shadow-report.json`
- The 1-page architecture (`docs/PhaseE/portfolio/one-page-architecture.md`)
