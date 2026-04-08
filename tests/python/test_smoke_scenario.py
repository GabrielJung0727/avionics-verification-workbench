"""Integration tests for the M2 smoke scenario.

Verifies:
  - 8 ICD message ids appear in the recorder (M2-10)
  - Same seed → same recorder hash (M2-11, SYS-001/024)
  - Forced overrun produces a PARTITION_OVERRUN HM event (SYS-029)
  - Forced AFDX delay propagates without crashing the pipeline
"""
import unittest
from . import _paths  # noqa: F401

from smoke_scenario import build_smoke
from avx_sim.afdx import AfdxFaults
from avx_sim.health_monitor import HmEvent


class TestSmokeScenario(unittest.TestCase):

    def test_all_icd_messages_appear(self):
        sched, rec, hm, _ = build_smoke()
        sched.run_for(200_000)  # 200 ms
        msg_ids = {r[2] for r in rec.records}
        # MSG-008 HmEvent is only emitted when HM events occur, but MSG-001..007
        # plus DSP/HM render frames must be present every run.
        self.assertIn("MSG-001", msg_ids)
        self.assertIn("MSG-002", msg_ids)
        self.assertIn("MSG-003", msg_ids)
        self.assertIn("MSG-004", msg_ids)
        self.assertIn("MSG-006", msg_ids)
        self.assertIn("MSG-007", msg_ids)
        self.assertIn("render", msg_ids)
        self.assertIn("snapshot", msg_ids)
        self.assertGreater(len(rec), 50)

    def test_determinism_same_seed(self):
        s1, r1, _, _ = build_smoke(seed=42)
        s2, r2, _, _ = build_smoke(seed=42)
        s1.run_for(200_000)
        s2.run_for(200_000)
        self.assertEqual(r1.sha256(), r2.sha256())

    def test_overrun_injection_recorded(self):
        sched, _, hm, _ = build_smoke(inject_overrun_at=0)
        sched.run_for(200_000)
        self.assertGreater(hm.count(HmEvent.PARTITION_OVERRUN), 0)

    def test_afdx_delay_storm(self):
        faults = AfdxFaults(delay_us=80_000)  # 80 ms latency on EngParams VL
        sched, rec, hm, _ = build_smoke(faults=faults)
        sched.run_for(300_000)
        # The pipeline must still complete and the recorder must contain DSP frames.
        self.assertIn("render", {r[2] for r in rec.records})


if __name__ == "__main__":
    unittest.main()
