"""Phase B — Certification Intelligence tests."""
import json
import tempfile
import unittest
from pathlib import Path
from . import _paths  # noqa: F401

import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import numpy as np  # noqa: E402

from intelligence import (  # noqa: E402
    DatasetMeta,
    LocalRegistry,
    ModelMeta,
    ModelRecord,
)
from intelligence.data import (  # noqa: E402
    generate_fault_sweep,
    split_by_key,
)
from intelligence.predictors import (  # noqa: E402
    train_escape_predictor,
    score_escape,
    train_engine_anomaly,
    score_engine_window,
    rank_impacted_requirements,
)
from intelligence.predictors.engine_anomaly import _window_features  # noqa: E402
from intelligence.predictors.trace_gap_intel import evaluate_on_synthetic  # noqa: E402
from intelligence.registry.registry import dataset_hash_for  # noqa: E402


class TestFaultSweep(unittest.TestCase):
    def test_sweep_deterministic(self):
        a = generate_fault_sweep(seed=42, target_count=200)
        b = generate_fault_sweep(seed=42, target_count=200)
        self.assertEqual(len(a), len(b))
        self.assertEqual([r.classification for r in a],
                         [r.classification for r in b])

    def test_split_by_key_no_leakage(self):
        sweep = generate_fault_sweep(seed=42, target_count=300)
        train, test = split_by_key(
            sweep, key_fn=lambda r: f"seed_{r.seed}",
            holdout_keys=["seed_7"],
        )
        self.assertGreater(len(train), 0)
        self.assertGreater(len(test), 0)
        self.assertTrue(all(r.seed != 7 for r in train))
        self.assertTrue(all(r.seed == 7 for r in test))


class TestEscapePredictor(unittest.TestCase):
    def test_train_and_score(self):
        sweep = generate_fault_sweep(seed=42, target_count=600)
        train, test = split_by_key(
            sweep, key_fn=lambda r: f"seed_{r.seed}",
            holdout_keys=["seed_7"],
        )
        model, eval_, X = train_escape_predictor(train, test, seed=42)
        self.assertGreater(eval_.auc, 0.7)
        self.assertGreater(eval_.f1, 0.5)
        out = score_escape(model, sweep[0])
        self.assertIn("p_escape", out)
        self.assertIn("_draft", out)
        self.assertIn(out["advice"], {"run early", "lower priority", "review"})


class TestEngineAnomaly(unittest.TestCase):
    def _streams(self):
        rng = np.random.default_rng(42)
        T = 200
        clean = np.column_stack([
            88 + 0.5 * np.sin(np.linspace(0, 4, T)),
            95 + 0.3 * np.sin(np.linspace(0, 5, T)),
            700 + 5 * np.sin(np.linspace(0, 3, T)),
            3000 + 50 * np.sin(np.linspace(0, 2, T)),
        ]) + rng.normal(0, 0.4, (T, 4))
        anom = clean.copy()
        for i in range(T // 2, T):
            anom[i, 2] += (i - T // 2) * 1.5
            anom[i, 0] += 0.2 * (i - T // 2)
        return clean, anom

    def test_train_score(self):
        clean, anom = self._streams()
        model, eval_, X = train_engine_anomaly(
            clean, anom, window=8, contamination=0.05, seed=42,
        )
        # Detection rate should beat a coin flip on the anomalous tail.
        self.assertGreater(eval_.detection_rate, 0.3)
        self.assertLess(eval_.false_alarm_rate, 0.20)

    def test_score_window_returns_decision(self):
        clean, anom = self._streams()
        model, _, _ = train_engine_anomaly(
            clean, anom, window=8, contamination=0.05, seed=42,
        )
        feats = _window_features(anom, 8)[-1]
        out = score_engine_window(model, feats)
        self.assertIn(out["decision"], {
            "preventive_alert", "early_warning",
            "inspection_candidate", "nominal",
        })
        self.assertIn("_draft", out)


class TestTraceGapIntel(unittest.TestCase):
    REQ_IDS = ["HLR-FCC-001", "HLR-FCC-003", "HLR-ENG-001",
               "HLR-DSP-001", "HLR-HM-001", "SYS-001"]

    def test_rank_for_fcc_diff(self):
        ranked = rank_impacted_requirements(
            ["tools/sim_py/avx_sim/modules/fcc.py"], self.REQ_IDS,
        )
        self.assertGreater(len(ranked), 0)
        self.assertTrue(ranked[0]["req_id"].startswith("HLR-FCC"))

    def test_evaluate_on_synthetic_meets_baseline(self):
        ev = evaluate_on_synthetic(self.REQ_IDS)
        self.assertGreaterEqual(ev.precision_at_3, 0.8)
        self.assertGreater(ev.mrr, 0.5)


class TestRegistry(unittest.TestCase):
    def test_register_and_load(self):
        with tempfile.TemporaryDirectory() as tmp:
            reg = LocalRegistry(root=Path(tmp))
            ds_bytes = b"feature_matrix"
            rec = ModelRecord(
                meta=ModelMeta(
                    model_name="t_model",
                    version="v0.0.1",
                    intended_use="unit test",
                    out_of_scope=["control loop"],
                    training_seed=1,
                ),
                dataset=DatasetMeta(
                    dataset_version="ds-v1",
                    dataset_hash=dataset_hash_for(ds_bytes),
                    n_train=10, n_holdout=2,
                    split_strategy="campaign-family",
                    split_key="fam_x",
                    feature_columns=["a", "b"],
                    label_column="y",
                    label_version="oracle-v1",
                ),
                metrics={"auc": 0.91},
            )
            d = reg.register(model_obj={"weights": [1, 2, 3]},
                             record=rec, repo=ROOT)
            self.assertTrue((d / "model.pkl").exists())
            self.assertTrue((d / "meta.json").exists())
            self.assertTrue((d / "dataset.json").exists())
            self.assertTrue((d / "metrics.json").exists())
            self.assertTrue((d / "model_card.json").exists())
            self.assertTrue((d / "assurance_stub.md").exists())
            obj, rec2 = reg.load("t_model", "v0.0.1")
            self.assertEqual(obj["weights"], [1, 2, 3])
            self.assertEqual(rec2.dataset.dataset_hash, rec.dataset.dataset_hash)
            self.assertEqual(rec2.meta.frozen, True)


class TestRegistryMetadataDiscipline(unittest.TestCase):
    def test_meta_is_frozen_and_marked_draft(self):
        with tempfile.TemporaryDirectory() as tmp:
            reg = LocalRegistry(root=Path(tmp))
            rec = ModelRecord(
                meta=ModelMeta(
                    model_name="m",
                    version="v0",
                    intended_use="x",
                    out_of_scope=["y"],
                    training_seed=1,
                ),
                dataset=DatasetMeta(
                    dataset_version="v1", dataset_hash="abcd",
                    n_train=1, n_holdout=1,
                    split_strategy="campaign-family", split_key="k",
                    feature_columns=["a"], label_column="b",
                    label_version="oracle-v1",
                ),
                metrics={"auc": 0.5},
            )
            d = reg.register(model_obj={}, record=rec, repo=ROOT)
            meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
            self.assertTrue(meta["frozen"])
            self.assertEqual(meta["approval_state"], "auto-generated")
            stub = (d / "assurance_stub.md").read_text(encoding="utf-8")
            self.assertIn("DRAFT", stub)
            self.assertIn("Out of scope", stub)


if __name__ == "__main__":
    unittest.main()
