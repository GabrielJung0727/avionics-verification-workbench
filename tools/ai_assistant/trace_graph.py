"""Render a requirements-to-tests trace graph as Mermaid.js text.

Mermaid is chosen because the output is plain text, embeddable in GitHub
README / Notion / docs, and does not require a web server. If a full web
viewer is added later this helper becomes one of several render targets.
"""
from __future__ import annotations


def trace_mermaid(trace: dict[str, list[str]], *,
                  max_nodes: int = 80) -> str:
    lines = ["```mermaid", "graph LR"]
    reqs = list(trace.keys())[:max_nodes]
    seen_tests: set[str] = set()
    for req in reqs:
        safe_req = req.replace("-", "_")
        lines.append(f'  {safe_req}["{req}"]')
        for tc in trace[req]:
            safe_tc = tc.replace("-", "_")
            if safe_tc not in seen_tests:
                lines.append(f'  {safe_tc}(({tc}))')
                seen_tests.add(safe_tc)
            lines.append(f"  {safe_req} --> {safe_tc}")
    if len(trace) > max_nodes:
        lines.append(f'  more["... {len(trace) - max_nodes} more requirements"]')
    lines.append("```")
    return "\n".join(lines)
