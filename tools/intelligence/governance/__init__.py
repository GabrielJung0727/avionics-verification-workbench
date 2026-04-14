"""Phase C governance — assurance case lint, approval workflow, change
impact reset.

These tools ENFORCE the rules written in `docs/PhaseC/`:
  - every assurance case has all required sections
  - state transitions follow the documented machine
  - any change to a model's dataset_hash or git_sha demotes its state
"""
from .assurance_lint import (
    REQUIRED_SECTIONS,
    LintReport,
    lint_case,
    lint_all_cases,
)
from .approval import (
    ApprovalState,
    promote_state,
    demote_state,
    PromotionError,
)
from .change_impact import (
    detect_state_invalidations,
)

__all__ = [
    "REQUIRED_SECTIONS",
    "LintReport",
    "lint_case",
    "lint_all_cases",
    "ApprovalState",
    "promote_state",
    "demote_state",
    "PromotionError",
    "detect_state_invalidations",
]
