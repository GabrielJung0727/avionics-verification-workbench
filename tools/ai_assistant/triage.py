"""Log anomaly clustering + failure triage (rule-based)."""
from __future__ import annotations
from collections import Counter, defaultdict
from typing import Iterable


def cluster_log_events(events: Iterable) -> dict:
    """Cluster HM events by (code, source). Accepts the ``HmRecord`` dataclass
    instances produced by ``HealthMonitor`` or any object exposing ``code`` /
    ``source`` / ``severity``. Returns a dict {code: {"count", "by_source",
    "severities"}}."""
    code_counts: Counter = Counter()
    by_source: dict[str, Counter] = defaultdict(Counter)
    sev_by_code: dict[str, Counter] = defaultdict(Counter)
    first_seen: dict[str, int] = {}
    for ev in events:
        code = getattr(ev.code, "value", str(ev.code))
        source = getattr(ev, "source", "?")
        sev = getattr(ev, "severity", "?")
        ts = int(getattr(ev, "ts_us", 0))
        code_counts[code] += 1
        by_source[code][source] += 1
        sev_by_code[code][sev] += 1
        first_seen.setdefault(code, ts)
    clusters: dict = {}
    for code, count in code_counts.most_common():
        clusters[code] = {
            "count": count,
            "first_seen_us": first_seen[code],
            "by_source": dict(by_source[code]),
            "severities": dict(sev_by_code[code]),
        }
    return clusters


def triage_summary(events: Iterable, *, top_n: int = 3) -> str:
    """Return a DRAFT human-readable triage summary."""
    clusters = cluster_log_events(events)
    if not clusters:
        return "DRAFT triage: no events recorded during this run."
    lines = ["DRAFT triage summary (rule-based, human review required):"]
    for i, (code, info) in enumerate(list(clusters.items())[:top_n], 1):
        top_src = max(info["by_source"].items(), key=lambda kv: kv[1])[0]
        sev = max(info["severities"].items(), key=lambda kv: kv[1])[0]
        lines.append(
            f"  {i}. {code}: count={info['count']} "
            f"primary_source={top_src} worst_severity={sev} "
            f"first_seen_us={info['first_seen_us']}"
        )
    remainder = len(clusters) - top_n
    if remainder > 0:
        lines.append(f"  ... and {remainder} more cluster(s)")
    return "\n".join(lines)
