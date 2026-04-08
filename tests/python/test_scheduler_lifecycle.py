"""Scheduler lifecycle tests: cold/warm start, partition restart, stats."""
import unittest
from . import _paths  # noqa: F401

from avx_sim.scheduler import (
    Partition,
    PartitionState,
    Scheduler,
    SystemState,
)
from avx_sim.sim_clock import SimClock
from avx_sim.health_monitor import HealthMonitor, HmEvent


def make_sched():
    clock = SimClock()
    hm = HealthMonitor()
    return clock, hm, Scheduler(clock=clock, hm=hm, tick_us=1000)


class TestSchedulerLifecycle(unittest.TestCase):

    def test_cold_start_transitions_to_operational(self):
        clock, hm, sched = make_sched()
        sched.add_partition(Partition("P", 10_000, 500, 0, "C", lambda t: None))
        self.assertEqual(sched.system_state, SystemState.OFF)
        sched.cold_start()
        self.assertEqual(sched.system_state, SystemState.OPERATIONAL)

    def test_warm_start_preserves_partitions(self):
        clock, hm, sched = make_sched()
        sched.add_partition(Partition("P", 10_000, 500, 0, "C", lambda t: None))
        sched.cold_start()
        sched.run_for(50_000)
        acts_before = sched.partitions[0].stats.activations
        sched.warm_start()
        sched.run_for(20_000)
        self.assertGreater(sched.partitions[0].stats.activations, acts_before)

    def test_partition_restart_records_event(self):
        clock, hm, sched = make_sched()
        hits = []
        sched.add_partition(Partition("P", 10_000, 500, 0, "C",
                                       lambda t: hits.append(t)))
        sched.cold_start()
        sched.run_for(30_000)
        sched.restart_partition("P", brownout_ticks=5)
        sched.run_for(30_000)
        self.assertEqual(hm.count(HmEvent.MODULE_RESTART), 1)
        self.assertEqual(sched.partitions[0].stats.restarts, 1)
        self.assertEqual(sched.partitions[0].state, PartitionState.RUNNING)

    def test_restart_unknown_raises(self):
        clock, hm, sched = make_sched()
        with self.assertRaises(KeyError):
            sched.restart_partition("nope")

    def test_stats_report_has_all_partitions(self):
        clock, hm, sched = make_sched()
        sched.add_partition(Partition("A", 10_000, 500, 0, "C",
                                       lambda t: None, simulated_exec_us=400))
        sched.add_partition(Partition("B", 20_000, 500, 0, "C",
                                       lambda t: None, simulated_exec_us=600))
        sched.cold_start()
        sched.run_for(100_000)
        rpt = sched.stats_report()
        self.assertIn("A", rpt)
        self.assertIn("B", rpt)
        self.assertGreater(rpt["A"]["activations"], 0)
        self.assertIn("exec_mean_us", rpt["A"])
        self.assertIn("period_jitter_us", rpt["A"])


if __name__ == "__main__":
    unittest.main()
