"""AI assistance layer tests."""
import json
import tempfile
import unittest
from pathlib import Path
from . import _paths  # noqa: F401

import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from ai_assistant import (
    generate_test_skeletons,
    cluster_log_events,
    triage_summary,
    build_impact_index,
    impact_for_requirement,
    summarize_evidence_markdown,
    draft_do178c_objective_table,
    trace_mermaid,
    DRAFT_BANNER,
)
from avx_sim.health_monitor import HealthMonitor, HmEvent

REQ_CSV = ROOT / "docs" / "M1" / "requirements" / "requirements.csv"
TEST_CASES = ROOT / "tools" / "runner" / "test_cases"


class TestSkeletonGenerator(unittest.TestCase):

    def test_generates_one_file_per_HLR(self):
        with tempfile.TemporaryDirectory() as td:
            written = generate_test_skeletons(REQ_CSV, td, overwrite=True)
            self.assertGreater(len(written), 10)
            # Every generated file carries the DRAFT banner and HLR id
            any_file = written[0]
            data = json.loads(any_file.read_text(encoding="utf-8"))
            self.assertIn("DRAFT", data["_draft"])
            self.assertTrue(any(r.startswith("HLR-") for r in data["req"]))


class TestTriage(unittest.TestCase):

    def _events(self):
        hm = HealthMonitor()
        hm.record(0, "FCC", HmEvent.LANE_DISAGREE, "HIGH")
        hm.record(10, "FCC", HmEvent.LANE_DISAGREE, "HIGH")
        hm.record(20, "DC:L", HmEvent.IPC_STALE, "MED")
        return hm.events

    def test_cluster_counts(self):
        clusters = cluster_log_events(self._events())
        self.assertIn("LANE_DISAGREE", clusters)
        self.assertEqual(clusters["LANE_DISAGREE"]["count"], 2)

    def test_triage_summary_has_draft_label(self):
        summary = triage_summary(self._events())
        self.assertIn("DRAFT", summary)
        self.assertIn("LANE_DISAGREE", summary)

    def test_empty_triage(self):
        self.assertIn("no events", triage_summary([]))


class TestChangeImpact(unittest.TestCase):

    def test_index_links_req_to_tests_and_code(self):
        idx = build_impact_index(TEST_CASES)
        self.assertIn("HLR-FCC-004", idx.req_to_tests)
        res = impact_for_requirement(idx, "HLR-FCC-004")
        self.assertIn("TC-FCC-004", res["tests"])
        self.assertTrue(any("fcc.py" in p for p in res["code_paths"]))
        self.assertIn("DRAFT", res["_draft"])


class TestEvidenceSummary(unittest.TestCase):

    def test_summary_renders_markdown(self):
        report = ROOT / "evidence" / "verification-report.json"
        if not report.exists():
            self.skipTest("no verification report yet")
        md = summarize_evidence_markdown(report)
        self.assertIn("DRAFT", md)
        self.assertIn("coverage", md.lower())


class TestObjectiveDraft(unittest.TestCase):

    def test_objective_table_renders(self):
        report = ROOT / "evidence" / "verification-report.json"
        if not report.exists():
            self.skipTest("no verification report yet")
        md = draft_do178c_objective_table(report)
        self.assertIn("DRAFT", md)
        self.assertIn("| Objective |", md)


class TestTraceGraph(unittest.TestCase):

    def test_mermaid_output_contains_arrows(self):
        g = trace_mermaid({"HLR-FCC-004": ["TC-FCC-004"],
                           "HLR-ENG-001": ["TC-ENG-001"]})
        self.assertIn("```mermaid", g)
        self.assertIn("-->", g)
        self.assertIn("HLR_FCC_004", g)


if __name__ == "__main__":
    unittest.main()
