"""M5 HIL-lite bridge tests."""
import unittest
from . import _paths  # noqa: F401

from avx_sim.hil import HilBridge, HilFaults, LoopbackMcu


def _tick_many(bridge: HilBridge, n: int, period_us: int,
               cmd=(0.0, 0.0, 0.0)) -> None:
    for i in range(n):
        bridge.tick(now_us=i * period_us, cmd=cmd)
    # drain any outputs due before the last tick + period
    bridge.drain(now_us=(n + 1) * period_us + 10_000)


class TestHilBridge(unittest.TestCase):

    def test_latency_zero_when_no_faults(self):
        bridge = HilBridge(mcu=LoopbackMcu())
        _tick_many(bridge, n=20, period_us=10_000)
        summary = bridge.measurement.summary()
        self.assertEqual(summary["drops"], 0)
        self.assertEqual(summary["reboots"], 0)
        self.assertEqual(summary["latency_max_us"], 0)
        self.assertEqual(summary["cycles"], 20)

    def test_constant_latency(self):
        # period << latency so observed latency reflects the MCU delay,
        # not the bridge polling granularity. Period=100us, latency=5000us.
        bridge = HilBridge(mcu=LoopbackMcu(faults=HilFaults(latency_us=5000)))
        _tick_many(bridge, n=80, period_us=100)
        summary = bridge.measurement.summary()
        self.assertGreaterEqual(summary["latency_max_us"], 5000)
        self.assertLess(summary["latency_max_us"], 5000 + 200)
        self.assertEqual(summary["drops"], 0)

    def test_jitter_captured(self):
        bridge = HilBridge(mcu=LoopbackMcu(
            faults=HilFaults(latency_us=2000, jitter_us=3000)))
        _tick_many(bridge, n=80, period_us=100)
        summary = bridge.measurement.summary()
        # odd cycles see latency + jitter → max latency >= 5000
        self.assertGreaterEqual(summary["latency_max_us"], 5000)

    def test_drop_every_n(self):
        bridge = HilBridge(mcu=LoopbackMcu(faults=HilFaults(drop_every_n=3)))
        _tick_many(bridge, n=30, period_us=10_000)
        # every 3rd cycle drops at the bridge layer
        self.assertGreaterEqual(bridge.measurement.drops, 10)

    def test_reboot_counted_and_recovers(self):
        bridge = HilBridge(mcu=LoopbackMcu(
            faults=HilFaults(reboot_at_cycle=5, brownout_cycles=2)))
        _tick_many(bridge, n=30, period_us=10_000)
        summary = bridge.measurement.summary()
        self.assertEqual(summary["reboots"], 1)
        # Post-reboot + brownout the MCU comes back; we should still have
        # recorded latencies for a bunch of successful cycles.
        self.assertGreater(summary["cycles"], 10)


if __name__ == "__main__":
    unittest.main()
