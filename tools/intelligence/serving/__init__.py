"""Local model-serving HTTP layer.

Wraps the registered Phase B models behind a tiny ``http.server`` so that
any consumer (CLI, ai_assistant, future web UI) can talk to them via
HTTP — exactly the same way a managed endpoint (MLflow Model Serving,
Databricks Model Serving, Azure ML Endpoint, SageMaker Endpoint) would
be reached. Swapping the local server for a managed one is a one-line
change in the client.

Every response carries the DRAFT banner; every load goes through
``load_with_approval_gate(Mode.SHADOW)`` so Phase D / Phase C invariants
hold here too.
"""
from .server import (
    IntelligenceHandler,
    IntelligenceServer,
    build_server,
)
from .client import (
    IntelligenceClient,
    IntelligenceClientError,
    DEFAULT_ENDPOINT,
)

__all__ = [
    "IntelligenceHandler",
    "IntelligenceServer",
    "build_server",
    "IntelligenceClient",
    "IntelligenceClientError",
    "DEFAULT_ENDPOINT",
]
