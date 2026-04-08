# Block Diagram

## 모듈 책임 매트릭스
| 모듈 | 입력 | 출력 | 상태 | 가정 DAL |
|---|---|---|---|---|
| Data Concentrator (DC) | sensor stubs | A429 labels (air data, attitude, eng raw) | health, freshness | C |
| FCC Surrogate (FCC) | bus (sensor labels) | bus (control cmd, mode) | mode, lane health | B (가정) |
| Engine Interface (ENG) | bus (eng raw) | bus (eng params, exceedance) | limit state | C |
| Display Computer (DSP) | bus (mode, eng, alerts) | UI events | annunciation list | C |
| Health Monitor (HM) | partition events | fault log | global state | B |

## 상호작용 (요약 시퀀스)
```
DC --air_data--> FCC : 50 Hz
DC --attitude--> FCC : 100 Hz
DC --eng_raw---> ENG : 20 Hz
ENG --eng_params--> DSP : 10 Hz
ENG --exceedance--> DSP : event
FCC --mode_state--> DSP : on change
FCC --cmd--> (actuator stub) : 50 Hz
HM <-- events -- ALL : async
```

## Partition 배치 (초안)
| Partition | 모듈 | 주기 | budget (us) |
|---|---|---|---|
| P1 | DC | 10 ms | 800 |
| P2 | FCC cmd lane | 20 ms | 1500 |
| P3 | FCC mon lane | 20 ms | 1500 |
| P4 | ENG | 50 ms | 1200 |
| P5 | DSP | 100 ms | 2000 |
| P6 | HM | 100 ms | 500 |

> 주기·예산은 M2에서 측정 후 조정.
