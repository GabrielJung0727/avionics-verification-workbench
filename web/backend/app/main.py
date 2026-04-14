"""FastAPI app — read-only API surface over the avionics-verification
workbench evidence + lakehouse + registry, plus a thin proxy to the Phase B
intelligence endpoint.

The backend never mutates the workbench. It serves what the Python
orchestrator (``scripts/run_verification.py``) has already written.
"""
from __future__ import annotations
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import (
    ALLOWED_ORIGINS,
    DRAFT_BANNER,
    INTELLIGENCE_ENDPOINT,
    LAKEHOUSE_DB,
    REGISTRY_DIR,
    REPORT_PATH,
)
from .routes import lakehouse, predict, registry, results


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.boot_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    yield


app = FastAPI(
    title="Avionics Verification Workbench — Web API",
    description=(
        "Read-only API over evidence/, lakehouse, and the Phase B "
        "model registry. All responses include a DRAFT marker."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return JSONResponse({
        "_draft": DRAFT_BANNER,
        "service": "avionics-verification-workbench-api",
        "version": app.version,
        "routes": [
            "/api/health",
            "/api/results/summary",
            "/api/results/tests",
            "/api/results/campaigns",
            "/api/results/mcdc",
            "/api/results/coverage",
            "/api/results/hf",
            "/api/results/hil",
            "/api/results/trace",
            "/api/results/shadow",
            "/api/results/bundles",
            "/api/lakehouse/health",
            "/api/lakehouse/gold",
            "/api/lakehouse/gold/{view}",
            "/api/lakehouse/runs",
            "/api/lakehouse/runs/{run_id}/lineage",
            "/api/registry/models",
            "/api/registry/models/{name}/{version}",
            "/api/predict/health",
            "/api/predict/fault_escape",
            "/api/predict/engine_anomaly",
            "/api/predict/trace_gap",
        ],
    })


@app.get("/api/health")
def health():
    return {
        "_draft": DRAFT_BANNER,
        "ok": True,
        "report_present": REPORT_PATH.exists(),
        "lakehouse_present": LAKEHOUSE_DB.exists(),
        "registry_present": REGISTRY_DIR.exists(),
        "intelligence_endpoint": INTELLIGENCE_ENDPOINT or None,
    }


app.include_router(results.router)
app.include_router(lakehouse.router)
app.include_router(registry.router)
app.include_router(predict.router)
