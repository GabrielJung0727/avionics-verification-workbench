"""Escape-candidate + pilot-timing tests."""
import unittest
from pathlib import Path
from . import _paths  # noqa: F401

import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from fault_injector.escape import (
    EscapeCandidate,
    collect_escapes,
    render_markdown,
)
from avx_sim.hf import PilotTask, TaskStep, response_budget, STANDARD_TASKS


class TestEscapeCollector(unittest.TestCase):

    def test_collect_from_classified_campaigns(self):
        campaigns = [
            {"id": "FC-003", "classification": "escaped", "_fault_hint": "afdx_delay"},
            {"id": "FC-001", "classification": "mitigated_only"},
        ]
        out = collect_escapes(campaigns)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].campaign_id, "FC-003")
        self.assertEqual(out[0].fc_id, "FC-10")

    def test_markdown_has_draft_banner(self):
        md = render_markdown([
            EscapeCandidate("FC-003", "afdx_delay", "FC-10", "REQ-CAND-X"),
        ])
        self.assertIn("DRAFT", md)
        self.assertIn("FC-003", md)

    def test_empty_escapes_render(self):
        md = render_markdown([])
        self.assertIn("No escapes", md)


class TestPilotTiming(unittest.TestCase):

    def test_standard_tasks_within_budget(self):
        for tid, task in STANDARD_TASKS.items():
            rep = response_budget(task, display_latency_us=50_000)
            self.assertTrue(rep["within_budget"], f"{tid} busted budget")
            self.assertIn("steps", rep)

    def test_large_display_latency_eats_margin(self):
        task = STANDARD_TASKS["engine-caution-ack"]
        rep = response_budget(task, display_latency_us=task.deadline_us)
        self.assertFalse(rep["within_budget"])

    def test_custom_task(self):
        task = PilotTask(
            id="test",
            description="custom",
            steps=[TaskStep("a", 100), TaskStep("b", 200)],
            deadline_us=500,
        )
        rep = response_budget(task)
        self.assertTrue(rep["within_budget"])
        self.assertEqual(rep["total_us"], 300)


if __name__ == "__main__":
    unittest.main()
