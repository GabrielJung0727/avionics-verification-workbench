# FAQ — "왜 AI를 비행제어 루프에 직접 안 넣었나요?"

> **30초 답변**
> EASA의 2024 AI Concept Paper는 현재 Level 1·2만 수용 범위로 두고
> Level 3는 후속 문서 대상으로 명시했고, online learning과
> reinforcement learning은 범위 밖으로 둡니다. FAA Roadmap도
> learned vs learning을 구분해 incremental approach + runtime
> assurance를 강조합니다. **자기학습형 AI 제어기는 현재 규정과
> 업계 가이던스 양쪽 모두에서 인정 경로가 없습니다.** 그래서 이
> 프로젝트는 AI를 verification·assurance layer 전용으로 두고,
> 제어 루프는 deterministic safety shell이 1차 권한을 갖도록
> 설계했습니다.

## 5초 답변 (면접용)
> *"AI is bounded to the verification layer; the deterministic
> channel always has primary authority. EASA Level 1·2 / FAA
> incremental — that's the only path the regulator currently
> accepts."*

## 길게 (포트폴리오용)

### 1. 규정 / 가이던스가 그렇게 말한다
- **EASA AI Concept Paper (Issue 2, 2024)** — Level 1·2 중심, Level 3는 후속.
  Online learning, RL은 범위 밖.
- **FAA Roadmap for AI Safety Assurance (v1)** — learned AI vs learning AI 분리.
  Incremental approach + runtime assurance 강조.
- **DO-178C / ARP4754A / DO-330** — 위 어느 문서도 자기학습형 control
  component를 다루지 않는다. 대안 문서가 아직 없다.

### 2. 업계가 실제로 그렇게 한다
- **Airbus Skywise** — predictive maintenance, operational analytics.
  비행 제어 루프 안의 AI가 아님.
- **Boeing × Microsoft** — 디지털 항공 전략에 Microsoft Cloud + AI.
  운영·분석 레이어.
- **GE Aerospace, Honeywell Forge, Collins Aerospace** — 모두
  preventive alert / inspection candidate / operational analytics를 판다.
  AI flight controller가 아님.

### 3. 그래서 이 프로젝트는 어떻게 했나
- **Phase B**: 3개 모델은 모두 frozen (online learning 금지)
- **Phase C**: assurance case + reviewer 승인 워크플로우
- **Phase D**: runtime assurance shell (range / rate / authority /
  watchdog) + shadow → advisory → limited supervised 단계
- **`OnlineLearningAttempt` exception**: `model.fit()` 호출은 코드
  레벨에서 거부

### 4. 그럼 AI는 어디서 가치를 더하나?
| 위치 | 가치 |
|---|---|
| **Verification 우선순위** | escape predictor가 어느 fault campaign을 먼저 돌릴지 추천 |
| **Predictive maintenance** | engine anomaly가 inspection candidate flag |
| **Trace 효율** | trace gap intel이 변경 영향 받을 req 후보 ranking |

이 셋 모두 control loop 밖이고, 모두 reviewer 승인 후에만 다음 단계로
진행된다. 정확히 EASA Level 1·2 + FAA incremental approach가 권하는
도입 순서다.

## 안티-패턴 (이 프로젝트가 *피한* 것들)
- "AI 비행제어 자동화" 데모
- "ChatGPT로 조종사 보조" 챗봇
- 자기학습 fault tolerance controller
- override 없는 mode confusion 자동 해소

## 더 깊이 들어가고 싶다면
- `docs/PhaseD/architecture/runtime-assurance-shell.md`
- `docs/PhaseC/cases/*.md` (assurance cases)
- `docs/M1/certification/safety.md` (failure conditions)
- `tools/intelligence/runtime/loader.py` (`OnlineLearningAttempt` 코드)
