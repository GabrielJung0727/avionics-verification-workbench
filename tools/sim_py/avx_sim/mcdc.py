"""MC/DC condition tracker for designated decisions.

Pure data sink: modules call ``McdcTracker.record(name, conditions, outcome)``
inside designated decision points. The tracker is **off by default** so that
production runs incur zero cost; the verification runner enables it via
``McdcTracker.enable()``.

Pair detection follows the textbook MC/DC definition: for each condition,
find two test cases that differ only in that condition and produce different
decision outcomes.
"""
from __future__ import annotations
from typing import Iterable


class McdcTracker:
    enabled: bool = False
    decisions: dict[str, list[tuple[tuple[bool, ...], bool]]] = {}

    @classmethod
    def enable(cls) -> None:
        cls.enabled = True

    @classmethod
    def disable(cls) -> None:
        cls.enabled = False

    @classmethod
    def reset(cls) -> None:
        cls.decisions = {}

    @classmethod
    def record(cls, name: str, conditions: Iterable[bool], outcome: bool
               ) -> None:
        if not cls.enabled:
            return
        cls.decisions.setdefault(name, []).append(
            (tuple(bool(c) for c in conditions), bool(outcome))
        )

    @classmethod
    def report(cls) -> dict[str, dict]:
        out: dict[str, dict] = {}
        for name, samples in cls.decisions.items():
            if not samples:
                continue
            n_conds = len(samples[0][0])
            unique = list(dict.fromkeys(samples))   # stable order
            covered = []
            for k in range(n_conds):
                found = False
                for i in range(len(unique)):
                    a, oa = unique[i]
                    for j in range(i + 1, len(unique)):
                        b, ob = unique[j]
                        if a[k] == b[k]:
                            continue
                        if oa == ob:
                            continue
                        if all(a[m] == b[m] for m in range(n_conds) if m != k):
                            found = True
                            break
                    if found:
                        break
                covered.append(found)
            out[name] = {
                "conditions": n_conds,
                "covered_conditions": sum(covered),
                "pct": (sum(covered) / n_conds) if n_conds else 0.0,
                "samples": len(samples),
                "unique_rows": len(unique),
                "per_condition": covered,
            }
        return out
