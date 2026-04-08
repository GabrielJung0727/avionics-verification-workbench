# M5 — Status Snapshot

## Module map
| Component | File | Notes |
|---|---|---|
| HF evaluators | `tools/sim_py/avx_sim/hf/eval.py` | 6 findings: HF-01..HF-06 |
| Mode-confusion scenarios | `tools/sim_py/avx_sim/hf/mode_confusion.py` | MC-01 dual-fault, MC-02 latched engine warning, MC-03 multi-alert |
| HIL-lite bridge | `tools/sim_py/avx_sim/hil/bridge.py` | in-process loopback, deterministic faults |
| Loopback MCU | `tools/sim_py/avx_sim/hil/bridge.py` `LoopbackMcu` | latency/jitter/drop/reboot/brownout |
| Measurement | `HilMeasurement.summary()` | mean/max latency, jitter stddev, drops, reboots |
| Orchestrator integration | `scripts/run_verification.py` | HF + mode confusion + 4 HIL runs |
| Tests | `tests/python/test_hf.py` (10), `tests/python/test_hil.py` (5) | — |

## Exit Criteria
- [x] HF 평가 6+ 항목 자동 측정 — HF-01~06 all passing
- [x] mode confusion 시나리오 3개 — MC-01/02/03 in `MODE_CONFUSION_SCENARIOS`
- [x] AC 20-175 / AC 25.1322 매핑 표 v1 — `HfFinding.ac_ref`
- [x] HIL-lite: in-process loopback MCU 연결, sensor/actuator stub 동작
- [x] HIL run 결과가 evidence report에 포함 — `hil_runs` in `m4-verification-report.json`
- [x] HIL latency/jitter 리포트 v0 — `HilMeasurement.summary()`

## Local run
```
Ran 74 tests in 0.532s — OK

=== M4/M5 Verification Summary ===
  tests_total: 6        tests_passed: 6
  campaigns_total: 3    campaigns_passed: 2
  coverage_pct: 37.15
  mcdc_pct_avg: 100.0
  hf_total: 6           hf_passed: 6
  mode_confusion_total: 3   mode_confusion_ok: 3
  hil_runs: 4

=== HF Evaluation ===
  OK HF-01: Alert prioritization - ordered
  OK HF-02: Color usage (red/amber/green) - OK
  OK HF-03: Mode annunciation latency - violations=0
  OK HF-04: Information salience score - score=5
  OK HF-05: Dashed value on stale input - ias_rendered=----
  OK HF-06: Mode history window pruning - kept=0

=== HIL-lite ===
  nominal        cycles=60 lat_mean=0us lat_max=0us drops=0 reboots=0
  latency-5ms    cycles=60 lat_mean=5000us lat_max=5000us drops=0 reboots=0
  drop-every-3   cycles=40 lat_mean=0us lat_max=0us drops=20 reboots=0
  reboot         cycles=57 lat_mean=0us lat_max=0us drops=3 reboots=1
```

## Design notes
- **Why in-process loopback instead of real UART/UDP?** Determinism. The sim
  clock is the only source of time; the MCU surrogate schedules its delivery
  against that clock so two runs produce identical measurement vectors.
  Swapping in a real transport is a M6 integration task and does not change
  the measurement semantics.
- **Why latency uses `due - sent` instead of `now - sent`?** So the reported
  delay reflects the MCU processing budget, not the sim polling period.

## Carry-overs to M6
- Replace loopback with real UDP for an optional physical HIL run
- Visualize HF findings + HIL runs in the portfolio dashboard
- Link mode-confusion scenarios into the fault-campaign catalog
