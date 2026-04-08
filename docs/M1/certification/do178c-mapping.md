# DO-178C Objective Mapping (v0)

> 학습/포트폴리오 목적의 매핑이며 실제 인증 산출물이 아님을 명시한다.

## 가정 DAL
| 모듈 | 가정 DAL | 근거 |
|---|---|---|
| FCC Surrogate (cmd+mon) | B | 비행 자세 제어 영향 가정 |
| Health Monitor | B | 안전 분리·복구 책임 |
| Engine I/F | C | 운용 영향 |
| Display Computer | C | 정보성 + alerting |
| Data Concentrator | C | 데이터 분배 |

## 핵심 objective 매핑 (요약)
| Objective area | 워크벤치 산출물 |
|---|---|
| Software planning | `docs/M1/plan/` + `docs/M1/README.md` |
| Software requirements | `requirements/requirements-tree.md`, `requirements.csv` |
| Software design | `architecture/`, ICD v0, 모듈 README |
| Source code | `src/modules/*`, `src/core/*` |
| Verification of requirements | `tests/requirement_based/` |
| Verification of code (structural coverage) | `tools/coverage_reporter`, `tools/mcdc_analyzer` |
| Configuration management | git + evidence bundle manifest |
| Quality assurance | CI gate + review checklist |
| Tool qualification | `docs/M1/certification/tool-qualification-notes.md` (M3+) |

## ARP4754A 측면
- system requirements → HLR → LLR 흐름 + change impact
- safety 가정 → failure condition 목록(추후 `safety.md`)

## DO-297 / AC 20-170 측면
- IMA partition 정의는 `architecture/block-diagram.md`
- HM 구조는 partition fault containment를 입증하는 핵심

## 다음 산출물
- `do330-tool-qualification.md` (M3)
- `do331-model-based-notes.md` (옵션)
- `safety.md` (failure condition + DAL 근거)
