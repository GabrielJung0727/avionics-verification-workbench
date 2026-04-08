"""Display Computer — HLR-DSP-001..007.

The display has no real GUI; it produces a structured ``DisplayFrame`` per
``render`` call that downstream tests / human-factors evaluators can inspect.

Implements:
  HLR-DSP-001  alert priority WARNING > CAUTION > ADVISORY
  HLR-DSP-002  red/amber/green color rule (token mapping + static check)
  HLR-DSP-003  mode annunciation update within 100 ms of FCC notice
  HLR-DSP-004  cap visible alerts and summarize the rest
  HLR-DSP-005  dashed value on stale input
  HLR-DSP-006  keep mode history for N seconds
  HLR-DSP-007  measure own refresh rate
"""
from __future__ import annotations
from collections import deque
from dataclasses import dataclass, field

from ..messages import (
    AlertLevel,
    EngineExceed,
    EngineParams,
    FccMode,
    FccModeMsg,
    Freshness,
)


COLOR_RULE = {
    AlertLevel.WARNING: "RED",
    AlertLevel.CAUTION: "AMBER",
    AlertLevel.ADVISORY: "GREEN",
}


@dataclass(frozen=True)
class AlertEntry:
    ts_us: int
    level: AlertLevel
    text: str
    color: str


@dataclass
class DisplayFrame:
    ts_us: int
    mode: FccMode
    mode_color: str
    alerts: list[AlertEntry]
    summarized: int
    n1: float | str
    egt: float | str
    ias: float | str
    refresh_dt_us: int


@dataclass
class DisplayComputer:
    max_alerts: int = 5
    history_window_us: int = 5_000_000
    mode_latency_budget_us: int = 100_000
    mode: FccMode = FccMode.OFF
    mode_color: str = "GREEN"
    _last_render_us: int = -1
    _last_mode_change_seen_us: int = -1
    _last_mode_msg_ts: int = -1
    _alerts: list[AlertEntry] = field(default_factory=list)
    _ias: float | None = None
    _ias_ts_us: int = -1
    _engine: EngineParams | None = None
    _mode_history: deque = field(default_factory=lambda: deque())
    mode_latency_violations: int = 0

    def _add_alert(self, level: AlertLevel, text: str, ts_us: int) -> None:
        self._alerts.append(AlertEntry(ts_us=ts_us, level=level, text=text,
                                       color=COLOR_RULE[level]))

    def receive_mode(self, msg: FccModeMsg, now_us: int) -> None:
        self._last_mode_msg_ts = msg.ts_us
        self._last_mode_change_seen_us = now_us
        latency = now_us - msg.ts_us
        if latency > self.mode_latency_budget_us:
            self.mode_latency_violations += 1
        self.mode = msg.mode
        self.mode_color = COLOR_RULE[
            AlertLevel.WARNING if msg.mode == FccMode.DIRECT
            else AlertLevel.CAUTION if msg.mode == FccMode.ALTERNATE
            else AlertLevel.ADVISORY
        ]
        self._mode_history.append((now_us, msg.mode))

    def receive_engine_params(self, params: EngineParams, now_us: int) -> None:
        self._engine = params

    def receive_engine_exceed(self, ev: EngineExceed) -> None:
        self._add_alert(ev.level, f"{ev.param}={ev.value:.1f}", ev.ts_us)

    def receive_air_data(self, ias: float, ts_us: int,
                         freshness: Freshness) -> None:
        if freshness == Freshness.OK:
            self._ias = ias
            self._ias_ts_us = ts_us
        else:
            self._ias = None  # HLR-DSP-005 → dashed

    # ---- render ----------------------------------------------------------
    def render(self, now_us: int) -> DisplayFrame:
        # prune mode history
        cutoff = now_us - self.history_window_us
        while self._mode_history and self._mode_history[0][0] < cutoff:
            self._mode_history.popleft()

        # HLR-DSP-001: priority sort (highest level first, newest within level)
        ranked = sorted(self._alerts,
                        key=lambda a: (-int(a.level), -a.ts_us))
        # HLR-DSP-004: cap and summarize
        visible = ranked[: self.max_alerts]
        summarized = max(0, len(ranked) - self.max_alerts)

        # HLR-DSP-007: refresh dt
        refresh_dt = (now_us - self._last_render_us) if self._last_render_us >= 0 else 0
        self._last_render_us = now_us

        n1 = self._engine.n1 if self._engine else "----"
        egt = self._engine.egt if self._engine else "----"
        ias_disp = self._ias if self._ias is not None else "----"

        return DisplayFrame(
            ts_us=now_us,
            mode=self.mode,
            mode_color=self.mode_color,
            alerts=visible,
            summarized=summarized,
            n1=n1,
            egt=egt,
            ias=ias_disp,
            refresh_dt_us=refresh_dt,
        )

    # ---- HLR-DSP-002 static color check ---------------------------------
    @staticmethod
    def static_color_check(tokens: dict[AlertLevel, str]) -> list[str]:
        """Return a list of violations (empty list = pass)."""
        bad = []
        if tokens.get(AlertLevel.WARNING) != "RED":
            bad.append("WARNING must be RED")
        if tokens.get(AlertLevel.CAUTION) != "AMBER":
            bad.append("CAUTION must be AMBER")
        if tokens.get(AlertLevel.ADVISORY) != "GREEN":
            bad.append("ADVISORY must be GREEN")
        return bad
