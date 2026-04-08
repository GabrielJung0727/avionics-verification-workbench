# M1 — Status Snapshot

## Exit Criteria
- [x] 4개 모듈(FCC / Engine I/F / Display / Data Concentrator) 경계 확정 — `architecture/block-diagram.md`
- [x] 시스템 요구사항 30+ / HLR 모듈별 5+ — `requirements/requirements-tree.md` (SYS 33, HLR 35)
- [x] ICD v0에 모든 인터-모듈 메시지 등록 — `icd/icd-v0.md` (8 메시지)
- [x] criticality / DAL 가정 문서화 — `certification/safety.md`
- [x] DO-178C objective 매핑 표 v0 — `certification/do178c-mapping.md`
- [x] M2 진입 조건 충족 — `../M2/backlog.md`

## Definition of Done
- [x] system-overview / block-diagram 합의
- [x] SYS 30+, HLR 모듈별 5+
- [x] ICD v0 8개 메시지 + payload 정의
- [x] DO-178C 매핑 v0, DAL 가정 문서화
- [x] HF 평가 항목 6+ seed — `human-factors/hf-mapping.md`
- [x] CI: docs lint + requirements CSV check + CMake hello build — `.github/workflows/ci.yml`
- [x] Trace DB schema 초안 — `architecture/trace-db-schema.md`
- [x] evidence manifest 포맷 초안 — `architecture/evidence-manifest-format.md`
- [x] M2 백로그 5+ 등록 — `../M2/backlog.md` (14 항목)

## 추가 산출물 (Day 4~5)
- `certification/safety.md` — failure conditions FC-01~12, DAL 가정 근거
- `certification/change-procedure.md` — CR → impact → review → apply 절차
- `certification/arp4754a-flow.md` — 1-pager assurance flow
- `scripts/check_requirements.py` — CSV lint (CI에서 사용)

## 다음 (M2 진입)
- `docs/M2/backlog.md` 의 P0부터 시작
- 첫 PR: M2-01 (sim clock + tick loop)
