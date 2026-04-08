# M1 — 2주 작업 계획

목표: 아키텍처 / 요구사항 / ICD / 인증 매핑 v0 합의 + 리포 스캐폴드 + CI hello-world.

## Week 1 — Architecture & Requirements
- **Day 1** 시스템 경계, 외부 액터, 4 모듈 책임 매트릭스 확정 → `architecture/system-overview.md` 리뷰
- **Day 2** 블록 다이어그램 / partition 배치 초안 → `architecture/block-diagram.md`
- **Day 3** SYS 요구사항 30+ 작성 → `requirements/requirements-tree.md` + CSV
- **Day 4** 모듈별 HLR seed (각 모듈 5개 이상)
- **Day 5** 요구사항 셀프 리뷰: orphan, 모호, 미검증 항목 표시

## Week 2 — ICD, Cert mapping, Repo, CI
- **Day 6** ICD v0 메시지 인덱스/payload 작성 → `icd/icd-v0.md`
- **Day 7** DO-178C objective 매핑 v0, DAL 가정 문서화 → `certification/`
- **Day 8** HF 평가 항목 seed → `human-factors/hf-mapping.md`
- **Day 9** 리포 스캐폴드 점검, CMake hello-world build, GitHub Actions 최소 워크플로우
- **Day 10** Trace DB schema 초안(ERD), evidence bundle manifest 포맷 초안, M2 진입 리뷰

## Definition of Done
- [ ] system-overview / block-diagram 합의
- [ ] SYS 요구사항 30+, HLR 모듈별 5+
- [ ] ICD v0에 8개 이상 메시지 등록, payload 정의
- [ ] DO-178C 매핑 v0, DAL 가정 문서화
- [ ] HF 평가 항목 6+ seed
- [ ] CI에서 빈 빌드 + lint + markdown lint 통과
- [ ] Trace DB schema 초안 + evidence manifest 포맷 초안
- [ ] M2 백로그(스케줄러/버스)에 열린 이슈 5+ 등록

## 리스크 / 가정
- 혼자 진행 → 리뷰는 self-review 체크리스트로 대체, 단 결정 사항은 모두 문서화
- 실 인증 산출물이 아님을 README/매핑 문서에 명시
- 시간 초과 시 우선순위: 요구사항 + ICD > 인증 매핑 > HF > CI 디테일
