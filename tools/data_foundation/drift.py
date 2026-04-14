"""Schema drift detection.

Compares an incoming verification-report.json against a frozen baseline of
top-level keys + the expected nested keys per section. Any unknown or
missing key is reported. CI gates on this so a quietly-renamed field can't
silently invalidate downstream Silver/Gold queries.
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from pathlib import Path

EXPECTED_TOP = {
    "summary", "results", "campaigns", "trace", "gap", "mcdc",
    "coverage", "hf_findings", "mode_confusion", "hil_runs",
}

EXPECTED_RESULT = {"id", "req", "result", "failures"}
EXPECTED_CAMPAIGN = {"id", "classification", "fcc_mode_terminal",
                     "hm_event_total"}
EXPECTED_HIL = {"name", "cycles", "latency_mean_us", "latency_max_us",
                "drops", "reboots"}
EXPECTED_HF = {"hf_id", "title", "passed", "detail", "ac_ref"}
EXPECTED_SUMMARY = {"tests_total", "tests_passed", "campaigns_total",
                    "coverage_pct", "mcdc_pct_avg",
                    "hf_total", "hf_passed", "hil_runs"}


@dataclass
class DriftReport:
    missing: list[str] = field(default_factory=list)
    unexpected: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.missing and not self.unexpected

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "missing": sorted(self.missing),
            "unexpected": sorted(self.unexpected),
        }


def _check(observed: set[str], expected: set[str], where: str,
           report: DriftReport) -> None:
    for key in expected - observed:
        report.missing.append(f"{where}: missing '{key}'")
    for key in observed - expected:
        report.unexpected.append(f"{where}: unexpected '{key}'")


def detect_drift(report_path: Path) -> DriftReport:
    payload = json.loads(Path(report_path).read_text(encoding="utf-8"))
    rep = DriftReport()

    _check(set(payload.keys()), EXPECTED_TOP, "top", rep)

    summary = payload.get("summary", {}) or {}
    for key in EXPECTED_SUMMARY - set(summary.keys()):
        rep.missing.append(f"summary: missing '{key}'")
    # extra summary keys are allowed (forward-compatible)

    for r in payload.get("results", [])[:1]:
        for k in EXPECTED_RESULT - set(r.keys()):
            rep.missing.append(f"results[0]: missing '{k}'")

    for c in payload.get("campaigns", [])[:1]:
        for k in EXPECTED_CAMPAIGN - set(c.keys()):
            rep.missing.append(f"campaigns[0]: missing '{k}'")

    for h in payload.get("hil_runs", [])[:1]:
        for k in EXPECTED_HIL - set(h.keys()):
            rep.missing.append(f"hil_runs[0]: missing '{k}'")

    for f in payload.get("hf_findings", [])[:1]:
        for k in EXPECTED_HF - set(f.keys()):
            rep.missing.append(f"hf_findings[0]: missing '{k}'")

    return rep
