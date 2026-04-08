"""Cooperative IMA-style partitioned scheduler.

Deterministic: same partition table + same partition bodies + same seed
yields the same execution trace and the same Recorder hash.

Implements:
  SYS-001 deterministic tick
  SYS-029 partition budget enforcement -> PARTITION_OVERRUN
  HLR-HM-001 deadline miss collection
  HLR-HM-004 partition restart
  HLR-HM-005 cold / warm start transition
  SYS-011 cold and warm start sequences
  per-partition jitter / latency statistics (M2 carry-over)

A partition body receives the current sim time and returns nothing; the
partition's ``simulated_exec_us`` attribute models the execution duration
without relying on wall-clock measurement so every run is reproducible.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from statistics import mean, pstdev
from typing import Callable

from .sim_clock import SimClock
from .health_monitor import HealthMonitor, HmEvent


PartitionBody = Callable[[int], None]


class PartitionState(Enum):
    STOPPED = "STOPPED"
    RUNNING = "RUNNING"
    RESTARTING = "RESTARTING"


class SystemState(Enum):
    OFF = "OFF"
    COLD_START = "COLD_START"
    WARM_START = "WARM_START"
    OPERATIONAL = "OPERATIONAL"
    SHUTDOWN = "SHUTDOWN"


@dataclass
class PartitionStats:
    activations: int = 0
    overruns: int = 0
    deadline_misses: int = 0
    restarts: int = 0
    exec_samples_us: list[int] = field(default_factory=list)
    period_gaps_us: list[int] = field(default_factory=list)

    def summary(self) -> dict:
        exec_s = self.exec_samples_us or [0]
        gaps = self.period_gaps_us or [0]
        return {
            "activations": self.activations,
            "overruns": self.overruns,
            "deadline_misses": self.deadline_misses,
            "restarts": self.restarts,
            "exec_mean_us": round(mean(exec_s), 2),
            "exec_max_us": max(exec_s),
            "period_jitter_us": round(pstdev(gaps), 2) if len(gaps) > 1 else 0.0,
        }


@dataclass
class Partition:
    id: str
    period_us: int
    budget_us: int
    offset_us: int
    criticality: str
    body: PartitionBody
    simulated_exec_us: int = 0
    state: PartitionState = PartitionState.RUNNING
    last_run_us: int = -1
    stats: PartitionStats = field(default_factory=PartitionStats)
    # back-compat fields kept for any previous consumers
    activations: int = 0
    overruns: int = 0


@dataclass
class Scheduler:
    clock: SimClock
    hm: HealthMonitor
    tick_us: int = 1000          # default 1 ms minor frame
    partitions: list[Partition] = field(default_factory=list)
    system_state: SystemState = SystemState.OFF
    # per-partition restart bookkeeping
    _skip_until: dict[str, int] = field(default_factory=dict)

    def add_partition(self, p: Partition) -> None:
        if p.period_us % self.tick_us != 0:
            raise ValueError(f"{p.id}: period {p.period_us} not aligned to tick {self.tick_us}")
        if p.offset_us % self.tick_us != 0:
            raise ValueError(f"{p.id}: offset {p.offset_us} not aligned to tick {self.tick_us}")
        if p.budget_us > p.period_us:
            raise ValueError(f"{p.id}: budget exceeds period")
        self.partitions.append(p)

    # ---- lifecycle -------------------------------------------------------
    def cold_start(self) -> None:
        """SYS-011 — reset every partition and transition OFF -> OPERATIONAL."""
        self.system_state = SystemState.COLD_START
        for p in self.partitions:
            p.state = PartitionState.RUNNING
            p.last_run_us = -1
            p.stats = PartitionStats()
        self._skip_until.clear()
        self.system_state = SystemState.OPERATIONAL

    def warm_start(self) -> None:
        """SYS-011 — preserve latch state, only clear transient counters."""
        self.system_state = SystemState.WARM_START
        for p in self.partitions:
            p.state = PartitionState.RUNNING
        self._skip_until.clear()
        self.system_state = SystemState.OPERATIONAL

    def shutdown(self) -> None:
        self.system_state = SystemState.SHUTDOWN
        for p in self.partitions:
            p.state = PartitionState.STOPPED

    def restart_partition(self, partition_id: str, *, brownout_ticks: int = 2) -> None:
        """HLR-HM-004 — partition restart with brief brownout window."""
        for p in self.partitions:
            if p.id == partition_id:
                p.state = PartitionState.RESTARTING
                p.stats.restarts += 1
                p.last_run_us = -1
                self._skip_until[p.id] = self.clock.now_us + brownout_ticks * self.tick_us
                self.hm.record(self.clock.now_us, p.id, HmEvent.MODULE_RESTART,
                               "HIGH", f"brownout={brownout_ticks}ticks")
                return
        raise KeyError(f"unknown partition: {partition_id}")

    # ---- run loop --------------------------------------------------------
    def run_for(self, duration_us: int) -> None:
        if self.system_state == SystemState.OFF:
            self.cold_start()
        end = self.clock.now_us + duration_us
        while self.clock.now_us < end:
            now = self.clock.now_us
            for p in self.partitions:
                if p.state == PartitionState.STOPPED:
                    continue
                skip_until = self._skip_until.get(p.id, 0)
                if now < skip_until:
                    continue
                if p.state == PartitionState.RESTARTING and now >= skip_until:
                    p.state = PartitionState.RUNNING
                if (now - p.offset_us) % p.period_us == 0 and now >= p.offset_us:
                    self._activate(p, now)
            self.clock.advance(self.tick_us)

    def _activate(self, p: Partition, now_us: int) -> None:
        if p.last_run_us >= 0:
            gap = now_us - p.last_run_us
            p.stats.period_gaps_us.append(gap)
            if gap > p.period_us:
                p.stats.deadline_misses += 1
                self.hm.record(now_us, p.id, HmEvent.DEADLINE_MISS, "HIGH",
                               f"gap={gap}us")
        p.last_run_us = now_us
        p.stats.activations += 1
        p.activations = p.stats.activations
        p.body(now_us)
        p.stats.exec_samples_us.append(p.simulated_exec_us)
        if p.simulated_exec_us > p.budget_us:
            p.stats.overruns += 1
            p.overruns = p.stats.overruns
            self.hm.record(now_us, p.id, HmEvent.PARTITION_OVERRUN, "HIGH",
                           f"exec={p.simulated_exec_us}us budget={p.budget_us}us")

    # ---- reporting -------------------------------------------------------
    def stats_report(self) -> dict:
        return {p.id: p.stats.summary() for p in self.partitions}
