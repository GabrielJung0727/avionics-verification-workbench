"""Phase B certification intelligence layer.

Three frozen learned components served from a local model registry:
  - fault_escape_predictor
  - engine_anomaly_detector
  - trace_gap_intel

All artifacts ship with dataset_hash + label_version + approval_state so the
metadata story stays intact when the registry adapter is swapped for MLflow,
Databricks, Azure ML, or SageMaker.
"""
from .registry import (
    LocalRegistry,
    ModelRecord,
    DatasetMeta,
    ModelMeta,
    DRAFT_BANNER,
)
from .serving import (
    IntelligenceClient,
    IntelligenceClientError,
    IntelligenceServer,
    build_server,
)

__all__ = [
    "LocalRegistry",
    "ModelRecord",
    "DatasetMeta",
    "ModelMeta",
    "DRAFT_BANNER",
    "IntelligenceClient",
    "IntelligenceClientError",
    "IntelligenceServer",
    "build_server",
]
