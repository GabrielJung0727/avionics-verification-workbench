"""Sampling and queuing IPC ports with freshness and overflow semantics."""
from __future__ import annotations
from collections import deque
from dataclasses import dataclass, field
from typing import Generic, TypeVar

from .health_monitor import HealthMonitor, HmEvent

T = TypeVar("T")


@dataclass
class SamplingPort(Generic[T]):
    """Holds latest value with publish timestamp; freshness budget enforced
    on read."""
    name: str
    freshness_budget_us: int
    hm: HealthMonitor | None = None
    _value: T | None = None
    _ts_us: int = -1

    def write(self, value: T, now_us: int) -> None:
        self._value = value
        self._ts_us = now_us

    def read(self, now_us: int) -> tuple[T | None, bool]:
        """Return (value, fresh)."""
        if self._ts_us < 0:
            return (None, False)
        fresh = (now_us - self._ts_us) <= self.freshness_budget_us
        if not fresh and self.hm is not None:
            self.hm.record(now_us, self.name, HmEvent.IPC_STALE, "MED",
                           f"age={now_us - self._ts_us}us")
        return (self._value, fresh)


@dataclass
class QueuingPort(Generic[T]):
    name: str
    capacity: int
    hm: HealthMonitor | None = None
    _q: deque = field(default_factory=deque)

    def push(self, value: T, now_us: int) -> bool:
        if len(self._q) >= self.capacity:
            if self.hm is not None:
                self.hm.record(now_us, self.name, HmEvent.IPC_OVERFLOW, "MED",
                               f"cap={self.capacity}")
            return False
        self._q.append(value)
        return True

    def pop(self) -> T | None:
        if not self._q:
            return None
        return self._q.popleft()

    def __len__(self) -> int:
        return len(self._q)
