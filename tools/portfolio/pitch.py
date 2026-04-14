"""Elevator pitch text - three lengths, one source of truth.

Used by the CLI (`scripts/elevator_pitch.py`) and pinned by tests so the
core message stays consistent across README / FAQ / LinkedIn / interviews.

Plain ASCII only so the CLI prints cleanly on every console (including
Windows cp949).
"""
from __future__ import annotations

PITCH_5S = (
    "AI bounded to the verification layer; the deterministic channel always "
    "has primary authority. EASA Level 1-2 / FAA incremental - that's the "
    "only path the regulator currently accepts."
)

PITCH_30S = (
    "This project is not an AI flight controller. It's a certification-aligned "
    "avionics verification intelligence platform. The classical workbench "
    "(M1-M6) gives you a partitioned IMA scheduler, ARINC 429-lite + AFDX-lite "
    "buses, FCC / Engine / Display surrogates, requirement-based testing with "
    "MC/DC, fault campaigns, AC 20-175 human factors, HIL-lite, and immutable "
    "evidence bundles. Phase A-D adds a Bronze/Silver/Gold lakehouse, a "
    "frozen-model registry with assurance metadata, GSN-lite assurance cases "
    "with a reviewer workflow, and a runtime assurance shell so AI components "
    "stay strictly outside the control loop. Aligns with EASA AI Concept "
    "Paper Level 1-2 and the FAA AI Roadmap incremental approach."
)

PITCH_60S = PITCH_30S + (
    " The hard line is enforced in code: model.fit() raises "
    "OnlineLearningAttempt; the loader refuses Advisory+ modes below "
    "board-approved; Phase C reviewer-confirmation requires a separate "
    "reviewer; every AI output is marked DRAFT and parked in an ack queue "
    "before any low-criticality consumer sees it. The deterministic "
    "verification pipeline runs unchanged whether the AI components are "
    "present or not - they only reorder, prioritize, and flag. That's the "
    "differentiator: the platform demonstrates how an enterprise team would "
    "actually adopt AI inside a DO-178C / ARP4754A lifecycle without "
    "violating any of the existing certification frameworks."
)

HARD_LINE = (
    "This project is not an AI flight controller. It is a certification-aligned "
    "avionics verification intelligence platform that uses governed datasets, "
    "traceable evidence, and bounded learned components to improve verification "
    "prioritization, anomaly detection, and operational assurance under "
    "existing aviation safety frameworks."
)


def pitch(length: str = "30s") -> str:
    return {
        "5s": PITCH_5S,
        "30s": PITCH_30S,
        "60s": PITCH_60S,
        "hard-line": HARD_LINE,
    }[length]
