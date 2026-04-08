#!/usr/bin/env python3
"""Sanity-check requirements.csv: unique IDs, required fields, allowed enums."""
from __future__ import annotations
import csv
import sys
from pathlib import Path

REQUIRED = ["id", "level", "text", "rationale", "source", "criticality", "verify_method"]
LEVELS = {"SYS", "HLR", "LLR"}
CRIT = {"High", "Med", "Low"}


def main(path: str) -> int:
    p = Path(path)
    if not p.exists():
        print(f"ERR: not found: {path}")
        return 2
    rows = list(csv.DictReader(p.open(encoding="utf-8")))
    errors: list[str] = []
    seen: set[str] = set()
    for i, row in enumerate(rows, start=2):  # +1 header, +1 to be 1-indexed
        for f in REQUIRED:
            if not row.get(f):
                errors.append(f"line {i}: missing field {f}")
        rid = row.get("id", "")
        if rid in seen:
            errors.append(f"line {i}: duplicate id {rid}")
        seen.add(rid)
        if row.get("level") not in LEVELS:
            errors.append(f"line {i}: bad level {row.get('level')}")
        if row.get("criticality") not in CRIT:
            errors.append(f"line {i}: bad criticality {row.get('criticality')}")

    sys_count = sum(1 for r in rows if r.get("level") == "SYS")
    hlr_count = sum(1 for r in rows if r.get("level") == "HLR")
    print(f"rows={len(rows)} SYS={sys_count} HLR={hlr_count}")

    if sys_count < 30:
        errors.append(f"SYS count {sys_count} < 30 (M1 DoD)")
    if hlr_count < 20:
        errors.append(f"HLR count {hlr_count} < 20 (M1 DoD)")

    if errors:
        print("FAIL")
        for e in errors:
            print(" -", e)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "docs/M1/requirements/requirements.csv"))
