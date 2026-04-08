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
from avx_sim.hf import (                                # noqa: E402
    HfEvaluator,
    MODE_CONFUSION_SCENARIOS,
    run_mode_confusion,
)
from avx_sim.hil import HilBridge, HilFaults, LoopbackMcu  # noqa: E402
from avx_sim.messages import AlertLevel, EngineExceed     # noqa: E402
from avx_sim.modules import DisplayComputer               # noqa: E402
from evidence_bundler import build_bundle, verify_bundle  # noqa: E402
from ai_assistant import (                                  # noqa: E402
    triage_summary,
    build_impact_index,
    summarize_evidence_markdown,
    draft_do178c_objective_table,
    trace_mermaid,
)
from fault_injector.escape import collect_escapes, write_markdown  # noqa: E402
from avx_sim.hf import STANDARD_TASKS, response_budget     # noqa: E402

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

        # ---- M5: Human Factors evaluation -------------------------------
        dsp_hf = DisplayComputer()
        dsp_hf.receive_engine_exceed(EngineExceed(1, "n1", AlertLevel.WARNING, 105, True))
        dsp_hf.receive_engine_exceed(EngineExceed(0, "egt", AlertLevel.CAUTION, 880, True))
        hf_report = HfEvaluator(dsp_hf).run(now_us=0)
        hf_findings = [
            {"hf_id": f.hf_id, "title": f.title, "passed": f.passed,
             "detail": f.detail, "ac_ref": f.ac_ref}
            for f in hf_report.findings
        ]

        mode_confusion_results = [
            run_mode_confusion(s) for s in MODE_CONFUSION_SCENARIOS
        ]

        # ---- M5: HIL-lite loopback ---------------------------------------
        hil_runs = []
        for name, faults in (
            ("nominal", HilFaults()),
            ("latency-5ms", HilFaults(latency_us=5000)),
            ("drop-every-3", HilFaults(drop_every_n=3)),
            ("reboot", HilFaults(reboot_at_cycle=10, brownout_cycles=3)),
        ):
            bridge = HilBridge(mcu=LoopbackMcu(faults=faults))
            for i in range(60):
                bridge.tick(now_us=i * 100, cmd=(0.0, 0.0, 0.0))
            bridge.drain(now_us=60 * 100 + faults.latency_us + 1000)
            hil_runs.append({"name": name, **bridge.measurement.summary()})

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
        "hf_total": len(hf_report.findings),
        "hf_passed": sum(1 for f in hf_report.findings if f.passed),
        "hf_failed": sum(1 for f in hf_report.findings if not f.passed),
        "mode_confusion_total": len(mode_confusion_results),
        "mode_confusion_ok": sum(
            1 for r in mode_confusion_results
            if r["terminal_mode_matches"] and r["history_depth_ok"]
        ),
        "hil_runs": len(hil_runs),
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

    print("\n=== HF Evaluation ===")
    for f in hf_report.findings:
        marker = "OK " if f.passed else "!! "
        print(f"  {marker}{f.hf_id}: {f.title} - {f.detail}")

    print("\n=== Mode Confusion ===")
    for r in mode_confusion_results:
        marker = "OK " if (r["terminal_mode_matches"] and r["history_depth_ok"]) else "!! "
        print(f"  {marker}{r['id']}: mode={r['terminal_mode']} "
              f"seen={r['modes_seen']} latency_violations={r['mode_latency_violations']}")

    print("\n=== HIL-lite ===")
    for r in hil_runs:
        print(f"  {r['name']:<14} cycles={r['cycles']} "
              f"lat_mean={r['latency_mean_us']}us lat_max={r['latency_max_us']}us "
              f"drops={r['drops']} reboots={r['reboots']}")

    print(f"\n=== Coverage (avx_sim) ===")
    print(f"  total: {coverage['__summary__']['hit']}/"
          f"{coverage['__summary__']['executable']} "
          f"({summary['coverage_pct']}%)")

    out_path = EVIDENCE / "verification-report.json"
    payload = {
        "summary": summary,
        "results": [asdict(r) for r in results],
        "campaigns": campaigns,
        "trace": trace,
        "gap": gap,
        "mcdc": mcdc,
        "coverage": coverage,
        "hf_findings": hf_findings,
        "mode_confusion": mode_confusion_results,
        "hil_runs": hil_runs,
    }
    out_path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print(f"\nwrote {out_path.relative_to(ROOT)}")

    # ---- Assurance extras (rule-based AI + escape + pilot timing) ------
    ASSURANCE = EVIDENCE / "assurance"
    ASSURANCE.mkdir(exist_ok=True)

    # triage summary from the worst campaign's HM events would require the
    # underlying record list; for now we summarize the overall structure.
    triage_text = triage_summary([])
    (ASSURANCE / "triage-DRAFT.md").write_text(
        "# Triage (DRAFT)\n\n" + triage_text + "\n", encoding="utf-8"
    )

    # evidence markdown summary
    (ASSURANCE / "evidence-summary-DRAFT.md").write_text(
        summarize_evidence_markdown(out_path), encoding="utf-8"
    )

    # DO-178C objective draft
    (ASSURANCE / "do178c-objectives-DRAFT.md").write_text(
        draft_do178c_objective_table(out_path), encoding="utf-8"
    )

    # trace graph (mermaid text)
    (ASSURANCE / "trace-graph-DRAFT.md").write_text(
        "# Trace graph (DRAFT)\n\n" + trace_mermaid(trace) + "\n",
        encoding="utf-8"
    )

    # change-impact index
    idx = build_impact_index(TEST_DIR)
    (ASSURANCE / "change-impact-index-DRAFT.json").write_text(
        json.dumps({
            "_draft": "DRAFT - human-in-the-loop",
            "req_to_tests": idx.req_to_tests,
            "req_to_code": idx.req_to_code,
        }, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    # escape candidates
    escape_input = []
    for c in campaigns:
        if c.get("classification") == "escaped":
            # Locate the original campaign JSON to discover the fault type
            src_path = CAMP_DIR / f"{c['id']}-afdx-delay.json"
            # Best effort: match by id prefix
            for p in CAMP_DIR.glob("*.json"):
                if p.stem.startswith(c["id"]):
                    src = json.loads(p.read_text(encoding="utf-8"))
                    c = dict(c)
                    c["_fault_hint"] = (src.get("faults") or [{}])[0].get("type", "")
                    break
        escape_input.append(c)
    escapes = collect_escapes(escape_input)
    write_markdown(escapes, ASSURANCE / "escape-candidates-DRAFT.md")

    # pilot timing budget against current DSP latency
    pilot_results = [
        response_budget(t, display_latency_us=0)
        for t in STANDARD_TASKS.values()
    ]
    (ASSURANCE / "pilot-timing-DRAFT.json").write_text(
        json.dumps({"_draft": "DRAFT", "results": pilot_results},
                   indent=2, sort_keys=True),
        encoding="utf-8"
    )

    print("\n=== Assurance extras ===")
    print(f"  triage-DRAFT.md, evidence-summary-DRAFT.md,")
    print(f"  do178c-objectives-DRAFT.md, trace-graph-DRAFT.md,")
    print(f"  change-impact-index-DRAFT.json,")
    print(f"  escape-candidates-DRAFT.md ({len(escapes)} entries),")
    print(f"  pilot-timing-DRAFT.json ({len(pilot_results)} tasks)")

    # ---- M6: build evidence bundle + self-verify -----------------------
    bundle_path = build_bundle(payload, ROOT, EVIDENCE / "bundles")
    verify = verify_bundle(bundle_path)
    print(f"\n=== Evidence bundle ===")
    print(f"  path: {bundle_path.relative_to(ROOT)}")
    print(f"  files: {len(verify['manifest']['files'])}")
    print(f"  git_sha: {verify['manifest']['build']['git_sha'][:12]}")
    print(f"  verify: {'OK' if verify['ok'] else 'FAIL'}")
    if not verify["ok"]:
        for m in verify["mismatches"]:
            print(f"    - {m}")
        return 1

    if fail_count or err_count:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
