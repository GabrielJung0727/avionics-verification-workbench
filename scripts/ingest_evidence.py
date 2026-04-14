#!/usr/bin/env python3
"""CLI for the Phase A data foundation.

Subcommands:
    ingest <report.json> [--bundle <bundle.zip>]
    lineage <run_id>
    drift <report.json>
    gold              -- dump every Gold view as JSON to stdout
"""
from __future__ import annotations
import argparse
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from data_foundation import (  # noqa: E402
    Catalog,
    LakehouseLayout,
    detect_drift,
    ingest_report,
    lineage_for_run,
)

EVIDENCE = ROOT / "evidence"
LAKE = EVIDENCE / "lakehouse"


def _cmd_ingest(args) -> int:
    bundle = Path(args.bundle) if args.bundle else None
    if bundle is None:
        # auto-pick the most recent bundle if any
        candidates = sorted((EVIDENCE / "bundles").glob("bundle-*.zip"))
        bundle = candidates[-1] if candidates else None
    summary = ingest_report(Path(args.report), LAKE, bundle)
    print(f"run_id      : {summary.run_id}")
    print(f"bronze_path : {summary.bronze_path.relative_to(ROOT)}")
    print(f"bundle_used : {summary.bundle_used.name if summary.bundle_used else 'none'}")
    print("rows_per_table:")
    for k, v in summary.rows_per_table.items():
        print(f"  {k}: {v}")
    return 0


def _cmd_lineage(args) -> int:
    out = lineage_for_run(LAKE / "silver" / "catalog.sqlite", args.run_id)
    print(json.dumps(out, indent=2, default=str))
    return 0 if out.get("found") else 1


def _cmd_drift(args) -> int:
    rep = detect_drift(Path(args.report))
    drift_dir = LAKE / "drift"
    drift_dir.mkdir(parents=True, exist_ok=True)
    out_path = drift_dir / "latest.json"
    out_path.write_text(json.dumps(rep.to_dict(), indent=2), encoding="utf-8")
    print(json.dumps(rep.to_dict(), indent=2))
    return 0 if rep.ok else 1


def _cmd_gold(_args) -> int:
    db = LAKE / "silver" / "catalog.sqlite"
    if not db.exists():
        print("no catalog yet; run ingest first")
        return 1
    out: dict = {}
    with sqlite3.connect(str(db)) as conn:
        conn.row_factory = sqlite3.Row
        for view in ("daily_coverage", "weekly_escape_rate",
                     "req_pass_rate", "hil_latency_distribution"):
            try:
                rows = conn.execute(f"SELECT * FROM {view}").fetchall()
                out[view] = [dict(r) for r in rows]
            except sqlite3.OperationalError as e:
                out[view] = {"error": str(e)}
    print(json.dumps(out, indent=2, default=str))
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="ingest_evidence")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_ing = sub.add_parser("ingest")
    p_ing.add_argument("report")
    p_ing.add_argument("--bundle", default=None)
    p_ing.set_defaults(func=_cmd_ingest)

    p_lin = sub.add_parser("lineage")
    p_lin.add_argument("run_id")
    p_lin.set_defaults(func=_cmd_lineage)

    p_drift = sub.add_parser("drift")
    p_drift.add_argument("report")
    p_drift.set_defaults(func=_cmd_drift)

    p_gold = sub.add_parser("gold")
    p_gold.set_defaults(func=_cmd_gold)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
