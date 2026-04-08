#!/usr/bin/env python3
"""Verify an evidence bundle by recomputing every file's sha256 and
comparing against the embedded manifest.

Usage: python scripts/replay_bundle.py <bundle.zip>
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from evidence_bundler import verify_bundle  # noqa: E402


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: replay_bundle.py <bundle.zip>")
        return 2
    zip_path = Path(argv[1])
    if not zip_path.exists():
        print(f"not found: {zip_path}")
        return 2
    report = verify_bundle(zip_path)
    m = report["manifest"]
    print(f"run_id        : {m['run_id']}")
    print(f"created_at    : {m['created_at']}")
    print(f"git_sha       : {m['build']['git_sha']}")
    print(f"files         : {len(m['files'])}")
    summary = m.get("summary", {})
    if summary:
        print("summary:")
        for k, v in summary.items():
            print(f"  {k}: {v}")
    if report["ok"]:
        print("\nverify: OK (all sha256 hashes match manifest)")
        return 0
    print("\nverify: FAIL")
    for mism in report["mismatches"]:
        print(f"  - {mism}")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
