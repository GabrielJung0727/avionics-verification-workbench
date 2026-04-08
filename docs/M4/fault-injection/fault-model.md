# Fault Model & Campaigns (M4)

## Fault categories
- **Sensor**: drift, stuck, NaN, out-of-range, noise, dropout
- **Bus**: drop, delay, reorder, duplicate, corrupt
- **Partition**: overrun, crash, restart, IPC overflow
- **Compute**: clock skew, brownout, memory pressure (흉내)

## Campaign config (YAML)
```yaml
id: FC-001
description: Air data drift + AFDX delay storm
seed: 7
duration_ms: 30000
faults:
  - type: sensor_drift
    target: AirData.ias
    rate_per_s: 1.5
  - type: bus_delay
    bus: AFDX
    vl: 0x110
    delay_ms: 80
expectations:
  fcc_mode_eventual: ALTERNATE
  hm_events_min:
    LANE_DISAGREE: 1
```

## Result classification
- **detected**: HM 또는 monitor가 fault를 잡음
- **mitigated**: 시스템이 degraded mode 등으로 안전 측 동작
- **escaped**: 영향 발생했으나 감지/대응 실패 → 신규 req 후보로 등록

## 출력
- per-campaign 리포트 (counts, timeline)
- escape 목록 → trace DB의 "candidate requirement" 큐로
- evidence bundle에 포함
