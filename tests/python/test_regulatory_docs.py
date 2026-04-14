"""Regulatory stack reference — verifies that every required 1-pager
exists, declares its scope honestly, and links into the master disclaimer.
"""
import unittest
from pathlib import Path
from . import _paths  # noqa: F401

ROOT = Path(__file__).resolve().parents[2]
REG = ROOT / "docs" / "regulatory"


REQUIRED_PAGES = [
    "README.md",
    "disclaimer.md",
    "arp4754a.md",
    "arp4761a.md",
    "do178c.md",
    "do330.md",
    "do160g.md",
    "do254.md",
    "ac-20-174.md",
    "ac-20-115d.md",
    "ac-20-175.md",
    "easa-ai-concept-paper.md",
    "faa-ai-roadmap.md",
]


class TestRegulatoryFolderExists(unittest.TestCase):

    def test_required_pages_present(self):
        for name in REQUIRED_PAGES:
            self.assertTrue((REG / name).exists(),
                            f"missing {name}")

    def test_index_lists_every_page(self):
        index = (REG / "README.md").read_text(encoding="utf-8")
        for name in REQUIRED_PAGES:
            if name == "README.md":
                continue
            self.assertIn(name, index, f"index does not link to {name}")


class TestExplicitOutOfScopeDeclarations(unittest.TestCase):

    def test_do160g_is_explicitly_out_of_scope(self):
        body = (REG / "do160g.md").read_text(encoding="utf-8")
        self.assertIn("OUT OF SCOPE", body)
        self.assertIn("DO-160G compliance", body)

    def test_do254_is_explicitly_out_of_scope(self):
        body = (REG / "do254.md").read_text(encoding="utf-8")
        self.assertIn("OUT OF SCOPE", body)


class TestAiMemos(unittest.TestCase):

    def test_easa_memo_covers_levels_and_frozen(self):
        body = (REG / "easa-ai-concept-paper.md").read_text(encoding="utf-8")
        for token in ("Level 1A", "Level 1B", "Level 2A", "Level 2B",
                      "frozen", "online learning",
                      "OnlineLearningAttempt", "Shadow"):
            self.assertIn(token, body)

    def test_faa_memo_covers_learned_vs_learning_and_runtime(self):
        body = (REG / "faa-ai-roadmap.md").read_text(encoding="utf-8")
        for token in ("Learned AI", "Learning AI", "Runtime assurance",
                      "Incremental", "Shadow", "Advisory",
                      "LimitedSupervised", "OnlineLearningAttempt"):
            self.assertIn(token, body)


class TestM1MappingExtended(unittest.TestCase):

    def test_m1_mapping_links_to_regulatory_folder(self):
        body = (ROOT / "docs" / "M1" / "certification"
                / "do178c-mapping.md").read_text(encoding="utf-8")
        for token in ("docs/regulatory/", "ARP4754A", "ARP4761A", "DO-330",
                      "DO-160G", "DO-254", "AC 20-174", "AC 20-115D",
                      "AC 20-175", "EASA AI Concept Paper",
                      "FAA AI Roadmap"):
            self.assertIn(token, body)

    def test_m1_mapping_keeps_disclaimer(self):
        body = (ROOT / "docs" / "M1" / "certification"
                / "do178c-mapping.md").read_text(encoding="utf-8")
        self.assertIn("disclaimer", body.lower())


class TestMasterDisclaimer(unittest.TestCase):

    def test_disclaimer_covers_dal_tql_and_ai_levels(self):
        body = (REG / "disclaimer.md").read_text(encoding="utf-8")
        self.assertIn("learning", body.lower())
        for token in ("DAL", "TQL", "AI-level"):
            self.assertIn(token, body)


if __name__ == "__main__":
    unittest.main()
