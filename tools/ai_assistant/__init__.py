"""AI assistance layer — assurance and tooling helpers.

Principle: **never in the control loop**. Every output from this package is
labelled ``DRAFT — human-in-the-loop`` and carries a visible warning.

The current implementation is rule-based so the outputs are deterministic
and reproducible; an LLM backend can be plugged in later without changing
the call sites.
"""
from .skeleton import generate_test_skeletons, DRAFT_BANNER
from .triage import cluster_log_events, triage_summary
from .change_impact import build_impact_index, impact_for_requirement
from .evidence_summary import summarize_evidence_markdown
from .artifact_draft import draft_do178c_objective_table
from .trace_graph import trace_mermaid

__all__ = [
    "generate_test_skeletons",
    "cluster_log_events",
    "triage_summary",
    "build_impact_index",
    "impact_for_requirement",
    "summarize_evidence_markdown",
    "draft_do178c_objective_table",
    "trace_mermaid",
    "DRAFT_BANNER",
]
