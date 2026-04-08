"""M4 verification runner tests."""
import unittest
from pathlib import Path
from . import _paths  # noqa: F401

import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from runner import (  # noqa: E402
    discover_test_cases,
    run_all,
    build_trace,
    build_gap_report,
)

CASES_DIR = ROOT / "tools" / "runner" / "test_cases"
REQ_CSV = ROOT / "docs" / "M1" / "requirements" / "requirements.csv"


class TestVerificationRunner(unittest.TestCase):

    def setUp(self):
        self.cases = discover_test_cases(CASES_DIR)

    def test_discovers_test_cases(self):
        self.assertGreaterEqual(len(self.cases), 5)
        ids = {tc.id for tc in self.cases}
        self.assertIn("TC-FCC-001", ids)
        self.assertIn("TC-FCC-004", ids)

    def test_all_cases_pass(self):
        results = run_all(self.cases)
        failures = [r for r in results if r.result != "PASS"]
        if failures:
            for f in failures:
                print(f.id, f.result, f.failures)
        self.assertEqual(failures, [])

    def test_trace_links_req_to_tests(self):
        results = run_all(self.cases)
        trace = build_trace(results)
        # HLR-FCC-004 must be covered by TC-FCC-004
        self.assertIn("HLR-FCC-004", trace)
        self.assertIn("TC-FCC-004", trace["HLR-FCC-004"])

    def test_gap_report_finds_uncovered_requirements(self):
        gap = build_gap_report(self.cases, REQ_CSV)
        # We have many requirements; only a handful are covered by M4 seed
        self.assertGreater(gap["requirements_total"], 30)
        self.assertGreater(len(gap["requirements_uncovered"]), 0)
        # No tests should reference unknown reqs
        self.assertEqual(gap["tests_referencing_unknown_req"], [])


if __name__ == "__main__":
    unittest.main()
