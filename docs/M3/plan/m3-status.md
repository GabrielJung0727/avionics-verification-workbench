# M3 — Status Snapshot

## Module map
| Module | File | Backlog | HLR coverage |
|---|---|---|---|
| Data Concentrator | `tools/sim_py/avx_sim/modules/data_concentrator.py` | M3-DC | HLR-DC-001/002/003/004/006/007 |
| Engine Interface | `tools/sim_py/avx_sim/modules/engine.py` | M3-ENG | HLR-ENG-001/002/003/004/005/006/007 |
| FCC Surrogate | `tools/sim_py/avx_sim/modules/fcc.py` | M3-FCC | HLR-FCC-001/002/003/004/005/006/007/008 |
| Display Computer | `tools/sim_py/avx_sim/modules/display.py` | M3-DSP | HLR-DSP-001/002/003/004/005/006/007 |
| M3 integration | `sim/scenarios/m3_scenario.py` | — | wires all four through scheduler + AFDX |

## Tests
| File | Count | Notes |
|---|---|---|
| `tests/python/test_dc.py` | 5 | HLR-DC-001/003/004/006/007 |
| `tests/python/test_engine.py` | 4 | classify, latch, hot-start, config |
| `tests/python/test_fcc.py` | 6 | self-test, freshness, limiter, dual fault, modes, mode-msg |
| `tests/python/test_display.py` | 8 | priority, color rule, latency, cap, dashed, history, refresh |
| `tests/python/test_m3_integration.py` | 6 | smoke, determinism, caution propagation, dual fault → DIRECT, mode latency, AFDX delay tolerance |

## Local run
```
Ran 48 tests in 0.009s — OK
```
- M2 suite (19) still green
- M3 unit suite (23) all green
- M3 integration (6) all green
- determinism hash unchanged from M2

## Exit Criteria
- [x] FCC 4 mode 전환 가능 — `Fcc.mode` enum + tests
- [x] FCC dual sensor fault → DIRECT — `test_HLR_FCC_004` + integration
- [x] Engine 한계 위반 → caution/warning + latch — `test_HLR_ENG_001/002`
- [x] Hot start 시나리오 감지 — `test_HLR_ENG_003`
- [x] DSP가 mode 변경을 100ms 내 반영 — `mode_latency_violations == 0`
- [x] Alert 우선순위/색 규칙 정적 검사 통과 — `static_color_check`
- [x] M1 HLR (FCC/ENG/DSP/DC) 전 항목 trace 연결 — 테스트 이름에 HLR ID 포함

## Carry-overs
- Hung start scenario: detector 구현됨, 전용 시나리오 테스트는 M4에서 fault campaign으로
- LLR 도출 + MC/DC 함수 식별: M4 verification runner와 함께
- Display refresh 측정 export: M5 HF 평가에서
