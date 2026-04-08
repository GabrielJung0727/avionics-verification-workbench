# Requirements Tree (M1)

표기: `SYS-###` 시스템, `HLR-XXX-###` 모듈 HLR (LLR은 M3+에서).
각 항목은 `id | text | rationale | source | criticality | verifiable_by` 형식이며, CSV 시드는 `requirements.csv` 참조.

## HLR / LLR 분리 규칙
- **SYS**: 시스템 외부에서 관측 가능한 동작과 품질 속성
- **HLR**: 모듈 단위 기능, 인터페이스, 모드, 안전 속성
- **LLR (M3+)**: 함수/파일 단위 동작, 알고리즘, 자료구조 결정
- 모든 HLR은 ≥1 SYS에서 도출, 모든 LLR은 ≥1 HLR에서 도출
- 동일 사실의 중복 금지 (HLR이 SYS를 그대로 복사 ❌)

---

## SYS — System level (33)

### 결정성 / 재현성
- **SYS-001** 시스템은 결정론적 sim tick으로 동작해야 한다. *Crit:* High *Verify:* 동일 seed 재실행 비교
- **SYS-002** 모든 모듈 간 메시지는 timestamped 되어야 한다. *Crit:* High *Verify:* 버스 레코더 검사
- **SYS-016** 시스템은 wall-clock에 의존하지 않아야 한다. *Crit:* High *Verify:* 정적 검사 + sandbox run
- **SYS-017** 모든 random source는 seed 주입식이어야 한다. *Crit:* High *Verify:* 코드 리뷰 + 회귀 테스트

### 버스 / 인터페이스
- **SYS-003** 시스템은 ARINC 429-lite와 AFDX-lite 두 버스를 동시에 운용할 수 있어야 한다. *Crit:* Med
- **SYS-018** 시스템은 ICD에 등록된 메시지만 publish/subscribe 한다. *Crit:* High
- **SYS-019** 시스템은 메시지 schema 버전을 검사해야 한다. *Crit:* Med

### 안전 / 분리
- **SYS-004** 시스템은 partition 단위 fault containment를 보장해야 한다. *Crit:* High
- **SYS-020** monitor lane은 command lane과 독립적으로 계산되어야 한다. *Crit:* High
- **SYS-021** dual sensor fault 발생 시 시스템은 안전 측 (Direct mode 또는 안전 정지)으로 전이해야 한다. *Crit:* High

### 결함 주입 / 강건성
- **SYS-005** 시스템은 sensor / bus / partition / compute 결함을 주입할 수 있어야 한다. *Crit:* High
- **SYS-022** 결함 주입은 config 파일로 재현 가능해야 한다. *Crit:* High
- **SYS-023** escape (감지 실패 결함) 는 자동 보고되어야 한다. *Crit:* Med

### 검증 / 증거
- **SYS-006** 모든 테스트 결과는 evidence bundle로 export 되어야 한다. *Crit:* High
- **SYS-007** evidence bundle은 git SHA, tool version, seed, hash를 포함해야 한다. *Crit:* High
- **SYS-024** evidence bundle은 단독으로 재실행 가능해야 한다. *Crit:* High *Verify:* replay hash 비교
- **SYS-025** 시스템은 statement / branch / decision coverage를 생성해야 한다. *Crit:* High
- **SYS-015** 시스템은 MC/DC 대상 함수에 대해 coverage 리포트를 생성해야 한다. *Crit:* High

### Traceability
- **SYS-008** 시스템은 요구사항-테스트 양방향 trace를 제공해야 한다. *Crit:* High
- **SYS-009** 시스템은 orphan requirement와 trace gap을 보고해야 한다. *Crit:* Med
- **SYS-026** 모든 요구사항은 unique ID, source, rationale, criticality를 가져야 한다. *Crit:* High
- **SYS-027** 요구사항 변경은 change request → impact analysis → approval 절차를 따라야 한다. *Crit:* High

### Runtime / Health Monitor
- **SYS-010** 시스템은 deadline miss 발생 시 health monitor에 기록해야 한다. *Crit:* High
- **SYS-028** health monitor는 fault → action 매핑을 config로 가져야 한다. *Crit:* High
- **SYS-029** partition은 자체 budget을 초과할 수 없다. *Crit:* High

### 운용 / 모드
- **SYS-011** 시스템은 cold start와 warm start 두 시퀀스를 지원해야 한다. *Crit:* Med
- **SYS-012** 시스템은 degraded mode 진입 / 이탈 이벤트를 기록해야 한다. *Crit:* Med
- **SYS-030** mode 전환은 1 sim tick 내 통지되어야 한다. *Crit:* High

### 인간 요인 / UI
- **SYS-014** 워크벤치 UI는 mode confusion 위험 항목을 표시할 수 있어야 한다. *Crit:* Med
- **SYS-031** alert는 warning > caution > advisory 순으로 정렬되어야 한다. *Crit:* High
- **SYS-032** color 사용은 red/amber/green 규칙을 따라야 한다. *Crit:* High

### AI / 도구
- **SYS-013** AI assistant 출력은 모두 draft 표시되어야 하며 자동 머지 금지. *Crit:* High
- **SYS-033** 자체 제작 도구는 DO-330 관점의 용도/제약을 문서화해야 한다. *Crit:* Med

---

## HLR — Module level

### Data Concentrator (DC) — 7
- **HLR-DC-001** DC는 각 sensor 입력에 timestamp를 부착한 뒤 publish 한다.
- **HLR-DC-002** DC는 stale 입력을 freshness flag와 함께 전달한다.
- **HLR-DC-003** DC는 입력 range 위반 시 INVALID flag를 부착한다.
- **HLR-DC-004** DC는 sensor source ID를 메시지에 포함한다.
- **HLR-DC-005** DC는 publish 주기를 partition 주기와 정렬한다.
- **HLR-DC-006** DC는 sensor dropout을 N tick 내 감지한다.
- **HLR-DC-007** DC는 자체 health 상태를 HM에 보고한다.

### FCC Surrogate (FCC) — 8
- **HLR-FCC-001** FCC 입력은 range / rate / freshness 검사를 통과해야 사용된다.
- **HLR-FCC-002** Command lane과 Monitor lane은 독립 계산 후 비교한다.
- **HLR-FCC-003** Lane disagreement 임계 초과 시 ALTERNATE 모드로 전환한다.
- **HLR-FCC-004** Dual sensor fault 시 DIRECT 모드로 reversion 한다.
- **HLR-FCC-005** Mode 전환은 1 tick 내 DSP에 통지된다.
- **HLR-FCC-006** FCC는 NORMAL/ALTERNATE/DIRECT/OFF 4개 모드를 가진다.
- **HLR-FCC-007** FCC command 출력은 limiter를 통과해야 한다.
- **HLR-FCC-008** FCC는 startup 시 self-test를 수행한다.

### Engine Interface (ENG) — 7
- **HLR-ENG-001** ENG는 N1/N2/EGT/FF 한계 위반 시 caution/warning을 분류한다.
- **HLR-ENG-002** Exceedance는 hysteresis 포함 latch 된다.
- **HLR-ENG-003** ENG는 hot start / hung start 패턴을 감지한다.
- **HLR-ENG-004** ENG는 latched exceedance를 운항 종료까지 유지한다.
- **HLR-ENG-005** ENG는 EGT 급상승률을 모니터링한다.
- **HLR-ENG-006** ENG는 모든 exceedance event를 HM에 보고한다.
- **HLR-ENG-007** ENG는 limit table을 config로 가진다.

### Display Computer (DSP) — 7
- **HLR-DSP-001** DSP는 alert를 warning > caution > advisory 순으로 표시한다.
- **HLR-DSP-002** DSP는 red / amber / green 색 규칙을 따른다.
- **HLR-DSP-003** DSP는 mode annunciation을 FCC 통지 후 100 ms 내 갱신한다.
- **HLR-DSP-004** DSP는 동시 alert 최대 N개를 표시하고 초과는 요약한다.
- **HLR-DSP-005** DSP는 입력 freshness 위반 시 dashed value를 표시한다.
- **HLR-DSP-006** DSP는 mode 전환 이력을 N초간 보존한다.
- **HLR-DSP-007** DSP는 자체 refresh rate를 측정 가능해야 한다.

### Health Monitor (HM) — 6
- **HLR-HM-001** HM은 partition fault, deadline miss, IPC error를 수집한다.
- **HLR-HM-002** HM은 fault → action 매핑을 config로 가진다.
- **HLR-HM-003** HM은 모든 이벤트를 trace DB로 기록한다.
- **HLR-HM-004** HM은 partition restart action을 트리거할 수 있다.
- **HLR-HM-005** HM은 cold/warm start 전이를 결정한다.
- **HLR-HM-006** HM은 자체 deadline을 만족해야 한다.

---

## 셀프 리뷰 결과 (Day 5)
- ✅ 모든 SYS에 ID/criticality/verify 부여
- ✅ 모든 HLR이 ≥1 SYS에서 도출
- ⚠️ MC/DC 대상 함수 식별은 M3에서 (`certification/safety.md`와 함께)
- ⚠️ LLR 작성은 모듈 코드 진입(M3) 시 시작
- ✅ orphan: 없음
- ✅ 모호 표현 ("적절히", "가능한") 미사용
