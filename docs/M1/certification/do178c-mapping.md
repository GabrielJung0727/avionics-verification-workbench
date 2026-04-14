# DO-178C Objective Mapping (v1, 2026-04-14)

> 학습/포트폴리오 목적의 매핑이며 실제 인증 산출물이 아님을 명시한다.
> 전체 표준 스택은 **[`docs/regulatory/`](../../regulatory/)** 의 1-pager
> 들에서 확인. 종합 매핑(v2)은 [`docs/PhaseE/standards/standards-mapping-v2.md`](../../PhaseE/standards/standards-mapping-v2.md).

## 표준 / 가이던스 공식 연결

| 분류 | 문서 | 1-pager |
|---|---|---|
| 시스템 개발 보증 | **ARP4754A** | [`docs/regulatory/arp4754a.md`](../../regulatory/arp4754a.md) |
| 안전 평가 | **ARP4761A** | [`docs/regulatory/arp4761a.md`](../../regulatory/arp4761a.md) |
| 소프트웨어 보증 | **DO-178C** | [`docs/regulatory/do178c.md`](../../regulatory/do178c.md) |
| 도구 자격 | **DO-330** | [`docs/regulatory/do330.md`](../../regulatory/do330.md) |
| 환경 시험 (out of scope) | **DO-160G** | [`docs/regulatory/do160g.md`](../../regulatory/do160g.md) |
| 항공전자 HW (out of scope) | **DO-254** | [`docs/regulatory/do254.md`](../../regulatory/do254.md) |
| FAA AC — ARP4754A 인정 | **AC 20-174** | [`docs/regulatory/ac-20-174.md`](../../regulatory/ac-20-174.md) |
| FAA AC — DO-178C 인정 | **AC 20-115D** | [`docs/regulatory/ac-20-115d.md`](../../regulatory/ac-20-115d.md) |
| Flight-deck controls / HF | **AC 20-175** | [`docs/regulatory/ac-20-175.md`](../../regulatory/ac-20-175.md) |
| AI 가이던스 (EU) | **EASA AI Concept Paper (Issue 2, 2024)** | [`docs/regulatory/easa-ai-concept-paper.md`](../../regulatory/easa-ai-concept-paper.md) |
| AI 가이던스 (US) | **FAA AI Roadmap (v1)** | [`docs/regulatory/faa-ai-roadmap.md`](../../regulatory/faa-ai-roadmap.md) |
| 라이프사이클 데이터 | **FAA Order 8110.49A** | (Phase A `tools/data_foundation` lineage가 informed) |

> ⚠️ **DAL · TQL · AI level 등급은 모두 가정.** 환경 시험(DO-160G)·HW
> 보증(DO-254)은 명시적으로 out-of-scope. 자세히는
> [`docs/regulatory/disclaimer.md`](../../regulatory/disclaimer.md).

## 가정 DAL
| 모듈 | 가정 DAL | 근거 |
|---|---|---|
| FCC Surrogate (cmd+mon) | B | 비행 자세 제어 영향 가정 |
| Health Monitor | B | 안전 분리·복구 책임 |
| Engine I/F | C | 운용 영향 |
| Display Computer | C | 정보성 + alerting |
| Data Concentrator | C | 데이터 분배 |

## 핵심 objective 매핑 (요약)
| Objective area | 워크벤치 산출물 | 표준 링크 |
|---|---|---|
| Software planning | `docs/M1/plan/` + `docs/M1/README.md` | [DO-178C](../../regulatory/do178c.md) |
| Software requirements | `requirements/requirements-tree.md`, `requirements.csv` | [DO-178C](../../regulatory/do178c.md), [ARP4754A](../../regulatory/arp4754a.md) |
| Software design | `architecture/`, ICD v0, 모듈 README | [DO-178C](../../regulatory/do178c.md) |
| Source code | `tools/sim_py/avx_sim/` | [DO-178C](../../regulatory/do178c.md) |
| Verification of requirements | `tools/runner/`, `tests/python/` | [DO-178C](../../regulatory/do178c.md) |
| Verification of code (structural coverage) | `tools/coverage_reporter`, `avx_sim/mcdc.py` | [DO-178C](../../regulatory/do178c.md) |
| Configuration management | git + `tools/evidence_bundler` | [DO-178C](../../regulatory/do178c.md), Order 8110.49A |
| Quality assurance | `.github/workflows/ci.yml` + Phase A drift gate + Phase C lint | [DO-178C](../../regulatory/do178c.md) |
| Tool qualification | `docs/PhaseC/tool-qualification/do330-classification.md` | [DO-330](../../regulatory/do330.md) |
| Lifecycle data traceability | `tools/data_foundation` lineage | Order 8110.49A |

## ARP4754A 측면
- System requirements → HLR → LLR 흐름 + change impact —
  [`docs/M1/certification/arp4754a-flow.md`](arp4754a-flow.md) +
  [`docs/regulatory/arp4754a.md`](../../regulatory/arp4754a.md)
- Change procedure — [`change-procedure.md`](change-procedure.md)

## ARP4761A 측면
- FHA 가설 + DAL 근거 — [`safety.md`](safety.md) (FC-01..12)
- 자세히 — [`docs/regulatory/arp4761a.md`](../../regulatory/arp4761a.md)

## DO-330 측면
- 자체 제작 도구 분류 + TQL 가정 —
  [`docs/PhaseC/tool-qualification/do330-classification.md`](../../PhaseC/tool-qualification/do330-classification.md)
- 자세히 — [`docs/regulatory/do330.md`](../../regulatory/do330.md)

## DO-297 / AC 20-170 측면
- IMA partition 정의는 [`architecture/block-diagram.md`](../architecture/block-diagram.md)
- HM 구조는 partition fault containment를 입증하는 핵심

## AC 20-175 측면
- Flight deck controls / alerting → `tools/sim_py/avx_sim/modules/display.py`
  + `tools/sim_py/avx_sim/hf/eval.py`
- 자세히 — [`docs/regulatory/ac-20-175.md`](../../regulatory/ac-20-175.md)

## DO-160G / DO-254 측면 (명시적 out-of-scope)
- 환경 시험 — [`docs/regulatory/do160g.md`](../../regulatory/do160g.md)
- 항공전자 하드웨어 — [`docs/regulatory/do254.md`](../../regulatory/do254.md)

## AI guidance 측면 (Phase B/C/D)
- EASA AI Concept Paper Level 1·2 — [`docs/regulatory/easa-ai-concept-paper.md`](../../regulatory/easa-ai-concept-paper.md)
- FAA AI Roadmap incremental + runtime assurance —
  [`docs/regulatory/faa-ai-roadmap.md`](../../regulatory/faa-ai-roadmap.md)
- Phase D 코드 enforcement: `tools/intelligence/runtime/loader.py` —
  `OnlineLearningAttempt`, approval-state gating

## 다음 산출물
- 추가 supplements (DO-331/332/333) — 현재 사용 안 함, 명시적 disclaimer
- 실제 PSAC / SCI / SAS — 학습 범위 밖
