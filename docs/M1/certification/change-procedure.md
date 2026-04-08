# Change Procedure (M1)

요구사항 / ICD / 설계 변경은 다음 절차를 따른다. 학습/포트폴리오 환경이라 단순화했지만 흐름은 인증 환경의 형태를 유지한다.

## 1. 절차 개요
```
[CR draft] → [Impact analysis] → [Review] → [Approve] → [Apply] → [Re-verify] → [Close]
```

## 2. CR 항목
| 필드 | 설명 |
|---|---|
| CR-ID | `CR-YYYYMMDD-NN` |
| Title | 한 줄 요약 |
| Type | requirement / design / ICD / config / tool |
| Trigger | escape, gap, defect, scope, refactor |
| Linked items | 영향 받는 SYS/HLR/LLR/TC/code path |
| Risk | low / med / high |
| Author | git author |

## 3. Impact Analysis 체크리스트
- [ ] 직접 영향 받는 요구사항 ID 목록
- [ ] 영향 받는 테스트 케이스 ID 목록
- [ ] 영향 받는 코드 경로 (파일/함수)
- [ ] 영향 받는 ICD 메시지
- [ ] 회귀 범위 (smoke / partial / full)
- [ ] DAL 가정에 영향 있음 ?
- [ ] safety FC에 영향 있음 ?
- [ ] 도구 자격(가정)에 영향 있음 ?

## 4. Review 기준
- 솔로 환경에서는 self-review + 24h cooling-off
- review note는 CR에 첨부

## 5. Apply / Re-verify
- merge 전 PR이 trace gap 0
- 영향 범위에 해당하는 테스트 모두 통과
- evidence bundle 재실행 hash 일치

## 6. Tooling
- CR은 `docs/changes/CR-*.md` 또는 GitHub Issue로 관리
- trace DB가 자동으로 영향 후보를 표시 (M4 dashboard)
