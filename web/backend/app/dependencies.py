"""Shared FastAPI dependencies."""
from __future__ import annotations
import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from fastapi import HTTPException, status

from .config import LAKEHOUSE_DB, REPORT_PATH


def load_report() -> dict:
    if not REPORT_PATH.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "verification-report.json not found. Run "
                "`python scripts/run_verification.py` first."
            ),
        )
    return json.loads(REPORT_PATH.read_text(encoding="utf-8"))


@contextmanager
def lakehouse_conn():
    if not LAKEHOUSE_DB.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "lakehouse catalog.sqlite not found. Run "
                "`python scripts/run_verification.py` to populate it."
            ),
        )
    conn = sqlite3.connect(str(LAKEHOUSE_DB))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def safe_json_read(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"corrupted JSON at {path.name}: {e}",
        )
