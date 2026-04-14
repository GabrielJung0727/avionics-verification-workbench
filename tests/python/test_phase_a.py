"""Phase A — Enterprise Data Foundation tests."""
import json
import sqlite3
import unittest
from pathlib import Path
from . import _paths  # noqa: F401

import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from data_foundation import (  # noqa: E402
    Catalog,
    LakehouseLayout,
    SCHEMA_VERSION,
    detect_drift,
    ingest_report,
    lineage_for_run,
    parse_bus_recording,
)
from avx_sim.recorder import Recorder  # noqa: E402


def _sample_payload() -> dict:
    return {
        "summary": {
            "tests_total": 6, "tests_passed": 6, "tests_failed": 0,
            "tests_errored": 0, "campaigns_total": 3, "campaigns_passed": 2,
            "coverage_pct": 32.77, "mcdc_pct_avg": 100.0,
            "gap_uncovered_count": 55, "hf_total": 6, "hf_passed": 6,
            "hf_failed": 0, "mode_confusion_total": 3, "mode_confusion_ok": 3,
            "hil_runs": 4,
        },
        "results": [
            {"id": "TC-FCC-001", "req": ["HLR-FCC-008", "SYS-001"],
             "result": "PASS", "failures": []},
            {"id": "TC-ENG-001", "req": ["HLR-ENG-001", "HLR-ENG-002"],
             "result": "PASS", "failures": []},
        ],
        "campaigns": [
            {"id": "FC-001", "classification": "mitigated_only",
             "fcc_mode_terminal": "DIRECT", "hm_event_total": 0,
             "pass": True, "hm_event_counts": {}},
            {"id": "FC-003", "classification": "escaped",
             "fcc_mode_terminal": "NORMAL", "hm_event_total": 0,
             "pass": False, "hm_event_counts": {}},
        ],
        "trace": {"HLR-FCC-008": ["TC-FCC-001"]},
        "gap": {"requirements_total": 68, "requirements_uncovered": []},
        "mcdc": {
            "fcc.validate": {"conditions": 4, "covered_conditions": 4,
                             "pct": 1.0, "samples": 100, "unique_rows": 6},
        },
        "coverage": {"__summary__": {"hit": 432, "executable": 1163,
                                      "pct": 0.37}},
        "hf_findings": [
            {"hf_id": "HF-01", "title": "Alert prioritization",
             "passed": True, "detail": "ordered", "ac_ref": "AC 25.1322"},
        ],
        "mode_confusion": [],
        "hil_runs": [
            {"name": "nominal", "cycles": 60, "latency_mean_us": 0.0,
             "latency_max_us": 0, "jitter_stddev_us": 0.0,
             "drops": 0, "reboots": 0},
            {"name": "latency-5ms", "cycles": 60, "latency_mean_us": 5000.0,
             "latency_max_us": 5000, "jitter_stddev_us": 0.0,
             "drops": 0, "reboots": 0},
        ],
    }


class TestCatalogSchema(unittest.TestCase):
    def test_initialize_creates_tables_and_views(self):
        tmp = ROOT / "evidence" / "test_lakehouse"
        layout = LakehouseLayout(root=tmp)
        layout.ensure()
        cat = Catalog(db_path=layout.silver_db)
        cat.initialize()
        self.assertEqual(cat.schema_version(), SCHEMA_VERSION)
        with sqlite3.connect(str(layout.silver_db)) as conn:
            tables = {r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()}
            self.assertIn("run_manifest", tables)
            self.assertIn("verification_outcome", tables)
            self.assertIn("telemetry_event", tables)
            self.assertIn("artifact_index", tables)
            views = {r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='view'"
            ).fetchall()}
            for v in ("daily_coverage", "weekly_escape_rate",
                      "req_pass_rate", "hil_latency_distribution"):
                self.assertIn(v, views)


class TestIngestAndLineage(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.tmp = Path(tempfile.mkdtemp(prefix="avx_phasea_"))
        self.report = self.tmp / "verification-report.json"
        self.report.write_text(
            json.dumps(_sample_payload()), encoding="utf-8"
        )

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_ingest_populates_tables(self):
        summary = ingest_report(self.report, self.tmp / "lakehouse", None)
        rpt = summary.rows_per_table
        self.assertEqual(rpt["verification_outcome"], 4)
        self.assertEqual(rpt["fault_injection_case"], 2)
        self.assertEqual(rpt["mcdc_sample"], 1)
        self.assertEqual(rpt["hil_measurement"], 2)
        self.assertEqual(rpt["hf_finding"], 1)

    def test_lineage_returns_full_record(self):
        summary = ingest_report(self.report, self.tmp / "lakehouse", None)
        out = lineage_for_run(
            self.tmp / "lakehouse" / "silver" / "catalog.sqlite",
            summary.run_id,
        )
        self.assertTrue(out["found"])
        self.assertEqual(len(out["verification_outcomes"]), 4)
        self.assertEqual(len(out["campaigns"]), 2)
        self.assertEqual(len(out["mcdc"]), 1)

    def test_gold_views_queryable(self):
        ingest_report(self.report, self.tmp / "lakehouse", None)
        db = self.tmp / "lakehouse" / "silver" / "catalog.sqlite"
        with sqlite3.connect(str(db)) as conn:
            esc = conn.execute(
                "SELECT escape_rate FROM weekly_escape_rate LIMIT 1"
            ).fetchone()
            self.assertIsNotNone(esc)
            # one of two campaigns escaped → 0.5
            self.assertAlmostEqual(esc[0], 0.5, places=2)
            cov = conn.execute(
                "SELECT mean_mcdc_pct FROM daily_coverage LIMIT 1"
            ).fetchone()
            self.assertIsNotNone(cov)


class TestDriftDetector(unittest.TestCase):
    def test_clean_payload_passes(self):
        path = ROOT / "evidence" / "test_drift_clean.json"
        path.write_text(json.dumps(_sample_payload()), encoding="utf-8")
        rep = detect_drift(path)
        self.assertTrue(rep.ok, rep.to_dict())

    def test_missing_top_level_key_caught(self):
        payload = _sample_payload()
        del payload["mcdc"]
        path = ROOT / "evidence" / "test_drift_missing.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        rep = detect_drift(path)
        self.assertFalse(rep.ok)
        self.assertTrue(any("mcdc" in m for m in rep.missing))

    def test_unexpected_top_level_key_caught(self):
        payload = _sample_payload()
        payload["weird_new_section"] = []
        path = ROOT / "evidence" / "test_drift_unexpected.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        rep = detect_drift(path)
        self.assertFalse(rep.ok)
        self.assertTrue(any("weird_new_section" in m for m in rep.unexpected))


class TestBusParser(unittest.TestCase):
    def test_round_trip_through_recorder(self):
        rec = Recorder()
        rec.append(0, "A429", "MSG-001", b"\x01\x02")
        rec.append(1000, "AFDX", "MSG-004", b"\x03\x04\x05")
        events = list(parse_bus_recording(rec.to_bytes()))
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0].msg_id, "MSG-001")
        self.assertEqual(events[0].payload_len, 2)
        self.assertEqual(events[1].bus, "AFDX")


if __name__ == "__main__":
    unittest.main()
