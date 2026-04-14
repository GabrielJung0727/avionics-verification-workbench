"""HTTP serving layer for Phase B frozen models.

Stdlib-only (`http.server` + `json`). Designed so the same routes map onto
MLflow Model Serving / Databricks Model Serving / Azure ML Online Endpoint
/ SageMaker Endpoint when the project moves to a real cloud.
"""
from __future__ import annotations
import json
import threading
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import numpy as np

from ..predictors.engine_anomaly import _window_features
from ..predictors.trace_gap_intel import rank_impacted_requirements
from ..registry.registry import LocalRegistry
from ..runtime.loader import (
    ApprovalGateError,
    Mode,
    load_with_approval_gate,
)


DRAFT_BANNER = (
    "DRAFT - human-in-the-loop. Frozen learned component, advisory only, "
    "served via local endpoint; never closes a control loop."
)


@dataclass
class _LoadedModels:
    escape: Any | None = None
    escape_meta: dict | None = None
    anomaly: Any | None = None
    anomaly_meta: dict | None = None
    trace_gap_meta: dict | None = None     # rule-based, no inner model needed


def _try_load(registry_root: Path, name: str, version: str
              ) -> tuple[Any | None, dict | None, str | None]:
    try:
        m, meta = load_with_approval_gate(
            registry_root, name, version, mode=Mode.SHADOW,
        )
        return m, meta, None
    except (ApprovalGateError, FileNotFoundError, KeyError) as exc:
        return None, None, f"{type(exc).__name__}: {exc}"


def _load_all(registry_root: Path) -> tuple[_LoadedModels, dict[str, str]]:
    state = _LoadedModels()
    errors: dict[str, str] = {}

    state.escape, state.escape_meta, err = _try_load(
        registry_root, "fault_escape_predictor", "v0.1.0")
    if err:
        errors["fault_escape_predictor"] = err

    state.anomaly, state.anomaly_meta, err = _try_load(
        registry_root, "engine_anomaly_detector", "v0.1.0")
    if err:
        errors["engine_anomaly_detector"] = err

    _, state.trace_gap_meta, err = _try_load(
        registry_root, "trace_gap_intel", "v0.1.0")
    if err:
        errors["trace_gap_intel"] = err

    return state, errors


class IntelligenceHandler(BaseHTTPRequestHandler):
    """Routes:
       GET  /health
       GET  /models
       POST /predict/fault_escape
       POST /predict/engine_anomaly
       POST /predict/trace_gap
    """

    # Server-side state (set by build_server)
    models: _LoadedModels = _LoadedModels()
    load_errors: dict[str, str] = {}
    requirement_ids: list[str] = []

    def log_message(self, fmt, *args):
        # Quiet — orchestrator captures stdout, server messages would be noise.
        return

    # ---- helpers ---------------------------------------------------------
    def _write_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict:
        n = int(self.headers.get("Content-Length", "0"))
        if n <= 0:
            return {}
        raw = self.rfile.read(n).decode("utf-8")
        return json.loads(raw) if raw else {}

    def _draft(self, **fields) -> dict:
        return {"_draft": DRAFT_BANNER, **fields}

    # ---- routes ----------------------------------------------------------
    def do_GET(self) -> None:
        if self.path == "/health":
            self._write_json(200, self._draft(
                status="ok",
                models_loaded=sorted({
                    "fault_escape_predictor" if self.models.escape else None,
                    "engine_anomaly_detector" if self.models.anomaly else None,
                    "trace_gap_intel" if self.models.trace_gap_meta else None,
                } - {None}),
                errors=self.load_errors,
            ))
            return
        if self.path == "/models":
            metas = []
            for meta in (self.models.escape_meta, self.models.anomaly_meta,
                         self.models.trace_gap_meta):
                if meta:
                    metas.append(meta)
            self._write_json(200, self._draft(models=metas))
            return
        self._write_json(404, self._draft(error="unknown route", path=self.path))

    def do_POST(self) -> None:
        try:
            payload = self._read_json()
        except json.JSONDecodeError as e:
            self._write_json(400, self._draft(error=f"invalid JSON: {e}"))
            return

        if self.path == "/predict/fault_escape":
            self._predict_escape(payload)
            return
        if self.path == "/predict/engine_anomaly":
            self._predict_anomaly(payload)
            return
        if self.path == "/predict/trace_gap":
            self._predict_trace_gap(payload)
            return
        self._write_json(404, self._draft(error="unknown route", path=self.path))

    # ---- predictors ------------------------------------------------------
    def _predict_escape(self, body: dict) -> None:
        if self.models.escape is None:
            self._write_json(503, self._draft(error="escape predictor unavailable"))
            return
        try:
            X = np.array([[
                float(body["delay_us"]),
                float(body["drop_every_n"]),
                float(body["n1_at_t1s"]),
                float(body["egt_at_t1s"]),
                float(body["dual_fault_us"]),
                float(body.get("seed", 1)),
            ]], dtype=float)
        except (KeyError, ValueError, TypeError) as exc:
            self._write_json(400, self._draft(error=f"bad payload: {exc}"))
            return
        p = float(self.models.escape.predict_proba(X)[0, 1])
        advice = ("run early" if p > 0.5
                  else "lower priority" if p < 0.2 else "review")
        self._write_json(200, self._draft(
            model="fault_escape_predictor",
            version=(self.models.escape_meta or {}).get("version"),
            p_escape=p,
            advice=advice,
        ))

    def _predict_anomaly(self, body: dict) -> None:
        if self.models.anomaly is None:
            self._write_json(503, self._draft(error="engine anomaly unavailable"))
            return
        try:
            if "features" in body:
                feats = np.array(body["features"], dtype=float)
                if feats.ndim == 1:
                    feats = feats.reshape(1, -1)
            elif "window" in body:
                stream = np.array(body["window"], dtype=float)
                feats = _window_features(stream, len(stream))[-1].reshape(1, -1)
            else:
                self._write_json(400, self._draft(
                    error="provide either 'features' (12-vector) or 'window' (Tx4 array)"
                ))
                return
        except (ValueError, TypeError) as exc:
            self._write_json(400, self._draft(error=f"bad payload: {exc}"))
            return
        score = float(self.models.anomaly.score_samples(feats)[0])
        pred = int(self.models.anomaly.predict(feats)[0])
        if pred == -1:
            decision = "preventive_alert"
        elif score < -0.05:
            decision = "early_warning"
        else:
            decision = "inspection_candidate" if score < 0 else "nominal"
        self._write_json(200, self._draft(
            model="engine_anomaly_detector",
            version=(self.models.anomaly_meta or {}).get("version"),
            score=score,
            decision=decision,
            advice="advisory only; never use for maintenance authority",
        ))

    def _predict_trace_gap(self, body: dict) -> None:
        if self.models.trace_gap_meta is None:
            self._write_json(503, self._draft(error="trace gap intel unavailable"))
            return
        diff_paths = body.get("diff_paths") or []
        req_ids = body.get("requirement_ids") or self.requirement_ids
        top_k = int(body.get("top_k", 10))
        if not diff_paths:
            self._write_json(400, self._draft(error="diff_paths required"))
            return
        ranked = rank_impacted_requirements(diff_paths, req_ids, top_k=top_k)
        self._write_json(200, self._draft(
            model="trace_gap_intel",
            version=(self.models.trace_gap_meta or {}).get("version"),
            ranked=ranked,
        ))


@dataclass
class IntelligenceServer:
    httpd: ThreadingHTTPServer
    thread: threading.Thread | None = None

    @property
    def port(self) -> int:
        return self.httpd.server_address[1]

    def start_in_thread(self) -> None:
        if self.thread is not None:
            return
        t = threading.Thread(target=self.httpd.serve_forever,
                             name="intelligence-server", daemon=True)
        t.start()
        self.thread = t

    def stop(self) -> None:
        self.httpd.shutdown()
        self.httpd.server_close()
        if self.thread is not None:
            self.thread.join(timeout=2)


def build_server(*, registry_root: Path, host: str = "127.0.0.1",
                 port: int = 0,
                 requirement_ids: list[str] | None = None
                 ) -> IntelligenceServer:
    """Construct the server. ``port=0`` lets the OS pick a free port — used
    by tests so they never collide on CI."""
    state, errors = _load_all(registry_root)
    handler_cls = type(
        "BoundIntelligenceHandler", (IntelligenceHandler,),
        {
            "models": state,
            "load_errors": errors,
            "requirement_ids": list(requirement_ids or []),
        },
    )
    httpd = ThreadingHTTPServer((host, port), handler_cls)
    return IntelligenceServer(httpd=httpd)
