# Runtime Design (M2)

## 1. 결정론 모델
- 단일 sim clock (`u64 tick_us`), wall clock 의존 금지
- 모든 random은 seed 주입식 PRNG
- 모든 모듈 entry는 (state, inputs, time) → (state', outputs)

## 2. 스케줄러
- Major frame = LCM(partition periods)
- Minor frame = sim tick (기본 1 ms)
- Partition은 (period, budget, offset, criticality) 튜플
- budget 초과 시 preempt + HM event
- 실행 순서: priority desc → offset asc

## 3. IPC
- **Sampling port**: 최신 값만 유지, freshness flag 동반
- **Queuing port**: bounded FIFO, overflow 시 drop + HM event
- 모두 schema 기반 직렬화 (Protobuf 후보)

## 4. Health Monitor
- Event: PARTITION_OVERRUN, DEADLINE_MISS, IPC_OVERFLOW, IPC_STALE, MODULE_RESTART
- HM table: event → action(LOG/RESTART_PARTITION/COLD_START)
- 모든 HM 이벤트는 trace DB로 동시에 기록

## 5. Startup
- COLD_START: 모든 partition 초기화 → 자가진단 → 운용 진입
- WARM_START: 마지막 정상 상태 복원 시도 → 실패 시 COLD_START

## 6. 측정 항목
- partition 실행 시간 분포
- IPC end-to-end latency
- bus enqueue→dequeue 지연
- jitter (period 편차)

## 7. 미해결 결정
- Protobuf vs FlatBuffers (M2 초에 결정)
- partition thread 모델: cooperative single-thread vs thread pool
