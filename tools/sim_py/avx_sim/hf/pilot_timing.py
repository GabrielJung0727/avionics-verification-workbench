"""Pilot task timing simulation (tiny closed-form model).

Not a psychometric tool — a deterministic budget calculator. Each task is a
list of steps (notice, decide, act) with typical durations drawn from the
aerospace HF literature (simplified). Given a scenario alert, the model
returns:

  - total response time budget
  - whether the DSP mode-annunciation latency eats into the budget
  - a per-step breakdown

The point is to produce a number the verification runner can gate on. Any
real study would replace this with measured distributions.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class TaskStep:
    name: str
    typical_us: int


@dataclass
class PilotTask:
    id: str
    description: str
    steps: list[TaskStep] = field(default_factory=list)
    deadline_us: int = 5_000_000

    def total_us(self) -> int:
        return sum(s.typical_us for s in self.steps)


def response_budget(task: PilotTask, *, display_latency_us: int = 0
                    ) -> dict:
    total = task.total_us() + display_latency_us
    margin = task.deadline_us - total
    return {
        "_draft": "DRAFT - human-in-the-loop pilot timing estimate",
        "task": task.id,
        "deadline_us": task.deadline_us,
        "display_latency_us": display_latency_us,
        "total_us": total,
        "margin_us": margin,
        "within_budget": margin >= 0,
        "steps": [{"name": s.name, "typical_us": s.typical_us} for s in task.steps],
    }


STANDARD_TASKS: dict[str, PilotTask] = {
    "engine-caution-ack": PilotTask(
        id="engine-caution-ack",
        description="Recognise engine caution annunciation and acknowledge",
        steps=[
            TaskStep("notice", 500_000),
            TaskStep("decide", 800_000),
            TaskStep("act", 400_000),
        ],
        deadline_us=3_000_000,
    ),
    "mode-reversion-check": PilotTask(
        id="mode-reversion-check",
        description="Confirm FCC mode change and cross-check flight state",
        steps=[
            TaskStep("notice", 400_000),
            TaskStep("decide", 1_200_000),
            TaskStep("cross-check", 1_000_000),
            TaskStep("act", 500_000),
        ],
        deadline_us=5_000_000,
    ),
    "multi-alert-priority": PilotTask(
        id="multi-alert-priority",
        description="Prioritise simultaneous warning + caution alerts",
        steps=[
            TaskStep("notice", 600_000),
            TaskStep("triage", 1_500_000),
            TaskStep("act-primary", 800_000),
            TaskStep("act-secondary", 1_000_000),
        ],
        deadline_us=6_000_000,
    ),
}
