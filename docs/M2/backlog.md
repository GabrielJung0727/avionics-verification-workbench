# M2 Backlog (M1 Day 10 산출)

M1 종료 시점에 M2로 넘어가는 열린 작업. GitHub Issue로 옮길 항목.

## P0 — 진입 직후
- **M2-01** Sim clock + tick loop 골격 (`src/core/scheduler/`)
  - 단일 `u64 tick_us`, wall-clock 의존 금지 (SYS-001/016)
  - 단위 테스트: 동일 seed → 동일 trace
- **M2-02** Partition table loader (`config/partitions/*.yaml` 스키마 + 파서)
  - 필드: id, period_ms, budget_us, offset_ms, criticality
  - `docs/M2/scheduler/partition-table.md` 와 일치
- **M2-03** Cooperative scheduler v0
  - budget enforcement → PARTITION_OVERRUN event
  - deadline miss → DEADLINE_MISS event
  - 단위 테스트로 결정성 검증
- **M2-04** Health Monitor stub + event sink
  - HM table loader, action enum
  - 모든 이벤트를 trace DB로 흘릴 hook (M4에서 wiring)

## P1 — Bus 1차
- **M2-05** Message schema codegen 결정 (Protobuf vs FlatBuffers 스파이크)
  - 결정 노트 → `docs/M2/design/runtime-design.md` 업데이트
- **M2-06** ARINC 429-lite encoder/decoder
  - label/SDI/data/SSM/parity 필드
  - fault hook: drop, bit-flip, stuck-label
- **M2-07** AFDX-lite UDP transport
  - VL ID + BAG enforcement
  - fault hook: drop, delay, reorder, duplicate
- **M2-08** Sampling / Queuing port IPC
  - freshness flag 전파
  - queue overflow → IPC_OVERFLOW event

## P2 — 검증 / 측정
- **M2-09** Bus recorder + replay
  - binary + csv index, hash-stable
- **M2-10** Smoke 시나리오: M1 ICD 8 메시지 전체 흐름
  - DC publish → FCC consume → DSP consume
- **M2-11** 결정성 회귀 테스트 (CI)
  - 동일 seed 두 번 실행 → recorder hash diff = 0
- **M2-12** Jitter / latency 측정 스크립트
  - per-partition 실행 시간 분포
  - bus enqueue→dequeue 지연

## P3 — 정리
- **M2-13** M2 진입 전 trace DB schema (M1 v0) → DDL 적용 스크립트
- **M2-14** evidence manifest 빈 골격 자동 생성기 (M2 run에서 채워 넣기)

## 라벨 / 마일스톤
- 모두 milestone `M2 — Runtime & Bus`
- 라벨: `core` `bus` `verification` `infra`
