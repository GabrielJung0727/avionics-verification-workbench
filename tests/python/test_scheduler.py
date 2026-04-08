import unittest
from . import _paths  # noqa: F401

from avx_sim.sim_clock import SimClock
from avx_sim.health_monitor import HealthMonitor, HmEvent
from avx_sim.scheduler import Partition, Scheduler


class TestScheduler(unittest.TestCase):

    def test_periodic_activation_count(self):
        clock = SimClock()
        hm = HealthMonitor()
        sched = Scheduler(clock=clock, hm=hm, tick_us=1000)

        seen: list[int] = []

        def body(now_us: int) -> None:
            seen.append(now_us)

        sched.add_partition(Partition(
            id="P", period_us=10_000, budget_us=500, offset_us=0,
            criticality="C", body=body,
        ))
        sched.run_for(100_000)  # 100 ms → 10 activations
        self.assertEqual(len(seen), 10)
        self.assertEqual(seen[0], 0)
        self.assertEqual(seen[-1], 90_000)

    def test_offset_respected(self):
        clock = SimClock()
        hm = HealthMonitor()
        sched = Scheduler(clock=clock, hm=hm, tick_us=1000)
        seen: list[int] = []
        sched.add_partition(Partition(
            id="P", period_us=20_000, budget_us=500, offset_us=5_000,
            criticality="C", body=lambda t: seen.append(t),
        ))
        sched.run_for(60_000)
        self.assertEqual(seen, [5_000, 25_000, 45_000])

    def test_budget_overrun_recorded(self):
        clock = SimClock()
        hm = HealthMonitor()
        sched = Scheduler(clock=clock, hm=hm, tick_us=1000)
        sched.add_partition(Partition(
            id="P_over", period_us=10_000, budget_us=500, offset_us=0,
            criticality="B", body=lambda t: None,
            simulated_exec_us=900,   # exceeds 500us budget
        ))
        sched.run_for(50_000)
        self.assertGreaterEqual(hm.count(HmEvent.PARTITION_OVERRUN), 5)

    def test_invalid_alignment_rejected(self):
        clock = SimClock()
        hm = HealthMonitor()
        sched = Scheduler(clock=clock, hm=hm, tick_us=1000)
        with self.assertRaises(ValueError):
            sched.add_partition(Partition(
                id="bad", period_us=1500, budget_us=100, offset_us=0,
                criticality="C", body=lambda t: None,
            ))


if __name__ == "__main__":
    unittest.main()
