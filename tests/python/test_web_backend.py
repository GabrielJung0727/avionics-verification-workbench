"""Smoke tests for the FastAPI backend at web/backend/.

Uses Starlette TestClient so no live server is needed. Skips if FastAPI
or the evidence/ artefacts are missing — both are easy to forget in
fresh clones, and we'd rather skip than fail spuriously.
"""
import unittest
from pathlib import Path
from . import _paths  # noqa: F401

import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "web" / "backend"))

try:
    from fastapi.testclient import TestClient  # noqa: E402
    from app.main import app  # noqa: E402
    _IMPORT_OK = True
except Exception as e:  # pragma: no cover
    _IMPORT_OK = False
    _IMPORT_ERR = repr(e)


@unittest.skipUnless(_IMPORT_OK, "fastapi or backend app not importable")
class TestBackendSurface(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_root_lists_routes(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        body = r.json()
        self.assertIn("_draft", body)
        self.assertGreater(len(body["routes"]), 10)

    def test_health(self):
        r = self.client.get("/api/health")
        self.assertEqual(r.status_code, 200)
        body = r.json()
        for k in ("ok", "report_present", "lakehouse_present",
                  "registry_present"):
            self.assertIn(k, body)

    def test_lakehouse_health(self):
        r = self.client.get("/api/lakehouse/health")
        self.assertEqual(r.status_code, 200)
        self.assertIn("db_present", r.json())

    def test_lakehouse_gold_lists_whitelisted_views(self):
        r = self.client.get("/api/lakehouse/gold")
        self.assertEqual(r.status_code, 200)
        views = r.json()["views"]
        for expected in ("daily_coverage", "weekly_escape_rate",
                         "req_pass_rate", "hil_latency_distribution"):
            self.assertIn(expected, views)

    def test_lakehouse_gold_rejects_unknown_view(self):
        r = self.client.get("/api/lakehouse/gold/__pwn__")
        self.assertEqual(r.status_code, 404)

    def test_lakehouse_gold_rejects_bad_limit(self):
        r = self.client.get("/api/lakehouse/gold/daily_coverage?limit=99999")
        self.assertEqual(r.status_code, 400)


@unittest.skipUnless(
    _IMPORT_OK and (ROOT / "evidence" / "verification-report.json").exists(),
    "evidence/verification-report.json not present; "
    "run scripts/run_verification.py first",
)
class TestBackendWithEvidence(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_results_summary_has_keys(self):
        r = self.client.get("/api/results/summary")
        self.assertEqual(r.status_code, 200)
        s = r.json()["summary"]
        for k in ("tests_total", "tests_passed", "campaigns_total"):
            self.assertIn(k, s)

    def test_results_tests_returns_list(self):
        r = self.client.get("/api/results/tests")
        self.assertEqual(r.status_code, 200)
        self.assertIsInstance(r.json()["results"], list)

    def test_registry_lists_models(self):
        r = self.client.get("/api/registry/models")
        self.assertEqual(r.status_code, 200)
        models = r.json()["models"]
        names = {m["model_name"] for m in models}
        self.assertIn("fault_escape_predictor", names)


@unittest.skipUnless(_IMPORT_OK, "fastapi not importable")
class TestPredictGracefulWhenEndpointMissing(unittest.TestCase):

    def setUp(self):
        # Force the env var off so we exercise the no-endpoint branch.
        import os
        self._prev = os.environ.pop("INTELLIGENCE_ENDPOINT", None)
        # Re-import config so the change takes effect
        import importlib
        import app.config
        import app.routes.predict as p
        importlib.reload(app.config)
        importlib.reload(p)
        from app.main import app as app_  # re-import
        self.client = TestClient(app_)

    def tearDown(self):
        import os
        if self._prev is not None:
            os.environ["INTELLIGENCE_ENDPOINT"] = self._prev

    def test_predict_health_reports_unavailable(self):
        r = self.client.get("/api/predict/health")
        self.assertEqual(r.status_code, 200)
        self.assertFalse(r.json().get("available"))

    def test_predict_post_503_when_no_endpoint(self):
        r = self.client.post(
            "/api/predict/fault_escape",
            json={"delay_us": 0, "drop_every_n": 0, "n1_at_t1s": 80,
                  "egt_at_t1s": 700, "dual_fault_us": -1, "seed": 1},
        )
        self.assertEqual(r.status_code, 503)


if __name__ == "__main__":
    unittest.main()
