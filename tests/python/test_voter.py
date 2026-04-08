"""Voter / mid-value-select tests."""
import unittest
from . import _paths  # noqa: F401

from avx_sim.modules import mid_value_select, majority_vote


class TestMidValueSelect(unittest.TestCase):

    def test_normal_triplex(self):
        res = mid_value_select([(10.0, True), (10.2, True), (10.1, True)])
        self.assertAlmostEqual(res.value, 10.1, places=3)
        self.assertEqual(res.reason, "mid-value")

    def test_one_stuck_channel_rejected_by_majority(self):
        res = majority_vote([(10.0, True), (10.1, True), (99.0, True)],
                            tolerance=1.0)
        self.assertAlmostEqual(res.value, 10.05, places=2)
        self.assertEqual(res.reason, "majority")

    def test_no_majority_falls_back_to_mid_value(self):
        res = majority_vote([(1.0, True), (50.0, True), (100.0, True)],
                            tolerance=0.5)
        self.assertEqual(res.reason, "no-majority -> mid-value")
        self.assertAlmostEqual(res.value, 50.0, places=2)

    def test_single_healthy_channel(self):
        res = mid_value_select([(5.0, True), (0.0, False), (0.0, False)])
        self.assertEqual(res.value, 5.0)
        self.assertEqual(res.reason, "single channel")

    def test_no_healthy_channels_returns_none(self):
        res = mid_value_select([(5.0, False), (6.0, False)])
        self.assertIsNone(res.value)


if __name__ == "__main__":
    unittest.main()
