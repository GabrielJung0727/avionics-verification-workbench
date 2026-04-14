"""Fault Escape Predictor (v0).

sklearn GradientBoostingClassifier wrapped with the Phase A dataset contract.
Trains on the synthetic fault sweep, splits by ``campaign_family`` (NOT
random), and registers the model with full metadata.

The predictor is *advisory*: it ranks fault campaigns by P(escape) so the
verification team knows which combinations to run first. It never decides
whether a campaign passes or fails.
"""
from __future__ import annotations
from dataclasses import dataclass, field

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import (
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from ..data.fault_sweep import FaultSweepRecord


FEATURE_COLUMNS = [
    "delay_us", "drop_every_n", "n1_at_t1s",
    "egt_at_t1s", "dual_fault_us", "seed",
]
LABEL_COLUMN = "label_escape"


def _to_matrix(records: list[FaultSweepRecord]) -> tuple[np.ndarray, np.ndarray]:
    X = np.array([
        [r.delay_us, r.drop_every_n, r.n1_at_t1s,
         r.egt_at_t1s, r.dual_fault_us, r.seed] for r in records
    ], dtype=float)
    y = np.array([r.label_escape for r in records], dtype=int)
    return X, y


@dataclass
class EscapeEvaluation:
    auc: float
    precision: float
    recall: float
    f1: float
    confusion_matrix: list[list[int]]
    n_train: int
    n_holdout: int
    holdout_keys: list[str] = field(default_factory=list)


def train_escape_predictor(train_records: list[FaultSweepRecord],
                           holdout_records: list[FaultSweepRecord],
                           seed: int = 42
                           ) -> tuple[GradientBoostingClassifier,
                                      EscapeEvaluation,
                                      np.ndarray]:
    X_train, y_train = _to_matrix(train_records)
    X_test, y_test = _to_matrix(holdout_records)

    model = GradientBoostingClassifier(
        n_estimators=80, max_depth=3, learning_rate=0.1, random_state=seed,
    )
    model.fit(X_train, y_train)

    if len(set(y_test)) > 1:
        proba = model.predict_proba(X_test)[:, 1]
        auc = float(roc_auc_score(y_test, proba))
    else:
        auc = float("nan")
    pred = model.predict(X_test)
    cm = confusion_matrix(y_test, pred, labels=[0, 1]).tolist()
    eval_ = EscapeEvaluation(
        auc=auc,
        precision=float(precision_score(y_test, pred, zero_division=0)),
        recall=float(recall_score(y_test, pred, zero_division=0)),
        f1=float(f1_score(y_test, pred, zero_division=0)),
        confusion_matrix=cm,
        n_train=len(train_records),
        n_holdout=len(holdout_records),
        holdout_keys=sorted({r.campaign_family for r in holdout_records}),
    )
    return model, eval_, X_train


def score_escape(model: GradientBoostingClassifier,
                 record: FaultSweepRecord) -> dict:
    X = np.array([[record.delay_us, record.drop_every_n, record.n1_at_t1s,
                   record.egt_at_t1s, record.dual_fault_us, record.seed]],
                 dtype=float)
    p = float(model.predict_proba(X)[0, 1])
    return {
        "_draft": "DRAFT - human-in-the-loop escape probability",
        "p_escape": p,
        "advice": ("run early" if p > 0.5
                   else "lower priority" if p < 0.2 else "review"),
    }
