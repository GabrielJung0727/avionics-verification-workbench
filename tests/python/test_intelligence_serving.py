"""Tests for the local intelligence-serving HTTP layer."""
import os
import unittest
from pathlib import Path
from . import _paths  # noqa: F401

import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from intelligence import IntelligenceClient, build_server  # noqa: E402

REGISTRY = ROOT / "evidence" / "registry"


def _bring_up_server():
    server = build_server(
        registry_root=REGISTRY,
        host="127.0.0.1", port=0,
        requirement_ids=["HLR-FCC-001", "HLR-FCC-003", "HLR-ENG-001",
                         "HLR-DSP-001", "HLR-HM-001", "SYS-001"],
    )
    server.start_in_thread()
    return server, IntelligenceClient(endpoint=f"http://127.0.0.1:{server.port}")


@unittest.skipUnless((REGISTRY / "fault_escape_predictor" / "v0.1.0" /
                      "model.pkl").exists(),
                     "Phase B registry not populated; run train_intelligence.py")
class TestIntelligenceServer(unittest.TestCase):

    def setUp(self):
        self.server, self.client = _bring_up_server()

    def tearDown(self):
        self.server.stop()

    def test_health_returns_loaded_models_and_draft(self):
        out = self.client.health()
        self.assertEqual(out["status"], "ok")
        self.assertIn("_draft", out)
        self.assertIn("fault_escape_predictor", out["models_loaded"])
        self.assertIn("engine_anomaly_detector", out["models_loaded"])
        self.assertIn("trace_gap_intel", out["models_loaded"])

    def test_models_route_returns_metadata(self):
        out = self.client.models()
        self.assertIn("_draft", out)
        names = {m["model_name"] for m in out["models"]}
        self.assertIn("fault_escape_predictor", names)

    def test_predict_escape_returns_probability(self):
        out = self.client.predict_escape(
            delay_us=80_000, drop_every_n=3, n1_at_t1s=80,
            egt_at_t1s=700, dual_fault_us=-1, seed=1,
        )
        self.assertIn("p_escape", out)
        self.assertGreaterEqual(out["p_escape"], 0.0)
        self.assertLessEqual(out["p_escape"], 1.0)
        self.assertIn(out["advice"], {"run early", "lower priority", "review"})
        self.assertIn("_draft", out)

    def test_predict_escape_rejects_bad_payload(self):
        # Missing required field 'n1_at_t1s'
        out = self.client._post("/predict/fault_escape", {
            "delay_us": 0, "drop_every_n": 0,
            "egt_at_t1s": 0, "dual_fault_us": -1,
        })
        self.assertIn("error", out)

    def test_predict_engine_anomaly_with_features(self):
        feats = [88, 0.4, 0.0, 95, 0.3, 0.0,
                 700, 5.0, 0.0, 3000, 50.0, 0.0]
        out = self.client.predict_engine_anomaly(features=feats)
        self.assertIn(out["decision"], {
            "preventive_alert", "early_warning",
            "inspection_candidate", "nominal",
        })
        self.assertIn("_draft", out)

    def test_predict_trace_gap(self):
        out = self.client.predict_trace_gap(
            diff_paths=["tools/sim_py/avx_sim/modules/fcc.py"],
        )
        self.assertIn("ranked", out)
        self.assertGreater(len(out["ranked"]), 0)
        self.assertTrue(out["ranked"][0]["req_id"].startswith("HLR-FCC"))


@unittest.skipUnless((REGISTRY / "fault_escape_predictor" / "v0.1.0" /
                      "model.pkl").exists(),
                     "Phase B registry not populated; run train_intelligence.py")
class TestAiAssistantIntegration(unittest.TestCase):

    def setUp(self):
        self.server, _ = _bring_up_server()
        self._prev = os.environ.get("INTELLIGENCE_ENDPOINT")
        os.environ["INTELLIGENCE_ENDPOINT"] = (
            f"http://127.0.0.1:{self.server.port}")

    def tearDown(self):
        self.server.stop()
        if self._prev is None:
            os.environ.pop("INTELLIGENCE_ENDPOINT", None)
        else:
            os.environ["INTELLIGENCE_ENDPOINT"] = self._prev

    def test_change_impact_augmented_when_endpoint_present(self):
        from ai_assistant.change_impact import (
            build_impact_index, impact_for_requirement,
        )
        idx = build_impact_index(
            ROOT / "tools" / "runner" / "test_cases"
        )
        out = impact_for_requirement(
            idx, "HLR-FCC-004",
            all_requirement_ids=["HLR-FCC-001", "HLR-FCC-003", "HLR-FCC-004",
                                  "HLR-ENG-001", "HLR-DSP-001"],
        )
        self.assertIn("adjacent_req_candidates", out)
        self.assertTrue(out.get("_endpoint_used"))

    def test_change_impact_falls_back_when_endpoint_unset(self):
        os.environ.pop("INTELLIGENCE_ENDPOINT", None)
        from ai_assistant.change_impact import (
            build_impact_index, impact_for_requirement,
        )
        idx = build_impact_index(
            ROOT / "tools" / "runner" / "test_cases"
        )
        out = impact_for_requirement(
            idx, "HLR-FCC-004",
            all_requirement_ids=["HLR-FCC-001", "HLR-FCC-003"],
        )
        self.assertNotIn("adjacent_req_candidates", out)
        self.assertNotIn("_endpoint_used", out)


if __name__ == "__main__":
    unittest.main()
