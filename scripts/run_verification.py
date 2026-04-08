#!/usr/bin/env python3
"""M4 verification orchestrator.

Runs every JSON test case under ``tools/runner/test_cases``, every fault
campaign under ``tools/fault_injector/campaigns``, and produces:

  - per-test PASS/FAIL summary
  - req → test trace
  - gap report against ``docs/M1/requirements/requirements.csv``
  - MC/DC report for the designated decisions
  - line-coverage report over avx_sim/

Writes a JSON summary to ``evidence/m4-verification-report.json``.
"""
from __future__ import annotations
import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "sim_py"))
sys.path.insert(0, str(ROOT / "sim" / "scenarios"))

from runner import (  # noqa: E402
    discover_test_cases,
    run_all,
    build_trace,
    build_gap_report,
)
from fault_injector import load_campaign, run_campaign  # noqa: E402
from coverage_reporter import LineCoverage              # noqa: E402
from avx_sim.mcdc import McdcTracker                    # noqa: E402

REQ_CSV = ROOT / "docs" / "M1" / "requirements" / "requirements.csv"
TEST_DIR = ROOT / "tools" / "runner" / "test_cases"
CAMP_DIR = ROOT / "tools" / "fault_injector" / "campaigns"
COV_ROOT = (ROOT / "tools" / "sim_py" / "avx_sim").resolve()
EVIDENCE = ROOT / "evidence"


def _exercise_mcdc_decisions() -> None:
    """Drive the MC/DC-instrumented decisions through input combinations
    that target every per-condition independence pair. This is the verification
    counterpart to a "decision unit test set"."""
    from avx_sim.health_monitor import HealthMonitor
    from avx_sim.messages import AirData, Attitude, EngineRaw, Freshness
    from avx_sim.modules import EngineInterface, Fcc

    hm = HealthMonitor()
    fcc = Fcc(hm=hm)
    air_ok = AirData(0, 250, 0, 0, Freshness.OK)
    air_stale = AirData(0, 250, 0, 0, Freshness.STALE)
    att_ok = Attitude(0, 0, 0, 0, Freshness.OK)
    att_stale = Attitude(0, 0, 0, 0, Freshness.STALE)
    # 6 carefully chosen rows giving every condition an independent flip pair
    for air, att in [
        (None, None),
        (air_ok, None),
        (None, att_ok),
        (air_ok, att_ok),
        (air_stale, att_ok),
        (air_ok, att_stale),
    ]:
        fcc._validate(air, att, now_us=0)

    from avx_sim.messages import AlertLevel
    eng = EngineInterface(hm=HealthMonitor())
    # 4 carefully chosen rows giving the latch_promote (c1, c2) decision
    # every independence pair (TT, TF, FT, FF).
    eng.latched["x"] = AlertLevel.ADVISORY
    eng._update_latch("x", AlertLevel.WARNING)        # c1=T c2=T  out=T
    eng.latched["x"] = AlertLevel.WARNING
    eng._update_latch("x", AlertLevel.WARNING)        # c1=F c2=T  out=F
    eng.latched["x"] = AlertLevel.ADVISORY
    eng._update_latch("x", AlertLevel.CAUTION)        # c1=T c2=F  out=F
    eng.latched["x"] = AlertLevel.CAUTION
    eng._update_latch("x", AlertLevel.CAUTION)        # c1=F c2=F  out=F


def main() -> int:
    EVIDENCE.mkdir(exist_ok=True)
    cases = discover_test_cases(TEST_DIR)
    print(f"discovered {len(cases)} test cases")

    McdcTracker.reset()
    McdcTracker.enable()

    with LineCoverage(roots=[COV_ROOT]) as cov:
        _exercise_mcdc_decisions()
        results = run_all(cases)
        campaigns = []
        for path in sorted(CAMP_DIR.glob("*.json")):
            c = load_campaign(path)
            campaigns.append(run_campaign(c))

    McdcTracker.disable()

    trace = build_trace(results)
    gap = build_gap_report(cases, REQ_CSV)
    mcdc = McdcTracker.report()
    coverage = cov.report()

    pass_count = sum(1 for r in results if r.result == "PASS")
    fail_count = sum(1 for r in results if r.result == "FAIL")
    err_count = sum(1 for r in results if r.result == "ERROR")
    camp_pass = sum(1 for c in campaigns if c.get("pass"))

    summary = {
        "tests_total": len(results),
        "tests_passed": pass_count,
        "tests_failed": fail_count,
        "tests_errored": err_count,
        "campaigns_total": len(campaigns),
        "campaigns_passed": camp_pass,
        "coverage_pct": round(coverage["__summary__"]["pct"] * 100, 2),
        "mcdc_decisions": list(mcdc.keys()),
        "mcdc_pct_avg": round(
            (sum(d["pct"] for d in mcdc.values()) / len(mcdc) * 100)
            if mcdc else 0.0,
            2,
        ),
        "gap_uncovered_count": len(gap["requirements_uncovered"]),
    }

    print("\n=== M4 Verification Summary ===")
    for k, v in summary.items():
        print(f"  {k}: {v}")

    print("\n=== Per-test ===")
    for r in results:
        marker = "OK " if r.result == "PASS" else "!! "
        print(f"  {marker}{r.id:<24} req={','.join(r.req):<28} {r.result}")
        for f in r.failures:
            print(f"      - {f}")

    print("\n=== Campaigns ===")
    for c in campaigns:
        marker = "OK " if c.get("pass") else "!! "
        print(f"  {marker}{c['id']:<10} class={c['classification']:<26} "
              f"hm={c['hm_event_total']} mode={c['fcc_mode_terminal']}")

    print("\n=== MC/DC ===")
    for name, info in mcdc.items():
        print(f"  {name}: {info['covered_conditions']}/{info['conditions']} "
              f"({info['pct'] * 100:.0f}%)  samples={info['samples']}")

    print(f"\n=== Coverage (avx_sim) ===")
    print(f"  total: {coverage['__summary__']['hit']}/"
          f"{coverage['__summary__']['executable']} "
          f"({summary['coverage_pct']}%)")

    out_path = EVIDENCE / "m4-verification-report.json"
    payload = {
        "summary": summary,
        "results": [asdict(r) for r in results],
        "campaigns": campaigns,
        "trace": trace,
        "gap": gap,
        "mcdc": mcdc,
        "coverage": coverage,
    }
    out_path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print(f"\nwrote {out_path.relative_to(ROOT)}")

    if fail_count or err_count:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
