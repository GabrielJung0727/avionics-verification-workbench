#!/usr/bin/env python3
"""Phase D shadow run for the engine_anomaly_detector.

Runs the model in Shadow mode against a deterministic engine telemetry
stream. The deterministic engine I/F latch logic is the source of truth;
the AI is observed but never granted authority.

Output: ``evidence/phaseD-shadow-report.json``
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "sim_py"))

from intelligence.runtime import (  # noqa: E402
    AuthorityBudget,
    Mode,
    RuntimeAssuranceShell,
    RuntimeHarness,
    ShadowMode,
    ShellConfig,
    load_with_approval_gate,
)
from intelligence.predictors.engine_anomaly import _window_features  # noqa: E402
from avx_sim.health_monitor import HealthMonitor   # noqa: E402
from avx_sim.messages import EngineRaw             # noqa: E402
from avx_sim.modules import EngineInterface        # noqa: E402


REGISTRY = ROOT / "evidence" / "registry"


def _stream(seed: int = 42) -> np.ndarray:
    rng = np.random.default_rng(seed)
    T = 200
    s = np.column_stack([
        88 + 0.5 * np.sin(np.linspace(0, 4, T)),
        95 + 0.3 * np.sin(np.linspace(0, 5, T)),
        700 + 5 * np.sin(np.linspace(0, 3, T)),
        3000 + 50 * np.sin(np.linspace(0, 2, T)),
    ]) + rng.normal(0, 0.4, (T, 4))
    # Inject EGT runaway at index 100
    for i in range(100, T):
        s[i, 2] += (i - 100) * 1.5
    return s


def main() -> int:
    # Phase D requires Shadow mode -> any approval state allowed for shadow
    model, model_meta = load_with_approval_gate(
        REGISTRY, "engine_anomaly_detector", "v0.1.0", mode=Mode.SHADOW,
    )

    stream = _stream(seed=42)
    feats = _window_features(stream, 8)

    # Deterministic source of truth: the existing engine I/F latch logic.
    hm = HealthMonitor()
    eng = EngineInterface(hm=hm)

    def deterministic_decision(idx: int) -> str:
        i = int(idx)
        # idx is window-end index in the stream; we replay the raw row.
        n1, n2, egt, ff = stream[i]
        eng.step(EngineRaw(0, float(n1), float(n2), float(egt), float(ff)),
                 now_us=i * 10_000)
        worst = max(eng.latched.values(), default=None)
        if worst is None:
            return "nominal"
        from avx_sim.messages import AlertLevel
        return {
            AlertLevel.WARNING: "preventive_alert",
            AlertLevel.CAUTION: "early_warning",
            AlertLevel.ADVISORY: "nominal",
        }.get(worst, "nominal")

    def ai_decision(idx: int) -> dict:
        feat = feats[int(idx) - 8 + 1]   # match window indexing
        score = float(model.score_samples(np.atleast_2d(feat))[0])
        pred = int(model.predict(np.atleast_2d(feat))[0])
        if pred == -1:
            decision = "preventive_alert"
        elif score < -0.05:
            decision = "early_warning"
        else:
            decision = "inspection_candidate" if score < 0 else "nominal"
        return {"score": score, "decision": decision}

    def ai_to_decision(guarded: dict) -> str:
        return guarded.get("decision", "nominal")

    shell = RuntimeAssuranceShell(
        config=ShellConfig(
            output_keys=["score"],
            ranges={"score": (-1.0, 1.0)},
            rate_limits={"score": 0.5},
            authority={"score": AuthorityBudget(max_abs_value=0.6,
                                                max_abs_delta=0.5)},
            watchdog_us=500_000,    # 500 ms — generous because we run on CPU
        ),
        fallback_provider=lambda raw: {"score": 0.0, "decision": "nominal"},
    )

    harness = RuntimeHarness(
        mode_obj=ShadowMode(),
        shell=shell,
        ai_decision_fn=ai_decision,
        deterministic_decision_fn=deterministic_decision,
        ai_to_decision=ai_to_decision,
    )

    # Iterate over each window (index in the stream)
    for end in range(8, len(stream)):
        harness.tick(end, sim_ts_us=end * 10_000)

    report = harness.report()
    payload = {
        "_draft": "DRAFT - Phase D shadow run, advisory observation only",
        "model": model_meta,
        "mode": report.mode,
        "samples": report.samples,
        "agreement_rate": report.agreement_rate,
        "fallback_rate": report.fallback_rate,
        "violation_counts": report.violation_counts,
        "pending_acks": report.pending_acks,
        "applied_actions": report.applied_actions,
        "notes": report.notes,
    }

    out = ROOT / "evidence" / "phaseD-shadow-report.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True),
                   encoding="utf-8")
    print(f"\n=== Phase D shadow run ===")
    print(f"  model            : {model_meta['model_name']} {model_meta['version']}")
    print(f"  approval_state   : {model_meta['approval_state']}")
    print(f"  mode             : {report.mode}")
    print(f"  samples          : {report.samples}")
    print(f"  agreement_rate   : {report.agreement_rate:.3f}")
    print(f"  fallback_rate    : {report.fallback_rate:.3f}")
    print(f"  violation_counts : {report.violation_counts}")
    print(f"  wrote            : {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
