# Phase C — Status Snapshot (2026-04-14)

## Module map
| Component | File | Notes |
|---|---|---|
| GSN-lite template | `docs/PhaseC/template/assurance-case-template.md` | 12 required sections |
| Assurance cases (3) | `docs/PhaseC/cases/escape-predictor.md`, `engine-anomaly.md`, `trace-gap-intel.md` | Phase B 모델 1:1 매핑 |
| DO-330 classification | `docs/PhaseC/tool-qualification/do330-classification.md` | 모든 in-house 도구 분류 + TQL 가정 |
| Reviewer flow | `docs/PhaseC/human-flow/reviewer-flow.md` | 상태 머신 + 역할 + 승인 규칙 |
| Lint engine | `tools/intelligence/governance/assurance_lint.py` | section/identity/state 자동 검증 |
| Approval workflow | `tools/intelligence/governance/approval.py` | promote/demote + audit log + self-review 차단 |
| Change impact | `tools/intelligence/governance/change_impact.py` | dataset_hash/git_sha 변경 시 reset 후보 감지 |
| Orchestrator integration | `scripts/run_verification.py` | 모든 case lint + invalidation 게이트 |
| Tests | `tests/python/test_phase_c.py` (10) | lint, promote, demote, change-impact |

## Local run
```
Ran 132 tests in 3.529s — OK   (Phase C: 10 신규)

=== Phase C assurance lint ===
  OK engine-anomaly.md          state=auto-generated
  OK escape-predictor.md        state=auto-generated
  OK trace-gap-intel.md         state=auto-generated

=== Phase C change-impact reset ===
  no registered models above auto-generated; nothing to reset
```

## 강제되는 규칙 (테스트로 입증)
- 모든 assurance case가 12개 필수 섹션을 가져야 함 (orchestrator fail gate)
- Identity 블록의 5개 필드(model_name/version/case_owner/last_reviewed/state)가 비어 있으면 fail
- `state` 필드는 `auto-generated | reviewer-confirmed | board-approved` 중 하나
- 승급 (auto → reviewer)에는 assurance_case_path 필수, lint 통과 필수
- self-review 금지 (reviewer ≠ author)
- 모든 승급/강등은 `approval_log.json`에 audit 기록
- 강등은 항상 `auto-generated`로 (즉시 reset)
- 등록 후 dataset_hash 또는 git_sha 변경 시 invalidation 감지

## Exit Criteria
- [x] GSN-lite 템플릿 + linter (`assurance_lint.py`)로 형식 자동 검증
- [x] Phase B 3개 모델 모두 full assurance case 작성
- [x] 12개 필수 섹션 (Identity / Top claim / Context / Assumptions / Strategy / Sub-goals / Failure modes / Fallback / Human override / Change impact / Standards / Reviewer log)
- [x] DO-178C / ARP4754A / ARP4761A 매핑 (각 case §11 + DO-330 표)
- [x] 자체 제작 도구별 DO-330 분류 + TQL 가정 표
- [x] Approval workflow: 3-state 머신 + audit + self-review 차단
- [x] Change impact: dataset_hash/git_sha 변경 감지 + reset 트리거
- [x] orchestrator가 assurance lint를 PR 게이트로 실행

## Carry-over to Phase D
- Phase D는 Phase C의 `board-approved` 상태에 도달한 모델만 advisory 채널로
  소비할 수 있다 (shadow → advisory → limited supervised)
- runtime assurance shell이 모델 출력을 range/rate/authority로 제한
- override path는 이미 §9에 명시 — Phase D는 그것을 코드로 실행
