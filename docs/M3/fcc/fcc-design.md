# FCC Surrogate Design (M3)

## Modes
| Mode | Conditions | Behavior |
|---|---|---|
| NORMAL | both lanes agree, all sensors fresh | full law (gain + limiter) |
| ALTERNATE | lane disagree below dual fault | reduced gains, no envelope protection |
| DIRECT | dual sensor fault or major HM event | pass-through with simple limits |
| OFF | startup / inhibit | command invalid, valid=false |

## Input validation
- range check (per ICD)
- rate check (delta vs prev tick)
- freshness check (STALE → invalid)
- dual-source consistency (when applicable)

## Command lane
1. select valid sources
2. compute pitch/roll/yaw cmd (simple linear law)
3. apply limiter
4. publish MSG-007 with valid flag

## Monitor lane
- 독립 함수, 동일 입력으로 cmd 재계산
- |cmd - mon| > threshold → DISAGREE
- DISAGREE 누적 N tick → ALTERNATE 진입

## Reversion logic
- dual sensor fault (e.g. AirData + Attitude STALE) → DIRECT
- monitor lane crash (HM event) → DIRECT
- 복귀: cool-down 후 self-test 통과 시 NORMAL

## Trace
- HLR-FCC-001..005 → 단위 + req-based 테스트
- mode 전환 모두 MSG-006 publish, HM 기록
