"""Backend configuration — all paths resolve relative to the repo root.

The backend is intentionally **read-only**. It exposes evidence /
lakehouse / registry artefacts produced by the Python orchestrator
(``scripts/run_verification.py``) and proxies prediction calls to the
Phase B intelligence endpoint (``scripts/serve_intelligence.py``). It
never triggers a verification run on its own — those are heavy,
deterministic jobs that belong in CI.
"""
from __future__ import annotations
import os
from pathlib import Path

# ``web/backend/app/config.py`` -> repo root is parents[3]
REPO_ROOT = Path(__file__).resolve().parents[3]

EVIDENCE_DIR = REPO_ROOT / "evidence"
REPORT_PATH = EVIDENCE_DIR / "verification-report.json"
BUNDLES_DIR = EVIDENCE_DIR / "bundles"
LAKEHOUSE_DB = EVIDENCE_DIR / "lakehouse" / "silver" / "catalog.sqlite"
REGISTRY_DIR = EVIDENCE_DIR / "registry"
ASSURANCE_DIR = EVIDENCE_DIR / "assurance"
SHADOW_REPORT = EVIDENCE_DIR / "phaseD-shadow-report.json"

# Optional external intelligence endpoint to proxy /api/predict/* calls to.
# When unset the predict routes return 503 with a friendly hint.
INTELLIGENCE_ENDPOINT = os.environ.get(
    "INTELLIGENCE_ENDPOINT", ""
).rstrip("/")

# CORS — defaults to local Next.js dev server. Override via comma list.
ALLOWED_ORIGINS = [
    o.strip()
    for o in os.environ.get(
        "BACKEND_ALLOWED_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    if o.strip()
]

DRAFT_BANNER = (
    "DRAFT - read-only API surface over learning-grade artefacts. "
    "Not certification evidence. See docs/regulatory/disclaimer.md."
)
