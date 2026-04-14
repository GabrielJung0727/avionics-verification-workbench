"""Optional bridge from the rule-based ai_assistant tools to the Phase B
intelligence endpoint.

If the env var ``INTELLIGENCE_ENDPOINT`` is set (e.g. via
``scripts/serve_intelligence.py`` running in another shell), the helpers
here forward calls to the registered models. Otherwise they return None
and the caller silently falls back to the rule-based path.

Importantly: a missing or unreachable endpoint NEVER raises out of these
helpers — they return ``None``. The rule-based path stays the default
deterministic behaviour.
"""
from __future__ import annotations
import os
import sys
from pathlib import Path
from typing import Any

# Make the intelligence package importable when ai_assistant is used as
# a standalone tool (not via the orchestrator).
_TOOLS = Path(__file__).resolve().parents[1]
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

try:  # pragma: no cover - import guarded for environments without intelligence
    from intelligence import IntelligenceClient, IntelligenceClientError
except Exception:   # noqa: BLE001
    IntelligenceClient = None  # type: ignore[assignment]
    IntelligenceClientError = Exception  # type: ignore[assignment]


def maybe_client() -> "IntelligenceClient | None":
    """Return a configured client if the env var is set AND the endpoint is
    reachable; ``None`` otherwise."""
    if IntelligenceClient is None:
        return None
    url = os.environ.get("INTELLIGENCE_ENDPOINT")
    if not url:
        return None
    client = IntelligenceClient(endpoint=url.rstrip("/"))
    try:
        client.health()
    except IntelligenceClientError:
        return None
    return client


def trace_gap_or_none(diff_paths: list[str], requirement_ids: list[str],
                      top_k: int = 10) -> list[dict] | None:
    client = maybe_client()
    if client is None:
        return None
    try:
        out = client.predict_trace_gap(
            diff_paths=diff_paths,
            requirement_ids=requirement_ids,
            top_k=top_k,
        )
    except IntelligenceClientError:
        return None
    return out.get("ranked")


def escape_or_none(**fault_params: Any) -> dict | None:
    client = maybe_client()
    if client is None:
        return None
    try:
        return client.predict_escape(**fault_params)
    except (IntelligenceClientError, TypeError):
        return None
