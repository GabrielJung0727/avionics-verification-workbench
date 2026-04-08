"""Cooperative IMA-style partitioned scheduler (M2).

Deterministic: same partition table + same partition bodies + same seed
yields the same execution trace and the same Recorder hash.

Implements:
  SYS-001 deterministic tick
  SYS-029 partition budget enforcement → PARTITION_OVERRUN
  HLR-HM-001 deadline miss collection
  partition activation by (period, offset) on a sim tick
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable

from .sim_clock import SimClock
from .health_monitor import HealthMonitor, HmEvent


PartitionBody = Callable[[int], None]
"""Body signature: body(now_us) -> None.

The body may report its simulated execution time by returning normally; the
test/integration code sets ``simulated_exec_us`` on the partition descriptor
to model real execution duration without needing wall-clock measurement.
"""


@dataclass
class Partition:
    id: str
    period_us: int
    budget_us: int
    offset_us: int
    criticality: str
    body: PartitionBody
    simulated_exec_us: int = 0
    # internal
    last_run_us: int = -1
    activations: int = 0
    overruns: int = 0


@dataclass
class Scheduler:
    clock: SimClock
    hm: HealthMonitor
    tick_us: int = 1000          # default 1 ms minor frame
    partitions: list[Partition] = field(default_factory=list)

    def add_partition(self, p: Partition) -> None:
        if p.period_us % self.tick_us != 0:
            raise ValueError(f"{p.id}: period {p.period_us} not aligned to tick {self.tick_us}")
        if p.offset_us % self.tick_us != 0:
            raise ValueError(f"{p.id}: offset {p.offset_us} not aligned to tick {self.tick_us}")
        if p.budget_us > p.period_us:
            raise ValueError(f"{p.id}: budget exceeds period")
        self.partitions.append(p)

    def run_for(self, duration_us: int) -> None:
        end = self.clock.now_us + duration_us
        # Stable iteration order = insertion order = deterministic.
        while self.clock.now_us < end:
            now = self.clock.now_us
            for p in self.partitions:
                if (now - p.offset_us) % p.period_us == 0 and now >= p.offset_us:
                    self._activate(p, now)
            self.clock.advance(self.tick_us)

    def _activate(self, p: Partition, now_us: int) -> None:
        # Deadline miss check: previous activation should have completed
        # within its period. Modeled by comparing simulated_exec_us to budget.
        if p.last_run_us >= 0 and (now_us - p.last_run_us) > p.period_us:
            self.hm.record(now_us, p.id, HmEvent.DEADLINE_MISS, "HIGH",
                           f"gap={now_us - p.last_run_us}us")
        p.last_run_us = now_us
        p.activations += 1
        p.body(now_us)
        if p.simulated_exec_us > p.budget_us:
            p.overruns += 1
            self.hm.record(now_us, p.id, HmEvent.PARTITION_OVERRUN, "HIGH",
                           f"exec={p.simulated_exec_us}us budget={p.budget_us}us")
