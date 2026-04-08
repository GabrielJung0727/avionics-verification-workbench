import unittest
from . import _paths  # noqa: F401

from avx_sim.afdx import AfdxBus, VirtualLink, AfdxFaults
from avx_sim.health_monitor import HealthMonitor, HmEvent


class TestAfdx(unittest.TestCase):

    def test_basic_send_receive(self):
        bus = AfdxBus()
        bus.add_link(VirtualLink(vl_id=1, bag_us=1000))
        self.assertTrue(bus.send(1, b"hi", now_us=0))
        self.assertEqual(bus.receive_due(1, now_us=0), [b"hi"])

    def test_bag_violation_recorded(self):
        hm = HealthMonitor()
        bus = AfdxBus(hm=hm)
        bus.add_link(VirtualLink(vl_id=1, bag_us=2000, name="VL1"))
        self.assertTrue(bus.send(1, b"a", now_us=0))
        self.assertFalse(bus.send(1, b"b", now_us=500))     # too soon
        self.assertEqual(hm.count(HmEvent.IPC_OVERFLOW), 1)
        self.assertTrue(bus.send(1, b"c", now_us=2000))     # ok

    def test_drop_fault_drops_every_n(self):
        bus = AfdxBus()
        bus.add_link(VirtualLink(vl_id=1, bag_us=0,
                                 faults=AfdxFaults(drop_every_n=3)))
        results = [bus.send(1, b"x", now_us=i) for i in range(9)]
        # every 3rd should be dropped → 6 ok, 3 dropped
        self.assertEqual(sum(results), 6)

    def test_delay_holds_until_due(self):
        bus = AfdxBus()
        bus.add_link(VirtualLink(vl_id=1, bag_us=0,
                                 faults=AfdxFaults(delay_us=500)))
        bus.send(1, b"x", now_us=0)
        self.assertEqual(bus.receive_due(1, now_us=400), [])
        self.assertEqual(bus.receive_due(1, now_us=500), [b"x"])


if __name__ == "__main__":
    unittest.main()
