# M2 — IMA-style Scheduler + Bus Simulation

목표: 결정론적 partition scheduler와 가상 버스(A429-lite, AFDX-lite)를 동작시키고, M1 ICD 메시지가 실제로 흐르게 한다.

## 폴더
- `design/` — 런타임/버스 상세 설계, 시퀀스, 타이밍 모델
- `scheduler/` — partition 테이블, HM 매핑, 측정 결과
- `bus/` — A429-lite / AFDX-lite 스키마, freshness 규칙, recorder 포맷
- `plan/` — 2~3주 작업 계획, DoD

## Exit Criteria
- [ ] 결정론적 sim tick 동작 (동일 seed → 동일 trace)
- [ ] partition 6개 스케줄, deadline miss 감지/로그
- [ ] sampling/queuing port IPC 동작
- [ ] HM이 partition fault, deadline miss, IPC error 수집
- [ ] A429-lite publisher/consumer
- [ ] AFDX-lite virtual link (UDP)
- [ ] bus recorder + replay
- [ ] M1 ICD의 8개 메시지가 모두 흐르는 smoke 시나리오 통과
- [ ] jitter/latency 측정 리포트 v0
