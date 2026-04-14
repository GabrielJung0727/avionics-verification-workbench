"""Phase E — Portfolio packaging tests.

Ensures that:
  - the pitch text exists and stays under interview-friendly length budgets
  - the FAQ files exist with the expected anchors
  - the v2 standards mapping exists and references the new AI guidance
  - the README exposes the Phase A–E narrative
"""
import unittest
from pathlib import Path
from . import _paths  # noqa: F401

import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from portfolio import HARD_LINE, PITCH_5S, PITCH_30S, PITCH_60S, pitch  # noqa: E402


PHASE_E = ROOT / "docs" / "PhaseE"


class TestPitch(unittest.TestCase):

    def test_pitch_lengths_are_interview_friendly(self):
        # Approximate spoken-word budget: ~3 words/sec
        self.assertLess(len(PITCH_5S.split()), 35,
                        "5s pitch must fit roughly 5 seconds spoken")
        self.assertLess(len(PITCH_30S.split()), 200,
                        "30s pitch must fit roughly 30 seconds spoken")
        self.assertLess(len(PITCH_60S.split()), 350,
                        "60s pitch must fit roughly 60 seconds spoken")

    def test_hard_line_is_canonical(self):
        # The "not an AI flight controller" message must appear in README
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        normalised = (readme.lower()
                      .replace("**", "")
                      .replace("*", "")
                      .replace("_", ""))
        self.assertIn("not an ai flight controller", normalised)
        self.assertIn("certification-aligned", HARD_LINE.lower())

    def test_pitch_helper_routes_correctly(self):
        self.assertEqual(pitch("5s"), PITCH_5S)
        self.assertEqual(pitch("30s"), PITCH_30S)
        self.assertEqual(pitch("60s"), PITCH_60S)
        self.assertEqual(pitch("hard-line"), HARD_LINE)
        with self.assertRaises(KeyError):
            pitch("90s")


class TestFaqArtifacts(unittest.TestCase):

    def test_why_ai_not_in_loop_exists(self):
        p = PHASE_E / "faq" / "why-ai-not-in-control-loop.md"
        self.assertTrue(p.exists())
        body = p.read_text(encoding="utf-8")
        self.assertIn("EASA AI Concept Paper", body)
        self.assertIn("FAA Roadmap", body)
        self.assertIn("OnlineLearningAttempt", body)

    def test_vs_skywise_exists(self):
        p = PHASE_E / "faq" / "vs-skywise-forge-collins.md"
        self.assertTrue(p.exists())
        body = p.read_text(encoding="utf-8")
        for keyword in ("Skywise", "Forge", "Collins", "lakehouse"):
            self.assertIn(keyword, body)


class TestStandardsMappingV2(unittest.TestCase):

    def test_mapping_v2_exists_with_ai_guidance(self):
        p = PHASE_E / "standards" / "standards-mapping-v2.md"
        self.assertTrue(p.exists())
        body = p.read_text(encoding="utf-8")
        for token in ("EASA AI Concept Paper", "FAA AI Roadmap",
                      "FAA Order 8110.49A", "DO-330", "ARP4754A"):
            self.assertIn(token, body)


class TestPortfolioPack(unittest.TestCase):

    def test_one_page_architecture_present(self):
        p = PHASE_E / "portfolio" / "one-page-architecture.md"
        self.assertTrue(p.exists())
        body = p.read_text(encoding="utf-8")
        self.assertIn("Hard line", body)
        self.assertIn("Phase A", body)
        self.assertIn("Phase D", body)

    def test_resume_bullets_v2_present(self):
        p = PHASE_E / "portfolio" / "resume-bullets-v2.md"
        self.assertTrue(p.exists())
        body = p.read_text(encoding="utf-8")
        # At least 5 position-tailored variants mentioned
        for role in ("Flight software", "Verification", "Display",
                     "IMA", "Defence", "Data"):
            self.assertIn(role, body)

    def test_linkedin_v2_present(self):
        p = PHASE_E / "portfolio" / "linkedin-post-v2.md"
        self.assertTrue(p.exists())
        body = p.read_text(encoding="utf-8")
        self.assertIn("Phase A", body)
        self.assertIn("Phase D", body)
        self.assertIn("OnlineLearningAttempt", body)

    def test_demo_script_v2_present(self):
        p = PHASE_E / "demo" / "demo-script-v2.md"
        self.assertTrue(p.exists())
        body = p.read_text(encoding="utf-8")
        self.assertIn("Shadow", body)
        self.assertIn("lakehouse", body)


class TestReadmeNarrative(unittest.TestCase):

    def test_readme_lists_phase_a_through_e(self):
        body = (ROOT / "README.md").read_text(encoding="utf-8")
        # Accept either "Phase X" with a space, "PhaseX" (folder ref) or
        # "Phase A–E" range form.
        for letter in ("A", "B", "C", "D", "E"):
            patterns = [f"Phase {letter}", f"Phase{letter}", f"Phase A\u2013{letter}"]
            self.assertTrue(
                any(p in body for p in patterns),
                f"README must reference Phase {letter} in some form",
            )

    def test_readme_links_to_phase_e_docs(self):
        body = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("docs/PhaseE", body)


if __name__ == "__main__":
    unittest.main()
