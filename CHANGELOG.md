# Changelog

All notable changes to this project follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> Until v1.0.0 the project is in active build-out for portfolio purposes.
> Phase / milestone naming mirrors `docs/M*/` and `docs/Phase*/`.

## [Unreleased]

## [0.7.1] — 2026-04-14
### Fixed
- CI failures on GitHub / GitLab — added `requirements.txt` (numpy + scikit-learn pinned)
  and `pip install -r requirements.txt` step in both `ci.yml` and `nightly.yml`.

## [0.7.0] — 2026-04-14 — Regulatory Stack Reference
### Added
- `docs/regulatory/` with 13 1-pagers: ARP4754A, ARP4761A, DO-178C, DO-330,
  DO-160G (out-of-scope), DO-254 (out-of-scope), AC 20-174, AC 20-115D,
  AC 20-175, EASA AI Concept Paper, FAA AI Roadmap, master disclaimer.
- M1 `do178c-mapping.md` extended with cross-links to every regulatory page.
- 9 regulatory documentation tests.

## [0.6.0] — 2026-04-14 — Phase E (Portfolio Packaging)
### Added
- README v2 — new hero, TL;DR, architecture diagram, 7 highlight blocks, 5 FAQs.
- `docs/PhaseE/` — FAQ (AI not in loop, vs Skywise/Forge/Collins),
  standards mapping v2, 1-page architecture, demo script v2,
  resume bullets v2 (6 position-tailored), LinkedIn post v2.
- `tools/portfolio/pitch.py` + `scripts/elevator_pitch.py` (5s / 30s / 60s / hard-line).
- 12 Phase E tests pinning pitch lengths and required artefact presence.

## [0.5.0] — 2026-04-14 — Phase D (Bounded Operational AI)
### Added
- `tools/intelligence/runtime/` — runtime assurance shell (range / rate /
  authority / watchdog), Shadow / Advisory / LimitedSupervised modes,
  AckQueue, disagreement tracker.
- `tools/intelligence/runtime/loader.py` — approval-gated loader;
  `model.fit()` / `partial_fit()` raise `OnlineLearningAttempt`.
- `scripts/run_shadow.py` — engine anomaly model in shadow against the
  deterministic engine I/F.
- 13 Phase D tests.

### Local intelligence-serving (Phase B follow-up)
- `tools/intelligence/serving/` — stdlib `http.server` endpoint with
  `/health`, `/models`, `/predict/{fault_escape, engine_anomaly, trace_gap}`.
- `tools/ai_assistant/intelligence_client.py` — graceful endpoint
  augmentation for `change_impact.impact_for_requirement()`.

## [0.4.0] — 2026-04-14 — Phase C (Reviewable Safety Case)
### Added
- GSN-lite assurance case template + 3 model cases (escape, engine anomaly,
  trace gap intel).
- `docs/PhaseC/tool-qualification/do330-classification.md` — every in-house
  tool with use criterion + TQL hypothesis.
- `tools/intelligence/governance/` — assurance lint, approval workflow
  (3-state: auto → reviewer → board), change-impact reset detector.
- Self-review prohibited (`PromotionError`).
- 10 Phase C tests.

## [0.3.0] — 2026-04-14 — Phase B (Certification Intelligence)
### Added
- Local MLflow-style registry — `dataset_hash + label_version + approval_state`.
- 3 frozen learned components: escape predictor (sklearn GBC), engine
  anomaly detector (Isolation Forest), trace gap intel (rule-based v0).
- Non-random splits enforced (campaign-family / bench-seed / date).
- `scripts/train_intelligence.py` — trains, registers, dumps summary.
- 9 Phase B tests.

## [0.2.0] — 2026-04-14 — Phase A (Enterprise Data Foundation)
### Added
- `tools/data_foundation/` — Bronze / Silver / Gold lakehouse on SQLite
  (ANSI SQL maps to Databricks / BigQuery / Athena).
- 9 Silver tables, every row reachable by `run_id` (lineage anchor).
- `bus_recording.bin` parser → `telemetry_event` rows.
- Schema-drift gate fails the build on silent breakage.
- 4 Gold views.
- `scripts/ingest_evidence.py` — ingest / lineage / drift / gold subcommands.
- 8 Phase A tests.

## [0.1.0] — 2026-03 — M1–M6 deterministic verification workbench
### Added
- **M1** — architecture, 33 SYS / 35 HLR requirements, ICD v0,
  certification & HF mapping (DO-178C, ARP4754A, AC 20-175).
- **M2** — IMA-style partition scheduler, ARINC 429-lite + AFDX-lite
  buses, recorder with sha256 stable hash.
- **M3** — FCC surrogate (cmd/mon lane diversity, mode reversion),
  Engine I/F (latch + hot/hung start), Display Computer (alert priority,
  color rule, mode latency), Data Concentrator.
- **M4** — JSON test-case verification runner, line + MC/DC coverage,
  fault-injection campaigns with detected/mitigated/escaped classification.
- **M5** — 6 human-factors evaluators (AC 20-175 / 25.1322), mode-confusion
  scenarios, HIL-lite loopback with latency / jitter / drop / reboot
  faults.
- **M6** — Immutable evidence bundles (manifest + sha256 + replay), AI
  assistance helpers (DRAFT only), portfolio pack v1.
- Nightly CI workflow.
