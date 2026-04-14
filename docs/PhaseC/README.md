# Phase C — Reviewable Safety Case

> 2026-04-14 strategic pivot 산출물. Notion page 20과 1:1 매핑.

목표: Phase B에서 만든 3개의 frozen learned component 각각에 대해 **assurance
case**를 작성한다. 모델 카드(단순 메타정보)가 아니라, 리뷰어가 *이 모델을
이 맥락에서 쓰면 안전한가?* 를 60초 안에 판단할 수 있는 구조화된 안전 논증.

스타일은 **GSN-lite**(Goal Structuring Notation의 Markdown 버전) — 그래픽
도구 없이도 claim → strategy → evidence 사슬을 추적 가능.

## 폴더
- `template/` — 모든 case가 따라야 하는 골격 (필수 섹션 명시)
- `cases/` — `escape-predictor.md`, `engine-anomaly.md`, `trace-gap-intel.md`
- `tool-qualification/` — DO-330 관점의 자체 제작 도구 분류 + TQL 가정
- `human-flow/` — human-in-the-loop 워크플로우 다이어그램 (텍스트 기반)
- `plan/` — Phase C 작업 계획, DoD, status

## Exit Criteria
- [ ] GSN-lite 템플릿 + linter (`assurance_lint.py`)로 형식 자동 검증
- [ ] Phase B 3개 모델 모두 full assurance case 작성
- [ ] 각 case에 intended use / out-of-scope / training data pedigree / failure modes / fallback / human override / change impact 섹션 포함
- [ ] DO-178C / ARP4754A / ARP4761A 매핑 표 1부
- [ ] 자체 제작 도구별 DO-330 분류 + TQL 가정 표
- [ ] Approval workflow: `auto-generated → reviewer-confirmed → board-approved` 상태 머신 (변경 시 `human_review` Silver 적재)
- [ ] Change impact: 모델 / dataset_hash 변경 시 approval 자동 리셋
- [ ] orchestrator가 assurance lint를 PR 게이트로 실행
