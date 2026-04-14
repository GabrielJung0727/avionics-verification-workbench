#!/usr/bin/env python3
"""Print the project elevator pitch.

Usage:
    python scripts/elevator_pitch.py [5s|30s|60s|hard-line|all]
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from portfolio import (  # noqa: E402
    HARD_LINE,
    PITCH_30S,
    PITCH_5S,
    PITCH_60S,
)


def main(argv: list[str]) -> int:
    arg = argv[1] if len(argv) > 1 else "all"
    if arg == "all":
        print("# Hard line\n" + HARD_LINE + "\n")
        print("# 5-second pitch\n" + PITCH_5S + "\n")
        print("# 30-second pitch\n" + PITCH_30S + "\n")
        print("# 60-second pitch\n" + PITCH_60S + "\n")
        return 0
    table = {"5s": PITCH_5S, "30s": PITCH_30S, "60s": PITCH_60S,
             "hard-line": HARD_LINE}
    if arg not in table:
        print(f"unknown length '{arg}'. expected: 5s | 30s | 60s | hard-line | all")
        return 2
    print(table[arg])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
