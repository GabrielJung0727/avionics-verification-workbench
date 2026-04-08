<div align="center">

# ✈️ Avionics Verification Workbench

### Certification-aware integration & V&V platform for civil avionics software

*Not another flight-control demo — a system-of-systems workbench where requirements, design, code, tests, and evidence stay traceable end-to-end.*

[![Standards](https://img.shields.io/badge/aware%20of-DO--178C-0b3d91?style=flat-square)](docs/M1/certification/do178c-mapping.md)
[![Standards](https://img.shields.io/badge/aware%20of-ARP4754A-0b3d91?style=flat-square)](docs/M1/certification/do178c-mapping.md)
[![Standards](https://img.shields.io/badge/aware%20of-DO--297%20%2F%20AC%2020--170-0b3d91?style=flat-square)](docs/M1/certification/do178c-mapping.md)
[![HF](https://img.shields.io/badge/aware%20of-AC%2020--175-1f6feb?style=flat-square)](docs/M1/human-factors/hf-mapping.md)
[![Build](https://img.shields.io/badge/build-CMake%20%7C%20C%2B%2B20-informational?style=flat-square)](CMakeLists.txt)
[![Tooling](https://img.shields.io/badge/tooling-Python%20%7C%20React%20%7C%20Postgres-6f42c1?style=flat-square)](#-tech-stack)
[![Status](https://img.shields.io/badge/status-M1%20Foundation-yellow?style=flat-square)](docs/M1/plan/m1-2week-plan.md)
[![License](https://img.shields.io/badge/license-MIT-success?style=flat-square)](#-license)

[**🛠 What it is**](#-what-it-is) ·
[**🏗 Architecture**](#-architecture) ·
[**🎬 Demo**](#-demo-scenario) ·
[**🗺 Roadmap**](#-roadmap) ·
[**📚 Docs**](#-documentation)

</div>

---

## ⭐ TL;DR

> A learning-grade workbench that emulates how an **integrated modular avionics (IMA)** system is built, integrated, verified, and *evidenced* — the way real flight-software programs run, not the way side projects usually do.

- **System-of-systems** — FCC surrogate, Engine I/F, Display Computer, Data Concentrator over a partitioned runtime and a virtual ARINC 429 / AFDX-lite bus.
- **Verification-first** — requirement-based test runner, structural & MC/DC coverage, fault-injection campaigns, regression dashboard, immutable evidence bundles.
- **Traceable end-to-end** — Req ↔ Design ↔ Code ↔ Test ↔ Result, with orphan & gap reports.
- **AI in the assurance layer, never in the control loop** — test skeleton generation, log clustering, change-impact hints, all marked `draft, human-in-the-loop`.

If you build flight-critical software for a living, this repo is meant to feel familiar.
If you're hiring for one of those teams — keep reading. ⭐

---

## 🛠 What it is

Most "avionics" side projects re-implement a control law and stop. This one does the opposite: it takes the *boring but career-defining* parts of avionics software seriously.

| You usually see | This workbench shows |
|---|---|
| A single FBW law | A **partitioned runtime** with budget enforcement and health monitoring |
| Hard-coded I/O | A **virtual ARINC 429 + AFDX-lite bus** with timing, drop, delay, stale-data injection |
| `assert` and a screenshot | A **requirement-based test runner** with structural & MC/DC coverage |
| "It works on my machine" | **Immutable evidence bundles** — git SHA, tool versions, seeds, hashes, replay-verified |
| AI doing the flying | AI doing **triage, change impact, trace gap detection** — clearly marked draft |

**Positioning:** This is *not* a certified system, *not* a flight-control product, and *not* an attempt to ship production avionics. It's a workbench built to demonstrate the engineering vocabulary, lifecycle awareness, and V&V instincts that real avionics teams expect.

---

## 🏗 Architecture

```
+---------------------------------------------------------------+
|                      Workbench  (Web UI)                      |
|     Req Tree │ Trace │ Dashboard │ Evidence Viewer            |
+----------------------------+----------------------------------+
                             │
+----------------------------v----------------------------------+
|                Backend  /  Trace DB  (Postgres)               |
|       Evidence Bundler │ Coverage / MC-DC │ AI Assist         |
+----------------------------+----------------------------------+
                             │
+----------------------------v----------------------------------+
|             Deterministic Sim Kernel  (C++20)                 |
|     IMA-style Scheduler │ Health Monitor │ Sampling/Queuing   |
+--+-----------+-----------+----------+-----------+-------------+
   │           │           │          │           │
+--v--+    +---v---+   +---v----+ +---v----+  +---v---+
| FCC |    |Engine |   |Display | | Data   |  | Health|
| Sur |    |  I/F  |   |Computer| | Concen |  |Monitor|
+--+--+    +---+---+   +---+----+ +---+----+  +---+---+
   │           │           │          │           │
+--v-----------v-----------v----------v-----------v---+
|        Virtual Bus  ( ARINC 429-lite / AFDX-lite )  |
|        + Recorder · Replay · Fault Injection        |
+-----------------------------------------------------+
```

> Full block diagrams, partition tables, and ICD live under [`docs/M1/architecture`](docs/M1/architecture/) and [`docs/M1/icd`](docs/M1/icd/).

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

---

## 🎬 Demo scenario

> **"Sensor drift + bus latency spike + display refresh drop"** — one fault campaign that exercises the whole stack.

1. Left air-data sensor begins to drift → freshness & range checks fire.
2. FCC command and monitor lanes diverge → transition to `ALTERNATE`.
3. AFDX VL latency spikes → health monitor logs degraded path.
4. Display computer surfaces the new annunciation; mode-confusion risk flag is raised.
5. Test runner links the run back to the requirements that fired.
6. Regression dashboard updates pass / fail / coverage trends.
7. AI assistant drafts a triage + change-impact summary (clearly marked).
8. Evidence bundle is exported → re-run from the archive → hash matches.

📄 Full script → [`docs/M6/demo/demo-script.md`](docs/M6/demo/demo-script.md)

---

## 📐 Standards we're aware of

This is a **learning-grade** workbench, not a certified product. The goal is to demonstrate fluency with the documents and lifecycle the industry actually uses.

| Standard | Where it shows up here |
|---|---|
| **DO-178C** | Requirements tree, HLR/LLR split, structural & MC/DC coverage, objective mapping |
| **DO-330** | Tool-qualification notes for the in-repo tooling |
| **DO-331** | Model-based supplement notes for code-generated message schemas |
| **ARP4754A** | System-level requirements flow, DAL assumptions, change impact |
| **DO-297 / AC 20-170** | IMA partitioning, health monitoring, fault containment |
| **AC 20-175** | Flight-deck controls & alerting human-factors checklist |

> ⚠️ DAL ratings, failure conditions, and tool qualification levels in this repo are **assumptions for portfolio purposes**. They are not — and do not claim to be — substantiated for certification.

---

## 🧰 Tech stack

| Layer | Choice |
|---|---|
| Runtime core | **C++20** (some C) |
| Sim kernel | Deterministic tick scheduler, seeded PRNG |
| Tooling / scenarios | **Python 3** |
| Workbench UI | **React + TypeScript** |
| Data store | **PostgreSQL** |
| Message schema | **Protobuf** (FlatBuffers under evaluation) |
| Coverage | LLVM source-based + custom MC/DC reporter |
| CI | **GitHub Actions** |
| HIL bridge | UDP / Serial / CAN |

---

## 🗺 Roadmap

| Milestone | Focus | Status |
|:---:|---|:---:|
| **M1** | Architecture, requirements tree, ICD v0, certification & HF mapping | 🟡 In progress |
| **M2** | IMA-style scheduler, ARINC 429-lite & AFDX-lite buses | ⚪ Planned |
| **M3** | FCC surrogate, Engine I/F, Display Computer, Data Concentrator | ⚪ Planned |
| **M4** | Verification runner, coverage, MC/DC, fault-injection campaigns | ⚪ Planned |
| **M5** | Human factors evaluation, HIL-lite bridge | ⚪ Planned |
| **M6** | Evidence bundle, demo, portfolio pack | ⚪ Planned |

Each milestone has its own folder under `docs/` with design notes, checklists, and a Definition of Done.

---

## 📚 Documentation

```
docs/
├── M1  Foundation        — architecture · requirements · ICD · cert mapping · HF
├── M2  Runtime & Bus     — scheduler · A429-lite · AFDX-lite · recorder
├── M3  Functional        — FCC · Engine I/F · Display Computer
├── M4  Verification      — test runner · coverage · MC/DC · fault injection
├── M5  HF & HIL          — human-factors evaluation · HIL-lite bridge
└── M6  Delivery          — evidence bundle · demo · portfolio pack
```

Each milestone folder follows the same shape: **README → design notes → plan/DoD**.

---

## 📁 Repository layout

```
.
├── docs/        # Milestone-organized design, requirements, ICD, certification, HF
├── src/
│   ├── core/        # Scheduler, health monitor, IPC
│   ├── modules/     # FCC, Engine I/F, Display, Data Concentrator
│   ├── bus/         # ARINC 429-lite, AFDX-lite, CAN
│   └── common/      # Messages, time, logging
├── tools/       # Trace DB, evidence bundler, coverage, MC/DC, fault injector, AI assist
├── tests/       # unit · requirement-based · integration · fault campaigns · HIL
├── sim/         # SIL · HIL bridge · scenarios
├── web/         # Frontend (React/TS) + backend
├── config/      # Partition tables, bus config, fault campaigns
├── ci/          # CI helpers
└── evidence/    # Generated bundles (gitignored)
```

---

## 🚀 Getting started

> M2 produces the first runnable artifact. Until then, the value lives in `docs/`.

```bash
git clone https://github.com/<you>/avionics-verification-workbench.git
cd avionics-verification-workbench

# Skim the foundation
$EDITOR docs/M1/architecture/system-overview.md
$EDITOR docs/M1/requirements/requirements-tree.md
$EDITOR docs/M1/icd/icd-v0.md

# (M2+) build
cmake -S . -B build
cmake --build build
ctest --test-dir build
```

---

## 🙋 FAQ

<details>
<summary><b>Is this real avionics software?</b></summary>

No. It's a portfolio-grade workbench that mirrors how real avionics programs are structured. DAL ratings and failure conditions are assumptions for learning purposes.
</details>

<details>
<summary><b>Why not just implement a fly-by-wire control law?</b></summary>

Because the hard part of flight software is rarely the law itself — it's the requirements tree, the integration, the verification, the traceability, and the evidence. This repo focuses on those.
</details>

<details>
<summary><b>Where does AI fit?</b></summary>

In the **assurance and tooling layer only**: trace gap detection, log triage, test skeletons, change-impact hints. Never in the command path. Every AI output is rendered as a `draft` and requires human review.
</details>

<details>
<summary><b>Can I use this as a learning resource?</b></summary>

Yes. The `docs/Mn` tree is intentionally written as a study path through DO-178C, ARP4754A, DO-297, and AC 20-175 in a hands-on context.
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
