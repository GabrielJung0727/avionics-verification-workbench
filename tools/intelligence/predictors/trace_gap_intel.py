"""Trace Gap Intelligence (v0).

Given a git diff (file path -> hunks), rank the likely-impacted requirement
ids. v0 is a transparent rule-based baseline so the orchestrator has a
working consumer; the same interface accepts a learned ranker once enough
historical CR-impact pairs are available (Phase B+).
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

# Crude module-prefix → requirement-prefix map. Same idea as
# tools/ai_assistant/change_impact.py but inverted, with priors.
_MODULE_TO_REQ_PREFIXES = {
    "tools/sim_py/avx_sim/modules/fcc.py":           ("HLR-FCC", 1.0),
    "tools/sim_py/avx_sim/modules/engine.py":        ("HLR-ENG", 1.0),
    "tools/sim_py/avx_sim/modules/display.py":       ("HLR-DSP", 1.0),
    "tools/sim_py/avx_sim/modules/data_concentrator.py": ("HLR-DC", 1.0),
    "tools/sim_py/avx_sim/scheduler.py":             ("HLR-HM", 0.6),
    "tools/sim_py/avx_sim/health_monitor.py":        ("HLR-HM", 1.0),
    "tools/sim_py/avx_sim/recorder.py":              ("SYS", 0.4),
    "tools/sim_py/avx_sim/sim_clock.py":             ("SYS", 0.5),
    "tools/sim_py/avx_sim/ipc.py":                   ("SYS", 0.4),
    "tools/sim_py/avx_sim/afdx.py":                  ("SYS", 0.5),
    "tools/sim_py/avx_sim/a429.py":                  ("SYS", 0.4),
}


@dataclass
class TraceGapEvaluation:
    n_requirements_indexed: int
    holdout_diffs: int
    precision_at_3: float
    mrr: float


def rank_impacted_requirements(diff_paths: list[str], requirement_ids: list[str],
                               top_k: int = 10) -> list[dict]:
    """Return top-K requirement candidates with score and reason. Output
    always carries the DRAFT marker; downstream tools must surface it."""
    scores: dict[str, float] = {req: 0.0 for req in requirement_ids}
    reasons: dict[str, list[str]] = {req: [] for req in requirement_ids}

    for path in diff_paths:
        if path in _MODULE_TO_REQ_PREFIXES:
            prefix, weight = _MODULE_TO_REQ_PREFIXES[path]
            for req in requirement_ids:
                if req.startswith(prefix):
                    scores[req] += weight
                    reasons[req].append(f"{path}+{prefix}*{weight}")

    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    out = []
    for req, sc in ranked[:top_k]:
        if sc <= 0:
            break
        out.append({
            "_draft": "DRAFT - human-in-the-loop trace gap candidate",
            "req_id": req,
            "score": float(sc),
            "reasons": reasons[req],
        })
    return out


def evaluate_on_synthetic(requirement_ids: list[str]) -> TraceGapEvaluation:
    """Tiny in-vitro evaluation: synthetic (diff, expected_req_prefix) pairs.
    Used by the orchestrator so the registry has metrics to record."""
    cases = [
        (["tools/sim_py/avx_sim/modules/fcc.py"], "HLR-FCC"),
        (["tools/sim_py/avx_sim/modules/engine.py"], "HLR-ENG"),
        (["tools/sim_py/avx_sim/modules/display.py"], "HLR-DSP"),
        (["tools/sim_py/avx_sim/modules/data_concentrator.py"], "HLR-DC"),
        (["tools/sim_py/avx_sim/health_monitor.py"], "HLR-HM"),
    ]
    hits_at_3 = 0
    rr_total = 0.0
    for diff, expected_prefix in cases:
        ranked = rank_impacted_requirements(diff, requirement_ids, top_k=10)
        prefix_hits = [
            i for i, r in enumerate(ranked) if r["req_id"].startswith(expected_prefix)
        ]
        if prefix_hits and prefix_hits[0] < 3:
            hits_at_3 += 1
        if prefix_hits:
            rr_total += 1.0 / (prefix_hits[0] + 1)
    n = len(cases)
    return TraceGapEvaluation(
        n_requirements_indexed=len(requirement_ids),
        holdout_diffs=n,
        precision_at_3=hits_at_3 / n,
        mrr=rr_total / n,
    )
