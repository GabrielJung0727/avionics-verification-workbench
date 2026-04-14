# Phase B — Certification Intelligence

> 2026-04-14 strategic pivot 산출물. Notion page 19 와 1:1 매핑.

목표: Phase A의 Silver 위에 **3개의 frozen learned component**를 학습/등록/서빙
파이프라인으로 묶는다. 모든 모델은 **제어 루프 밖**에 머무르며 출력은 `DRAFT,
human-in-the-loop` 으로 표기된다.

## 모델 (v0)
1. **Fault Escape Predictor** — campaign parameter → P(escape)
2. **Engine Telemetry Anomaly Detector** — EngineRaw 스트림 → preventive alert
3. **Trace Gap Intelligence** — git diff 시그널 → 영향 받을 req 후보

## 원칙 (Phase A에서 이어옴)
- frozen-after-training (online learning, RL 금지)
- dataset_version + label_version + approval_state 묶음으로 등록
- split 기준: build / bench / campaign-family / date / hw-rev (랜덤 금지)
- 모든 출력은 DRAFT 표기, assurance card 첨부 (Phase C 연결점)
- 학습 데이터는 Phase A Silver SQL로만 추출

## 폴더
- `architecture/` — registry 레이아웃, dataset/label/approval 묶음 정의
- `assurance-stubs/` — 모델별 assurance card seed (Phase C가 확장)
- `plan/` — 작업 계획, DoD, status

## Exit Criteria
- [ ] Local MLflow-style registry (`evidence/registry/`)
- [ ] dataset_hash + label_version + approval_state 가 model entry에 포함
- [ ] Escape predictor v0 학습/등록/예측 (sklearn GBC)
- [ ] Engine anomaly v0 학습/등록/스코어링 (Isolation Forest)
- [ ] Trace gap intelligence v0 (rule-based baseline + ML 인터페이스 정의)
- [ ] non-random split 강제 (campaign-family / date 기준)
- [ ] orchestrator가 모든 모델의 evaluation 결과를 evidence report에 포함
- [ ] DRAFT 배너 모든 출력에 자동 부착
