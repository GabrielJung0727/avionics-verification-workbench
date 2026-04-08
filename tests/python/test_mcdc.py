"""MC/DC tracker tests + integration via the M3 scenario."""
import unittest
from . import _paths  # noqa: F401

from avx_sim.mcdc import McdcTracker


class TestMcdcTracker(unittest.TestCase):

    def setUp(self):
        McdcTracker.reset()
        McdcTracker.enable()

    def tearDown(self):
        McdcTracker.disable()
        McdcTracker.reset()

    def test_full_mcdc_for_two_condition_decision(self):
        # Full truth table for (A AND B): 4 rows
        for a, b in [(False, False), (False, True), (True, False), (True, True)]:
            McdcTracker.record("d", (a, b), a and b)
        rep = McdcTracker.report()
        self.assertEqual(rep["d"]["covered_conditions"], 2)
        self.assertEqual(rep["d"]["pct"], 1.0)

    def test_partial_mcdc(self):
        # Only the (False,False) and (True,True) rows — A is independent but
        # B's effect cannot be observed without flipping A as well.
        McdcTracker.record("d", (False, False), False)
        McdcTracker.record("d", (True, True), True)
        rep = McdcTracker.report()
        self.assertEqual(rep["d"]["covered_conditions"], 0)


class TestMcdcInScenario(unittest.TestCase):

    def test_fcc_validate_decision_observed(self):
        from m3_scenario import M3World, build_m3
        McdcTracker.reset()
        McdcTracker.enable()
        try:
            sched, _, _, _ = build_m3(M3World())
            sched.run_for(100_000)
        finally:
            McdcTracker.disable()
        rep = McdcTracker.report()
        self.assertIn("fcc.validate", rep)
        self.assertGreater(rep["fcc.validate"]["samples"], 0)
        McdcTracker.reset()


if __name__ == "__main__":
    unittest.main()
