<div align="center">

# ✈️ Avionics Verification Intelligence Platform

### Certification-aligned V&V + governed AI assurance layer for civil avionics software

*Not another flight-control demo. A platform where governed datasets, frozen learned components, and a deterministic safety shell improve verification under the lifecycles regulators currently accept.*

[![Standards](https://img.shields.io/badge/aware%20of-DO--178C-0b3d91?style=flat-square)](docs/PhaseE/standards/standards-mapping-v2.md)
[![Standards](https://img.shields.io/badge/aware%20of-ARP4754A-0b3d91?style=flat-square)](docs/PhaseE/standards/standards-mapping-v2.md)
[![Standards](https://img.shields.io/badge/aware%20of-DO--297%20%2F%20AC%2020--170-0b3d91?style=flat-square)](docs/PhaseE/standards/standards-mapping-v2.md)
[![HF](https://img.shields.io/badge/aware%20of-AC%2020--175-1f6feb?style=flat-square)](docs/M1/human-factors/hf-mapping.md)
[![AI](https://img.shields.io/badge/aligned-EASA%20AI%20Concept%20Paper%20L1%C2%B72-9b59b6?style=flat-square)](docs/PhaseE/standards/standards-mapping-v2.md)
[![AI](https://img.shields.io/badge/aligned-FAA%20AI%20Roadmap-9b59b6?style=flat-square)](docs/PhaseE/standards/standards-mapping-v2.md)
[![Tooling](https://img.shields.io/badge/tooling-Python%20%7C%20sklearn%20%7C%20SQLite%E2%86%92Lakehouse-6f42c1?style=flat-square)](#-tech-stack)
[![Status](https://img.shields.io/badge/status-Phase%20E%20Portfolio-brightgreen?style=flat-square)](docs/PhaseE/plan/phaseE-status.md)
[![License](https://img.shields.io/badge/license-MIT-success?style=flat-square)](#-license)

[**🛠 What it is**](#-what-it-is) ·
[**🏗 Architecture**](#-architecture) ·
[**🎬 Demo**](#-demo-scenario) ·
[**🗺 Roadmap**](#-roadmap) ·
[**📚 Docs**](#-documentation)

</div>

---

## ⭐ TL;DR

> *This project is not an AI flight controller. It is a **certification-aligned avionics verification intelligence platform** that uses governed datasets, traceable evidence, and bounded learned components to improve verification prioritization, anomaly detection, and operational assurance under existing aviation safety frameworks.*

Two layers, one story:

**The classical workbench (M1–M6)** — IMA-style partitioned scheduler, virtual ARINC 429 / AFDX-lite buses, FCC / Engine / Display / DC surrogates, requirement-based runner with MC/DC, fault-injection campaigns, AC 20-175 human-factors evaluators, HIL-lite loopback, **immutable evidence bundles with sha256 replay**.

**The intelligence platform (Phase A–D)** — Bronze/Silver/Gold **lakehouse** + **frozen-model registry** + **GSN-lite assurance cases** with reviewer workflow + **runtime assurance shell** (range/rate/authority/watchdog) so AI components stay in the verification layer and never close a control loop. Aligned with EASA AI Concept Paper Level 1·2 and the FAA AI Roadmap incremental approach.

If this kind of work matters to you — keep reading. ⭐

---

## 🛠 What it is

| You usually see | This platform shows |
|---|---|
| A single FBW law | A **partitioned runtime** with budget enforcement and health monitoring |
| Hard-coded I/O | A **virtual ARINC 429 + AFDX-lite bus** with timing / drop / delay / stale-data injection |
| `assert` and a screenshot | A **requirement-based test runner** with structural + MC/DC coverage |
| "It works on my machine" | **Immutable evidence bundles** — git SHA, tool versions, seeds, hashes, replay-verified |
| Random model on a CSV | A **lakehouse + frozen-model registry** — `dataset_hash`, `label_version`, `approval_state` |
| Model card | A **GSN-lite assurance case** with 12 required sections and a reviewer workflow |
| "AI for autopilot" | A **runtime assurance shell** + Shadow → Advisory → LimitedSupervised; control loop stays deterministic |

**Positioning:** Not a certified system. Not a flight-control product. A platform that demonstrates the engineering vocabulary, lifecycle awareness, V&V instincts, and **AI-in-aviation discipline** that real avionics teams expect — under the lifecycles regulators currently accept.

---

## 🏗 Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                Verification Intelligence (Phase B/C/D)           │
│                                                                  │
│  Phase B frozen models           Phase D runtime guard           │
│  ┌──────────────────┐            ┌──────────────────────────┐    │
│  │ escape predictor │ ─raw out─► │ Range / Rate / Authority │    │
│  │ engine anomaly   │            │ Watchdog / Operator gate │    │
│  │ trace gap intel  │            └──────────────┬───────────┘    │
│  └──────────────────┘                           │                │
│         ▲                                       ▼                │
│         │ load(approval_state)        Shadow / Advisory /        │
│         │                             LimitedSupervised          │
│  Phase C: GSN-lite assurance case + 3-state reviewer workflow    │
└──────────────────────────────────────────────────────────────────┘
                                ▲
                                │ trains on Silver
┌──────────────────────────────────────────────────────────────────┐
│   Phase A — Lakehouse  (Bronze → Silver → Gold)                  │
│   schema-drift gate · run_id lineage · dataset contract          │
└──────────────────────────────────────────────────────────────────┘
                                ▲
                                │ orchestrator dumps
┌──────────────────────────────────────────────────────────────────┐
│   Deterministic Verification Workbench (M1–M6)                   │
│                                                                  │
│   IMA Scheduler · ARINC 429-lite · AFDX-lite · FCC / ENG / DSP   │
│   Requirement-based runner · MC/DC · Fault campaigns · HF · HIL  │
│   Immutable evidence bundles (manifest + sha256 + replay)        │
└──────────────────────────────────────────────────────────────────┘
```

> Full Phase A–E design lives under [`docs/PhaseA`](docs/PhaseA/) … [`docs/PhaseE`](docs/PhaseE/). Workbench M1–M6 lives under [`docs/M1`](docs/M1/) … [`docs/M6`](docs/M6/). 1-page architecture for PDF: [`docs/PhaseE/portfolio/one-page-architecture.md`](docs/PhaseE/portfolio/one-page-architecture.md).

---

## ✨ Highlights

<details open>
<summary><b>🧩 IMA-style partitioned runtime</b></summary>

- Deterministic sim tick, seeded PRNG, single-clock guarantee
- Major / minor frame scheduling with per-partition budgets
- Sampling & queuing IPC ports with freshness flags
- Health monitor with configurable `event → action` table
- Cold / warm start sequences

</details>

<details>
<summary><b>🚌 Virtual buses (ARINC 429-lite + AFDX-lite)</b></summary>

- 32-bit A429 word emulation (label / SDI / data / SSM / parity)
- AFDX-lite virtual links over UDP with BAG enforcement
- Recorder + replay (binary + CSV index, hash-stable)
- Fault hooks: drop, delay, reorder, duplicate, bit-flip, stuck-label

</details>

<details>
<summary><b>🛡 Verification & evidence pipeline</b></summary>

- YAML-defined test cases with `req-link`, `seed`, `expected`
- LLVM source-based coverage + custom MC/DC reporter
- Fault-injection campaigns with `detected / mitigated / escaped` classification
- Immutable evidence bundles — manifest, hashes, replay-verified
- Trace DB with bidirectional Req ↔ Test links and gap reports

</details>

<details>
<summary><b>👨‍✈️ Flight-deck human factors</b></summary>

- Alert prioritization (warning > caution > advisory)
- Static color-rule checking (red / amber / green tokens)
- Mode-annunciation latency budget
- Mode-confusion scenario library
- AC 20-175 mapping checklist

</details>

<details>
<summary><b>🔌 SIL → HIL-lite bridge</b></summary>

- Pure-software closed-loop SIL
- HIL-lite with one MCU/SBC over UART or UDP
- Master-tick time sync, latency / jitter measurement
- Brownout, reboot, packet-drop campaigns

</details>

<details>
<summary><b>🤖 AI in the assurance layer (not the loop)</b></summary>

- Requirement → test skeleton drafts
- Log anomaly clustering & failure triage summaries
- Change-impact hints across the trace graph
- Certification-artifact draft generation
- Every output flagged `draft, human-in-the-loop`

</details>

<details open>
<summary><b>🗄 Phase A — Enterprise Data Foundation</b></summary>

- Bronze / Silver / Gold lakehouse on SQLite (same SQL on Databricks / BigQuery / Athena)
- 9 Silver tables, every row reachable by `run_id` (lineage anchor)
- `bus_recording.bin` parsed into `telemetry_event` rows
- Schema-drift gate fails the build on silent breakage
- 4 Gold views: `daily_coverage`, `weekly_escape_rate`, `req_pass_rate`, `hil_latency_distribution`

</details>

<details open>
<summary><b>🧠 Phase B — Certification Intelligence</b></summary>

- 3 frozen learned components: escape predictor (sklearn GBC), engine anomaly (Isolation Forest), trace gap intel (rule-based v0 + ML interface)
- Local MLflow-style registry — `dataset_hash + label_version + approval_state`
- **Non-random splits enforced** (campaign-family / bench-seed / date — random forbidden)
- Honest holdout AUC ≈ 0.99 with controlled label noise

</details>

<details open>
<summary><b>📜 Phase C — Reviewable Safety Case</b></summary>

- GSN-lite assurance case per model — 12 required sections, lint as PR gate
- 3-state approval workflow (`auto-generated → reviewer-confirmed → board-approved`) with audit log
- Self-review prohibited at code level (`PromotionError`)
- DO-330 tool classification + TQL hypotheses for every in-house tool

</details>

<details open>
<summary><b>🔬 Phase D — Bounded Operational AI</b></summary>

- Runtime assurance shell: range / rate / authority / watchdog
- Shadow → Advisory → LimitedSupervised mode progression
- Below `board-approved` → loader refuses Advisory+ at runtime
- `model.fit()` and `partial_fit()` raise `OnlineLearningAttempt`
- Aligns with **EASA AI Concept Paper Level 1·2** + **FAA AI Roadmap incremental approach**

</details>

---

## 🎬 Demo scenario

> One command. End-to-end. Five minutes.

```bash
$ python scripts/run_verification.py
```

1. Verification runner — 6 requirement-based test cases pass.
2. Fault campaigns — 3 scenarios, classified `detected / mitigated / escaped`.
3. MC/DC — 100% on the two designated decisions.
4. Human factors — 6/6 evaluators green, 3/3 mode-confusion scenarios.
5. HIL-lite — 4 configs (nominal / latency-5ms / drop-every-3 / reboot) with mean/max latency, jitter stddev, drops, reboots reported.
6. Evidence bundle — built, sha256 self-verified, replayable from the archive.
7. **Phase A** — schema-drift gate green, lakehouse ingest (13 outcomes / 3 campaigns / 88 telemetry events).
8. **Phase B** — 3 frozen learned components trained, registered, dataset hashed.
9. **Phase C** — every assurance case lint-passes; reviewer state machine enforced.
10. **Phase D** — engine anomaly model runs in shadow against deterministic engine I/F; agreement / fallback / violation stats published. The deterministic pipeline is unaffected.

📄 Full script v2 → [`docs/PhaseE/demo/demo-script-v2.md`](docs/PhaseE/demo/demo-script-v2.md)

---

## 📐 Standards & guidance

Learning-grade mapping — engineering fluency, not certified credit.

| Standard / Guidance | Where it shows up |
|---|---|
| **DO-178C** | Requirements tree (33 SYS / 35 HLR), MC/DC + line coverage, objective mapping |
| **DO-330** | Phase C tool classification + TQL hypotheses for every in-house tool |
| **ARP4754A** | System-level requirements flow + DAL assumptions + change procedure |
| **ARP4761A** | FC-01..12 failure conditions + safety analysis hypotheses |
| **DO-297 / AC 20-170** | M2 IMA partitioning, health monitoring, fault containment |
| **AC 20-175** | Flight-deck controls & alerting human-factors checklist |
| **EASA AI Concept Paper (Issue 2, 2024)** | Phase B `frozen=true` + Phase D Shadow→Advisory ladder (Level 1·2 today) |
| **FAA AI Roadmap (v1)** | Phase D runtime assurance shell + incremental adoption + `OnlineLearningAttempt` |
| **FAA Order 8110.49A** | Phase A lineage queries (every Silver row reachable by `run_id`) |

📄 Full v2 mapping → [`docs/PhaseE/standards/standards-mapping-v2.md`](docs/PhaseE/standards/standards-mapping-v2.md)

> ⚠️ DAL ratings, failure conditions, TQL classifications, and AI level assignments in this repo are **assumptions for portfolio purposes**. They are not — and do not claim to be — substantiated for certification.

---

## 🧰 Tech stack

| Layer | Choice |
|---|---|
| Runtime sim kernel | **Python 3.11** (deterministic tick, seeded PRNG; C++20 port deferred to hot paths) |
| Lakehouse | **SQLite** (Bronze/Silver/Gold) — same ANSI SQL on Databricks / BigQuery / Athena |
| Model registry | Local MLflow-style — pickle artifact + meta + dataset + metrics + assurance stub |
| ML | **scikit-learn** (GradientBoostingClassifier + IsolationForest) |
| Coverage | `sys.settrace` (line) + custom MC/DC tracker on designated decisions |
| Bus sim | ARINC 429-lite (32-bit word + parity) + AFDX-lite (UDP-shaped, BAG-enforced) |
| Evidence | Hermetic zip + manifest + sha256 + replay verifier |
| CI | **GitHub Actions** |
| HIL bridge | Loopback (UART/UDP-extensible) |

---

## 🗺 Roadmap

**Workbench (M1–M6) — Deterministic verification platform**

| Milestone | Focus | Status |
|:---:|---|:---:|
| **M1** | Architecture, requirements tree, ICD v0, certification & HF mapping | 🟢 Done |
| **M2** | IMA-style scheduler, ARINC 429-lite & AFDX-lite buses | 🟢 Done |
| **M3** | FCC surrogate, Engine I/F, Display Computer, Data Concentrator | 🟢 Done |
| **M4** | Verification runner, coverage, MC/DC, fault-injection campaigns | 🟢 Done |
| **M5** | Human factors evaluation, HIL-lite bridge | 🟢 Done |
| **M6** | Evidence bundle, demo, portfolio pack | 🟢 Done |

**Intelligence Platform (Phase A–E) — 2026-04-14 strategic pivot**

| Phase | Focus | Status |
|:---:|---|:---:|
| **A** | Enterprise data foundation (Bronze/Silver/Gold + dataset contract + drift gate) | 🟢 Done |
| **B** | Frozen learned components + local model registry (escape / engine anomaly / trace gap) | 🟢 Done |
| **C** | GSN-lite assurance case + 3-state reviewer workflow + DO-330 classification | 🟢 Done |
| **D** | Runtime assurance shell + Shadow → Advisory → LimitedSupervised + online-learning ban | 🟢 Done |
| **E** | Portfolio packaging — README v2, FAQ, standards v2, 1-page architecture, demo v2 | 🟢 Done |

Each phase has its own folder under `docs/PhaseX/` with design notes, checklists, and a Definition of Done.

---

## 📚 Documentation

```
docs/
├── M1  Foundation         — architecture · requirements · ICD · cert mapping · HF
├── M2  Runtime & Bus      — scheduler · A429-lite · AFDX-lite · recorder
├── M3  Functional         — FCC · Engine I/F · Display Computer · DC
├── M4  Verification       — test runner · coverage · MC/DC · fault injection
├── M5  HF & HIL           — human-factors evaluation · HIL-lite bridge
├── M6  Delivery           — evidence bundle · demo · portfolio pack v1
├── PhaseA  Data Foundation — Bronze/Silver/Gold lakehouse + dataset contract
├── PhaseB  Cert Intel     — frozen learned components + local model registry
├── PhaseC  Safety Case    — GSN-lite assurance cases + reviewer workflow
├── PhaseD  Bounded AI     — runtime assurance shell + Shadow→Advisory→LimSup
└── PhaseE  Portfolio v2   — README v2 · FAQ · standards v2 · 1-page arch · demo v2
```

Every folder follows the same shape: **README → design notes → plan/DoD/status**.

---

## 📁 Repository layout

```
.
├── docs/                       # M1–M6 + Phase A–E design / status
├── tools/
│   ├── sim_py/avx_sim/         # Runtime sim (scheduler, bus, modules, HF, HIL)
│   ├── runner/                 # JSON test-case verification runner
│   ├── fault_injector/         # Campaign loader + escape classifier
│   ├── coverage_reporter/      # Line coverage via sys.settrace
│   ├── evidence_bundler/       # Hermetic zip + manifest + sha256
│   ├── ai_assistant/           # Rule-based assurance helpers (DRAFT)
│   ├── data_foundation/        # Phase A: Bronze/Silver/Gold + lineage + drift
│   └── intelligence/           # Phase B/C/D: registry + governance + runtime
├── tests/python/               # 145 tests (M2..Phase D)
├── sim/scenarios/              # Smoke + M3 integration scenarios
├── scripts/                    # Orchestrators + CLIs
├── config/                     # Partition tables, bus config
└── evidence/                   # verification-report.json + bundles + lakehouse + registry (gitignored)
```

---

## 🚀 Getting started

```bash
git clone https://github.com/<you>/avionics-verification-workbench.git
cd avionics-verification-workbench

# Run the whole platform (M1–M6 + Phase A–D) end-to-end
python scripts/run_verification.py

# Inspect lineage for any run
python scripts/ingest_evidence.py lineage <run_id>

# Re-verify an evidence bundle
python scripts/replay_bundle.py evidence/bundles/bundle-*.zip

# Print the elevator pitch
python scripts/elevator_pitch.py
```

---

## 🙋 FAQ

<details>
<summary><b>Is this real avionics software?</b></summary>

No. It's a portfolio-grade platform that mirrors how real avionics programs are structured. DAL / TQL ratings, failure conditions, and AI-level assignments are assumptions for learning purposes.
</details>

<details open>
<summary><b>Why isn't AI in the control loop?</b> ⭐</summary>

Because regulators currently don't accept it that way. **EASA AI Concept Paper (Issue 2, 2024)** is Level 1·2 only, with online learning and RL out of scope. **FAA AI Roadmap (v1)** distinguishes learned vs learning AI and emphasizes incremental adoption + runtime assurance. Phase D enforces this in code: `model.fit()` raises `OnlineLearningAttempt`, the loader refuses Advisory+ below `board-approved`, and the deterministic safety shell always has primary authority.

📄 Full answer → [`docs/PhaseE/faq/why-ai-not-in-control-loop.md`](docs/PhaseE/faq/why-ai-not-in-control-loop.md)
</details>

<details>
<summary><b>How is this different from Skywise / Honeywell Forge / Collins?</b></summary>

Same lakehouse + ML pattern, **different entry point**. Those are fleet-operations platforms — they consume post-flight data. This is a **certification-aligned verification platform** — it produces evidence before flight. Complementary, not competitive.

📄 Full answer → [`docs/PhaseE/faq/vs-skywise-forge-collins.md`](docs/PhaseE/faq/vs-skywise-forge-collins.md)
</details>

<details>
<summary><b>Why not implement a fly-by-wire control law?</b></summary>

Because the hard part of flight software is rarely the law itself — it's the requirements tree, integration, verification, traceability, evidence, and assurance. This platform focuses on those.
</details>

<details>
<summary><b>Where does AI fit?</b></summary>

In the **verification & assurance layer only**: escape predictor, engine anomaly detector (preventive alert / inspection candidate), trace gap intelligence. Never in the command path. Every AI output is rendered as `DRAFT` and requires human review per Phase C.
</details>

<details>
<summary><b>Can I use this as a learning resource?</b></summary>

Yes. The `docs/Mn` and `docs/PhaseX` trees are intentionally written as a study path through DO-178C, ARP4754A, DO-297, AC 20-175, EASA AI Concept Paper, and the FAA AI Roadmap — in a hands-on, code-anchored context.
</details>

---

## 🤝 Contributing

Issues, discussions, and reviewer-style critiques are very welcome — especially from people working in real avionics, V&V, IMA integration, or human-factors. If something here would make a real reviewer wince, **please open an issue**: that's exactly the feedback this repo exists to attract.

---

## 📄 License

MIT — see [`LICENSE`](LICENSE).

---

<div align="center">

### ⭐ If this kind of work matters to you, a star helps it reach the right people.

*Built as a public engineering notebook by an engineer who'd like to do this for a living.*

</div>
