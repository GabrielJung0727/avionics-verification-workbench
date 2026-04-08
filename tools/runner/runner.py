"""Requirement-based verification runner.

Loads JSON test cases, runs each through the M3 scenario with the given
``world`` parameters, asserts the listed expectations, and produces:

  - per-test result (PASS / FAIL / ERROR)
  - req → test trace
  - gap report (requirements with no test, tests with no requirement)

The runner is deterministic — every test is built from a fresh ``M3World``
seeded by the JSON file. Two runs with the same set of files yield byte-equal
result hashes (M2 determinism guarantee carries over).
"""
from __future__ import annotations
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SIM_PY = ROOT / "tools" / "sim_py"
SCEN = ROOT / "sim" / "scenarios"
for p in (SIM_PY, SCEN):
    s = str(p)
    if s not in sys.path:
        sys.path.insert(0, s)

from m3_scenario import M3World, build_m3       # noqa: E402
from avx_sim.afdx import AfdxFaults              # noqa: E402
from avx_sim.health_monitor import HmEvent       # noqa: E402
from avx_sim.messages import FccMode, AlertLevel  # noqa: E402


@dataclass
class TestCase:
    id: str
    req: list[str]
    description: str
    duration_ms: int
    world: dict
    expects: dict
    source_path: str = ""


@dataclass
class TestResult:
    id: str
    req: list[str]
    result: str             # PASS | FAIL | ERROR
    failures: list[str] = field(default_factory=list)
    recorder_sha256: str = ""
    fcc_mode_terminal: str = ""
    hm_event_total: int = 0


def load_test_case(path: str | Path) -> TestCase:
    p = Path(path)
    data = json.loads(p.read_text(encoding="utf-8"))
    return TestCase(
        id=data["id"],
        req=list(data.get("req", [])),
        description=data.get("description", ""),
        duration_ms=int(data.get("duration_ms", 200)),
        world=dict(data.get("world", {})),
        expects=dict(data.get("expects", {})),
        source_path=str(p),
    )


def discover_test_cases(directory: str | Path) -> list[TestCase]:
    out: list[TestCase] = []
    for path in sorted(Path(directory).glob("*.json")):
        out.append(load_test_case(path))
    return out


def _build_world(spec: dict) -> M3World:
    w = M3World(seed=int(spec.get("seed", 42)))
    if "ias_drift_per_tick" in spec:
        w.ias_drift_per_tick = float(spec["ias_drift_per_tick"])
    if "force_dual_fault_at_us" in spec:
        w.force_dual_fault_at_us = int(spec["force_dual_fault_at_us"])
    if "n1_at_t1s" in spec:
        w.n1_at_t1s = float(spec["n1_at_t1s"])
    if "egt_at_t1s" in spec:
        w.egt_at_t1s = float(spec["egt_at_t1s"])
    if "afdx_delay_us" in spec:
        w.afdx_faults = AfdxFaults(delay_us=int(spec["afdx_delay_us"]))
    return w


def _check(expects: dict, sched, rec, hm, handles) -> list[str]:
    failures: list[str] = []

    if "fcc_mode_terminal" in expects:
        actual = handles["fcc"].mode.name
        if actual != expects["fcc_mode_terminal"]:
            failures.append(
                f"fcc_mode_terminal expected={expects['fcc_mode_terminal']} got={actual}"
            )

    if "hm_event_min_total" in expects:
        if len(hm.events) < int(expects["hm_event_min_total"]):
            failures.append(
                f"hm_event_min_total expected>={expects['hm_event_min_total']} got={len(hm.events)}"
            )

    if "hm_events_min" in expects:
        for code, minimum in expects["hm_events_min"].items():
            try:
                want = HmEvent(code)
            except ValueError:
                failures.append(f"unknown hm event code: {code}")
                continue
            actual = hm.count(want)
            if actual < int(minimum):
                failures.append(
                    f"hm_events_min[{code}] expected>={minimum} got={actual}"
                )

    if "engine_state_min" in expects:
        params, _ = handles["eng"].step_dummy() if hasattr(handles["eng"], "step_dummy") else (None, None)
        # use stored worst latched
        worst = max(handles["eng"].latched.values(), default=AlertLevel.ADVISORY)
        want = AlertLevel[expects["engine_state_min"]]
        if worst < want:
            failures.append(
                f"engine_state_min expected>={want.name} got={worst.name}"
            )

    if "msg_ids_present" in expects:
        present = {r[2] for r in rec.records}
        for m in expects["msg_ids_present"]:
            if m not in present:
                failures.append(f"missing msg id: {m}")

    return failures


def run_test_case(tc: TestCase) -> TestResult:
    try:
        world = _build_world(tc.world)
        sched, rec, hm, handles = build_m3(world)
        sched.run_for(tc.duration_ms * 1000)
        failures = _check(tc.expects, sched, rec, hm, handles)
        result = "PASS" if not failures else "FAIL"
        return TestResult(
            id=tc.id, req=list(tc.req), result=result,
            failures=failures,
            recorder_sha256=rec.sha256(),
            fcc_mode_terminal=handles["fcc"].mode.name,
            hm_event_total=len(hm.events),
        )
    except Exception as e:
        return TestResult(
            id=tc.id, req=list(tc.req), result="ERROR",
            failures=[f"{type(e).__name__}: {e}"],
        )


def run_all(test_cases: list[TestCase]) -> list[TestResult]:
    return [run_test_case(tc) for tc in test_cases]


def build_trace(results: list[TestResult]) -> dict[str, list[str]]:
    trace: dict[str, list[str]] = {}
    for r in results:
        for req in r.req:
            trace.setdefault(req, []).append(r.id)
    return {k: sorted(v) for k, v in sorted(trace.items())}


def build_gap_report(test_cases: list[TestCase], req_csv: str | Path) -> dict:
    """Find requirements without tests, tests without requirements."""
    import csv
    req_ids: set[str] = set()
    with open(req_csv, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            rid = row.get("id", "")
            if rid:
                req_ids.add(rid)
    covered: set[str] = set()
    orphan_tests: list[str] = []
    for tc in test_cases:
        if not tc.req:
            orphan_tests.append(tc.id)
        for r in tc.req:
            covered.add(r)
    return {
        "requirements_total": len(req_ids),
        "requirements_covered": sorted(covered & req_ids),
        "requirements_uncovered": sorted(req_ids - covered),
        "tests_without_requirement": orphan_tests,
        "tests_referencing_unknown_req": sorted(
            {r for tc in test_cases for r in tc.req if r not in req_ids}
        ),
    }
