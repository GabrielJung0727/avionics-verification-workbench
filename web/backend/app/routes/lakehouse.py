"""Read-only routes over the Phase A SQLite lakehouse."""
from __future__ import annotations
import sys
from fastapi import APIRouter, HTTPException, status
from pathlib import Path

from ..config import DRAFT_BANNER, LAKEHOUSE_DB, REPO_ROOT
from ..dependencies import lakehouse_conn

# Allow Phase A's lineage helper to be reused — same rows as the CLI.
_TOOLS = REPO_ROOT / "tools"
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

router = APIRouter(prefix="/api/lakehouse", tags=["lakehouse"])


def _draft(payload: dict) -> dict:
    return {"_draft": DRAFT_BANNER, **payload}


# Whitelist Gold views to keep the surface read-only and predictable.
GOLD_VIEWS = {
    "daily_coverage",
    "weekly_escape_rate",
    "req_pass_rate",
    "hil_latency_distribution",
}


@router.get("/health")
def health():
    return _draft({"db_present": LAKEHOUSE_DB.exists(),
                   "path": str(LAKEHOUSE_DB.relative_to(REPO_ROOT))})


@router.get("/gold")
def list_gold_views():
    return _draft({"views": sorted(GOLD_VIEWS)})


@router.get("/gold/{view}")
def query_gold_view(view: str, limit: int = 200):
    if view not in GOLD_VIEWS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"unknown gold view '{view}'",
        )
    if not 1 <= limit <= 1000:
        raise HTTPException(400, "limit out of range (1..1000)")
    with lakehouse_conn() as conn:
        rows = [dict(r) for r in conn.execute(
            f"SELECT * FROM {view} LIMIT ?", (limit,)
        ).fetchall()]
    return _draft({"view": view, "row_count": len(rows), "rows": rows})


@router.get("/runs")
def list_runs(limit: int = 50):
    """Latest verification runs from the run_manifest table."""
    if not 1 <= limit <= 1000:
        raise HTTPException(400, "limit out of range (1..1000)")
    with lakehouse_conn() as conn:
        rows = [dict(r) for r in conn.execute(
            """SELECT run_id, ingested_at, git_sha, git_dirty,
                      bench_id, operator, env_profile, bronze_sha256
               FROM run_manifest
               ORDER BY ingested_at DESC
               LIMIT ?""",
            (limit,),
        ).fetchall()]
    return _draft({"runs": rows})


@router.get("/runs/{run_id}/lineage")
def run_lineage(run_id: str):
    """Full lineage record for a single run_id (mirrors the CLI)."""
    from data_foundation.lineage import lineage_for_run  # type: ignore
    out = lineage_for_run(LAKEHOUSE_DB, run_id)
    if not out.get("found"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"run_id not found: {run_id}",
        )
    out["_draft"] = DRAFT_BANNER
    return out
