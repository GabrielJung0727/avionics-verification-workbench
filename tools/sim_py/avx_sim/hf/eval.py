"""Human-factors evaluation suite (M5).

Each evaluator returns an ``HfFinding`` that links back to an HF-id and an
AC 20-175 / AC 25.1322 bucket. The suite is deliberately mechanical — no
subjective judgement — so that results can be re-run and diffed.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Iterable

from ..messages import (
    AlertLevel,
    EngineExceed,
    FccMode,
    FccModeMsg,
    Freshness,
)
from ..modules import DisplayComputer


@dataclass(frozen=True)
class HfFinding:
    hf_id: str          # HF-01 ... HF-06
    title: str
    passed: bool
    detail: str
    ac_ref: str = ""


@dataclass
class HfReport:
    findings: list[HfFinding] = field(default_factory=list)

    def add(self, f: HfFinding) -> None:
        self.findings.append(f)

    @property
    def passed(self) -> bool:
        return all(f.passed for f in self.findings)

    def summary(self) -> dict:
        return {
            "total": len(self.findings),
            "passed": sum(1 for f in self.findings if f.passed),
            "failed": sum(1 for f in self.findings if not f.passed),
            "ids": [f.hf_id for f in self.findings],
        }


# ---- individual evaluators ------------------------------------------------

def evaluate_alert_priority(dsp_alerts: Iterable[tuple[int, AlertLevel]]
                            ) -> HfFinding:
    """HF-01: rendered alerts must be ordered WARNING > CAUTION > ADVISORY,
    newest-first within a level."""
    alerts = list(dsp_alerts)   # tuples are (ts_us, level)
    ok = True
    detail = "ordered"
    for a, b in zip(alerts, alerts[1:]):
        ts_a, lvl_a = a
        ts_b, lvl_b = b
        if int(lvl_b) > int(lvl_a):
            ok = False
            detail = f"out-of-order: {lvl_a.name}@{ts_a} before {lvl_b.name}@{ts_b}"
            break
        if int(lvl_b) == int(lvl_a) and ts_b > ts_a:
            ok = False
            detail = f"same-level newer precedes older: {ts_a} before {ts_b}"
            break
    return HfFinding("HF-01", "Alert prioritization", ok, detail,
                     ac_ref="AC 25.1322")


def evaluate_color_rule(tokens: dict) -> HfFinding:
    """HF-02: static color token check."""
    violations = DisplayComputer.static_color_check(tokens)
    return HfFinding(
        "HF-02", "Color usage (red/amber/green)",
        passed=(not violations),
        detail="OK" if not violations else "; ".join(violations),
        ac_ref="AC 20-175",
    )


def evaluate_mode_latency(dsp: DisplayComputer) -> HfFinding:
    """HF-03: no mode-annunciation latency budget violations."""
    ok = dsp.mode_latency_violations == 0
    return HfFinding(
        "HF-03", "Mode annunciation latency",
        passed=ok,
        detail=f"violations={dsp.mode_latency_violations} "
               f"budget_us={dsp.mode_latency_budget_us}",
        ac_ref="HLR-DSP-003",
    )


def evaluate_dashed_on_stale(dsp: DisplayComputer, now_us: int) -> HfFinding:
    """HF-05: stale inputs must be presented as dashed / masked."""
    dsp.receive_air_data(250.0, ts_us=now_us, freshness=Freshness.STALE)
    frame = dsp.render(now_us=now_us + 1000)
    ok = frame.ias == "----"
    return HfFinding(
        "HF-05", "Dashed value on stale input",
        passed=ok,
        detail=f"ias_rendered={frame.ias}",
        ac_ref="HLR-DSP-005",
    )


def evaluate_mode_history(dsp: DisplayComputer) -> HfFinding:
    """HF-06: mode history window is enforced."""
    dsp.receive_mode(FccModeMsg(0, FccMode.NORMAL, "", False), now_us=0)
    dsp.receive_mode(FccModeMsg(1_000_000, FccMode.ALTERNATE, "", True),
                     now_us=1_000_000)
    dsp.render(now_us=dsp.history_window_us + 2_000_000)   # well past window
    ok = len(dsp._mode_history) == 0
    return HfFinding(
        "HF-06", "Mode history window pruning",
        passed=ok,
        detail=f"kept={len(dsp._mode_history)}",
        ac_ref="HLR-DSP-006",
    )


def evaluate_salience(alerts: list[AlertEntry] | None = None) -> HfFinding:  # noqa: F821
    """HF-04 / information salience — a tiny weighted score so the
    evaluation has a numeric output, not a subjective one. The thresholds are
    learning-grade but they make the metric auditable."""
    from ..modules.display import AlertEntry
    alerts = alerts or []
    score = 0
    for a in alerts:
        if a.level == AlertLevel.WARNING:
            score += 3
        elif a.level == AlertLevel.CAUTION:
            score += 2
        else:
            score += 1
    # "well-salient" means the top alerts reach at least 3 points or there
    # are no alerts at all — that's a trivially valid display.
    ok = (not alerts) or score >= 3
    return HfFinding(
        "HF-04", "Information salience score",
        passed=ok,
        detail=f"score={score} n={len(alerts)}",
        ac_ref="AC 25.1322",
    )


# ---- top-level evaluator --------------------------------------------------

@dataclass
class HfEvaluator:
    dsp: DisplayComputer

    def run(self, now_us: int = 0) -> HfReport:
        report = HfReport()
        # HF-01 — priority order
        alerts = [(a.ts_us, a.level) for a in self.dsp.render(now_us).alerts]
        report.add(evaluate_alert_priority(alerts))
        # HF-02 — color rule (the canonical rule)
        report.add(evaluate_color_rule({
            AlertLevel.WARNING: "RED",
            AlertLevel.CAUTION: "AMBER",
            AlertLevel.ADVISORY: "GREEN",
        }))
        # HF-03 — latency
        report.add(evaluate_mode_latency(self.dsp))
        # HF-04 — salience
        report.add(evaluate_salience(self.dsp.render(now_us).alerts))
        # HF-05 — dashed on stale
        report.add(evaluate_dashed_on_stale(self.dsp, now_us))
        # HF-06 — mode history
        report.add(evaluate_mode_history(self.dsp))
        return report
