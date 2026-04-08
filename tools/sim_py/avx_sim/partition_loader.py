"""Tiny partition-table loader.

Format (one partition per line, comments start with ``#``):

    id  period_ms  budget_us  offset_ms  criticality

Whitespace separated. Periods/offsets are given in ms for human readability,
budget in microseconds. Returns a list of dicts ready to feed Partition().
"""
from __future__ import annotations
from pathlib import Path


REQUIRED_COLS = ("id", "period_ms", "budget_us", "offset_ms", "criticality")


def load_partition_table(path: str | Path) -> list[dict]:
    p = Path(path)
    out: list[dict] = []
    for raw in p.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) != 5:
            raise ValueError(f"bad partition row: {raw!r}")
        pid, period_ms, budget_us, offset_ms, crit = parts
        out.append({
            "id": pid,
            "period_us": int(period_ms) * 1000,
            "budget_us": int(budget_us),
            "offset_us": int(offset_ms) * 1000,
            "criticality": crit,
        })
    return out
