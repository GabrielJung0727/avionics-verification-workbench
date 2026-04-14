# 1-Page Architecture (PDF-ready)

> Render with any markdown→PDF tool (`pandoc`, VS Code "Markdown PDF",
> Typora). Page layout is tuned for A4 portrait at 11pt.

# Certification-aligned Avionics Verification Intelligence Platform

```
┌──────────────────────────────────────────────────────────────────┐
│                      Verification Intelligence                    │
│                                                                  │
│  Phase B (Frozen learned)        Phase D (Runtime guard)         │
│  ┌──────────────────┐            ┌──────────────────────────┐    │
│  │ escape predictor │            │ Range / Rate / Authority │    │
│  │ engine anomaly   │ ─raw out─► │ Watchdog / Operator gate │    │
│  │ trace gap intel  │            └──────────────────────────┘    │
│  └──────────────────┘                       │                    │
│         ▲                                   ▼                    │
│         │ load(approval_state)      Shadow / Advisory /          │
│         │                           LimitedSupervised            │
│  Phase C: assurance case + workflow                              │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │ GSN-lite case  ·  DO-330 TQL  ·  3-state approval audit  │    │
│  └──────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
                                ▲
                                │ trains on Silver
                                │ writes evidence rows
                                │
┌──────────────────────────────────────────────────────────────────┐
│  Phase A — Enterprise Data Foundation (Lakehouse)                │
│                                                                  │
│  Bronze (raw JSON)  →  Silver (9 tables)  →  Gold (4 views)     │
│  schema drift gate · run_id lineage · dataset contract           │
└──────────────────────────────────────────────────────────────────┘
                                ▲
                                │ orchestrator dumps
                                │ verification-report.json
                                │ + bundle-*.zip
┌──────────────────────────────────────────────────────────────────┐
│  M1 → M6 — Deterministic Verification Workbench                  │
│                                                                  │
│  M1 Architecture / Reqs (33 SYS + 35 HLR) / ICD / FC-01..12      │
│  M2 IMA scheduler · ARINC 429-lite · AFDX-lite · recorder        │
│  M3 FCC surrogate · Engine I/F · Display Computer · DC           │
│  M4 Verification runner · MC/DC · fault campaigns · escapes      │
│  M5 HF evaluators (AC 20-175) · HIL-lite loopback                │
│  M6 Immutable evidence bundle · manifest sha256 · replay verify  │
└──────────────────────────────────────────────────────────────────┘
```

## Hard line — what this platform does NOT do
- AI never closes a control loop
- No online learning, no RL flight control
- No primary FCC authority transfer
- No automatic decision without operator override path

## Standards & guidance (Phase A–D)
- **DO-178C** verification objectives → tools/runner + coverage + MC/DC
- **ARP4754A** development assurance → requirements tree + safety.md
- **DO-330** tool qualification → docs/PhaseC/tool-qualification/
- **EASA AI Concept Paper (Level 1·2)** → Phase B `frozen` + Phase D shell
- **FAA AI Roadmap (incremental)** → Phase D Shadow→Advisory→LimitedSup

## Numbers (latest run)
- 145 tests passing (M2 19 / M3 29 / M4 11 / M5 15 / M6 4 / Phase A 8 / B 9 / C 10 / D 13 / others)
- coverage 33% on `avx_sim`, MC/DC 100% on instrumented decisions
- 6/6 verification cases · 2/3 fault campaigns (1 escape catalogued)
- 6/6 HF findings · 3/3 mode-confusion scenarios · 4 HIL configs
- 21-file evidence bundle, sha256 replay verified

## Tagline
> *This project is not an AI flight controller. It is a certification-aligned
> avionics verification intelligence platform that uses governed datasets,
> traceable evidence, and bounded learned components to improve verification
> prioritization, anomaly detection, and operational assurance under existing
> aviation safety frameworks.*
