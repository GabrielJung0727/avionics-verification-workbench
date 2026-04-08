"""Deterministic simulation clock — single source of time for the workbench."""
from __future__ import annotations


class SimClock:
    """Monotonic, manually advanced clock in microseconds.

    Wall-clock dependence is forbidden anywhere in the workbench (SYS-001/016).
    """

    def __init__(self) -> None:
        self._now_us: int = 0

    @property
    def now_us(self) -> int:
        return self._now_us

    def advance(self, delta_us: int) -> None:
        if delta_us < 0:
            raise ValueError("clock cannot go backwards")
        self._now_us += delta_us

    def reset(self) -> None:
        self._now_us = 0
