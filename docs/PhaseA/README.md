# Phase A — Enterprise Data Foundation

> 2026-04-14 strategic pivot 산출물. Notion page 18과 1:1 매핑.

목표: `evidence/verification-report.json` + `evidence/bundles/*.zip`을
**Bronze → Silver → Gold** 레이크하우스 구조로 재구성한다. 클라우드 없이도
설계가 검증되도록 SQLite 백엔드를 1차 구현으로 사용하고, 같은 스키마를
Databricks/SageMaker/Vertex AI/Azure ML에 그대로 옮길 수 있게 한다.

## 폴더
- `architecture/` — Lakehouse 레이아웃, 데이터 흐름, 런타임 vs 분석 분리
- `schemas/` — 7 dataset-contract 테이블의 DDL + Bronze/Silver/Gold 정의
- `plan/` — Phase A 작업 계획, DoD, 마이그레이션 노트

## Exit Criteria
- [ ] `tools/data_foundation/` 패키지로 ingest / lineage / drift / gold 명령 제공
- [ ] 매 verification run마다 자동 ingest → SQLite catalog 갱신
- [ ] 임의 `run_id` → full lineage 출력 (req → test → code → evidence → review)
- [ ] schema drift PR fail 게이트 동작 (CI에서)
- [ ] Gold 뷰 4종 (`daily_coverage`, `weekly_escape_rate`, `req_pass_rate`, `hil_latency_distribution`) SQL로 즉시 조회
- [ ] `bus_recording.bin`이 `telemetry_event` 행으로 분해되어 적재
- [ ] 같은 SQL이 SQLite / Databricks SQL / BigQuery 에서 호환되도록 표준 SQL만 사용

## 비-목표 (의도적 제외)
- 실제 클라우드 클러스터 구동 (설계는 클라우드 호환, 실행은 로컬)
- 실시간 스트리밍 ingest (배치만)
- ACL/RBAC 구현 (설계 문서까지만)
- 시각 대시보드 (Phase E에서)
