"""HIL-lite bridge — deterministic loopback to a simulated MCU.

A real HIL uses a physical board over UART/UDP. For portability we model the
MCU with a ``LoopbackMcu`` class whose behaviour (latency, jitter, drop,
reboot, brownout) is controlled by ``HilFaults``. Everything is driven by the
shared ``SimClock`` so the bridge is reproducible.

Protocol (in-process):
  HIL_SYNC    sim -> mcu    tick id + sim time (latches local clock)
  HIL_INPUT   sim -> mcu    (pitch, roll, yaw) command
  HIL_OUTPUT  mcu -> sim    actuator feedback
  HIL_HEALTH  mcu -> sim    cycle counter + miss count

Measurements:
  end-to-end latency (input publish -> output ack)
  cycle jitter (interval between HIL_SYNC messages)
  drop count, reboot count
"""
from __future__ import annotations
from dataclasses import dataclass, field
from statistics import mean, pstdev


@dataclass
class HilFaults:
    latency_us: int = 0        # constant delay per round-trip
    jitter_us: int = 0         # added on every odd cycle (deterministic)
    drop_every_n: int = 0      # every Nth INPUT dropped
    reboot_at_cycle: int = -1  # one-shot reboot at this cycle index
    brownout_cycles: int = 0   # number of cycles after reboot before MCU responds


@dataclass
class HilMeasurement:
    latencies_us: list[int] = field(default_factory=list)
    cycle_gaps_us: list[int] = field(default_factory=list)
    drops: int = 0
    reboots: int = 0

    def summary(self) -> dict:
        lat = self.latencies_us or [0]
        gaps = self.cycle_gaps_us or [0]
        return {
            "cycles": len(self.latencies_us),
            "latency_mean_us": round(mean(lat), 2),
            "latency_max_us": max(lat),
            "jitter_stddev_us": round(pstdev(gaps), 2) if len(gaps) > 1 else 0.0,
            "drops": self.drops,
            "reboots": self.reboots,
        }


@dataclass
class HilSync:
    cycle: int
    sim_time_us: int


@dataclass
class LoopbackMcu:
    """In-process MCU surrogate: remembers last input and produces an output
    after an emulated processing delay."""
    faults: HilFaults = field(default_factory=HilFaults)
    alive: bool = True
    pending_inputs: list[tuple[int, int, tuple[float, float, float]]] = field(default_factory=list)
    # ^ (cycle, deliver_at_us, value)
    last_cycle: int = -1
    brownout_left: int = 0

    def recv_sync(self, sync: HilSync, now_us: int) -> None:
        if sync.cycle == self.faults.reboot_at_cycle and self.alive:
            self.alive = False
            self.brownout_left = max(1, self.faults.brownout_cycles)
            return
        if not self.alive:
            self.brownout_left -= 1
            if self.brownout_left <= 0:
                self.alive = True
        self.last_cycle = sync.cycle

    def recv_input(self, cycle: int, value: tuple[float, float, float],
                   now_us: int) -> bool:
        if not self.alive:
            return False
        base_latency = self.faults.latency_us
        if self.faults.jitter_us and (cycle % 2 == 1):
            base_latency += self.faults.jitter_us
        deliver_at = now_us + base_latency
        self.pending_inputs.append((cycle, deliver_at, value))
        return True

    def poll_output(self, now_us: int
                    ) -> tuple[int, int, tuple[float, float, float]] | None:
        """Return (cycle, deliver_at_us, value) if head-of-queue is due."""
        if not self.pending_inputs:
            return None
        cycle, due, value = self.pending_inputs[0]
        if due > now_us:
            return None
        self.pending_inputs.pop(0)
        return cycle, due, value


@dataclass
class HilBridge:
    mcu: LoopbackMcu = field(default_factory=LoopbackMcu)
    measurement: HilMeasurement = field(default_factory=HilMeasurement)
    _cycle: int = 0
    _last_sync_us: int = -1
    _outstanding: dict[int, int] = field(default_factory=dict)  # cycle -> sent_us

    def tick(self, now_us: int, cmd: tuple[float, float, float]) -> None:
        """Run one sim <-> MCU exchange."""
        # jitter measurement on SYNC gap
        if self._last_sync_us >= 0:
            self.measurement.cycle_gaps_us.append(now_us - self._last_sync_us)
        self._last_sync_us = now_us

        sync = HilSync(cycle=self._cycle, sim_time_us=now_us)
        prev_alive = self.mcu.alive
        self.mcu.recv_sync(sync, now_us)
        if prev_alive and not self.mcu.alive:
            self.measurement.reboots += 1

        # drop pattern
        drop_n = self.mcu.faults.drop_every_n
        dropped = drop_n > 0 and ((self._cycle + 1) % drop_n == 0)
        if dropped:
            self.measurement.drops += 1
        else:
            accepted = self.mcu.recv_input(self._cycle, cmd, now_us)
            if accepted:
                self._outstanding[self._cycle] = now_us
            else:
                self.measurement.drops += 1

        # poll output(s) due at this now — measure latency from the actual
        # delivery timestamp, not the polling moment, so granularity is the
        # MCU delay, not the sim tick period.
        while True:
            out = self.mcu.poll_output(now_us)
            if out is None:
                break
            cycle, due, _value = out
            sent = self._outstanding.pop(cycle, None)
            if sent is not None:
                self.measurement.latencies_us.append(due - sent)

        self._cycle += 1

    def drain(self, now_us: int) -> None:
        """Flush any outputs already due up to ``now_us``."""
        while True:
            out = self.mcu.poll_output(now_us)
            if out is None:
                break
            cycle, due, _ = out
            sent = self._outstanding.pop(cycle, None)
            if sent is not None:
                self.measurement.latencies_us.append(due - sent)
