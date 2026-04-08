"""HLR-ENG-001..007 unit tests."""
import unittest
from . import _paths  # noqa: F401

from avx_sim.health_monitor import HealthMonitor
from avx_sim.messages import EngineRaw, AlertLevel
from avx_sim.modules import EngineInterface, EngineLimits


def make_eng():
    hm = HealthMonitor()
    return hm, EngineInterface(hm=hm)


class TestEngineInterface(unittest.TestCase):

    def test_HLR_ENG_001_classify_caution_warning(self):
        hm, eng = make_eng()
        # caution band
        params, ev = eng.step(EngineRaw(0, n1=101, n2=80, egt=400, ff=2000), now_us=1)
        self.assertTrue(any(e.param == "n1" for e in ev))
        # warning band
        _, ev2 = eng.step(EngineRaw(0, n1=104, n2=80, egt=400, ff=2000), now_us=2)
        self.assertTrue(any(e.level == AlertLevel.WARNING for e in ev2))

    def test_HLR_ENG_002_004_latch_persists(self):
        hm, eng = make_eng()
        eng.step(EngineRaw(0, n1=104, n2=80, egt=400, ff=2000), now_us=1)
        # value drops back to normal but latch must persist
        params, _ = eng.step(EngineRaw(0, n1=80, n2=80, egt=400, ff=2000), now_us=2)
        self.assertEqual(eng.latched.get("n1"), AlertLevel.WARNING)
        self.assertEqual(params.state, AlertLevel.WARNING)

    def test_HLR_ENG_003_hot_start_detected(self):
        hm, eng = make_eng()
        # baseline
        eng.step(EngineRaw(0, n1=10, n2=10, egt=200, ff=100), now_us=0)
        # 1 sec later EGT jumps 500C → 500 C/s, exceeds 200 default
        _, ev = eng.step(EngineRaw(0, n1=12, n2=12, egt=700, ff=100),
                         now_us=1_000_000)
        self.assertTrue(any(e.param == "egt_rate" for e in ev))
        self.assertIn("hot_start", eng.latched)

    def test_HLR_ENG_007_limits_from_config(self):
        hm = HealthMonitor()
        custom = EngineLimits.default()
        eng = EngineInterface(hm=hm, limits=custom)
        self.assertIs(eng.limits, custom)


if __name__ == "__main__":
    unittest.main()
