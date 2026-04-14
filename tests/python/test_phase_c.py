"""Phase C — Reviewable Safety Case tests."""
import json
import tempfile
import unittest
from pathlib import Path
from . import _paths  # noqa: F401

import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from intelligence import (  # noqa: E402
    DatasetMeta,
    LocalRegistry,
    ModelMeta,
    ModelRecord,
)
from intelligence.governance import (  # noqa: E402
    REQUIRED_SECTIONS,
    lint_case,
    lint_all_cases,
    promote_state,
    demote_state,
    PromotionError,
    detect_state_invalidations,
)
from intelligence.governance.approval import ApprovalState  # noqa: E402
from intelligence.registry.registry import dataset_hash_for  # noqa: E402

CASES_DIR = ROOT / "docs" / "PhaseC" / "cases"


class TestAssuranceLint(unittest.TestCase):

    def test_all_real_cases_pass_lint(self):
        reports = lint_all_cases(CASES_DIR)
        # We expect at least the three Phase B model cases.
        self.assertGreaterEqual(len(reports), 3)
        bad = [r for r in reports if not r.ok]
        if bad:
            for r in bad:
                print(r.to_dict())
        self.assertEqual(bad, [])

    def test_required_sections_list_non_empty(self):
        self.assertGreaterEqual(len(REQUIRED_SECTIONS), 12)

    def test_lint_catches_missing_section(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "broken.md"
            # Missing every section except #1
            p.write_text(
                "### 1. Identity\n```\nmodel_name: x\nversion: v\n"
                "case_owner: o\nlast_reviewed: 2026-04-14\n"
                "state: auto-generated\n```\n",
                encoding="utf-8",
            )
            rep = lint_case(p)
            self.assertFalse(rep.ok)
            self.assertGreater(len(rep.missing_sections), 5)

    def test_lint_catches_invalid_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "weird.md"
            body = "### 1. Identity\n```\nmodel_name: x\nversion: v\n" \
                   "case_owner: o\nlast_reviewed: 2026-04-14\n" \
                   "state: GOD-MODE\n```\n"
            for s in REQUIRED_SECTIONS[1:]:
                body += f"\n### {s}\nbody\n"
            p.write_text(body, encoding="utf-8")
            rep = lint_case(p)
            self.assertEqual(rep.invalid_state, "GOD-MODE")
            self.assertFalse(rep.ok)


class _RegistryHelper:
    @staticmethod
    def make(tmp: Path, *, state: str = "auto-generated") -> tuple[LocalRegistry, str, str]:
        reg = LocalRegistry(root=tmp)
        rec = ModelRecord(
            meta=ModelMeta(
                model_name="m",
                version="v0",
                intended_use="x",
                out_of_scope=["y"],
                training_seed=1,
                approval_state=state,
            ),
            dataset=DatasetMeta(
                dataset_version="v1",
                dataset_hash=dataset_hash_for(b"abc"),
                n_train=1, n_holdout=1,
                split_strategy="campaign-family", split_key="k",
                feature_columns=["a"], label_column="b",
                label_version="oracle-v1",
            ),
            metrics={"auc": 0.9},
        )
        reg.register(model_obj={}, record=rec, repo=ROOT)
        return reg, "m", "v0"


class TestApprovalWorkflow(unittest.TestCase):

    def test_promote_requires_assurance_case_for_first_step(self):
        with tempfile.TemporaryDirectory() as tmp:
            reg, name, version = _RegistryHelper.make(Path(tmp))
            with self.assertRaises(PromotionError):
                promote_state(
                    Path(tmp), name, version,
                    reviewer="alice", author="bob",
                    rationale="lgtm",
                    assurance_case_path=None,
                )

    def test_promote_blocks_self_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            reg, name, version = _RegistryHelper.make(Path(tmp))
            case = CASES_DIR / "escape-predictor.md"
            with self.assertRaises(PromotionError):
                promote_state(
                    Path(tmp), name, version,
                    reviewer="bob", author="bob",
                    rationale="self-promote",
                    assurance_case_path=case,
                )

    def test_promote_succeeds_with_valid_case(self):
        with tempfile.TemporaryDirectory() as tmp:
            reg, name, version = _RegistryHelper.make(Path(tmp))
            case = CASES_DIR / "escape-predictor.md"
            rec = promote_state(
                Path(tmp), name, version,
                reviewer="alice", author="bob",
                rationale="reviewed end to end",
                assurance_case_path=case,
            )
            self.assertEqual(rec.from_state, ApprovalState.AUTO.value)
            self.assertEqual(rec.to_state, ApprovalState.REVIEWER.value)
            meta = json.loads(
                (Path(tmp) / name / version / "meta.json").read_text(encoding="utf-8")
            )
            self.assertEqual(meta["approval_state"], ApprovalState.REVIEWER.value)
            log = json.loads(
                (Path(tmp) / name / version / "approval_log.json").read_text(encoding="utf-8")
            )
            self.assertEqual(len(log), 1)
            self.assertEqual(log[0]["reviewer"], "alice")

    def test_demote_returns_to_auto(self):
        with tempfile.TemporaryDirectory() as tmp:
            reg, name, version = _RegistryHelper.make(Path(tmp))
            case = CASES_DIR / "escape-predictor.md"
            promote_state(
                Path(tmp), name, version,
                reviewer="alice", author="bob",
                rationale="ok",
                assurance_case_path=case,
            )
            rec = demote_state(
                Path(tmp), name, version,
                reviewer="alice", rationale="dataset hash changed",
            )
            self.assertEqual(rec.to_state, ApprovalState.AUTO.value)


class TestChangeImpactDetector(unittest.TestCase):

    def test_no_invalidations_when_all_auto(self):
        with tempfile.TemporaryDirectory() as tmp:
            _RegistryHelper.make(Path(tmp))
            invs = detect_state_invalidations(Path(tmp))
            self.assertEqual(invs, [])

    def test_orphan_state_without_audit_is_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            reg, name, version = _RegistryHelper.make(Path(tmp))
            # Manually advance state without going through the workflow
            meta_path = Path(tmp) / name / version / "meta.json"
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            meta["approval_state"] = ApprovalState.REVIEWER.value
            meta_path.write_text(json.dumps(meta), encoding="utf-8")
            invs = detect_state_invalidations(Path(tmp))
            self.assertEqual(len(invs), 1)
            self.assertIn("no audit record for current state",
                          invs[0].reasons)


if __name__ == "__main__":
    unittest.main()
