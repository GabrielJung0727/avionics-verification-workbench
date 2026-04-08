# Requirements Tree (M1 seed)

표기: `SYS-###` 시스템, `HLR-XXX-###` 모듈 HLR, `LLR-XXX-###` LLR (M2~).
각 항목은 `id | text | rationale | source | criticality | verifiable_by`.

## SYS — System level
- **SYS-001** 시스템은 결정론적 sim tick으로 동작해야 한다. *Rationale:* 재현성. *Source:* 품질속성. *Crit:* High. *Verify:* 동일 시드 재실행 비교.
- **SYS-002** 모든 모듈 간 메시지는 timestamped 되어야 한다. *Crit:* High. *Verify:* 버스 레코더 검사.
- **SYS-003** 시스템은 ARINC 429-lite와 AFDX-lite 두 버스를 동시에 운용할 수 있어야 한다.
- **SYS-004** 시스템은 partition 단위 fault containment를 보장해야 한다.
- **SYS-005** 시스템은 sensor drift / bus latency / packet drop 결함을 주입할 수 있어야 한다.
- **SYS-006** 모든 테스트 결과는 evidence bundle로 export 되어야 한다.
- **SYS-007** evidence bundle은 git SHA, tool version, seed, hash를 포함해야 한다.
- **SYS-008** 시스템은 요구사항-테스트 양방향 trace를 제공해야 한다.
- **SYS-009** 시스템은 orphan requirement와 trace gap을 보고해야 한다.
- **SYS-010** 시스템은 deadline miss 발생 시 health monitor에 기록해야 한다.
- **SYS-011** 시스템은 cold start와 warm start 두 시퀀스를 지원해야 한다.
- **SYS-012** 시스템은 degraded mode 진입/이탈 이벤트를 기록해야 한다.
- **SYS-013** AI assistant 출력은 모두 draft 표시되어야 하며 자동 머지 금지.
- **SYS-014** 워크벤치 UI는 mode confusion 위험 항목을 표시할 수 있어야 한다.
- **SYS-015** 시스템은 MC/DC 대상 함수에 대해 coverage 리포트를 생성해야 한다.

## HLR — Module level (M1 seed)
### FCC Surrogate
- **HLR-FCC-001** 입력은 range / rate / freshness 검사를 통과해야 사용된다.
- **HLR-FCC-002** Command lane과 Monitor lane은 독립 계산 후 비교한다.
- **HLR-FCC-003** Lane disagreement 임계 초과 시 Alternate mode로 전환한다.
- **HLR-FCC-004** 센서 dual fault 시 Direct mode로 reversion 한다.
- **HLR-FCC-005** Mode 전환은 1 tick 내 DSP에 통지된다.

### Engine Interface
- **HLR-ENG-001** N1/N2/EGT/FF 한계 초과 시 caution/warning을 분류한다.
- **HLR-ENG-002** Exceedance는 hysteresis 포함 latch 된다.
- **HLR-ENG-003** Hot start / hung start 패턴을 감지한다.

### Display Computer
- **HLR-DSP-001** Alert는 warning > caution > advisory 순으로 표시된다.
- **HLR-DSP-002** Color usage는 red/amber/green 규칙을 따른다.
- **HLR-DSP-003** Mode annunciation은 FCC 통지 후 100 ms 내 갱신된다.

### Data Concentrator
- **HLR-DC-001** 각 sensor 입력은 timestamp 부착 후 publish 된다.
- **HLR-DC-002** Stale 입력은 freshness flag와 함께 전달된다.

### Health Monitor
- **HLR-HM-001** Partition fault, deadline miss, IPC error를 수집한다.
- **HLR-HM-002** Fault → action 매핑은 config 기반이다.

## CSV 시드
`requirements.csv` 참조 — 동일 항목을 toolable 형태로 둔다.
