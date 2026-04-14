"""Thin proxy to the Phase B intelligence-serving endpoint.

This route does NOT load models in-process. It forwards to the endpoint
documented in tools/intelligence/serving/, configured via the
INTELLIGENCE_ENDPOINT env var. Keeping it a proxy means:

  - the backend stays read-only at the artefact layer
  - all approval-state / online-learning enforcement stays in one place
    (tools/intelligence/runtime/loader.py)
  - swapping the upstream for MLflow / Databricks / SageMaker only
    changes one env var
"""
from __future__ import annotations
import json
import urllib.error
import urllib.request
from typing import Any
from fastapi import APIRouter, HTTPException, Request, status

from ..config import DRAFT_BANNER, INTELLIGENCE_ENDPOINT

router = APIRouter(prefix="/api/predict", tags=["predict"])


def _no_endpoint() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=(
            "INTELLIGENCE_ENDPOINT is not set. Start the local "
            "intelligence server with `python scripts/serve_intelligence.py` "
            "and re-run the backend with INTELLIGENCE_ENDPOINT set, e.g. "
            "`INTELLIGENCE_ENDPOINT=http://127.0.0.1:8081 uvicorn ...`."
        ),
    )


def _proxy(path: str, body: dict) -> dict:
    if not INTELLIGENCE_ENDPOINT:
        raise _no_endpoint()
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        INTELLIGENCE_ENDPOINT + path,
        data=data, method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {"raw": raw}
        raise HTTPException(status_code=e.code, detail=payload)
    except urllib.error.URLError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"upstream unreachable: {e}",
        )


@router.get("/health")
def health():
    if not INTELLIGENCE_ENDPOINT:
        return {"_draft": DRAFT_BANNER, "endpoint": None,
                "available": False}
    try:
        with urllib.request.urlopen(
            INTELLIGENCE_ENDPOINT + "/health", timeout=3,
        ) as r:
            upstream = json.loads(r.read().decode("utf-8"))
        return {"_draft": DRAFT_BANNER, "endpoint": INTELLIGENCE_ENDPOINT,
                "available": True, "upstream": upstream}
    except urllib.error.URLError as e:
        return {"_draft": DRAFT_BANNER, "endpoint": INTELLIGENCE_ENDPOINT,
                "available": False, "error": str(e)}


@router.post("/fault_escape")
async def fault_escape(req: Request):
    body: dict[str, Any] = await req.json()
    return _proxy("/predict/fault_escape", body)


@router.post("/engine_anomaly")
async def engine_anomaly(req: Request):
    body: dict[str, Any] = await req.json()
    return _proxy("/predict/engine_anomaly", body)


@router.post("/trace_gap")
async def trace_gap(req: Request):
    body: dict[str, Any] = await req.json()
    return _proxy("/predict/trace_gap", body)
