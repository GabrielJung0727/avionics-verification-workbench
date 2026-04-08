"""M5 human-factors evaluation tests."""
import unittest
from . import _paths  # noqa: F401

from avx_sim.hf import (
    HfEvaluator,
    evaluate_alert_priority,
    evaluate_color_rule,
    evaluate_mode_latency,
    evaluate_dashed_on_stale,
    evaluate_mode_history,
    run_mode_confusion,
    MODE_CONFUSION_SCENARIOS,
)
from avx_sim.messages import (
    AlertLevel,
    EngineExceed,
    FccMode,
    FccModeMsg,
    Freshness,
)
from avx_sim.modules import DisplayComputer


class TestHfEvaluators(unittest.TestCase):

    def test_alert_priority_pass(self):
        alerts = [
            (10, AlertLevel.WARNING),
            (9, AlertLevel.CAUTION),
            (5, AlertLevel.CAUTION),
            (2, AlertLevel.ADVISORY),
        ]
        f = evaluate_alert_priority(alerts)
        self.assertTrue(f.passed, f.detail)

    def test_alert_priority_fail_level_order(self):
        alerts = [(10, AlertLevel.CAUTION), (9, AlertLevel.WARNING)]
        f = evaluate_alert_priority(alerts)
        self.assertFalse(f.passed)

    def test_color_rule_static(self):
        f = evaluate_color_rule({
            AlertLevel.WARNING: "RED",
            AlertLevel.CAUTION: "AMBER",
            AlertLevel.ADVISORY: "GREEN",
        })
        self.assertTrue(f.passed)
        g = evaluate_color_rule({
            AlertLevel.WARNING: "BLUE",
            AlertLevel.CAUTION: "AMBER",
            AlertLevel.ADVISORY: "GREEN",
        })
        self.assertFalse(g.passed)

    def test_mode_latency_zero_violations(self):
        d = DisplayComputer()
        f = evaluate_mode_latency(d)
        self.assertTrue(f.passed)

    def test_dashed_on_stale(self):
        d = DisplayComputer()
        f = evaluate_dashed_on_stale(d, now_us=0)
        self.assertTrue(f.passed, f.detail)

    def test_mode_history_pruned(self):
        d = DisplayComputer(history_window_us=5_000_000)
        f = evaluate_mode_history(d)
        self.assertTrue(f.passed)


class TestHfEvaluatorFull(unittest.TestCase):

    def test_report_all_pass_on_clean_display(self):
        d = DisplayComputer()
        d.receive_engine_exceed(EngineExceed(1, "n1", AlertLevel.WARNING, 105, True))
        d.receive_engine_exceed(EngineExceed(0, "egt", AlertLevel.CAUTION, 880, True))
        report = HfEvaluator(d).run(now_us=0)
        self.assertTrue(report.passed, [f.detail for f in report.findings if not f.passed])
        s = report.summary()
        self.assertEqual(s["total"], 6)
        self.assertEqual(s["failed"], 0)


class TestModeConfusionScenarios(unittest.TestCase):

    def test_MC_01_direct_mode_reached(self):
        out = run_mode_confusion(MODE_CONFUSION_SCENARIOS[0])
        self.assertTrue(out["terminal_mode_matches"], out)
        self.assertTrue(out["history_depth_ok"], out)
        self.assertEqual(out["mode_latency_violations"], 0)

    def test_MC_02_fcc_stays_normal_while_engine_latched(self):
        out = run_mode_confusion(MODE_CONFUSION_SCENARIOS[1])
        self.assertEqual(out["terminal_mode"], "NORMAL")

    def test_MC_03_multi_alert_pipeline_runs(self):
        out = run_mode_confusion(MODE_CONFUSION_SCENARIOS[2])
        self.assertGreater(out["records"], 0)


if __name__ == "__main__":
    unittest.main()
