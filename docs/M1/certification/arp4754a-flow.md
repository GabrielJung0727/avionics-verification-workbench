# ARP4754A Development Assurance Flow (1-pager)

워크벤치가 흉내내는 development assurance 흐름. 학습용 단순화 버전.

```
                 ┌────────────────────────┐
                 │  Aircraft / System     │
                 │  Functions             │
                 └───────────┬────────────┘
                             │ allocation
                             v
                 ┌────────────────────────┐
                 │  Functional Hazard     │
                 │  Assessment (FHA)      │  ──► Failure Conditions (FC-01..12)
                 └───────────┬────────────┘
                             │
                             v
                 ┌────────────────────────┐
                 │  System Architecture   │  ──► docs/M1/architecture/
                 │  + DAL Allocation      │      docs/M1/certification/safety.md
                 └───────────┬────────────┘
                             │
              ┌──────────────┼──────────────┐
              v              v              v
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │  Item Reqs   │ │  Item Reqs   │ │  Item Reqs   │
    │  (FCC HLR)   │ │  (ENG HLR)   │ │  (DSP HLR)   │  ──► docs/M1/requirements/
    └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
           │                │                │
           v                v                v
    ┌─────────────────────────────────────────────┐
    │           Implementation (M3)               │
    │  src/modules/{fcc,engine,display,dc}        │
    └──────┬──────────────────────────────────────┘
           │
           v
    ┌─────────────────────────────────────────────┐
    │   Verification (M4)                         │
    │   - requirement-based tests                 │
    │   - structural & MC/DC coverage             │
    │   - fault injection campaigns               │
    │   - trace gap / escape reports              │
    └──────┬──────────────────────────────────────┘
           │
           v
    ┌─────────────────────────────────────────────┐
    │   Evidence Bundle (M6)                      │
    │   manifest + hashes + replay verified       │
    └─────────────────────────────────────────────┘

  loop: Change Request → Impact → Re-verify  (docs/M1/certification/change-procedure.md)
```

## 매핑 요약
| ARP4754A 단계 | 본 워크벤치 산출물 |
|---|---|
| FHA / Failure Conditions | `safety.md` FC-01~12 |
| System Architecture | `architecture/system-overview.md`, `block-diagram.md` |
| DAL Allocation | `safety.md` DAL 가정 표 |
| Item Requirements (HLR) | `requirements/requirements-tree.md` |
| Implementation | `src/modules/*` (M3) |
| Verification | `tests/*`, `tools/coverage_reporter`, `tools/fault_injector` (M4) |
| Configuration / Change | `change-procedure.md`, git + evidence manifest |
