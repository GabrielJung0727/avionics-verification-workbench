# M2 — Plan

## Week 1 — Scheduler core
- [ ] sim clock + tick loop
- [ ] partition struct, table loader
- [ ] cooperative scheduler v0
- [ ] budget enforcement + overrun event
- [ ] HM stub + event sink
- [ ] 단위 테스트: 결정성, deadline miss

## Week 2 — Bus sim
- [ ] message schema codegen
- [ ] A429-lite encoder/decoder
- [ ] AFDX-lite UDP transport
- [ ] sampling/queuing port wiring
- [ ] recorder (binary + csv index)
- [ ] replay tool
- [ ] fault hooks (drop, delay, stuck)

## Week 3 — Integration & measurement
- [ ] M1 ICD 8 메시지 흐름 smoke
- [ ] jitter/latency 측정 스크립트
- [ ] CI에서 결정성 회귀 테스트 (run x2 → diff)
- [ ] M3 진입 백로그 정리

## DoD
- [ ] same seed → same recorder hash
- [ ] partition 6개 모두 schedule
- [ ] HM이 4종 이상 event 수집
- [ ] 두 버스 모두 메시지 통과
- [ ] 측정 리포트 v0 export
