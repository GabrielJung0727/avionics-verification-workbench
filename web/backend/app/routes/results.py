"""Read-only routes over evidence/verification-report.json + bundles."""
from __future__ import annotations
import os
from datetime import datetime, timezone
from fastapi import APIRouter

from ..config import BUNDLES_DIR, DRAFT_BANNER, SHADOW_REPORT
from ..dependencies import load_report, safe_json_read

router = APIRouter(prefix="/api/results", tags=["results"])


def _draft(payload: dict) -> dict:
    return {"_draft": DRAFT_BANNER, **payload}


@router.get("/summary")
def get_summary():
    """High-level numbers used by the frontend /results page."""
    rep = load_report()
    return _draft({"summary": rep.get("summary", {})})


@router.get("/tests")
def list_tests():
    """Per-test outcomes (verification runner output)."""
    rep = load_report()
    return _draft({"results": rep.get("results", [])})


@router.get("/campaigns")
def list_campaigns():
    rep = load_report()
    return _draft({"campaigns": rep.get("campaigns", [])})


@router.get("/mcdc")
def get_mcdc():
    rep = load_report()
    return _draft({"mcdc": rep.get("mcdc", {})})


@router.get("/coverage")
def get_coverage():
    rep = load_report()
    return _draft({"coverage": rep.get("coverage", {})})


@router.get("/hf")
def get_hf():
    rep = load_report()
    return _draft({"hf_findings": rep.get("hf_findings", [])})


@router.get("/hil")
def get_hil():
    rep = load_report()
    return _draft({"hil_runs": rep.get("hil_runs", [])})


@router.get("/trace")
def get_trace():
    rep = load_report()
    return _draft({
        "trace": rep.get("trace", {}),
        "gap": rep.get("gap", {}),
    })


@router.get("/shadow")
def get_shadow():
    """Latest Phase D shadow-run report."""
    if not SHADOW_REPORT.exists():
        return _draft({"available": False, "report": None})
    return _draft({"available": True, "report": safe_json_read(SHADOW_REPORT)})


@router.get("/bundles")
def list_bundles():
    """Discoverable evidence bundle archives."""
    if not BUNDLES_DIR.exists():
        return _draft({"bundles": []})
    items = []
    for p in sorted(BUNDLES_DIR.glob("bundle-*.zip")):
        st = p.stat()
        items.append({
            "name": p.name,
            "size_bytes": st.st_size,
            "modified_iso": datetime.fromtimestamp(
                st.st_mtime, tz=timezone.utc
            ).isoformat(timespec="seconds"),
        })
    return _draft({"bundles": items})
