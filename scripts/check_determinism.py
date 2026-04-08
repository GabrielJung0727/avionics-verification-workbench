#!/usr/bin/env python3
"""Run the M2 smoke scenario twice with the same seed and compare hashes."""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools" / "sim_py"))
sys.path.insert(0, str(ROOT / "sim" / "scenarios"))

from smoke_scenario import build_smoke  # noqa: E402


def main(duration_ms: int = 200) -> int:
    s1, r1, _, _ = build_smoke(seed=42)
    s2, r2, _, _ = build_smoke(seed=42)
    s1.run_for(duration_ms * 1000)
    s2.run_for(duration_ms * 1000)
    h1, h2 = r1.sha256(), r2.sha256()
    print(f"run1.sha256={h1}")
    print(f"run2.sha256={h2}")
    if h1 != h2:
        print("FAIL: determinism broken")
        return 1
    print("OK: deterministic")
    return 0


if __name__ == "__main__":
    sys.exit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 200))
