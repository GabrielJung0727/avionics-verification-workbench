"""Engine Interface — HLR-ENG-001..007.

Limit table is loaded from a config dict. Each parameter has caution/warning/
exceed thresholds and a hysteresis band; once latched, an exceedance stays
latched until the end of the run (HLR-ENG-004). Hot/hung start patterns are
detected over a startup window using EGT rise rate and N2 acceleration.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import IntEnum

from ..health_monitor import HealthMonitor, HmEvent
from ..mcdc import McdcTracker
from ..messages import (
    AlertLevel,
    EngineExceed,
    EngineParams,
    EngineRaw,
)


class LimitState(IntEnum):
    NORMAL = 0
    CAUTION = 1
    WARNING = 2
    EXCEED = 3


@dataclass
class ParamLimit:
    caution: float
    warning: float
    exceed: float
    hysteresis: float


@dataclass
class EngineLimits:
    n1: ParamLimit
    n2: ParamLimit
    egt: ParamLimit
    ff: ParamLimit

    @classmethod
    def default(cls) -> "EngineLimits":
        return cls(
            n1=ParamLimit(100, 103, 105, 1.0),
            n2=ParamLimit(100, 104, 106, 1.0),
            egt=ParamLimit(850, 900, 950, 10.0),
            ff=ParamLimit(3500, 3800, 4000, 50.0),
        )


@dataclass
class EngineInterface:
    hm: HealthMonitor
    limits: EngineLimits = field(default_factory=EngineLimits.default)
    # latch state per parameter
    latched: dict[str, AlertLevel] = field(default_factory=dict)
    # rise rate tracking
    last_egt: float = -1.0
    last_egt_us: int = -1
    last_n2: float = -1.0
    last_n2_us: int = -1
    in_startup: bool = True
    startup_end_us: int = 30_000_000  # 30 s
    hot_start_egt_rate: float = 200.0   # degC/sec
    hung_start_n2_rate: float = 0.5     # %/sec minimum

    def _classify(self, value: float, lim: ParamLimit) -> AlertLevel:
        if value >= lim.exceed:
            return AlertLevel.WARNING
        if value >= lim.warning:
            return AlertLevel.WARNING
        if value >= lim.caution:
            return AlertLevel.CAUTION
        return AlertLevel.ADVISORY

    def _update_latch(self, param: str, level: AlertLevel) -> AlertLevel:
        """Latch promotion. MC/DC instrumented on two independent conditions:
          c1 = level > previous_latched
          c2 = level >= WARNING (annunciate-worthy)
        outcome = c1 and c2 (should we *promote and annunciate*)"""
        prev = self.latched.get(param, AlertLevel.ADVISORY)
        c1 = level > prev
        c2 = level >= AlertLevel.WARNING
        outcome = c1 and c2
        McdcTracker.record("engine.latch_promote", (c1, c2), outcome)
        if c1:
            self.latched[param] = level
            return level
        return prev

    def step(self, raw: EngineRaw, now_us: int
             ) -> tuple[EngineParams, list[EngineExceed]]:
        events: list[EngineExceed] = []

        for name, value, lim in (
            ("n1", raw.n1, self.limits.n1),
            ("n2", raw.n2, self.limits.n2),
            ("egt", raw.egt, self.limits.egt),
            ("ff", raw.ff, self.limits.ff),
        ):
            level = self._classify(value, lim)
            if level >= AlertLevel.CAUTION:
                latched = self._update_latch(name, level)
                events.append(EngineExceed(
                    ts_us=now_us, param=name, level=latched,
                    value=value, latched=True,
                ))
                self.hm.record(now_us, "ENG", HmEvent.MODULE_RESTART
                               if level == AlertLevel.WARNING else HmEvent.IPC_STALE,
                               "HIGH" if level == AlertLevel.WARNING else "MED",
                               f"{name}={value} level={level.name}")

        # hot start: EGT rate too high during startup window
        if now_us <= self.startup_end_us and self.last_egt_us >= 0:
            dt_s = max(1e-6, (now_us - self.last_egt_us) / 1_000_000)
            rate = (raw.egt - self.last_egt) / dt_s
            if rate > self.hot_start_egt_rate:
                events.append(EngineExceed(
                    ts_us=now_us, param="egt_rate",
                    level=AlertLevel.WARNING, value=rate, latched=True,
                ))
                self.latched["hot_start"] = AlertLevel.WARNING

        # hung start: N2 acceleration too low during startup window
        if now_us <= self.startup_end_us and self.last_n2_us >= 0:
            dt_s = max(1e-6, (now_us - self.last_n2_us) / 1_000_000)
            rate = (raw.n2 - self.last_n2) / dt_s
            if 0 <= rate < self.hung_start_n2_rate and raw.n2 < 60:
                events.append(EngineExceed(
                    ts_us=now_us, param="n2_rate",
                    level=AlertLevel.WARNING, value=rate, latched=True,
                ))
                self.latched["hung_start"] = AlertLevel.WARNING

        self.last_egt = raw.egt
        self.last_egt_us = now_us
        self.last_n2 = raw.n2
        self.last_n2_us = now_us

        worst = max(self.latched.values(), default=AlertLevel.ADVISORY)
        params = EngineParams(
            ts_us=now_us, n1=raw.n1, n2=raw.n2, egt=raw.egt, ff=raw.ff,
            state=worst,
        )
        return params, events
