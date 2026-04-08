# System Overview

## 1. 목적
이 워크벤치는 항공기 전체를 만드는 것이 아니라, **항공전자 모듈이 들어가는 시스템을 어떻게 통합·검증·추적하는가**를 보여주는 플랫폼이다. 본 문서는 시스템 경계, 외부 액터, 내부 블록, 데이터 플로우를 정의한다.

## 2. 시스템 경계
- **In scope**: 시뮬레이션된 항공전자 4개 모듈, IMA-style 런타임, 가상 버스, 검증·증거 파이프라인, 워크벤치 UI
- **Out of scope**: 실제 비행 제어법칙의 인증 수준 구현, 실 항공기 하드웨어, 실제 FADEC ECU

## 3. 외부 액터
| 액터 | 역할 |
|---|---|
| Verification Engineer | 요구사항 작성, 테스트 작성/실행, 증거 검토 |
| Integration Engineer | 모듈 통합, 버스 구성, 결함 캠페인 운영 |
| Reviewer (Surrogate) | trace gap, coverage, evidence bundle 검토 |
| AI Assistant | trace gap 감지, 테스트 스켈레톤·요약 초안 (human-in-the-loop) |

## 4. 내부 블록
```
+--------------------------------------------------+
|                Workbench (Web UI)                |
|  Req Tree | Trace | Dashboard | Evidence Viewer  |
+----------------------+---------------------------+
                       |
+----------------------v---------------------------+
|              Backend / Trace DB                  |
|  Postgres | Evidence Bundler | Coverage/MCDC     |
+----------------------+---------------------------+
                       |
+----------------------v---------------------------+
|             Deterministic Sim Kernel             |
|   IMA-style Scheduler | Health Monitor | IPC     |
+--+----------+----------+-----------+-------------+
   |          |          |           |
+--v--+   +---v---+  +---v----+  +---v----+
| FCC |   |Engine |  |Display |  | Data   |
| Sur |   |  I/F  |  |Computer|  | Concen |
+--+--+   +---+---+  +---+----+  +---+----+
   |          |          |           |
+--v----------v----------v-----------v---+
|     Virtual Bus (A429 / AFDX-lite)     |
+----------------------------------------+
```

## 5. 데이터 플로우 (요약)
1. Sensor stub → Data Concentrator → Bus
2. Bus → FCC Surrogate (validation, mode logic, monitor)
3. FCC → Bus → Display Computer (mode/annunciation)
4. Engine I/F → Bus → Display Computer (EICAS-lite)
5. Health Monitor → 모든 partition fault 수집 → Trace DB
6. Test runner → scenario 실행 → Bus 기록 → Evidence bundle

## 6. 핵심 품질 속성
- **Determinism**: 동일 시드/시나리오 → 동일 결과
- **Traceability**: Req ↔ Code ↔ Test ↔ Result 양방향
- **Reproducibility**: evidence bundle만으로 재실행 가능
- **Observability**: 모든 메시지/이벤트 timestamped
- **Safety mindset**: monitor lane 독립, fault containment

## 7. 가정 / 제약
- 단일 머신 + 옵션 HIL-lite 1대
- 실시간 OS 미사용, 결정론적 sim tick으로 RT 흉내
- DAL 등급은 학습 목적의 가정값
- AI 출력은 항상 draft, 사람이 승인

## 8. 다음 단계
- ICD v0 (`../icd/`)
- 요구사항 시드 (`../requirements/`)
- 인증 매핑 (`../certification/`)
