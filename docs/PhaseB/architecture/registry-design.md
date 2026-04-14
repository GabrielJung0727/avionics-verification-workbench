# Local Model Registry (Phase B)

## 목적
MLflow / Databricks Model Registry / Azure ML Registry / SageMaker Model
Registry 의 **공통 필드만 가진** 로컬 implementation. 클라우드 이전 시 어댑터만
바꾸면 동일 메타데이터 묶음이 그대로 옮겨간다.

## 디렉터리 레이아웃

```
evidence/
└── registry/
    ├── manifest.json                           # registry-wide index
    └── <model_name>/
        └── <version>/
            ├── model.pkl                       # binary artifact (joblib/pickle)
            ├── model_card.json                 # what / why / for whom
            ├── assurance_stub.md               # Phase C extension hook
            ├── dataset.json                    # dataset_hash + split + label_version
            ├── metrics.json                    # holdout scores + confidence
            └── meta.json                       # frozen=true, approval_state, git_sha
```

## meta.json 필수 필드
```json
{
  "model_name": "fault_escape_predictor",
  "version": "v0.1.0",
  "created_at": "ISO-8601",
  "git_sha": "...",
  "frozen": true,
  "approval_state": "auto-generated",        // -> reviewer-confirmed -> board-approved
  "dataset_version": "sweep-2026-04-14-...",
  "label_version": "oracle-v1",
  "training_seed": 42,
  "intended_use": "verification prioritization (DRAFT)",
  "out_of_scope": [
    "any control-loop decision",
    "online learning",
    "primary FCC authority"
  ]
}
```

## dataset.json 필수 필드
- `dataset_hash` — sha256 of training feature matrix bytes
- `n_train`, `n_holdout`
- `split_strategy` — campaign-family / date / hw-rev (NEVER random)
- `split_key` — actual key used (e.g. "campaign_family")
- `feature_columns` — list of names
- `label_column` — single name
- `label_version` — vocabulary identifier

## metrics.json
- For classifiers: `auc`, `precision`, `recall`, `f1`, `confusion_matrix`
- For anomaly: `recall_at_fpr_1pct`, `false_alarm_rate`
- For trace gap: `precision_at_k`, `mrr`
- All fields include `_draft: true` so consumers can't accidentally treat them as certified

## Why local pickle and not MLflow proper

For this milestone we ship **the metadata story end-to-end** without bringing
in MLflow as a dependency. The registry adapter is one file; swapping it for
``mlflow.register_model`` is a 30-line change. The metadata schema stays
identical, so the assurance evidence carries over unchanged.
