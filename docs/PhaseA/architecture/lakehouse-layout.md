# Lakehouse Layout (Phase A)

## 1. 디렉터리 구조

```
evidence/
├── verification-report.json    (orchestrator 출력, Bronze 입력)
├── bundles/
│   └── bundle-*.zip            (immutable evidence packages)
└── lakehouse/                  ← Phase A 신규
    ├── bronze/
    │   └── runs/
    │       └── <run_id>.json   (raw payload, content-addressable)
    ├── silver/
    │   └── catalog.sqlite      (모든 정규화 테이블)
    ├── gold/
    │   └── views.sql           (materialized view 정의)
    ├── manifest.json           (lakehouse 자체의 schema_version + run count)
    └── drift/
        └── *.json              (감지된 drift report)
```

## 2. 데이터 흐름

```
run_verification.py
      │
      ▼ writes
verification-report.json + bundle-*.zip
      │
      ▼ ingest
[Bronze] runs/<run_id>.json   (raw, hashed copy)
      │
      ▼ normalize
[Silver] catalog.sqlite
   ├── run_manifest               1 row per run
   ├── verification_outcome       N rows per run (per test case)
   ├── fault_injection_case       N rows (per campaign)
   ├── telemetry_event            many rows (parsed bus_recording.bin)
   ├── derived_health_window      N rows (HM event windows)
   ├── human_review               0..N rows (reviewer state)
   ├── artifact_index             N rows (every file in the bundle)
   ├── mcdc_sample                per-decision MC/DC stats
   ├── hil_measurement            per HIL config
   └── hf_finding                 per HF evaluator
      │
      ▼ aggregate
[Gold] SQL views
   ├── daily_coverage
   ├── weekly_escape_rate
   ├── req_pass_rate
   └── hil_latency_distribution
      │
      ▼ consume
M6 dashboard / Phase B ML models / lineage queries
```

## 3. 왜 SQLite 인가

| 결정 사유 | 비고 |
|---|---|
| 외부 의존 없음 | `import sqlite3` 표준 라이브러리 |
| 단일 파일 = immutable artifact | bundle에 그대로 포함 가능 |
| 같은 SQL이 Databricks SQL / BigQuery / Athena 에서 동작 | ANSI SQL 부분집합만 사용 |
| 학습/포트폴리오 환경에서 클라우드 비용 0 | 동일 코드를 클라우드로 이전 가능 |

## 4. 클라우드 매핑 (실제 이전 시)

| Phase A (지금) | Databricks 등가물 | Azure ML 등가물 |
|---|---|---|
| `lakehouse/bronze/` | Delta Bronze table + Autoloader | ADLS Gen2 + Auto Loader |
| `lakehouse/silver/catalog.sqlite` | Delta Silver tables | Azure ML Feature Store |
| `lakehouse/gold/views.sql` | Delta Gold + SQL Warehouse | Azure Synapse Serverless |
| `manifest.json` | Unity Catalog metadata | Purview catalog |
| `drift/*.json` | Lakehouse Monitoring | Azure ML Data Drift |

## 5. 런타임 vs 분석 분리 원칙

`tools/sim_py/avx_sim/`는 **runtime**. 분석 도구가 절대 import하지 않는다.
`tools/data_foundation/`는 **analytics**. runtime을 import하지 않는다 (단방향).
`scripts/`는 두 layer를 묶는 thin orchestrator.

이 분리가 **EASA / FAA의 "AI는 assurance layer 전용" 원칙**을 코드 구조에서
강제하는 방법이다. 분석 코드 버그가 control loop를 오염시킬 수 없다.
