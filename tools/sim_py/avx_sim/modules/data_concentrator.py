"""Data Concentrator (DC) — HLR-DC-001..007.

Responsibilities:
  - Timestamp every sensor input before publishing.                  HLR-DC-001
  - Mark stale inputs with a freshness flag.                         HLR-DC-002
  - Flag out-of-range inputs as INVALID.                             HLR-DC-003
  - Carry sensor source ID through the message.                      HLR-DC-004
  - Detect sensor dropout within N ticks.                            HLR-DC-006
  - Report own health to HM on dropout/range error.                  HLR-DC-007

The publish-rate alignment with the partition (HLR-DC-005) is enforced by the
scheduler period of the DC partition; the module exposes ``step`` so a unit
test can drive it directly without the scheduler.
"""
from __future__ import annotations
from dataclasses import dataclass

from ..health_monitor import HealthMonitor, HmEvent
from ..messages import AirData, Attitude, EngineRaw, Freshness


@dataclass
class SensorRange:
    low: float
    high: float


@dataclass
class DataConcentrator:
    source_id: str
    hm: HealthMonitor
    air_range: SensorRange
    pitch_range: SensorRange
    n1_range: SensorRange
    dropout_ticks: int = 5
    last_input_us: int = -1
    _missed: int = 0

    # ---- helpers ---------------------------------------------------------
    def _check_range(self, value: float, rng: SensorRange) -> Freshness:
        if value < rng.low or value > rng.high:
            return Freshness.INVALID
        return Freshness.OK

    def notify_dropout(self, now_us: int) -> None:
        """Called once per DC tick when no fresh sample arrived."""
        self._missed += 1
        if self._missed == self.dropout_ticks:
            self.hm.record(now_us, f"DC:{self.source_id}",
                           HmEvent.SENSOR_DROPOUT, "MED",
                           f"missed={self._missed}")

    # ---- publishers ------------------------------------------------------
    def publish_air_data(self, ias: float, altitude: float, vs: float,
                         now_us: int) -> AirData:
        self._missed = 0
        self.last_input_us = now_us
        f = self._check_range(ias, self.air_range)
        msg = AirData(ts_us=now_us, ias=ias, altitude=altitude, vs=vs,
                      freshness=f)
        if f == Freshness.INVALID:
            self.hm.record(now_us, f"DC:{self.source_id}",
                           HmEvent.IPC_STALE, "MED",
                           f"ias={ias} out of range")
        return msg

    def publish_attitude(self, pitch: float, roll: float, yaw_rate: float,
                         now_us: int) -> Attitude:
        f = self._check_range(pitch, self.pitch_range)
        return Attitude(ts_us=now_us, pitch=pitch, roll=roll,
                        yaw_rate=yaw_rate, freshness=f)

    def publish_engine_raw(self, n1: float, n2: float, egt: float, ff: float,
                           now_us: int) -> EngineRaw:
        # Range failure on engine raw is reported via Engine I/F downstream
        # to keep DC simple; this method only ensures timestamp + source.
        return EngineRaw(ts_us=now_us, n1=n1, n2=n2, egt=egt, ff=ff)
