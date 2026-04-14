# Phase D — Bounded Operational AI Research

> 2026-04-14 strategic pivot. Notion page 21 1:1 매핑.

목표: Phase B의 frozen learned components가 **shadow → advisory → limited
supervised** 순서로만, 그리고 deterministic safety shell이 1차 권한을 항상
가지는 조건에서, 어떻게 운용 가능한지를 코드로 시연한다.

## 절대 금지 (hard line)
- online learning controller
- reinforcement learning flight control
- primary FCC authority를 AI에 양도
- pilot/operator override 없이 자동 의사결정
- `board-approved` 미만 모델의 advisory/supervised 채널 진입

## 허용 (low-criticality, frozen, runtime-guarded)
| 단계 | 의미 | 허용 범위 |
|---|---|---|
| **Shadow** | AI 출력은 **로그만**, 제어/표시에 영향 0 | board-approved 이전 모델도 가능 (학습 단계) |
| **Advisory** | AI 출력이 운영자에게 **표시**되지만 자동 동작 없음 | board-approved 모델만 |
| **Limited Supervised** | AI 출력이 사용자 명시 ack 후에만 **낮은 criticality 서비스**에 적용 | board-approved + 인프라 가드레일 입증 후 |

## 폴더
- `architecture/` — runtime assurance shell 설계, 4-layer 가드레일
- `scenarios/` — 시연 시나리오 2종 (shadow engine anomaly, advisory trace gap)
- `plan/` — 작업 계획, DoD, status

## Exit Criteria
- [ ] Runtime assurance shell: range / rate / authority / watchdog enforcement
- [ ] Approval-gated loader: `board-approved` 미만은 advisory+ 진입 불가
- [ ] Shadow harness: AI 출력 로그 + deterministic 결과와 disagreement 통계
- [ ] Advisory harness: 운영자 ack queue (자동 적용 차단)
- [ ] LimitedSupervised harness: low-criticality 서비스 한정 + ack 필수
- [ ] Online learning attempt detection (등록된 모델이 fit 호출 시 차단)
- [ ] Shadow run report가 verification report에 포함
- [ ] orchestrator가 Phase D 게이트를 PR에서 실행
