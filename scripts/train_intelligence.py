#!/usr/bin/env python3
"""Phase B trainer.

Trains the three v0 frozen learned components, registers each in the local
model registry under ``evidence/registry/``, and emits a summary JSON used
by the orchestrator to attach Phase B output to the verification report.
"""
from __future__ import annotations
import csv
import json
import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from intelligence import (  # noqa: E402
    DatasetMeta,
    LocalRegistry,
    ModelMeta,
    ModelRecord,
)
from intelligence.data import generate_fault_sweep, split_by_key  # noqa: E402
from intelligence.predictors import (  # noqa: E402
    train_escape_predictor,
    train_engine_anomaly,
    rank_impacted_requirements,
)
from intelligence.predictors.trace_gap_intel import evaluate_on_synthetic  # noqa: E402
from intelligence.registry.registry import dataset_hash_for             # noqa: E402

REQ_CSV = ROOT / "docs" / "M1" / "requirements" / "requirements.csv"


def _load_req_ids() -> list[str]:
    out: list[str] = []
    with REQ_CSV.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            rid = row.get("id")
            if rid:
                out.append(rid)
    return out


def _make_engine_streams(seed: int = 42) -> tuple[np.ndarray, np.ndarray]:
    """Build clean + anomalous EngineRaw streams for the anomaly detector
    holdout. Deterministic so the registry hash is stable across runs."""
    rng = np.random.default_rng(seed)
    T = 600
    base = np.column_stack([
        88 + 0.5 * np.sin(np.linspace(0, 6, T)),
        95 + 0.3 * np.sin(np.linspace(0, 5, T)),
        700 + 5 * np.sin(np.linspace(0, 4, T)),
        3000 + 50 * np.sin(np.linspace(0, 3, T)),
    ])
    base += rng.normal(0, 0.4, base.shape)

    anomalous = base.copy()
    # Inject an EGT runaway in the second half
    for i in range(T // 2, T):
        delta = (i - T // 2) * 1.5
        anomalous[i, 2] += delta
        anomalous[i, 0] += 0.2 * delta
    return base, anomalous


def main() -> int:
    registry_root = ROOT / "evidence" / "registry"
    registry = LocalRegistry(root=registry_root)

    sweep = generate_fault_sweep(seed=42, target_count=600)
    print(f"sweep size: {len(sweep)}")

    # ---- escape predictor ----------------------------------------------
    # Non-random split: holdout = a different seed (bench surrogate). Each
    # family appears on both sides so labels stay balanced; the model still
    # has to generalize to a never-seen seed/bench to score.
    train_recs, holdout_recs = split_by_key(
        sweep, key_fn=lambda r: f"seed_{r.seed}",
        holdout_keys=["seed_7"],
    )
    if not holdout_recs:
        print("no holdout, aborting")
        return 1
    model_esc, eval_esc, X_train_esc = train_escape_predictor(
        train_recs, holdout_recs, seed=42,
    )
    ds_hash_esc = dataset_hash_for(X_train_esc.tobytes())
    record_esc = ModelRecord(
        meta=ModelMeta(
            model_name="fault_escape_predictor",
            version="v0.1.0",
            intended_use="Rank fault campaigns by P(escape) for verification "
                         "prioritization. Advisory only.",
            out_of_scope=[
                "any control-loop decision",
                "online learning",
                "automatic test selection without human review",
            ],
            training_seed=42,
        ),
        dataset=DatasetMeta(
            dataset_version="sweep-2026-04-14-v1",
            dataset_hash=ds_hash_esc,
            n_train=eval_esc.n_train,
            n_holdout=eval_esc.n_holdout,
            split_strategy="bench-seed",
            split_key="seed_7",
            feature_columns=[
                "delay_us", "drop_every_n", "n1_at_t1s",
                "egt_at_t1s", "dual_fault_us", "seed",
            ],
            label_column="label_escape",
            label_version="oracle-v1",
        ),
        metrics={
            "auc": eval_esc.auc,
            "precision": eval_esc.precision,
            "recall": eval_esc.recall,
            "f1": eval_esc.f1,
            "confusion_matrix": eval_esc.confusion_matrix,
            "holdout_keys": eval_esc.holdout_keys,
        },
    )
    esc_dir = registry.register(
        model_obj=model_esc, record=record_esc, repo=ROOT,
    )

    # ---- engine anomaly detector ---------------------------------------
    clean, anom = _make_engine_streams(seed=42)
    model_anom, eval_anom, X_train_anom = train_engine_anomaly(
        clean, anom, window=8, contamination=0.05, seed=42,
    )
    ds_hash_anom = dataset_hash_for(X_train_anom.tobytes())
    record_anom = ModelRecord(
        meta=ModelMeta(
            model_name="engine_anomaly_detector",
            version="v0.1.0",
            intended_use="Surface preventive alert / early warning / "
                         "inspection candidate from EngineRaw windows. "
                         "Advisory only; never closes a maintenance loop.",
            out_of_scope=[
                "automated grounding decisions",
                "online learning",
                "any control-loop authority",
            ],
            training_seed=42,
        ),
        dataset=DatasetMeta(
            dataset_version="engine-stream-2026-04-14-v1",
            dataset_hash=ds_hash_anom,
            n_train=eval_anom.n_train_windows,
            n_holdout=eval_anom.n_holdout_windows,
            split_strategy="time",
            split_key="second-half-anomalous",
            feature_columns=[
                "n1_mean", "n1_std", "n1_d_mean",
                "n2_mean", "n2_std", "n2_d_mean",
                "egt_mean", "egt_std", "egt_d_mean",
                "ff_mean",  "ff_std",  "ff_d_mean",
            ],
            label_column="anomaly",
            label_version="oracle-v1",
        ),
        metrics={
            "detection_rate": eval_anom.detection_rate,
            "false_alarm_rate": eval_anom.false_alarm_rate,
            "contamination": eval_anom.contamination,
            "window": eval_anom.window,
        },
    )
    anom_dir = registry.register(
        model_obj=model_anom, record=record_anom, repo=ROOT,
    )

    # ---- trace gap intelligence (rule-based v0) -----------------------
    req_ids = _load_req_ids()
    eval_tg = evaluate_on_synthetic(req_ids)
    record_tg = ModelRecord(
        meta=ModelMeta(
            model_name="trace_gap_intel",
            version="v0.1.0",
            intended_use="Rank requirements likely impacted by a code diff. "
                         "Rule-based baseline; learned ranker plugs in via "
                         "the same interface.",
            out_of_scope=[
                "automated requirement merge / waiver",
                "control-loop decisions of any kind",
            ],
            training_seed=42,
        ),
        dataset=DatasetMeta(
            dataset_version="req-csv-" + str(len(req_ids)),
            dataset_hash=dataset_hash_for(",".join(sorted(req_ids)).encode()),
            n_train=0,
            n_holdout=eval_tg.holdout_diffs,
            split_strategy="synthetic-diff-cases",
            split_key="hand-curated",
            feature_columns=["diff_paths"],
            label_column="impacted_req_prefix",
            label_version="oracle-v1",
        ),
        metrics={
            "precision_at_3": eval_tg.precision_at_3,
            "mrr": eval_tg.mrr,
            "n_requirements_indexed": eval_tg.n_requirements_indexed,
        },
    )
    # Trace gap "model" is the rule table itself; we pickle a sentinel.
    tg_dir = registry.register(
        model_obj={"kind": "rule_based_v0",
                   "module": "intelligence.predictors.trace_gap_intel"},
        record=record_tg, repo=ROOT,
    )

    summary = {
        "_draft": "DRAFT - Phase B intelligence summary (frozen models)",
        "registered": [
            {"name": "fault_escape_predictor", "version": "v0.1.0",
             "metrics": record_esc.metrics, "dir": str(esc_dir.relative_to(ROOT))},
            {"name": "engine_anomaly_detector", "version": "v0.1.0",
             "metrics": record_anom.metrics, "dir": str(anom_dir.relative_to(ROOT))},
            {"name": "trace_gap_intel", "version": "v0.1.0",
             "metrics": record_tg.metrics, "dir": str(tg_dir.relative_to(ROOT))},
        ],
    }
    out_path = ROOT / "evidence" / "intelligence-summary.json"
    out_path.write_text(json.dumps(summary, indent=2, sort_keys=True),
                        encoding="utf-8")
    print(f"\nWrote {out_path.relative_to(ROOT)}")
    for r in summary["registered"]:
        print(f"  {r['name']:<26} v{r['version']}")
        for k, v in r["metrics"].items():
            if isinstance(v, float):
                print(f"     {k}: {v:.3f}")
            elif isinstance(v, list) and len(v) <= 4:
                print(f"     {k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
