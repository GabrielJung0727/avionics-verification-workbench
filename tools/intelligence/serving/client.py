"""Thin HTTP client for the local intelligence endpoint.

Same surface shape that an MLflow / Databricks / Azure ML / SageMaker
endpoint client would expose, so swapping the backend is a one-line
adapter change.
"""
from __future__ import annotations
import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass


DEFAULT_ENDPOINT = "http://127.0.0.1:8081"


class IntelligenceClientError(RuntimeError):
    pass


@dataclass
class IntelligenceClient:
    endpoint: str = DEFAULT_ENDPOINT
    timeout_s: float = 5.0

    @classmethod
    def from_env(cls) -> "IntelligenceClient | None":
        url = os.environ.get("INTELLIGENCE_ENDPOINT")
        if not url:
            return None
        return cls(endpoint=url.rstrip("/"))

    # ---- low-level ------------------------------------------------------
    def _get(self, path: str) -> dict:
        try:
            with urllib.request.urlopen(
                self.endpoint + path, timeout=self.timeout_s,
            ) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.URLError as e:
            raise IntelligenceClientError(f"GET {path} failed: {e}") from e

    def _post(self, path: str, body: dict) -> dict:
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            self.endpoint + path, data=data, method="POST",
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", errors="replace")
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                raise IntelligenceClientError(
                    f"POST {path} -> HTTP {e.code}: {raw}") from e
        except urllib.error.URLError as e:
            raise IntelligenceClientError(f"POST {path} failed: {e}") from e

    # ---- routes ---------------------------------------------------------
    def health(self) -> dict:
        return self._get("/health")

    def models(self) -> dict:
        return self._get("/models")

    def predict_escape(self, *, delay_us: float, drop_every_n: float,
                       n1_at_t1s: float, egt_at_t1s: float,
                       dual_fault_us: float, seed: float = 1) -> dict:
        return self._post("/predict/fault_escape", {
            "delay_us": delay_us, "drop_every_n": drop_every_n,
            "n1_at_t1s": n1_at_t1s, "egt_at_t1s": egt_at_t1s,
            "dual_fault_us": dual_fault_us, "seed": seed,
        })

    def predict_engine_anomaly(self, *, features=None, window=None) -> dict:
        body: dict = {}
        if features is not None:
            body["features"] = list(features)
        if window is not None:
            body["window"] = [list(row) for row in window]
        return self._post("/predict/engine_anomaly", body)

    def predict_trace_gap(self, *, diff_paths: list[str],
                          requirement_ids: list[str] | None = None,
                          top_k: int = 10) -> dict:
        body: dict = {"diff_paths": list(diff_paths), "top_k": int(top_k)}
        if requirement_ids:
            body["requirement_ids"] = list(requirement_ids)
        return self._post("/predict/trace_gap", body)
