# Human Factors Evaluation (M5)

## 평가 항목
| ID | 항목 | 측정 | 출처 |
|---|---|---|---|
| HF-01 | Alert prioritization 정확도 | 시나리오 alert 순서 vs 기대 순서 | AC 20-175 |
| HF-02 | Color usage 위반 | 토큰 정적 검사 | AC 20-175 |
| HF-03 | Mode annunciation latency | MSG-006 → render 시간 | Integration |
| HF-04 | Mode confusion 위험 | 사용자 시나리오 + UI 표시 | HF 가이드 |
| HF-05 | Information salience | 가중치 점수 | HF 가이드 |
| HF-06 | Input latency | 합성 입력 → action 시간 | HF 가이드 |

## Mode confusion 시나리오 (예시)
- MC-01: ALTERNATE 진입 시 명시 표시 누락
- MC-02: DIRECT 복귀 후 NORMAL로 자동 환원 시 통지 부족
- MC-03: 동일 색 alert 여러 개 동시 발생

## 리포트 템플릿
- 항목별 pass/fail
- 측정 raw 데이터 링크
- AC 20-175 매핑 셀
- 권장 조치 (개선/요구사항 후보/허용)
