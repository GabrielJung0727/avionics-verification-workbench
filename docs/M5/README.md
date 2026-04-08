# M5 — Human Factors & HIL-lite

목표: flight deck HF 평가 항목을 자동/반자동으로 측정하고, MCU/SBC 1대를 붙여 HIL-lite 루프를 닫는다.

## 폴더
- `human-factors/` — HF 평가 항목, 시나리오, 리포트 템플릿
- `hil/` — HIL-lite 브릿지 설계, I/O 매핑, 시간 동기
- `plan/` — 작업 계획, DoD

## Exit Criteria
- [ ] HF 평가 6+ 항목 자동/반자동 측정
- [ ] mode confusion 시나리오 3개
- [ ] AC 20-175 매핑 표 v1
- [ ] HIL-lite: MCU 1대 연결, sensor/actuator stub 동작
- [ ] HIL run 결과가 evidence bundle에 포함
- [ ] HIL latency/jitter 리포트 v0
