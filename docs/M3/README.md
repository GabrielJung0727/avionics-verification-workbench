# M3 — Functional Modules

목표: M2 런타임 위에 4개 기능 모듈 구현. FCC는 cmd/mon lane, Engine I/F는 limit/exceedance, Display는 PFD/EICAS-lite + alert 우선순위.

## 폴더
- `fcc/` — input validation, mode logic, lane diversity, reversion
- `engine/` — limit table, hysteresis, exceedance, hot/hung start
- `display/` — PFD/EICAS-lite, alert prioritization, color rule
- `plan/` — 작업 계획, DoD

## Exit Criteria
- [ ] FCC 4 mode (Normal/Alternate/Direct/Off) 전환 검증
- [ ] FCC dual sensor fault → Direct reversion 입증
- [ ] Engine 한계 위반 → caution/warning + latch 동작
- [ ] Hot start / hung start 시나리오 감지
- [ ] DSP가 mode 변경을 100ms 내 반영
- [ ] Alert 우선순위/색 규칙 정적 검사 통과
- [ ] M1 HLR (FCC/ENG/DSP/DC) 전 항목 trace 연결
