"""Harness that runs an AI model in shadow against a deterministic source
of truth and produces a comparison report.

The harness never modifies the deterministic pipeline; it observes it.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable

from .assurance_shell import RuntimeAssuranceShell, ShellResult
from .comparison import DisagreementTracker
from .modes import (
    AckQueue,
    AdvisoryMode,
    LimitedSupervisedMode,
    Mode,
    ShadowMode,
)


@dataclass
class RuntimeReport:
    mode: str
    samples: int
    agreement_rate: float
    fallback_rate: float
    violation_counts: dict[str, int]
    pending_acks: int = 0
    accepted_acks: int = 0
    applied_actions: int = 0
    notes: list[str] = field(default_factory=list)


class RuntimeHarness:
    """Couples a model + shell + mode + deterministic source. The caller
    feeds inputs via ``tick``; everything else is internal."""

    def __init__(self, *, mode_obj, shell: RuntimeAssuranceShell,
                 ai_decision_fn: Callable[[Any], dict],
                 deterministic_decision_fn: Callable[[Any], str],
                 ai_to_decision: Callable[[dict], str]):
        self.mode_obj = mode_obj
        self.shell = shell
        self.ai_decision_fn = ai_decision_fn
        self.deterministic_decision_fn = deterministic_decision_fn
        self.ai_to_decision = ai_to_decision
        self.tracker = DisagreementTracker()

    def tick(self, sample: Any, *, sim_ts_us: int | None = None
             ) -> ShellResult:
        result = self.shell.evaluate(
            model_call=lambda: self.ai_decision_fn(sample),
            sim_ts_us=sim_ts_us,
        )
        det = self.deterministic_decision_fn(sample)
        ai = self.ai_to_decision(result.guarded)
        self.tracker.record(
            ai_decision=ai,
            det_decision=det,
            fallback_engaged=result.fallback_engaged,
            violations=[v.value for v in result.violations],
        )

        # Mode-specific consumer
        if isinstance(self.mode_obj, ShadowMode):
            self.mode_obj.consume(result.guarded, result.raw,
                                  [v.value for v in result.violations])
        elif isinstance(self.mode_obj, AdvisoryMode):
            self.mode_obj.consume(result.guarded, result.raw,
                                  [v.value for v in result.violations])
        elif isinstance(self.mode_obj, LimitedSupervisedMode):
            self.mode_obj.consume(result.guarded, result.raw,
                                  [v.value for v in result.violations])
        return result

    def report(self) -> RuntimeReport:
        s = self.tracker.summary
        pending = accepted = applied = 0
        if isinstance(self.mode_obj, AdvisoryMode):
            pending = len(self.mode_obj.queue.pending)
            accepted = len(self.mode_obj.queue.accepted())
        if isinstance(self.mode_obj, LimitedSupervisedMode):
            pending = len(self.mode_obj.queue.pending)
            accepted = len(self.mode_obj.queue.accepted())
            applied = len(self.mode_obj.applied)
        return RuntimeReport(
            mode=self.mode_obj.name.value,
            samples=s.samples,
            agreement_rate=s.agreement_rate,
            fallback_rate=s.fallback_rate,
            violation_counts=dict(s.violation_counts),
            pending_acks=pending,
            accepted_acks=accepted,
            applied_actions=applied,
            notes=[
                "deterministic pipeline runs unaffected",
                "AI output gated by RuntimeAssuranceShell",
            ],
        )
