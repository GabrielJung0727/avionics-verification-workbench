# Display Computer Design (M3)

## 구성
- **PFD-lite**: attitude, ias, alt, vs, mode annunciator
- **EICAS-lite**: N1/N2/EGT/FF, exceedance list
- **Alert pane**: warning > caution > advisory

## Alert prioritization
- Queue priority: WARNING(2) > CAUTION(1) > ADVISORY(0)
- Same level → newest first
- 최대 N개 표시, 초과는 "+k more"

## Color rule
- RED: WARNING / unsafe
- AMBER: CAUTION / abnormal
- GREEN: normal
- WHITE: status
- 정적 검사: 토큰 사용 매트릭스 → 위반 시 CI fail (M4 연계)

## Mode annunciation
- MSG-006 수신 → 100ms 내 화면 갱신
- 측정: ts(MSG-006) → ts(render) latency 기록

## Inputs
- MSG-002 Attitude
- MSG-001 AirData
- MSG-004 EngineParams
- MSG-005 EngineExceed
- MSG-006 FCCMode

## Trace
- HLR-DSP-001..003 + HF 매핑
