# Phase E — Status Snapshot (2026-04-14)

## Module map
| Component | File | Notes |
|---|---|---|
| README v2 | `README.md` | New hero, TL;DR, architecture, Phase A–D highlights, FAQ |
| 1-page architecture | `docs/PhaseE/portfolio/one-page-architecture.md` | PDF-ready ASCII layout |
| Standards mapping v2 | `docs/PhaseE/standards/standards-mapping-v2.md` | DO-178C/ARP4754A/ARP4761A + EASA AI Concept Paper + FAA AI Roadmap + FAA Order 8110.49A |
| FAQ — AI not in loop | `docs/PhaseE/faq/why-ai-not-in-control-loop.md` | 5s / 30s / long answers + anti-patterns |
| FAQ — vs Skywise/Forge/Collins | `docs/PhaseE/faq/vs-skywise-forge-collins.md` | comparison table + differentiator |
| Resume bullets v2 | `docs/PhaseE/portfolio/resume-bullets-v2.md` | headline + 6 position-tailored variants |
| LinkedIn post v2 | `docs/PhaseE/portfolio/linkedin-post-v2.md` | Phase A–D narrative + hard line |
| Demo script v2 | `docs/PhaseE/demo/demo-script-v2.md` | 5-min flow with Phase A/D scenes |
| Pitch source of truth | `tools/portfolio/pitch.py` | 5s / 30s / 60s / hard-line constants |
| Elevator pitch CLI | `scripts/elevator_pitch.py` | `python scripts/elevator_pitch.py 5s\|30s\|60s\|hard-line\|all` |
| Tests | `tests/python/test_phase_e.py` (12) | pitch budgets, FAQ presence, README narrative, standards v2 |

## Local run
```
Ran 157 tests in 3.820s — OK   (Phase E: 12 신규)

$ python scripts/elevator_pitch.py 5s
AI bounded to the verification layer; the deterministic channel always
has primary authority. EASA Level 1-2 / FAA incremental - that's the only
path the regulator currently accepts.
```

## 핵심 메시지 (모든 채널 동일)
> *This project is not an AI flight controller. It is a certification-aligned
> avionics verification intelligence platform that uses governed datasets,
> traceable evidence, and bounded learned components to improve verification
> prioritization, anomaly detection, and operational assurance under existing
> aviation safety frameworks.*

## Exit Criteria
- [x] 영문 README v2 — Phase A–D narrative + 7 highlight blocks + 5 FAQs
- [x] 이력서 bullet 6종 (Flight software / Verification / Display / IMA / Defence / Data)
- [x] LinkedIn 포스트 v2 (Phase D differentiator + #frozenmodels + #runtimeassurance)
- [x] 5분 데모 시나리오 v2 — `docs/PhaseE/demo/demo-script-v2.md`
- [x] 1쪽 아키텍처 (PDF-ready) — `docs/PhaseE/portfolio/one-page-architecture.md`
- [x] FAQ 2종 — "왜 AI가 제어 루프에 없나?" + "Skywise/Forge/Collins와 차이?"
- [x] 표준 매핑 v2 — EASA AI Concept Paper + FAA AI Roadmap + FAA Order 8110.49A 추가
- [x] 면접 elevator pitch CLI — 5s / 30s / 60s / hard-line

## 면접 시뮬레이션 통과 기준
- "AI로 비행제어 개선?" 질문 → 5초 안에 "아니오, 이유는 EASA Level 1-2 / FAA incremental..." 응답 가능 (`PITCH_5S`)
- "Skywise / Forge와 뭐가 달라?" → 30초 답변 가능 (`docs/PhaseE/faq/vs-skywise-forge-collins.md`)
- "왜 sklearn?" → "Phase B는 모델 *파이프라인*을 시연. 동일 인터페이스로 PyTorch/TF로 교체 가능"
- "왜 SQLite?" → "동일 ANSI SQL이 Databricks/BigQuery/Athena에서 동작. 클라우드 비용 0으로 설계 검증"

## 6 마일스톤 + 5 페이즈 — 요약
- **M1–M6**: deterministic verification platform (78 tests)
- **Phase A**: 9 Silver / 4 Gold / lineage + drift gate (8 tests)
- **Phase B**: 3 frozen learned components + registry (9 tests)
- **Phase C**: 3 assurance cases + workflow + DO-330 (10 tests)
- **Phase D**: runtime assurance shell + 3 modes + online learning ban (13 tests)
- **Phase E**: README v2 + 6 portfolio docs + 12 tests
- **Total**: 157 tests, all green
