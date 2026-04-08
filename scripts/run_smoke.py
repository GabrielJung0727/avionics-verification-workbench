#!/usr/bin/env python3
"""Run the M2 smoke scenario and print a summary + recorder hash."""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools" / "sim_py"))
sys.path.insert(0, str(ROOT / "sim" / "scenarios"))

from smoke_scenario import build_smoke  # noqa: E402


def main(duration_ms: int = 200) -> int:
    sched, rec, hm, _ = build_smoke()
    sched.run_for(duration_ms * 1000)
    print(f"records={len(rec)}  hm_events={len(hm.events)}")
    print(f"recorder.sha256={rec.sha256()}")
    msg_ids = sorted({r[2] for r in rec.records})
    print(f"msg_ids={msg_ids}")
    return 0


if __name__ == "__main__":
    sys.exit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 200))
