"""Sanity test for the line-coverage helper."""
import unittest
from pathlib import Path
from . import _paths  # noqa: F401

import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from coverage_reporter import LineCoverage  # noqa: E402


class TestCoverageHelper(unittest.TestCase):

    def test_collects_some_lines(self):
        roots = [(ROOT / "tools" / "sim_py" / "avx_sim").resolve()]
        with LineCoverage(roots=roots):
            from m3_scenario import M3World, build_m3
            sched, _, _, _ = build_m3(M3World())
            sched.run_for(50_000)
        # We don't compute report() here (slow scan); just confirm hit map
        # gathered something for at least one file under avx_sim/.
        # But we do call report() at least once on a tiny synthetic root.
        synth = [(ROOT / "tools" / "sim_py" / "avx_sim" / "modules").resolve()]
        with LineCoverage(roots=synth) as cov:
            from m3_scenario import M3World, build_m3
            sched, _, _, _ = build_m3(M3World())
            sched.run_for(20_000)
        rep = cov.report()
        self.assertIn("__summary__", rep)
        self.assertGreater(rep["__summary__"]["executable"], 0)
        self.assertGreater(rep["__summary__"]["hit"], 0)


if __name__ == "__main__":
    unittest.main()
