# Partition Table (M2 v0)

| ID | Module | Period (ms) | Budget (us) | Offset (ms) | Crit |
|---|---|---|---|---|---|
| P1 | Data Concentrator | 10 | 800 | 0 | C |
| P2 | FCC cmd lane | 20 | 1500 | 2 | B |
| P3 | FCC mon lane | 20 | 1500 | 12 | B |
| P4 | Engine I/F | 50 | 1200 | 5 | C |
| P5 | Display Computer | 100 | 2000 | 30 | C |
| P6 | Health Monitor | 100 | 500 | 90 | B |

Major frame = 100 ms.

## HM 매핑 v0
| Event | Action |
|---|---|
| PARTITION_OVERRUN(P2) | LOG + LANE_DISAGREE_HINT |
| PARTITION_OVERRUN(P3) | LOG + LANE_DISAGREE_HINT |
| DEADLINE_MISS(P1) | LOG + DEGRADE_DC |
| IPC_OVERFLOW(* → P5) | LOG (display tolerant) |
| IPC_STALE(MSG-002) | LOG + FCC_FRESHNESS_FAIL |
| MODULE_RESTART(P4) | LOG + ENG_DEGRADED |

## 측정 슬롯
`measurements/` 하위에 run별 csv 저장 (M2 후반).
