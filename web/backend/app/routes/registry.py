"""Read-only routes over evidence/registry/."""
from __future__ import annotations
import json
from fastapi import APIRouter, HTTPException, status

from ..config import DRAFT_BANNER, REGISTRY_DIR

router = APIRouter(prefix="/api/registry", tags=["registry"])


def _draft(payload: dict) -> dict:
    return {"_draft": DRAFT_BANNER, **payload}


@router.get("/models")
def list_models():
    """List every registered (model, version) with assurance metadata."""
    if not REGISTRY_DIR.exists():
        return _draft({"models": []})
    out = []
    for model_dir in sorted(p for p in REGISTRY_DIR.iterdir() if p.is_dir()):
        if model_dir.name.startswith("."):
            continue
        for ver_dir in sorted(p for p in model_dir.iterdir() if p.is_dir()):
            meta_p = ver_dir / "meta.json"
            ds_p = ver_dir / "dataset.json"
            metrics_p = ver_dir / "metrics.json"
            if not meta_p.exists():
                continue
            meta = json.loads(meta_p.read_text(encoding="utf-8"))
            entry = {
                "model_name": model_dir.name,
                "version": ver_dir.name,
                "approval_state": meta.get("approval_state"),
                "frozen": meta.get("frozen"),
                "intended_use": meta.get("intended_use"),
                "out_of_scope": meta.get("out_of_scope", []),
                "git_sha": meta.get("git_sha"),
                "training_seed": meta.get("training_seed"),
            }
            if ds_p.exists():
                ds = json.loads(ds_p.read_text(encoding="utf-8"))
                entry["dataset"] = {
                    "version": ds.get("dataset_version"),
                    "hash_short": (ds.get("dataset_hash") or "")[:16],
                    "split_strategy": ds.get("split_strategy"),
                    "split_key": ds.get("split_key"),
                    "n_train": ds.get("n_train"),
                    "n_holdout": ds.get("n_holdout"),
                    "label_version": ds.get("label_version"),
                }
            if metrics_p.exists():
                metrics = json.loads(metrics_p.read_text(encoding="utf-8"))
                metrics.pop("_draft", None)
                entry["metrics"] = metrics
            out.append(entry)
    return _draft({"models": out})


@router.get("/models/{name}/{version}")
def get_model(name: str, version: str):
    d = REGISTRY_DIR / name / version
    if not d.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"unknown model: {name}/{version}",
        )
    payload: dict = {}
    for fn in ("meta.json", "dataset.json", "metrics.json", "model_card.json"):
        p = d / fn
        if p.exists():
            payload[fn.replace(".json", "")] = json.loads(
                p.read_text(encoding="utf-8")
            )
    stub = d / "assurance_stub.md"
    if stub.exists():
        payload["assurance_stub_md"] = stub.read_text(encoding="utf-8")
    return _draft(payload)
