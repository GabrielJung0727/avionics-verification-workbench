# Verification Runner Design (M4)

## Test case schema (YAML)
```yaml
id: TC-FCC-001
req: [HLR-FCC-003]
description: Lane disagreement above threshold transitions to ALTERNATE
seed: 42
preconditions:
  mode: NORMAL
  partitions: default
inputs:
  - inject: cmd_lane_offset
    value: 0.8
expected:
  mode_after_ms: ALTERNATE
  hm_event: LANE_DISAGREE
artifacts:
  - bus_recording
  - hm_log
```

## Runner 책임
- scenario load → sim init (seed) → run → assert → artifact 수집
- requirement-based: TC.req 항목 모두 trace DB 갱신
- deterministic: 동일 seed → 동일 결과
- artifact는 evidence bundle 매니페스트에 등록

## 결과 모델
- PASS / FAIL / ERROR / FLAKY (재실행 비교)
- gap report: req without TC, TC without req

## CI 통합
- PR: smoke set (수십 초)
- nightly: full set + fault campaigns
- artifact: bundle zip 업로드
