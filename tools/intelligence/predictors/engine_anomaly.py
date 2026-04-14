"""Engine telemetry anomaly detector (v0).

IsolationForest over rolling-window features extracted from EngineRaw
streams. Output is **preventive alert / early warning / inspection
candidate** — never a maintenance decision (matches GE Aerospace /
Honeywell Forge / Collins positioning).

Window features: mean and stddev of N1, N2, EGT, FF over a fixed window plus
their first differences.
"""
from __future__ import annotations
from dataclasses import dataclass

import numpy as np
from sklearn.ensemble import IsolationForest

WINDOW_FEATURES = [
    "n1_mean", "n1_std", "n1_d_mean",
    "n2_mean", "n2_std", "n2_d_mean",
    "egt_mean", "egt_std", "egt_d_mean",
    "ff_mean",  "ff_std",  "ff_d_mean",
]


def _window_features(stream: np.ndarray, window: int) -> np.ndarray:
    """stream: shape (T, 4) for (n1, n2, egt, ff). Returns (W, 12) features."""
    diffs = np.diff(stream, axis=0, prepend=stream[:1])
    rows = []
    for end in range(window, len(stream) + 1):
        seg = stream[end - window:end]
        dseg = diffs[end - window:end]
        feats = []
        for i in range(4):
            feats.append(seg[:, i].mean())
            feats.append(seg[:, i].std())
            feats.append(dseg[:, i].mean())
        rows.append(feats)
    return np.array(rows, dtype=float)


@dataclass
class EngineAnomalyEvaluation:
    n_train_windows: int
    n_holdout_windows: int
    detection_rate: float          # fraction of injected anomaly windows scored < 0
    false_alarm_rate: float        # fraction of clean windows scored < 0
    contamination: float
    window: int


def train_engine_anomaly(clean_stream: np.ndarray,
                         anomalous_stream: np.ndarray,
                         *, window: int = 8,
                         contamination: float = 0.05,
                         seed: int = 42
                         ) -> tuple[IsolationForest,
                                    EngineAnomalyEvaluation,
                                    np.ndarray]:
    """clean_stream and anomalous_stream are (T, 4). The model trains on
    clean_stream only; anomalous_stream is the holdout used to estimate
    detection_rate."""
    X_train = _window_features(clean_stream, window)
    X_anom = _window_features(anomalous_stream, window)

    model = IsolationForest(
        n_estimators=100, contamination=contamination, random_state=seed,
    )
    model.fit(X_train)

    train_pred = model.predict(X_train)         # +1 normal, -1 anomaly
    anom_pred = model.predict(X_anom)
    eval_ = EngineAnomalyEvaluation(
        n_train_windows=int(X_train.shape[0]),
        n_holdout_windows=int(X_anom.shape[0]),
        detection_rate=float((anom_pred == -1).mean()),
        false_alarm_rate=float((train_pred == -1).mean()),
        contamination=float(contamination),
        window=int(window),
    )
    return model, eval_, X_train


def score_engine_window(model: IsolationForest,
                        window_features: np.ndarray) -> dict:
    """window_features shape: (1, 12) or (12,)."""
    x = np.atleast_2d(window_features)
    score = float(model.score_samples(x)[0])
    pred = int(model.predict(x)[0])      # +1 normal, -1 anomaly
    if pred == -1:
        kind = "preventive_alert"
    elif score < -0.05:
        kind = "early_warning"
    else:
        kind = "inspection_candidate" if score < 0 else "nominal"
    return {
        "_draft": "DRAFT - human-in-the-loop engine anomaly score",
        "score": score,
        "decision": kind,
        "advice": "advisory only; never use for maintenance authority",
    }
