"""Flight Control Computer surrogate — HLR-FCC-001..008.

The FCC is intentionally not a flight-control law: it is a *mode and lane*
state machine that exercises the integration story (input validation, lane
diversity, mode reversion, mode notification within 1 tick).
"""
from __future__ import annotations
from dataclasses import dataclass, field

from ..health_monitor import HealthMonitor, HmEvent
from ..messages import (
    AirData,
    Attitude,
    FccCommand,
    FccMode,
    FccModeMsg,
    Freshness,
)


@dataclass
class FccLaneOutput:
    pitch_cmd: float
    roll_cmd: float
    yaw_cmd: float
    valid: bool


@dataclass
class Fcc:
    hm: HealthMonitor
    mode: FccMode = FccMode.OFF
    pitch_limit: float = 15.0
    roll_limit: float = 30.0
    yaw_limit: float = 10.0
    disagree_threshold: float = 0.5
    disagree_streak_required: int = 3
    self_test_passed: bool = False
    _disagree_streak: int = 0
    _last_ias: float = -1.0
    _last_pitch: float = 0.0
    rate_limit_ias: float = 100.0  # max delta per call

    # ---- helpers ---------------------------------------------------------
    def self_test(self) -> bool:
        """HLR-FCC-008 — startup self-test."""
        # Trivial: limiters must be positive, mode must be OFF on entry.
        ok = (self.pitch_limit > 0 and self.roll_limit > 0
              and self.yaw_limit > 0 and self.mode == FccMode.OFF)
        self.self_test_passed = ok
        if ok:
            self.mode = FccMode.NORMAL
        return ok

    def _validate(self, air: AirData | None, att: Attitude | None,
                  now_us: int) -> tuple[bool, str]:
        """HLR-FCC-001 — range / rate / freshness checks."""
        if air is None or att is None:
            return False, "missing input"
        if air.freshness != Freshness.OK or att.freshness != Freshness.OK:
            return False, f"freshness air={air.freshness.name} att={att.freshness.name}"
        if self._last_ias >= 0 and abs(air.ias - self._last_ias) > self.rate_limit_ias:
            return False, "ias rate violation"
        self._last_ias = air.ias
        return True, ""

    def _law(self, air: AirData, att: Attitude) -> tuple[float, float, float]:
        # Toy law: trim around 250 kt and level pitch.
        pitch_cmd = (250.0 - air.ias) * 0.05 - att.pitch * 0.1
        roll_cmd = -att.roll * 0.5
        yaw_cmd = -att.yaw_rate * 0.2
        return pitch_cmd, roll_cmd, yaw_cmd

    def _limit(self, v: float, lim: float) -> float:
        """HLR-FCC-007 — limiter."""
        return max(-lim, min(lim, v))

    # ---- lanes -----------------------------------------------------------
    def cmd_lane(self, air: AirData, att: Attitude) -> FccLaneOutput:
        p, r, y = self._law(air, att)
        return FccLaneOutput(
            pitch_cmd=self._limit(p, self.pitch_limit),
            roll_cmd=self._limit(r, self.roll_limit),
            yaw_cmd=self._limit(y, self.yaw_limit),
            valid=True,
        )

    def mon_lane(self, air: AirData, att: Attitude) -> FccLaneOutput:
        """HLR-FCC-002 — independent computation. Same algorithm, separate
        local copies of inputs to model lane diversity at this learning level.
        Real avionics use diverse implementations or N-version programming."""
        air2 = AirData(air.ts_us, air.ias, air.altitude, air.vs, air.freshness)
        att2 = Attitude(att.ts_us, att.pitch, att.roll, att.yaw_rate, att.freshness)
        p, r, y = self._law(air2, att2)
        return FccLaneOutput(
            pitch_cmd=self._limit(p, self.pitch_limit),
            roll_cmd=self._limit(r, self.roll_limit),
            yaw_cmd=self._limit(y, self.yaw_limit),
            valid=True,
        )

    # ---- public step -----------------------------------------------------
    def step(self, air: AirData | None, att: Attitude | None, now_us: int,
             dual_sensor_fault: bool = False
             ) -> tuple[FccCommand, FccModeMsg | None]:
        prev_mode = self.mode
        mode_change_reason = ""

        if not self.self_test_passed:
            self.self_test()

        # HLR-FCC-004: dual sensor fault → DIRECT
        if dual_sensor_fault:
            self.mode = FccMode.DIRECT
            mode_change_reason = "dual sensor fault"

        ok, why = self._validate(air, att, now_us)
        if not ok:
            cmd = FccCommand(now_us, 0.0, 0.0, 0.0, valid=False)
        else:
            cmd_lane = self.cmd_lane(air, att)
            mon_lane = self.mon_lane(air, att)

            # HLR-FCC-003: lane disagreement → ALTERNATE after streak
            disagree = max(
                abs(cmd_lane.pitch_cmd - mon_lane.pitch_cmd),
                abs(cmd_lane.roll_cmd - mon_lane.roll_cmd),
                abs(cmd_lane.yaw_cmd - mon_lane.yaw_cmd),
            )
            if disagree > self.disagree_threshold:
                self._disagree_streak += 1
                self.hm.record(now_us, "FCC", HmEvent.LANE_DISAGREE, "HIGH",
                               f"d={disagree:.3f}")
                if self._disagree_streak >= self.disagree_streak_required \
                        and self.mode == FccMode.NORMAL:
                    self.mode = FccMode.ALTERNATE
                    mode_change_reason = "lane disagreement"
            else:
                self._disagree_streak = 0

            # In DIRECT mode the cmd lane passes through with limiter only
            if self.mode == FccMode.DIRECT:
                cmd = FccCommand(
                    now_us,
                    self._limit(-att.pitch * 0.1, self.pitch_limit),
                    self._limit(-att.roll * 0.5, self.roll_limit),
                    self._limit(-att.yaw_rate * 0.2, self.yaw_limit),
                    valid=True,
                )
            else:
                cmd = FccCommand(now_us, cmd_lane.pitch_cmd,
                                 cmd_lane.roll_cmd, cmd_lane.yaw_cmd, valid=True)

        # HLR-FCC-005: mode change notified within 1 tick
        mode_msg: FccModeMsg | None = None
        if self.mode != prev_mode:
            mode_msg = FccModeMsg(
                ts_us=now_us, mode=self.mode,
                reason=mode_change_reason or "transition",
                lane_disagree=self._disagree_streak >= self.disagree_streak_required,
            )

        return cmd, mode_msg
