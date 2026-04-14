"""Phase A enterprise data foundation.

Reads `evidence/verification-report.json` (+ associated bundles) and turns
them into a SQLite-backed Bronze / Silver / Gold lakehouse under
`evidence/lakehouse/`. Designed so the same SQL maps 1:1 onto Databricks
SQL, BigQuery, or Athena once a real cloud is wired in.
"""
from .storage import LakehouseLayout, content_address, sha256_of_path
from .catalog import (
    Catalog,
    SCHEMA_VERSION,
    create_silver_schema,
    create_gold_views,
)
from .ingest import ingest_report, IngestSummary
from .lineage import lineage_for_run
from .drift import detect_drift, DriftReport
from .bus_parser import parse_bus_recording

__all__ = [
    "LakehouseLayout",
    "Catalog",
    "SCHEMA_VERSION",
    "create_silver_schema",
    "create_gold_views",
    "ingest_report",
    "IngestSummary",
    "lineage_for_run",
    "detect_drift",
    "DriftReport",
    "parse_bus_recording",
    "content_address",
    "sha256_of_path",
]
