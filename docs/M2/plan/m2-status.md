# M2 — Status Snapshot

## Implementation note
The M2 runtime is delivered as a **Python reference simulator** under
`tools/sim_py/avx_sim/`. C++20 was the original target but the M2 deliverables
(determinism, IPC semantics, fault injection, recorder hashing) are all about
*model correctness*, not throughput. Python lets us validate the model now and
keep one source of truth. The C++ port is deferred to M3 hot-paths once the
functional modules force performance decisions.

This trade is documented in `docs/M2/design/runtime-design.md` (decision log).

## Module map
| File | Responsibility | Backlog item |
|---|---|---|
| `tools/sim_py/avx_sim/sim_clock.py` | Deterministic monotonic clock | M2-01 |
| `tools/sim_py/avx_sim/scheduler.py` | Cooperative partitioned scheduler, budget enforcement, deadline miss | M2-01, M2-03 |
| `tools/sim_py/avx_sim/partition_loader.py` | Partition table parser | M2-02 |
| `tools/sim_py/avx_sim/health_monitor.py` | HM event log + action map | M2-04 |
| `tools/sim_py/avx_sim/ipc.py` | Sampling + queuing ports w/ freshness & overflow | M2-08 |
| `tools/sim_py/avx_sim/messages.py` | ICD message dataclasses (M1 ICD v0) | M2-05 |
| `tools/sim_py/avx_sim/a429.py` | ARINC 429-lite encode/decode + parity | M2-06 |
| `tools/sim_py/avx_sim/afdx.py` | AFDX-lite VL with BAG, drop, delay, reorder hooks | M2-07 |
| `tools/sim_py/avx_sim/recorder.py` | Append-only recorder + sha256 | M2-09 |
| `sim/scenarios/smoke_scenario.py` | M1 ICD 8-message smoke pipeline | M2-10 |
| `scripts/run_smoke.py` | Run smoke + print summary | M2-10 |
| `scripts/check_determinism.py` | Two-run hash comparison | M2-11 |
| `config/partitions/default.txt` | M2 v0 partition table | M2-02 |
| `tests/python/*` | unittest suite (19 tests) | M2-01..11 |
| `.github/workflows/ci.yml` | docs lint + req CSV + python tests + cmake stub | M2-11 (CI gate) |

## Exit Criteria
- [x] Deterministic sim tick — `SimClock`, no wall-clock dep
- [x] Partition 6개 스케줄, deadline miss 감지/로그 — `Scheduler` + tests
- [x] Sampling/queuing port IPC — `ipc.py` + tests
- [x] HM이 partition fault, deadline miss, IPC error 수집 — `HealthMonitor` + tests
- [x] A429-lite publisher/consumer — `a429.py` + smoke
- [x] AFDX-lite virtual link — `afdx.py` + smoke
- [x] Bus recorder + replay-stable hash — `recorder.py` + tests
- [x] M1 ICD 8 메시지 흐름 smoke 시나리오 통과 — `smoke_scenario.py` (8 ids confirmed)
- [x] Same seed → same recorder sha256 — `check_determinism.py` (verified locally)

## Test summary (local run)
```
Ran 19 tests in 0.003s — OK
records=88  hm_events=2
recorder.sha256=b4daaae4d7dbb214bd9f19bc7435df2cf1897633ff78ab5e8a29fc2f8b16d951
OK: deterministic
```

## Carry-overs to M3
- C++ port of hot paths if/when needed
- Real UDP transport for AFDX (currently in-process queue with delivery ts)
- Jitter/latency measurement export (`jitter.csv`) — deferred to M3 alongside FCC
- Trace-DB DDL apply script — deferred to M4 verification runner
