import unittest
from . import _paths  # noqa: F401

from avx_sim.ipc import SamplingPort, QueuingPort
from avx_sim.health_monitor import HealthMonitor, HmEvent


class TestSamplingPort(unittest.TestCase):
    def test_freshness(self):
        hm = HealthMonitor()
        port = SamplingPort[float]("p", freshness_budget_us=1000, hm=hm)
        port.write(1.5, now_us=0)
        v, fresh = port.read(now_us=500)
        self.assertEqual(v, 1.5)
        self.assertTrue(fresh)
        v, fresh = port.read(now_us=2000)  # too old
        self.assertFalse(fresh)
        self.assertEqual(hm.count(HmEvent.IPC_STALE), 1)


class TestQueuingPort(unittest.TestCase):
    def test_overflow(self):
        hm = HealthMonitor()
        q = QueuingPort[int]("q", capacity=2, hm=hm)
        self.assertTrue(q.push(1, 0))
        self.assertTrue(q.push(2, 0))
        self.assertFalse(q.push(3, 0))   # overflow
        self.assertEqual(hm.count(HmEvent.IPC_OVERFLOW), 1)
        self.assertEqual(q.pop(), 1)
        self.assertEqual(q.pop(), 2)
        self.assertIsNone(q.pop())


if __name__ == "__main__":
    unittest.main()
