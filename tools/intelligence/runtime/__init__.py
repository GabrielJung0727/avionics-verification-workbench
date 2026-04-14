"""Phase D runtime layer.

Wraps frozen Phase B models with a deterministic safety shell and routes
their output through one of three modes (Shadow / Advisory / Limited
Supervised). The shell is the only path through which an AI output may
ever leave the assurance perimeter.
"""
from .assurance_shell import (
    RuntimeAssuranceShell,
    ShellConfig,
    ShellViolation,
    ShellResult,
    AuthorityBudget,
)
from .modes import (
    Mode,
    ShadowMode,
    AdvisoryMode,
    LimitedSupervisedMode,
    OperatorAck,
    AckQueue,
)
from .comparison import (
    DisagreementTracker,
    DisagreementSummary,
)
from .loader import (
    ApprovalGateError,
    load_with_approval_gate,
    OnlineLearningAttempt,
)
from .harness import RuntimeHarness, RuntimeReport

__all__ = [
    "RuntimeAssuranceShell",
    "ShellConfig",
    "ShellViolation",
    "ShellResult",
    "AuthorityBudget",
    "Mode",
    "ShadowMode",
    "AdvisoryMode",
    "LimitedSupervisedMode",
    "OperatorAck",
    "AckQueue",
    "DisagreementTracker",
    "DisagreementSummary",
    "ApprovalGateError",
    "load_with_approval_gate",
    "OnlineLearningAttempt",
    "RuntimeHarness",
    "RuntimeReport",
]
