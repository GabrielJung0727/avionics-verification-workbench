# M4 — Status Snapshot

## Module map
| Component | File | Backlog item |
|---|---|---|
| Verification runner | `tools/runner/runner.py` | M4-runner |
| JSON test cases | `tools/runner/test_cases/*.json` (6) | M4-runner |
| Trace + gap report | `tools/runner/runner.py` (`build_trace`, `build_gap_report`) | M4-runner |
| MC/DC tracker | `tools/sim_py/avx_sim/mcdc.py` | M4-mcdc |
| MC/DC instrumentation | `fcc._validate`, `engine._update_latch` | M4-mcdc |
| Line coverage | `tools/coverage_reporter/coverage.py` (`sys.settrace` based) | M4-cov |
| Fault injection | `tools/fault_injector/campaign.py` + `campaigns/*.json` | M4-fault |
| Orchestrator | `scripts/run_verification.py` | M4-orchestrator |

## Test cases (M4 v0)
| TC ID | Linked req | Description |
|---|---|---|
| TC-FCC-001 | HLR-FCC-008, SYS-001 | self-test → NORMAL |
| TC-FCC-004 | HLR-FCC-004, SYS-021 | dual fault → DIRECT |
| TC-ENG-001 | HLR-ENG-001/002/004 | overlimit + latch persistence |
| TC-DSP-003 | HLR-DSP-003, HLR-FCC-005 | mode latency observable |
| TC-DC-001 | HLR-DC-001, SYS-002 | DC publishes timestamped MSGs |
| TC-AFDX-001 | SYS-005, SYS-022 | AFDX delay storm tolerance |

## Fault campaigns
| Campaign | Faults | Expected classification |
|---|---|---|
| FC-001 | dual sensor fault | mitigated (FCC → DIRECT) |
| FC-002 | n1 to warning band | detected (engine HM events) |
| FC-003 | AFDX 80 ms delay | escaped (benign — intentional smoke) |

## MC/DC
Two designated decisions, instrumented with logically independent conditions
so MC/DC pairs are well defined:

| Decision | Conditions | Coverage |
|---|---|---|
| `fcc.validate` | air-present, att-present, air-fresh, att-fresh | **4/4 (100%)** |
| `engine.latch_promote` | level > previous, level ≥ WARNING | **2/2 (100%)** |

The orchestrator drives a small "decision exercise" routine before running
the integration scenarios so the MC/DC pairs are guaranteed to be visible
without depending on which specific scenarios happened to fire.

## Local run
```
Ran 59 tests in 0.603s — OK

=== M4 Verification Summary ===
  tests_total: 6
  tests_passed: 6
  tests_failed: 0
  campaigns_total: 3
  campaigns_passed: 2
  coverage_pct: 29.35
  mcdc_decisions: ['fcc.validate', 'engine.latch_promote']
  mcdc_pct_avg: 100.0
  gap_uncovered_count: 55
```

Output: `evidence/m4-verification-report.json` (~per-test results, trace,
gap, MC/DC, coverage).

## Exit Criteria
- [x] requirement → test → result trace 자동 생성 — `build_trace`
- [x] statement coverage 리포트 (line-level via `sys.settrace`)
- [x] MC/DC 대상 함수 리포트 — fcc.validate, engine.latch_promote
- [x] fault campaign config 기반 실행 — FC-001/002/003
- [x] escape (감지 안 된 fault) 자동 보고 — `classification`
- [x] regression dashboard 데이터 (JSON) — `evidence/m4-verification-report.json`
- [x] CI에서 PR마다 실행 — `.github/workflows/ci.yml` `python-tests` job

## Carry-overs to M5/M6
- HTML coverage rendering (현재 JSON only) → optional later
- Branch / decision coverage (line만 측정) → optional later
- Dashboard 시각화 → M6 portfolio
- 더 많은 MC/DC 대상 함수 → M5+
