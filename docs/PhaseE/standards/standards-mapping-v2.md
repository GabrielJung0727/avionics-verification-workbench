# Standards & Guidance Mapping (v2, 2026-04-14)

> Updated for the 2026-04-14 strategic pivot. v1 lived in
> `docs/M1/certification/do178c-mapping.md`; this v2 adds **EASA AI
> Concept Paper** and **FAA AI Roadmap** + the Phase A–D evidence chain.

## Master table

| Standard / Guidance | Scope | Where this project addresses it | Phase |
|---|---|---|---|
| **ARP4754A** | Aircraft & system development assurance | `docs/M1/certification/arp4754a-flow.md`, requirements tree | M1 |
| **ARP4761A** | FHA / PSSA / SSA | `docs/M1/certification/safety.md` (FC-01..12) | M1 |
| **DO-178C** | Software development & verification | `docs/M1/certification/do178c-mapping.md`, MC/DC + line coverage | M1, M4 |
| **DO-330** | Tool qualification | `docs/PhaseC/tool-qualification/do330-classification.md` (TQL hypotheses) | C |
| **DO-160G** | Environmental qualification | Out of scope (declared) | — |
| **DO-254** | Airborne electronic hardware | Out of scope (declared) | — |
| **AC 20-115D** | DO-178C acceptance | Referenced in M1 mapping | M1 |
| **AC 20-174** | ARP4754A acceptance | Referenced in M1 mapping | M1 |
| **AC 20-170** | DO-297 IMA | M2 scheduler + HM | M2 |
| **AC 20-175** | Flight-deck controls | M5 HF evaluators | M5 |
| **EASA AI Concept Paper** (Issue 2, 2024) | AI safety for aviation, Level 1·2 | Phase B/C/D `out_of_scope` enforcement, no online learning, no RL | B–D |
| **FAA AI Roadmap** (v1) | Learned vs learning, runtime assurance, incremental adoption | Phase D `runtime/assurance_shell.py` + shadow → advisory progression | D |
| **FAA Order 8110.49A** | Software life-cycle data traceability | Phase A `tools/data_foundation` lineage queries | A |

## Per-phase evidence chain

### M1 — Foundation
- requirements tree (33 SYS + 35 HLR), CSV linter
- ICD v0 + 8 messages
- safety.md FC-01..12 + DAL hypotheses
- ARP4754A flow 1-pager

### M2 — Runtime + Bus
- IMA-style partition scheduler (DO-297 / AC 20-170 mapping)
- ARINC 429-lite + AFDX-lite
- HM event taxonomy

### M3 — Functional modules
- FCC surrogate w/ cmd/mon lane diversity
- Engine I/F latch + hot/hung start
- Display Computer w/ AC 20-175 alerting

### M4 — Verification
- requirement-based runner (DO-178C verification objectives)
- structural + MC/DC coverage
- fault campaigns + escape classification

### M5 — HF + HIL
- AC 20-175 / 25.1322 evaluators
- mode confusion scenario library
- HIL-lite loopback w/ deterministic faults

### M6 — Evidence
- immutable bundle + manifest + sha256 replay
- DO-178C objective table v0

### Phase A — Data Foundation
- `evidence/lakehouse/` (Bronze/Silver/Gold)
- 9 Silver tables — every row reachable by `run_id`
- schema drift gate enforces dataset contract
- aligns with FAA Order 8110.49A traceability principles

### Phase B — Certification Intelligence
- 3 frozen learned components (escape / engine anomaly / trace gap)
- registry with `dataset_hash + label_version + approval_state`
- non-random splits enforced
- aligns with EASA Level 1·2 (offline-trained, frozen, low-criticality)

### Phase C — Reviewable Safety Case
- GSN-lite assurance case per model
- DO-330 tool classification + TQL hypotheses
- 3-state approval workflow + audit log
- self-review prohibited

### Phase D — Bounded Operational AI
- Runtime assurance shell (range / rate / authority / watchdog)
- Shadow → Advisory → LimitedSupervised progression
- `OnlineLearningAttempt` exception (`fit` / `partial_fit` refused)
- aligns with FAA incremental approach + runtime assurance recommendation

## What this project explicitly does NOT claim
- Real certification credit
- Real DAL / TQL ratings
- Real environmental qualification (DO-160G)
- Real FHA / safety analysis (FC-01..12 are learning-grade hypotheses)
- Real airborne software status
- AI in the control loop in any form

## Disclaimer (must accompany any external publication of this map)
This is a **learning and portfolio** mapping. It demonstrates engineering
fluency with the documents and lifecycle, not a substitution for the work
of an AR / DER or a certification authority.
