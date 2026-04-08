"""HLR-DSP-001..007 unit tests."""
import unittest
from . import _paths  # noqa: F401

from avx_sim.messages import (
    AlertLevel,
    EngineExceed,
    EngineParams,
    FccMode,
    FccModeMsg,
    Freshness,
)
from avx_sim.modules import DisplayComputer


class TestDisplayComputer(unittest.TestCase):

    def test_HLR_DSP_001_alert_priority_order(self):
        d = DisplayComputer()
        d.receive_engine_exceed(EngineExceed(0, "egt", AlertLevel.CAUTION, 880, True))
        d.receive_engine_exceed(EngineExceed(1, "n1", AlertLevel.WARNING, 105, True))
        d.receive_engine_exceed(EngineExceed(2, "ff", AlertLevel.ADVISORY, 100, True))
        frame = d.render(now_us=10)
        levels = [a.level for a in frame.alerts]
        self.assertEqual(levels[0], AlertLevel.WARNING)
        self.assertEqual(levels[-1], AlertLevel.ADVISORY)

    def test_HLR_DSP_002_color_rule_static_check_passes(self):
        violations = DisplayComputer.static_color_check({
            AlertLevel.WARNING: "RED",
            AlertLevel.CAUTION: "AMBER",
            AlertLevel.ADVISORY: "GREEN",
        })
        self.assertEqual(violations, [])

    def test_HLR_DSP_002_color_rule_static_check_fails(self):
        violations = DisplayComputer.static_color_check({
            AlertLevel.WARNING: "BLUE",
            AlertLevel.CAUTION: "AMBER",
            AlertLevel.ADVISORY: "GREEN",
        })
        self.assertEqual(len(violations), 1)

    def test_HLR_DSP_003_mode_latency_violation_counted(self):
        d = DisplayComputer(mode_latency_budget_us=100_000)
        msg = FccModeMsg(ts_us=0, mode=FccMode.ALTERNATE, reason="x",
                         lane_disagree=True)
        d.receive_mode(msg, now_us=200_000)  # 200 ms > 100 ms budget
        self.assertEqual(d.mode_latency_violations, 1)

    def test_HLR_DSP_004_cap_and_summarize(self):
        d = DisplayComputer(max_alerts=2)
        for i in range(5):
            d.receive_engine_exceed(
                EngineExceed(i, f"p{i}", AlertLevel.CAUTION, i, True))
        frame = d.render(now_us=10)
        self.assertEqual(len(frame.alerts), 2)
        self.assertEqual(frame.summarized, 3)

    def test_HLR_DSP_005_dashed_value_on_stale(self):
        d = DisplayComputer()
        d.receive_air_data(250, ts_us=0, freshness=Freshness.STALE)
        frame = d.render(now_us=10)
        self.assertEqual(frame.ias, "----")

    def test_HLR_DSP_006_mode_history_window(self):
        d = DisplayComputer(history_window_us=5_000_000)
        d.receive_mode(FccModeMsg(0, FccMode.NORMAL, "", False), now_us=0)
        d.receive_mode(FccModeMsg(1_000_000, FccMode.ALTERNATE, "", True),
                       now_us=1_000_000)
        d.render(now_us=10_000_000)  # past window
        self.assertEqual(len(d._mode_history), 0)

    def test_HLR_DSP_007_refresh_dt_measured(self):
        d = DisplayComputer()
        d.render(now_us=0)
        f2 = d.render(now_us=10_000)
        self.assertEqual(f2.refresh_dt_us, 10_000)


if __name__ == "__main__":
    unittest.main()
