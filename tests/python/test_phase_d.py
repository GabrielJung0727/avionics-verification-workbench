"""Phase D — Bounded Operational AI Research tests.

Verifies the runtime assurance shell, the mode harnesses, the approval
gate, and the online-learning prohibition.
"""
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
from intelligence.runtime import (  # noqa: E402
    AckQueue,
    AdvisoryMode,
    ApprovalGateError,
    AuthorityBudget,
    DisagreementTracker,
    LimitedSupervisedMode,
    Mode,
    OnlineLearningAttempt,
    RuntimeAssuranceShell,
    RuntimeHarness,
    ShadowMode,
    ShellConfig,
    ShellViolation,
    load_with_approval_gate,
)
from intelligence.registry.registry import dataset_hash_for  # noqa: E402


class TestRuntimeAssuranceShell(unittest.TestCase):

    def test_range_violation_clamped(self):
        shell = RuntimeAssuranceShell(
            ShellConfig(output_keys=["x"], ranges={"x": (-1.0, 1.0)})
        )
        result = shell.evaluate(lambda: {"x": 3.0})
        self.assertEqual(result.guarded["x"], 1.0)
        self.assertIn(ShellViolation.RANGE, result.violations)

    def test_rate_violation_smoothed(self):
        shell = RuntimeAssuranceShell(
            ShellConfig(output_keys=["x"], rate_limits={"x": 0.1})
        )
        shell.evaluate(lambda: {"x": 0.0})
        result = shell.evaluate(lambda: {"x": 1.0})
        self.assertAlmostEqual(result.guarded["x"], 0.1, places=6)
        self.assertIn(ShellViolation.RATE, result.violations)

    def test_authority_engages_fallback(self):
        called = {"fallback": 0}

        def fb(_):
            called["fallback"] += 1
            return {"x": 0.0}

        shell = RuntimeAssuranceShell(
            ShellConfig(
                output_keys=["x"],
                authority={"x": AuthorityBudget(max_abs_value=0.5,
                                                max_abs_delta=0.5)},
            ),
            fallback_provider=fb,
        )
        result = shell.evaluate(lambda: {"x": 5.0})
        self.assertTrue(result.fallback_engaged)
        self.assertEqual(called["fallback"], 1)
        self.assertIn(ShellViolation.AUTHORITY, result.violations)

    def test_watchdog_engages_fallback(self):
        # Force the elapsed time past the watchdog by providing a fake clock
        # that always reports an enormous gap.
        clock = iter([0.0, 1.0])  # 1 second between start/end -> 1_000_000 us
        shell = RuntimeAssuranceShell(
            ShellConfig(output_keys=["x"], watchdog_us=1000),
            fallback_provider=lambda _: {"x": 0.0},
        )
        result = shell.evaluate(
            lambda: {"x": 0.5},
            wall_clock=lambda: next(clock),
        )
        self.assertIn(ShellViolation.WATCHDOG, result.violations)
        self.assertTrue(result.fallback_engaged)

    def test_invalid_output_engages_fallback(self):
        shell = RuntimeAssuranceShell(
            ShellConfig(output_keys=["x"]),
            fallback_provider=lambda _: {"x": 0.0},
        )
        result = shell.evaluate(lambda: "garbage")
        self.assertIn(ShellViolation.INVALID_OUTPUT, result.violations)
        self.assertTrue(result.fallback_engaged)


class TestModes(unittest.TestCase):

    def test_shadow_logs_only(self):
        m = ShadowMode()
        m.consume({"x": 1.0}, {"x": 1.0}, [])
        self.assertEqual(len(m.log), 1)

    def test_advisory_parks_to_queue(self):
        q = AckQueue()
        m = AdvisoryMode(q)
        m.consume({"x": 1.0}, {"x": 1.0}, [])
        self.assertEqual(len(q.pending), 1)
        ack = q.ack(q.pending[0]["ack_id"], "operator", "accept")
        self.assertEqual(ack.decision, "accept")

    def test_limited_supervised_requires_ack_then_applies(self):
        q = AckQueue()
        applied: list[dict] = []

        def consumer(payload):
            applied.append(payload)

        m = LimitedSupervisedMode(
            queue=q, consumer=consumer,
            allowed_consumer_keys={"x"},
        )
        ack_id = m.consume({"x": 0.5, "y": 99}, {"x": 0.5, "y": 99}, [])
        self.assertEqual(applied, [])           # nothing yet
        # accept -> still not applied until apply_if_acked is called
        q.ack(ack_id, "engineer", "accept")
        n = m.apply_if_acked()
        self.assertEqual(n, 1)
        self.assertEqual(applied[0], {"x": 0.5})  # y filtered out


class TestApprovalGate(unittest.TestCase):

    def _make_registry(self, tmp: Path, *, state: str):
        reg = LocalRegistry(root=tmp)
        rec = ModelRecord(
            meta=ModelMeta(
                model_name="m", version="v0",
                intended_use="x", out_of_scope=["y"],
                training_seed=1, approval_state=state,
            ),
            dataset=DatasetMeta(
                dataset_version="v1", dataset_hash=dataset_hash_for(b"abc"),
                n_train=1, n_holdout=1,
                split_strategy="campaign-family", split_key="k",
                feature_columns=["a"], label_column="b",
                label_version="oracle-v1",
            ),
            metrics={"auc": 0.9},
        )

        # Use a picklable dict so we don't need a top-level dummy class.
        reg.register(model_obj={"weights": [1, 2, 3]}, record=rec, repo=ROOT)

    def test_shadow_allowed_for_auto_generated(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._make_registry(Path(tmp), state="auto-generated")
            model, meta = load_with_approval_gate(
                Path(tmp), "m", "v0", mode=Mode.SHADOW,
            )
            self.assertEqual(meta["approval_state"], "auto-generated")

    def test_advisory_blocked_for_auto_generated(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._make_registry(Path(tmp), state="auto-generated")
            with self.assertRaises(ApprovalGateError):
                load_with_approval_gate(
                    Path(tmp), "m", "v0", mode=Mode.ADVISORY,
                )

    def test_advisory_allowed_for_board_approved(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._make_registry(Path(tmp), state="board-approved")
            # Phase C invalidation cross-check requires an audit log entry
            # consistent with the current state, so we seed one.
            log_path = Path(tmp) / "m" / "v0" / "approval_log.json"
            ds_hash = json.loads(
                (Path(tmp) / "m" / "v0" / "dataset.json").read_text(encoding="utf-8")
            )["dataset_hash"]
            git_sha = json.loads(
                (Path(tmp) / "m" / "v0" / "meta.json").read_text(encoding="utf-8")
            )["git_sha"]
            log_path.write_text(json.dumps([
                {"from_state": "auto-generated",
                 "to_state": "reviewer-confirmed",
                 "reviewer": "alice", "rationale": "ok",
                 "timestamp": "2026-04-14T00:00:00+00:00",
                 "meta_snapshot": {"git_sha": git_sha},
                 "dataset_snapshot": {"dataset_hash": ds_hash}},
                {"from_state": "reviewer-confirmed",
                 "to_state": "board-approved",
                 "reviewer": "carol", "rationale": "approved",
                 "timestamp": "2026-04-14T01:00:00+00:00",
                 "meta_snapshot": {"git_sha": git_sha},
                 "dataset_snapshot": {"dataset_hash": ds_hash}},
            ]), encoding="utf-8")
            model, meta = load_with_approval_gate(
                Path(tmp), "m", "v0", mode=Mode.ADVISORY,
            )
            self.assertEqual(meta["mode"], "advisory")

    def test_online_learning_attempt_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._make_registry(Path(tmp), state="auto-generated")
            model, _ = load_with_approval_gate(
                Path(tmp), "m", "v0", mode=Mode.SHADOW,
            )
            with self.assertRaises(OnlineLearningAttempt):
                model.fit([[1, 2]], [0])
            with self.assertRaises(OnlineLearningAttempt):
                model.partial_fit([[1, 2]], [0])


class TestHarnessSmoke(unittest.TestCase):

    def test_shadow_harness_records_disagreement(self):
        shell = RuntimeAssuranceShell(
            ShellConfig(output_keys=["score"],
                        ranges={"score": (-1.0, 1.0)})
        )

        def ai(sample):
            # alternates between two scores so we exercise the rate path
            return {"score": 0.3 if sample % 2 == 0 else -0.3,
                    "decision": "alert" if sample % 2 == 0 else "nominal"}

        def det(sample):
            return "nominal"     # always nominal -> AI disagrees half the time

        harness = RuntimeHarness(
            mode_obj=ShadowMode(),
            shell=shell,
            ai_decision_fn=ai,
            deterministic_decision_fn=det,
            ai_to_decision=lambda g: g["decision"],
        )
        for i in range(10):
            harness.tick(i)
        rep = harness.report()
        self.assertEqual(rep.samples, 10)
        self.assertAlmostEqual(rep.agreement_rate, 0.5, places=2)
        self.assertEqual(rep.fallback_rate, 0.0)


if __name__ == "__main__":
    unittest.main()
