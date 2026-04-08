"""HLR-DC-001..007 unit tests."""
import unittest
from . import _paths  # noqa: F401

from avx_sim.health_monitor import HealthMonitor, HmEvent
from avx_sim.messages import Freshness
from avx_sim.modules import DataConcentrator, SensorRange


def make_dc(**kw):
    hm = HealthMonitor()
    return hm, DataConcentrator(
        source_id="L",
        hm=hm,
        air_range=SensorRange(0, 600),
        pitch_range=SensorRange(-90, 90),
        n1_range=SensorRange(0, 110),
        **kw,
    )


class TestDataConcentrator(unittest.TestCase):

    def test_HLR_DC_001_timestamp_present(self):
        hm, dc = make_dc()
        msg = dc.publish_air_data(250, 10000, 0, now_us=12345)
        self.assertEqual(msg.ts_us, 12345)

    def test_HLR_DC_003_out_of_range_invalid(self):
        hm, dc = make_dc()
        msg = dc.publish_air_data(9999, 10000, 0, now_us=0)
        self.assertEqual(msg.freshness, Freshness.INVALID)

    def test_HLR_DC_004_source_id_traceable_via_hm(self):
        hm, dc = make_dc()
        dc.publish_air_data(9999, 0, 0, now_us=0)
        sources = {e.source for e in hm.events}
        self.assertIn("DC:L", sources)

    def test_HLR_DC_006_dropout_after_n_ticks(self):
        hm, dc = make_dc(dropout_ticks=3)
        for t in range(3):
            dc.notify_dropout(now_us=t * 1000)
        self.assertEqual(hm.count(HmEvent.SENSOR_DROPOUT), 1)

    def test_HLR_DC_007_health_reported(self):
        hm, dc = make_dc()
        dc.publish_air_data(9999, 0, 0, now_us=0)  # invalid → HM event
        self.assertGreater(len(hm.events), 0)


if __name__ == "__main__":
    unittest.main()
