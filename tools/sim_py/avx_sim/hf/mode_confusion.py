"""Mode-confusion scenario library (M5).

Each scenario drives the M3 world into a corner where pilot-in-the-loop
confusion is plausible, then asserts that the display either makes the
current mode unambiguous or flags a risk.

This module is intentionally side-effect free at import time so the HF
evaluator and the verification runner can enumerate scenarios without
touching the scheduler.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

from ..messages import FccMode


@dataclass(frozen=True)
class ModeConfusionScenario:
    id: str
    description: str
    expected_terminal_mode: FccMode
    expected_mode_history_min: int    # number of distinct modes expected


def _build_world(**kw):
    # Local import to avoid pulling sim/scenarios at module import time.
    import sys
    from pathlib import Path
    root = Path(__file__).resolve().parents[4]
    scen = root / "sim" / "scenarios"
    if str(scen) not in sys.path:
        sys.path.insert(0, str(scen))
    from m3_scenario import M3World   # noqa: E402
    return M3World(**kw)


def run_mode_confusion(scenario: ModeConfusionScenario) -> dict:
    """Execute the scenario and return an inspection dict."""
    import sys
    from pathlib import Path
    root = Path(__file__).resolve().parents[4]
    scen = root / "sim" / "scenarios"
    if str(scen) not in sys.path:
        sys.path.insert(0, str(scen))
    from m3_scenario import build_m3     # noqa: E402

    if scenario.id == "MC-01":
        world = _build_world(force_dual_fault_at_us=50_000)
        duration_ms = 250
    elif scenario.id == "MC-02":
        # Degraded engine state while FCC still thinks it's NORMAL
        world = _build_world(n1_at_t1s=104.0)
        duration_ms = 2_000
    elif scenario.id == "MC-03":
        # Three same-level alerts fighting for attention
        world = _build_world(n1_at_t1s=104.0, egt_at_t1s=905.0)
        duration_ms = 2_000
    else:
        raise ValueError(f"unknown scenario {scenario.id}")

    sched, rec, hm, h = build_m3(world)
    sched.run_for(duration_ms * 1000)
    fcc = h["fcc"]
    dsp = h["dsp"]
    modes_seen = {m for _, m in dsp._mode_history}
    return {
        "id": scenario.id,
        "terminal_mode": fcc.mode.name,
        "modes_seen": sorted(m.name for m in modes_seen),
        "distinct_mode_count": len(modes_seen),
        "mode_latency_violations": dsp.mode_latency_violations,
        "records": len(rec),
        "terminal_mode_matches": fcc.mode == scenario.expected_terminal_mode,
        "history_depth_ok": len(modes_seen) >= scenario.expected_mode_history_min,
    }


MODE_CONFUSION_SCENARIOS: list[ModeConfusionScenario] = [
    ModeConfusionScenario(
        id="MC-01",
        description="Dual sensor fault forces DIRECT; pilot must see the change",
        expected_terminal_mode=FccMode.DIRECT,
        expected_mode_history_min=2,  # OFF/NORMAL -> DIRECT
    ),
    ModeConfusionScenario(
        id="MC-02",
        description="Engine latched warning while FCC stays NORMAL",
        expected_terminal_mode=FccMode.NORMAL,
        expected_mode_history_min=1,
    ),
    ModeConfusionScenario(
        id="MC-03",
        description="Multiple simultaneous alerts — prioritization under pressure",
        expected_terminal_mode=FccMode.NORMAL,
        expected_mode_history_min=1,
    ),
]
