# Interface Control Document — v0

본 ICD는 모듈 간 메시지의 sender, receiver, 버스, 주기, payload, 단위, 갱신 의미를 정의한다. M2에서 schema 파일로 동기화한다.

## 1. 메시지 인덱스
| Msg ID | Name | From | To | Bus | Rate (Hz) | Criticality |
|---|---|---|---|---|---|---|
| MSG-001 | AirData | DC | FCC | A429 | 50 | High |
| MSG-002 | Attitude | DC | FCC | A429 | 100 | High |
| MSG-003 | EngineRaw | DC | ENG | A429 | 20 | Med |
| MSG-004 | EngineParams | ENG | DSP | AFDX-lite | 10 | Med |
| MSG-005 | EngineExceed | ENG | DSP, HM | AFDX-lite | event | High |
| MSG-006 | FCCMode | FCC | DSP, HM | AFDX-lite | on change | High |
| MSG-007 | FCCCommand | FCC | Actuator stub | A429 | 50 | High |
| MSG-008 | HMEvent | (any) | HM | AFDX-lite | event | High |

## 2. Payload 정의 (요약)
### MSG-001 AirData
| Field | Type | Unit | Range | Notes |
|---|---|---|---|---|
| timestamp_us | u64 | us | — | sim time |
| ias | f32 | knot | 0..600 | indicated airspeed |
| altitude | f32 | ft | -1000..50000 | pressure alt |
| vs | f32 | ft/min | -10000..10000 | vertical speed |
| freshness | u8 | enum | OK/STALE/INVALID | |

### MSG-002 Attitude
| Field | Type | Unit | Range |
|---|---|---|---|
| timestamp_us | u64 | us | — |
| pitch | f32 | deg | -90..90 |
| roll | f32 | deg | -180..180 |
| yaw_rate | f32 | deg/s | -200..200 |
| freshness | u8 | enum | — |

### MSG-003 EngineRaw
| Field | Type | Unit |
|---|---|---|
| timestamp_us | u64 | us |
| n1 | f32 | % |
| n2 | f32 | % |
| egt | f32 | degC |
| ff | f32 | kg/h |

### MSG-004 EngineParams
EngineRaw + 한계 상태 enum (`NORMAL/CAUTION/WARNING/EXCEED`).

### MSG-005 EngineExceed (event)
| Field | Type |
|---|---|
| ts_us | u64 |
| param | enum |
| level | enum |
| value | f32 |
| latched | bool |

### MSG-006 FCCMode (on change)
| Field | Type |
|---|---|
| ts_us | u64 |
| mode | enum NORMAL/ALTERNATE/DIRECT |
| reason | enum |
| lane_disagree | bool |

### MSG-007 FCCCommand
| Field | Type | Unit |
|---|---|---|
| ts_us | u64 | us |
| pitch_cmd | f32 | deg |
| roll_cmd | f32 | deg |
| yaw_cmd | f32 | deg |
| valid | bool | — |

### MSG-008 HMEvent
| Field | Type |
|---|---|
| ts_us | u64 |
| source | string |
| code | enum |
| severity | enum |
| detail | string |

## 3. 타이밍 / freshness 규칙
- 모든 메시지에 `timestamp_us` 필수
- consumer는 (now - ts) > freshness_budget 이면 STALE 처리
- freshness budget은 메시지별 config (`config/bus/freshness.yaml`, M2)

## 4. 변경 절차
- ICD 변경 → CR 생성 → impact 분석 → 영향 받는 req/test 표시 → 승인 → version bump
