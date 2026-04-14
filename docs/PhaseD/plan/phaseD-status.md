# Phase D — Status Snapshot (2026-04-14)

## Module map
| Component | File | Notes |
|---|---|---|
| Runtime assurance shell | `tools/intelligence/runtime/assurance_shell.py` | range / rate / authority / watchdog |
| Modes (3) | `tools/intelligence/runtime/modes.py` | Shadow / Advisory / LimitedSupervised + AckQueue |
| Comparison tracker | `tools/intelligence/runtime/comparison.py` | AI vs deterministic disagreement summary |
| Approval-gated loader | `tools/intelligence/runtime/loader.py` | refuses below-state load + online-learning attempt |
| Harness | `tools/intelligence/runtime/harness.py` | couples model + shell + mode + det source |
| Concrete shadow scenario | `scripts/run_shadow.py` | engine_anomaly v0.1.0 vs deterministic engine I/F |
| Orchestrator integration | `scripts/run_verification.py` | runs shadow after Phase C |
| Tests | `tests/python/test_phase_d.py` (13) | shell, modes, gate, harness, online learning |

## Local run
```
Ran 145 tests in 3.865s — OK   (Phase D: 13 신규)

=== Phase D shadow run ===
  model            : engine_anomaly_detector v0.1.0
  approval_state   : auto-generated
  mode             : shadow
  samples          : 192
  agreement_rate   : 0.464
  fallback_rate    : 0.000
  violation_counts : {}
```

## Architecture (4-layer guardrail)
```
AI raw → [range_check] → [rate_limiter] → [authority_cap]
       → [watchdog] → guarded output
                       │
   ┌───────────────────┼───────────────────┐
   ▼                   ▼                   ▼
 SHADOW           ADVISORY           LIMITED_SUPERVISED
 log only       ack queue only      ack-gated low-crit consumer

Deterministic pipeline runs UNCHANGED in parallel — always.
```

## 강제되는 규칙 (테스트로 입증)
- Range / rate / authority 위반은 **자동 클램프 + 로그**, never silent
- Watchdog 초과 시 deterministic fallback 즉시 engage
- Invalid output → fallback engage
- `approval_state < required_for_mode` → load 거부
- Phase C invalidation 존재 시 advisory+ load 거부
- `model.fit()`, `model.partial_fit()` 호출 시 `OnlineLearningAttempt` raise
- Shadow는 ack queue 미사용; Advisory는 park만; LimitedSupervised는 ack 후에만 consumer 호출 + 허용된 키만 통과

## 명시적 금지 사항 (loader에서 enforce)
- online learning controller → `OnlineLearningAttempt`
- reinforcement learning flight control → 모델 등록 시점에 frozen=true 강제 (Phase B)
- primary FCC authority 양도 → AckQueue 우회 경로 없음
- override 없는 자동 의사결정 → LimitedSupervised는 `apply_if_acked()` 호출만 액션 트리거

## Exit Criteria
- [x] Runtime assurance shell: range / rate / authority / watchdog
- [x] Approval-gated loader: board-approved 미만은 advisory+ 진입 불가
- [x] Shadow harness: AI 출력 로그 + disagreement 통계
- [x] Advisory harness: 운영자 ack queue (자동 적용 차단)
- [x] LimitedSupervised harness: low-criticality 서비스 한정 + ack 필수
- [x] Online learning attempt detection
- [x] Shadow run report가 verification report에 포함 (`evidence/phaseD-shadow-report.json`)
- [x] orchestrator가 Phase D 게이트를 PR에서 실행

## Carry-over to Phase E
- Phase D shadow run의 disagreement 통계가 portfolio 데모 자료의 핵심 그래프
- "AI는 control loop 밖" 메시지의 코드 근거가 이 layer
- runtime assurance shell 그림이 1쪽 아키텍처 PDF의 핵심 다이어그램
