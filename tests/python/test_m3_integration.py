"""M3 integration tests — wires DC + FCC + ENG + DSP through the bus."""
import unittest
from . import _paths  # noqa: F401

from m3_scenario import M3World, build_m3
from avx_sim.health_monitor import HmEvent
from avx_sim.messages import FccMode, AlertLevel


class TestM3Integration(unittest.TestCase):

    def test_smoke_runs_and_produces_messages(self):
        sched, rec, hm, h = build_m3()
        sched.run_for(200_000)  # 200 ms
        msg_ids = {r[2] for r in rec.records}
        for expected in ("MSG-001", "MSG-002", "MSG-003", "MSG-004",
                         "MSG-007", "render", "snapshot"):
            self.assertIn(expected, msg_ids)

    def test_determinism_same_seed(self):
        s1, r1, _, _ = build_m3(M3World(seed=7))
        s2, r2, _, _ = build_m3(M3World(seed=7))
        s1.run_for(200_000)
        s2.run_for(200_000)
        self.assertEqual(r1.sha256(), r2.sha256())

    def test_engine_caution_propagates_to_display(self):
        # n1 ramps to 102 → caution band
        sched, rec, hm, h = build_m3(M3World(n1_at_t1s=102.0))
        sched.run_for(2_000_000)  # 2 s
        # display received at least one alert
        frame = h["dsp"].render(now_us=2_000_000)
        self.assertTrue(any(a.level >= AlertLevel.CAUTION for a in frame.alerts))

    def test_dual_fault_drives_fcc_to_direct(self):
        sched, rec, hm, h = build_m3(M3World(force_dual_fault_at_us=50_000))
        sched.run_for(200_000)
        self.assertEqual(h["fcc"].mode, FccMode.DIRECT)

    def test_mode_change_visible_within_one_partition_cycle(self):
        sched, rec, hm, h = build_m3(M3World(force_dual_fault_at_us=50_000))
        sched.run_for(200_000)
        # display latency violations should be 0 (DSP partition is 100ms,
        # mode message is published immediately on transition)
        self.assertEqual(h["dsp"].mode_latency_violations, 0)

    def test_afdx_delay_does_not_break_pipeline(self):
        from avx_sim.afdx import AfdxFaults
        sched, rec, hm, h = build_m3(M3World(afdx_faults=AfdxFaults(delay_us=80_000)))
        sched.run_for(300_000)
        msg_ids = {r[2] for r in rec.records}
        self.assertIn("render", msg_ids)


if __name__ == "__main__":
    unittest.main()
