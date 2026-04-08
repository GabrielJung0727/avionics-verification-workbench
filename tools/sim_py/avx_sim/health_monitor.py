"""Health Monitor — partition fault, deadline miss, IPC error collector.

Implements HLR-HM-001..006. Maps events to actions per a config dict.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable


class HmEvent(str, Enum):
    PARTITION_OVERRUN = "PARTITION_OVERRUN"
    DEADLINE_MISS = "DEADLINE_MISS"
    IPC_OVERFLOW = "IPC_OVERFLOW"
    IPC_STALE = "IPC_STALE"
    MODULE_RESTART = "MODULE_RESTART"
    LANE_DISAGREE = "LANE_DISAGREE"
    SENSOR_DROPOUT = "SENSOR_DROPOUT"
    HM_DEADLINE_MISS = "HM_DEADLINE_MISS"


@dataclass(frozen=True)
class HmRecord:
    ts_us: int
    source: str
    code: HmEvent
    severity: str
    detail: str = ""


@dataclass
class HealthMonitor:
    """Append-only event log with optional action callback hook."""
    table: dict[HmEvent, str] = field(default_factory=dict)
    events: list[HmRecord] = field(default_factory=list)
    on_action: Callable[[HmRecord, str], None] | None = None

    def record(self, ts_us: int, source: str, code: HmEvent,
               severity: str = "MED", detail: str = "") -> HmRecord:
        rec = HmRecord(ts_us=ts_us, source=source, code=code,
                       severity=severity, detail=detail)
        self.events.append(rec)
        action = self.table.get(code, "LOG")
        if self.on_action is not None:
            self.on_action(rec, action)
        return rec

    def count(self, code: HmEvent) -> int:
        return sum(1 for e in self.events if e.code == code)

    def reset(self) -> None:
        self.events.clear()
