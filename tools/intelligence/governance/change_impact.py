"""Change-impact reset detector.

Walks every model in `evidence/registry/` and compares the current
`dataset.dataset_hash` and `meta.git_sha` to the values stored in the
audit log when the model last left `auto-generated`. A mismatch means
the case is now stale and the orchestrator should demote the state.

The reset itself is performed by `governance.approval.demote_state`; this
module only DETECTS what should be reset.
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class StateInvalidation:
    model_name: str
    version: str
    current_state: str
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "model_name": self.model_name,
            "version": self.version,
            "current_state": self.current_state,
            "reasons": list(self.reasons),
        }


def _read_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def _last_promotion_to(audit: list[dict], state: str) -> dict | None:
    for entry in reversed(audit):
        if entry.get("to_state") == state:
            return entry
    return None


def detect_state_invalidations(registry_root: Path) -> list[StateInvalidation]:
    out: list[StateInvalidation] = []
    if not registry_root.exists():
        return out
    for model_dir in sorted(registry_root.iterdir()):
        if not model_dir.is_dir() or model_dir.name.startswith("."):
            continue
        for version_dir in sorted(model_dir.iterdir()):
            if not version_dir.is_dir():
                continue
            meta = _read_json(version_dir / "meta.json")
            ds = _read_json(version_dir / "dataset.json")
            audit = _read_json(version_dir / "approval_log.json") or []
            if not isinstance(audit, list):
                audit = []
            current_state = meta.get("approval_state", "auto-generated")
            if current_state == "auto-generated":
                continue   # nothing to invalidate

            inv = StateInvalidation(
                model_name=model_dir.name, version=version_dir.name,
                current_state=current_state,
            )
            last = _last_promotion_to(audit, "reviewer-confirmed") \
                or _last_promotion_to(audit, "board-approved")
            if not last:
                inv.reasons.append("no audit record for current state")
                out.append(inv)
                continue
            promoted_meta = last.get("meta_snapshot", {})
            promoted_ds = last.get("dataset_snapshot", {})
            if promoted_meta and promoted_meta.get("git_sha") != meta.get("git_sha"):
                inv.reasons.append(
                    f"git_sha changed: {promoted_meta.get('git_sha')} -> "
                    f"{meta.get('git_sha')}"
                )
            if promoted_ds and promoted_ds.get("dataset_hash") != ds.get("dataset_hash"):
                inv.reasons.append(
                    f"dataset_hash changed: "
                    f"{promoted_ds.get('dataset_hash')[:12]}... -> "
                    f"{ds.get('dataset_hash')[:12]}..."
                )
            if inv.reasons:
                out.append(inv)
    return out
