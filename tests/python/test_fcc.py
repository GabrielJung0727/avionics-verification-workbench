"""HLR-FCC-001..008 unit tests."""
import unittest
from . import _paths  # noqa: F401

from avx_sim.health_monitor import HealthMonitor, HmEvent
from avx_sim.messages import AirData, Attitude, FccMode, Freshness
from avx_sim.modules import Fcc


def make_fcc(**kw):
    hm = HealthMonitor()
    return hm, Fcc(hm=hm, **kw)


def air(ias=250.0, fresh=Freshness.OK):
    return AirData(0, ias, 10000, 0, fresh)


def att(pitch=0.0, fresh=Freshness.OK):
    return Attitude(0, pitch, 0, 0, fresh)


class TestFcc(unittest.TestCase):

    def test_HLR_FCC_008_self_test_promotes_to_normal(self):
        hm, fcc = make_fcc()
        self.assertEqual(fcc.mode, FccMode.OFF)
        fcc.step(air(), att(), now_us=0)
        self.assertEqual(fcc.mode, FccMode.NORMAL)
        self.assertTrue(fcc.self_test_passed)

    def test_HLR_FCC_001_freshness_invalid_blocks_command(self):
        hm, fcc = make_fcc()
        fcc.step(air(), att(), now_us=0)  # init
        cmd, _ = fcc.step(air(fresh=Freshness.STALE), att(), now_us=1000)
        self.assertFalse(cmd.valid)

    def test_HLR_FCC_007_limiter_clamps_command(self):
        hm, fcc = make_fcc(pitch_limit=2.0, roll_limit=2.0)
        cmd, _ = fcc.step(air(ias=0.0), att(pitch=0.0), now_us=0)
        # large IAS error → big pitch cmd, must be clamped
        self.assertLessEqual(abs(cmd.pitch_cmd), 2.0)

    def test_HLR_FCC_004_dual_fault_to_direct(self):
        hm, fcc = make_fcc()
        fcc.step(air(), att(), now_us=0)  # NORMAL
        cmd, msg = fcc.step(air(), att(), now_us=1000, dual_sensor_fault=True)
        self.assertEqual(fcc.mode, FccMode.DIRECT)
        self.assertIsNotNone(msg)
        self.assertEqual(msg.mode, FccMode.DIRECT)

    def test_HLR_FCC_006_modes_present(self):
        # enum should expose all four
        names = {m.name for m in FccMode}
        self.assertEqual(names, {"OFF", "NORMAL", "ALTERNATE", "DIRECT"})

    def test_HLR_FCC_005_mode_change_msg_within_one_call(self):
        hm, fcc = make_fcc()
        fcc.step(air(), att(), now_us=0)  # init → NORMAL (mode_msg returned)
        # second call with no change → no mode_msg
        cmd, msg = fcc.step(air(), att(), now_us=1000)
        self.assertIsNone(msg)


if __name__ == "__main__":
    unittest.main()
