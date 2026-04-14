"""Approval-gated model loader.

A model can only be used in:
  Shadow              if approval_state >= auto-generated  (any frozen model)
  Advisory            if approval_state >= board-approved
  LimitedSupervised   if approval_state >= board-approved AND
                      Phase C invalidations report is empty for this model

Online learning attempts (calling .fit / .partial_fit on a loaded model)
are detected and refused.
"""
from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..registry.registry import LocalRegistry
from .modes import Mode


_REQUIRED_STATE = {
    Mode.SHADOW: {"auto-generated", "reviewer-confirmed", "board-approved"},
    Mode.ADVISORY: {"board-approved"},
    Mode.LIMITED_SUPERVISED: {"board-approved"},
}


class ApprovalGateError(RuntimeError):
    pass


class OnlineLearningAttempt(RuntimeError):
    pass


@dataclass
class _GuardedModel:
    """Wraps a sklearn-like model and refuses any in-place training call."""
    inner: Any
    name: str

    def predict(self, *args, **kwargs):
        if hasattr(self.inner, "predict"):
            return self.inner.predict(*args, **kwargs)
        raise AttributeError(f"{self.name} has no predict")

    def predict_proba(self, *args, **kwargs):
        if hasattr(self.inner, "predict_proba"):
            return self.inner.predict_proba(*args, **kwargs)
        raise AttributeError(f"{self.name} has no predict_proba")

    def score_samples(self, *args, **kwargs):
        if hasattr(self.inner, "score_samples"):
            return self.inner.score_samples(*args, **kwargs)
        raise AttributeError(f"{self.name} has no score_samples")

    def fit(self, *args, **kwargs):
        raise OnlineLearningAttempt(
            f"online learning forbidden by Phase D for {self.name}; "
            f"retrain offline + bump version + re-promote via Phase C."
        )

    def partial_fit(self, *args, **kwargs):
        raise OnlineLearningAttempt(
            f"online learning forbidden by Phase D for {self.name}."
        )


def load_with_approval_gate(registry_root: Path, model_name: str,
                            version: str, *, mode: Mode
                            ) -> tuple[_GuardedModel, dict]:
    """Load a model only if its approval_state satisfies the requested mode.
    Returns (guarded_model, meta)."""
    reg = LocalRegistry(root=registry_root)
    inner, record = reg.load(model_name, version)
    state = record.meta.approval_state
    allowed = _REQUIRED_STATE[mode]
    if state not in allowed:
        raise ApprovalGateError(
            f"{model_name} {version}: approval_state={state} "
            f"insufficient for mode={mode.value} (need one of {sorted(allowed)})"
        )
    if not record.meta.frozen:
        raise ApprovalGateError(
            f"{model_name} {version}: not frozen; refusing to load."
        )

    # Phase C invalidation cross-check (advisory+ only)
    if mode != Mode.SHADOW:
        from ..governance.change_impact import detect_state_invalidations
        invs = detect_state_invalidations(registry_root)
        for inv in invs:
            if inv.model_name == model_name and inv.version == version:
                raise ApprovalGateError(
                    f"{model_name} {version}: Phase C invalidation present: "
                    f"{', '.join(inv.reasons)}"
                )

    guarded = _GuardedModel(inner=inner, name=f"{model_name}:{version}")
    meta = {
        "model_name": model_name,
        "version": version,
        "approval_state": state,
        "mode": mode.value,
    }
    return guarded, meta
