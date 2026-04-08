"""M4 fault injection campaign tests."""
import unittest
from pathlib import Path
from . import _paths  # noqa: F401

import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from fault_injector import load_campaign, run_campaign  # noqa: E402

CAMP_DIR = ROOT / "tools" / "fault_injector" / "campaigns"


class TestFaultCampaigns(unittest.TestCase):

    def test_FC_001_dual_fault_classified(self):
        c = load_campaign(CAMP_DIR / "FC-001-dual-fault.json")
        out = run_campaign(c)
        self.assertEqual(out["fcc_mode_terminal"], "DIRECT")
        # FCC entered DIRECT → mitigated; HM may or may not record extra
        self.assertIn(out["classification"],
                      ("mitigated_only", "detected_and_mitigated"))
        self.assertTrue(out["pass"])

    def test_FC_002_engine_overlimit_detected(self):
        c = load_campaign(CAMP_DIR / "FC-002-engine-overlimit.json")
        out = run_campaign(c)
        # Engine I/F should produce HM events when n1 reaches warning band
        total_hm = sum(out["hm_event_counts"].values())
        self.assertGreater(total_hm, 0)
        self.assertTrue(out["pass"])

    def test_FC_003_afdx_delay_pipeline_alive(self):
        c = load_campaign(CAMP_DIR / "FC-003-afdx-delay.json")
        out = run_campaign(c)
        # No mode change expected; classification can be "escaped" in this
        # benign campaign — that's fine, the assertion is just that it runs
        # to completion and emits records.
        self.assertGreater(out["records"], 0)


if __name__ == "__main__":
    unittest.main()
