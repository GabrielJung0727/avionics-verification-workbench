# Phase A — Status Snapshot (2026-04-14)

## Module map
| Component | File | Notes |
|---|---|---|
| Lakehouse layout | `tools/data_foundation/storage.py` | Bronze/Silver/Gold/Drift dirs, sha256 helpers |
| Silver schema + Gold views | `tools/data_foundation/catalog.py` | ANSI SQL only — same DDL maps to Databricks/BigQuery/Athena |
| DDL reference | `docs/PhaseA/schemas/silver-ddl.sql`, `gold-views.sql` | Standalone for cloud porting |
| AVX-REC bus parser | `tools/data_foundation/bus_parser.py` | No runtime dependency (intentional) |
| Ingest | `tools/data_foundation/ingest.py` | report.json → Bronze + 7 Silver tables |
| Lineage | `tools/data_foundation/lineage.py` | run_id → full record |
| Drift gate | `tools/data_foundation/drift.py` | Top-level + per-section schema check |
| CLI | `scripts/ingest_evidence.py` | `ingest / lineage / drift / gold` subcommands |
| Orchestrator wiring | `scripts/run_verification.py` | drift → ingest after every run |
| Bus capture | `_capture_bus_recording()` in orchestrator | smoke run → `bus_recording_latest.bin` → bundle → telemetry_event |
| Tests | `tests/python/test_phase_a.py` (8) | catalog, ingest, lineage, gold, drift, parser |

## Local run snapshot
```
Ran 113 tests in 2.434s — OK

=== Phase A drift gate ===
  ok: True

=== Phase A lakehouse ingest ===
  run_id   : fe16678a-bee0-4f5b-a116-611c140b02bf
  silver rows:
    verification_outcome: 13
    fault_injection_case: 3
    mcdc_sample: 2
    hil_measurement: 4
    hf_finding: 6
    artifact_index: 22
    telemetry_event: 88
```

Lineage CLI:
```
$ python scripts/ingest_evidence.py lineage <run_id>
{
  "found": true,
  "manifest": { ingested_at, git_sha, bench_id, operator, env_profile,
                bronze_path, bronze_sha256 },
  "verification_outcomes": [...],
  "campaigns": [...],
  "artifacts": [...],
  "mcdc": [...],
  "telemetry_event_count": 88
}
```

Gold:
```
$ python scripts/ingest_evidence.py gold
daily_coverage         → 2026-04-14 runs=2 mean_mcdc=1.0
weekly_escape_rate     → 2026-W15 escape_rate=0.33
req_pass_rate          → HLR-DC-001 100%, ...
hil_latency_distribution → per config_name
```

## Exit Criteria
- [x] `tools/data_foundation/` 패키지로 ingest / lineage / drift / gold 명령 제공
- [x] 매 verification run마다 자동 ingest → SQLite catalog 갱신
- [x] 임의 `run_id` → full lineage 출력 (req → test → code → evidence)
- [x] schema drift PR fail 게이트 동작 (orchestrator 실패 코드 반환)
- [x] Gold 뷰 4종 SQL로 즉시 조회
- [x] `bus_recording.bin`이 `telemetry_event` 행으로 분해되어 적재
- [x] 같은 SQL이 SQLite / Databricks SQL / BigQuery 호환 (ANSI subset)

## 클라우드 이전 매핑 (재확인)
| 지금 | Databricks 등가물 |
|---|---|
| `evidence/lakehouse/bronze/runs/*.json` | Delta Bronze + Autoloader |
| `evidence/lakehouse/silver/catalog.sqlite` | Delta Silver tables |
| `evidence/lakehouse/gold/views.sql` | SQL Warehouse views |
| `manifest.json` | Unity Catalog metadata |
| `drift/latest.json` | Lakehouse Monitoring |

## Carry-over to Phase B
- `mcdc_sample`, `fault_injection_case`, `telemetry_event`, `verification_outcome` 가 모두 SQL로 조회 가능 → escape predictor / engine anomaly / trace gap intel 학습 데이터 기반 마련됨
- Phase B는 이 Silver 위에 MLflow와 모델 등록 레이어를 얹는다
