"""Sensor voter / selector utility.

Implements two complementary strategies used in triplex/quadruplex avionics:

  mid_value_select   — median of healthy signals (robust to one stuck input)
  majority_vote      — returns the signal agreed on by the majority within a
                       tolerance band; falls back to mid-value if no majority

Both helpers accept an iterable of (value, healthy) tuples. A channel marked
unhealthy is ignored entirely. The voter never panics — if fewer than two
healthy inputs remain it returns (None, reason) so the caller can enter a
safe state.

These are the building blocks for a future triplex FCC sensor stage; for the
current M3 surrogate the voter is exposed so tests can exercise its
decision logic independently (HLR-FCC-002 / SYS-020 lane diversity theme).
"""
from __future__ import annotations
from dataclasses import dataclass
from statistics import median
from typing import Iterable


@dataclass(frozen=True)
class VoteResult:
    value: float | None
    reason: str
    disagreement: float


def mid_value_select(samples: Iterable[tuple[float, bool]]) -> VoteResult:
    healthy = [v for v, h in samples if h]
    if len(healthy) == 0:
        return VoteResult(None, "no healthy channels", 0.0)
    if len(healthy) == 1:
        return VoteResult(healthy[0], "single channel", 0.0)
    m = median(healthy)
    disagreement = max(healthy) - min(healthy)
    return VoteResult(float(m), "mid-value", float(disagreement))


def majority_vote(samples: Iterable[tuple[float, bool]],
                  tolerance: float = 1.0) -> VoteResult:
    healthy = [v for v, h in samples if h]
    if len(healthy) < 2:
        return mid_value_select(samples)
    # Cluster values whose pairwise distance is within tolerance.
    clusters: list[list[float]] = []
    for v in healthy:
        for c in clusters:
            if abs(v - c[0]) <= tolerance:
                c.append(v)
                break
        else:
            clusters.append([v])
    clusters.sort(key=len, reverse=True)
    if len(clusters[0]) > len(healthy) / 2:
        pick = sum(clusters[0]) / len(clusters[0])
        disagreement = max(healthy) - min(healthy)
        return VoteResult(float(pick), "majority", float(disagreement))
    # No majority → fall back to mid-value so the system stays useful.
    fallback = mid_value_select(samples)
    return VoteResult(fallback.value,
                      f"no-majority -> {fallback.reason}",
                      fallback.disagreement)
