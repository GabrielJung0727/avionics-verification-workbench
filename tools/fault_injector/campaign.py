"""Fault injection campaign loader and runner.

Campaigns are JSON files describing one or more faults to apply to the M3
scenario. Result classification follows ``docs/M4/fault-injection/fault-model.md``:

  detected   — HM raised an event tied to the fault
  mitigated  — system entered a degraded mode (FCC ALTERNATE/DIRECT)
  escaped    — fault produced no observable response

Sample campaign:
{
  "id": "FC-001",
  "description": "Air data drift + AFDX delay",
  "seed": 7,
  "duration_ms": 2000,
  "faults": [
    {"type": "ias_drift", "rate_per_tick": 1.5},
    {"type": "afdx_delay", "delay_us": 80000},
    {"type": "force_dual_fault_at_us", "value": 1000000}
  ],
  "expectations": {
    "hm_events_min": {"LANE_DISAGREE": 0},
    "fcc_mode_terminal": "DIRECT"
  }
}
"""
from __future__ import annotations
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Make sim/scenarios importable when invoked from anywhere
ROOT = Path(__file__).resolve().parents[2]
SCEN = ROOT / "sim" / "scenarios"
SIM_PY = ROOT / "tools" / "sim_py"
for p in (SIM_PY, SCEN):
    s = str(p)
    if s not in sys.path:
        sys.path.insert(0, s)

from m3_scenario import M3World, build_m3   # noqa: E402
from avx_sim.afdx import AfdxFaults          # noqa: E402
from avx_sim.health_monitor import HmEvent   # noqa: E402
from avx_sim.messages import FccMode         # noqa: E402


@dataclass
class FaultCampaign:
    id: str
    description: str
    seed: int
    duration_ms: int
    faults: list[dict]
    expectations: dict = field(default_factory=dict)


def load_campaign(path: str | Path) -> FaultCampaign:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return FaultCampaign(
        id=data["id"],
        description=data.get("description", ""),
        seed=int(data.get("seed", 0)),
        duration_ms=int(data.get("duration_ms", 200)),
        faults=list(data.get("faults", [])),
        expectations=dict(data.get("expectations", {})),
    )


def _world_from_faults(seed: int, faults: list[dict]) -> M3World:
    world = M3World(seed=seed)
    for f in faults:
        t = f["type"]
        if t == "ias_drift":
            world.ias_drift_per_tick = float(f["rate_per_tick"])
        elif t == "force_dual_fault_at_us":
            world.force_dual_fault_at_us = int(f["value"])
        elif t == "n1_at_t1s":
            world.n1_at_t1s = float(f["value"])
        elif t == "egt_at_t1s":
            world.egt_at_t1s = float(f["value"])
        elif t == "afdx_delay":
            world.afdx_faults = AfdxFaults(delay_us=int(f["delay_us"]))
        elif t == "afdx_drop_every_n":
            world.afdx_faults = AfdxFaults(drop_every_n=int(f["n"]))
        else:
            raise ValueError(f"unknown fault type: {t}")
    return world


def run_campaign(campaign: FaultCampaign) -> dict:
    world = _world_from_faults(campaign.seed, campaign.faults)
    sched, rec, hm, handles = build_m3(world)
    sched.run_for(campaign.duration_ms * 1000)

    summary: dict = {
        "id": campaign.id,
        "duration_ms": campaign.duration_ms,
        "records": len(rec),
        "hm_event_total": len(hm.events),
        "hm_event_counts": {},
        "fcc_mode_terminal": handles["fcc"].mode.name,
        "recorder_sha256": rec.sha256(),
    }
    for ev in hm.events:
        summary["hm_event_counts"].setdefault(ev.code.value, 0)
        summary["hm_event_counts"][ev.code.value] += 1

    # classification
    detected = any(c > 0 for c in summary["hm_event_counts"].values())
    mitigated = handles["fcc"].mode in (FccMode.ALTERNATE, FccMode.DIRECT)
    if detected and mitigated:
        cls = "detected_and_mitigated"
    elif detected:
        cls = "detected"
    elif mitigated:
        cls = "mitigated_only"
    else:
        cls = "escaped"
    summary["classification"] = cls

    # expectation check
    expect = campaign.expectations
    failures: list[str] = []
    for code, minimum in expect.get("hm_events_min", {}).items():
        if summary["hm_event_counts"].get(code, 0) < minimum:
            failures.append(f"hm_events_min[{code}] expected>={minimum} "
                            f"got={summary['hm_event_counts'].get(code, 0)}")
    if "fcc_mode_terminal" in expect:
        if summary["fcc_mode_terminal"] != expect["fcc_mode_terminal"]:
            failures.append(f"fcc_mode_terminal expected="
                            f"{expect['fcc_mode_terminal']} "
                            f"got={summary['fcc_mode_terminal']}")
    summary["expectation_failures"] = failures
    summary["pass"] = (cls != "escaped") and (not failures)
    return summary
