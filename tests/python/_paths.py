"""Path bootstrap so unittest can import avx_sim and the smoke scenario
without requiring an installed package."""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SIM_PY = ROOT / "tools" / "sim_py"
SCENARIOS = ROOT / "sim" / "scenarios"

for p in (SIM_PY, SCENARIOS):
    s = str(p)
    if s not in sys.path:
        sys.path.insert(0, s)
