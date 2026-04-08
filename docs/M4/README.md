# M4 — Verification, Coverage, Fault Injection

목표: requirement-based test runner, structural / MC/DC coverage, fault injection 캠페인을 한 파이프라인으로 묶고 regression dashboard에 표시한다.

## 폴더
- `runner/` — test schema, runner 설계, CI 통합
- `coverage/` — LLVM source-based coverage, MC/DC 분석
- `fault-injection/` — fault model, campaign config, escape 분석
- `plan/` — 작업 계획, DoD

## Exit Criteria
- [ ] requirement → test → result trace 자동 생성
- [ ] statement / branch / decision coverage 리포트
- [ ] MC/DC 대상 함수 리포트
- [ ] fault campaign config 기반 실행
- [ ] escape (감지 안 된 fault) 자동 보고
- [ ] regression dashboard v0
- [ ] CI에서 PR마다 실행
