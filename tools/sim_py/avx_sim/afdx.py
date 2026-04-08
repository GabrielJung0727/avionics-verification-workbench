"""AFDX-lite virtual link bus.

In-process implementation: each VL is a queue with deterministic delivery
ordered by enqueue ts. BAG (bandwidth allocation gap) enforced as a minimum
inter-frame interval per VL. Fault hooks (drop, delay, reorder) take an
``AfdxFaults`` config and a deterministic counter — no wall-clock RNG.
"""
from __future__ import annotations
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable

from .health_monitor import HealthMonitor, HmEvent


@dataclass
class AfdxFaults:
    drop_every_n: int = 0       # 0 disables
    delay_us: int = 0           # constant added latency
    reorder_every_n: int = 0    # swap with previous frame periodically


@dataclass
class VirtualLink:
    vl_id: int
    bag_us: int                 # bandwidth allocation gap
    name: str = ""
    faults: AfdxFaults = field(default_factory=AfdxFaults)
    _q: deque = field(default_factory=deque)   # (delivery_ts, payload)
    _last_send_us: int = -10**18
    _drop_counter: int = 0
    _reorder_counter: int = 0


@dataclass
class AfdxBus:
    hm: HealthMonitor | None = None
    links: dict[int, VirtualLink] = field(default_factory=dict)

    def add_link(self, vl: VirtualLink) -> None:
        self.links[vl.vl_id] = vl

    def send(self, vl_id: int, payload: Any, now_us: int) -> bool:
        vl = self.links[vl_id]
        if (now_us - vl._last_send_us) < vl.bag_us:
            # BAG violation: drop, count as overflow
            if self.hm is not None:
                self.hm.record(now_us, f"AFDX:{vl.name or vl_id}",
                               HmEvent.IPC_OVERFLOW, "MED", "BAG violation")
            return False
        vl._last_send_us = now_us

        # drop fault
        if vl.faults.drop_every_n > 0:
            vl._drop_counter += 1
            if vl._drop_counter % vl.faults.drop_every_n == 0:
                return False

        delivery_ts = now_us + max(0, vl.faults.delay_us)
        vl._q.append((delivery_ts, payload))

        # reorder fault: swap last two if scheduled
        if vl.faults.reorder_every_n > 0 and len(vl._q) >= 2:
            vl._reorder_counter += 1
            if vl._reorder_counter % vl.faults.reorder_every_n == 0:
                a = vl._q.pop()
                b = vl._q.pop()
                vl._q.append(a)
                vl._q.append(b)
        return True

    def receive_due(self, vl_id: int, now_us: int) -> list[Any]:
        vl = self.links[vl_id]
        out: list[Any] = []
        while vl._q and vl._q[0][0] <= now_us:
            out.append(vl._q.popleft()[1])
        return out
