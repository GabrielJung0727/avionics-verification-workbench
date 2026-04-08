# Engine Interface Design (M3)

## 한계 테이블 (학습 가정값)
| Param | Caution | Warning | Exceed | Hysteresis |
|---|---|---|---|---|
| N1 (%) | 100 | 103 | 105 | 1.0 |
| N2 (%) | 100 | 104 | 106 | 1.0 |
| EGT (degC) | 850 | 900 | 950 | 10 |
| FF (kg/h) | 3500 | 3800 | 4000 | 50 |

## Latch 규칙
- exceedance 진입: value ≥ threshold 연속 N tick
- exit: value ≤ threshold - hysteresis 연속 N tick
- latched flag는 운항 종료까지 유지

## Hot start / Hung start
- Hot start: EGT 급상승 (delta/sec 임계 초과) during start phase
- Hung start: N2 가속률 < 임계 + 시간 초과
- 둘 다 MSG-005 EngineExceed (level=WARNING)

## Outputs
- MSG-004 EngineParams: 매 tick (10 Hz)
- MSG-005 EngineExceed: event
- HM 이벤트: ENG_LIMIT_EXCEED

## Trace
- HLR-ENG-001..003
