"""M6 evidence bundle exporter + verifier tests."""
import json
import unittest
from pathlib import Path
from . import _paths  # noqa: F401

import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from evidence_bundler import build_bundle, verify_bundle  # noqa: E402


class TestEvidenceBundle(unittest.TestCase):

    def setUp(self):
        self.out_dir = ROOT / "evidence" / "test_bundles"
        if self.out_dir.exists():
            for p in self.out_dir.glob("bundle-*.zip"):
                p.unlink()

    def _sample_payload(self):
        return {
            "summary": {"tests_total": 6, "tests_passed": 6,
                        "coverage_pct": 37.15, "mcdc_pct_avg": 100.0,
                        "hf_passed": 6, "hf_total": 6},
            "results": [{"id": "TC-FCC-001", "req": ["HLR-FCC-008"], "result": "PASS"}],
            "campaigns": [{"id": "FC-001", "pass": True}],
            "mcdc": {"fcc.validate": {"pct": 1.0, "covered_conditions": 4,
                                       "conditions": 4}},
            "coverage": {"__summary__": {"hit": 432, "executable": 1163, "pct": 0.37}},
            "hf_findings": [{"hf_id": "HF-01", "passed": True}],
            "mode_confusion": [],
            "hil_runs": [{"name": "nominal", "cycles": 60}],
            "trace": {"HLR-FCC-008": ["TC-FCC-001"]},
            "gap": {"requirements_total": 68, "requirements_uncovered": []},
        }

    def test_build_produces_zip(self):
        zip_path = build_bundle(self._sample_payload(), ROOT, self.out_dir)
        self.assertTrue(zip_path.exists())
        self.assertTrue(zip_path.name.startswith("bundle-"))
        self.assertTrue(zip_path.name.endswith(".zip"))

    def test_verify_matches_on_fresh_bundle(self):
        zip_path = build_bundle(self._sample_payload(), ROOT, self.out_dir)
        report = verify_bundle(zip_path)
        self.assertTrue(report["ok"], report["mismatches"])
        self.assertEqual(report["mismatches"], [])
        self.assertIn("files", report["manifest"])
        self.assertGreater(len(report["manifest"]["files"]), 5)

    def test_manifest_includes_dal_and_disclaimer(self):
        zip_path = build_bundle(self._sample_payload(), ROOT, self.out_dir)
        report = verify_bundle(zip_path)
        m = report["manifest"]
        self.assertIn("dal_assumptions", m)
        self.assertIn("disclaimer", m)
        self.assertIn("not certified", m["disclaimer"].lower())

    def test_verify_detects_tamper(self):
        import zipfile
        zip_path = build_bundle(self._sample_payload(), ROOT, self.out_dir)
        # Rebuild zip with one file replaced
        tampered = zip_path.with_name(zip_path.stem + "-tampered.zip")
        with zipfile.ZipFile(zip_path, "r") as zin, \
                zipfile.ZipFile(tampered, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename == "results/test_results.json":
                    data = b"[]"   # pretend no tests
                zout.writestr(item, data)
        report = verify_bundle(tampered)
        self.assertFalse(report["ok"])
        self.assertTrue(any("test_results.json" in m for m in report["mismatches"]))


if __name__ == "__main__":
    unittest.main()
