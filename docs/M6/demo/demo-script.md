# Demo Script (M6)

## 시나리오: "Sensor drift + Bus latency + Display drop"
- 길이: 5분
- 입력: 좌측 air data sensor drift, AFDX VL 0x110 latency 80ms, DSP 100Hz drop

## 흐름
1. **0:00** 워크벤치 UI / 아키텍처 1장
2. **0:30** scenario 시작, 정상 운항 확인
3. **1:00** sensor drift 주입 → freshness/range 감지
4. **1:30** lane disagree → ALTERNATE 전환 → DSP annunciation
5. **2:00** bus latency storm → HM 이벤트 누적
6. **2:30** display drop → mode confusion 위험 표시
7. **3:00** test runner가 trace에 결과 반영
8. **3:30** regression dashboard 갱신
9. **4:00** AI assistant가 failure triage / change impact 요약 (draft 표시)
10. **4:30** evidence bundle export → 재실행 검증

## 영상 자료
- 1개 메인 영상 (5분)
- 1장 아키텍처 다이어그램 PDF
- 1장 trace 흐름 PDF
- bundle.zip 샘플
