"""AI-vs-deterministic disagreement tracker.

For every shadow tick the harness produces (ai_decision, det_decision)
and feeds it here. The tracker accumulates statistics that ship in the
verification report: how often did the AI agree with the deterministic
pipeline, how often did the shell suppress the AI, and what was the
distribution of disagreement.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class DisagreementSummary:
    samples: int = 0
    agree: int = 0
    disagree: int = 0
    fallback_engaged: int = 0
    violation_counts: dict[str, int] = field(default_factory=dict)

    @property
    def agreement_rate(self) -> float:
        return self.agree / self.samples if self.samples else 0.0

    @property
    def fallback_rate(self) -> float:
        return self.fallback_engaged / self.samples if self.samples else 0.0

    def to_dict(self) -> dict:
        return {
            "_draft": "DRAFT - human-in-the-loop AI vs deterministic comparison",
            "samples": self.samples,
            "agree": self.agree,
            "disagree": self.disagree,
            "agreement_rate": self.agreement_rate,
            "fallback_engaged": self.fallback_engaged,
            "fallback_rate": self.fallback_rate,
            "violation_counts": dict(self.violation_counts),
        }


@dataclass
class DisagreementTracker:
    summary: DisagreementSummary = field(default_factory=DisagreementSummary)

    def record(self, *, ai_decision: str, det_decision: str,
               fallback_engaged: bool,
               violations: list[str] | None = None) -> None:
        self.summary.samples += 1
        if ai_decision == det_decision:
            self.summary.agree += 1
        else:
            self.summary.disagree += 1
        if fallback_engaged:
            self.summary.fallback_engaged += 1
        for v in violations or []:
            self.summary.violation_counts[v] = (
                self.summary.violation_counts.get(v, 0) + 1
            )

    def report(self) -> dict:
        return self.summary.to_dict()
