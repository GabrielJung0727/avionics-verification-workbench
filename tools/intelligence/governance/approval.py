"""Approval state machine for registered models.

State graph (also documented in `docs/PhaseC/human-flow/reviewer-flow.md`):

    auto-generated  --promote-->  reviewer-confirmed
    reviewer-confirmed  --promote-->  board-approved
    any --reset-->  auto-generated

Promotion rules (enforced here):
  - reviewer must differ from author (recorded `git_sha` author for now)
  - assurance lint must pass
  - state can never skip a level
"""
from __future__ import annotations
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

from .assurance_lint import LintReport, lint_case


class ApprovalState(str, Enum):
    AUTO = "auto-generated"
    REVIEWER = "reviewer-confirmed"
    BOARD = "board-approved"


_ORDER = [ApprovalState.AUTO, ApprovalState.REVIEWER, ApprovalState.BOARD]


class PromotionError(RuntimeError):
    pass


@dataclass
class PromotionRecord:
    model_name: str
    version: str
    from_state: str
    to_state: str
    reviewer: str
    timestamp: str
    rationale: str


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _meta_path(registry_root: Path, model_name: str, version: str) -> Path:
    return registry_root / model_name / version / "meta.json"


def _audit_path(registry_root: Path, model_name: str, version: str) -> Path:
    return registry_root / model_name / version / "approval_log.json"


def _read_meta(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def _write_meta(p: Path, meta: dict) -> None:
    p.write_text(json.dumps(meta, indent=2, sort_keys=True), encoding="utf-8")


def _append_audit(p: Path, record: PromotionRecord) -> None:
    log: list[dict] = []
    if p.exists():
        try:
            log = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            log = []
    log.append({
        "from_state": record.from_state,
        "to_state": record.to_state,
        "reviewer": record.reviewer,
        "timestamp": record.timestamp,
        "rationale": record.rationale,
    })
    p.write_text(json.dumps(log, indent=2, sort_keys=True), encoding="utf-8")


def promote_state(registry_root: Path, model_name: str, version: str,
                  *, reviewer: str, author: str | None,
                  rationale: str,
                  assurance_case_path: Path | None = None,
                  ) -> PromotionRecord:
    """Promote a model up exactly one level. Raises PromotionError if a
    rule is violated.

    `assurance_case_path` is required for the AUTO -> REVIEWER step.
    """
    meta = _read_meta(_meta_path(registry_root, model_name, version))
    current = ApprovalState(meta.get("approval_state", ApprovalState.AUTO.value))
    idx = _ORDER.index(current)
    if idx >= len(_ORDER) - 1:
        raise PromotionError(f"already at top state: {current.value}")
    target = _ORDER[idx + 1]

    if author is not None and reviewer == author:
        raise PromotionError("reviewer must differ from author")

    if current == ApprovalState.AUTO:
        if assurance_case_path is None or not Path(assurance_case_path).exists():
            raise PromotionError("assurance_case_path is required for "
                                 "AUTO -> REVIEWER promotion")
        rep = lint_case(Path(assurance_case_path))
        if not rep.ok:
            raise PromotionError(
                f"assurance lint failed: missing_sections={rep.missing_sections} "
                f"missing_identity={rep.missing_identity}"
            )

    meta["approval_state"] = target.value
    _write_meta(_meta_path(registry_root, model_name, version), meta)

    record = PromotionRecord(
        model_name=model_name, version=version,
        from_state=current.value, to_state=target.value,
        reviewer=reviewer, timestamp=_now_iso(), rationale=rationale,
    )
    _append_audit(_audit_path(registry_root, model_name, version), record)
    return record


def demote_state(registry_root: Path, model_name: str, version: str,
                 *, reviewer: str, rationale: str) -> PromotionRecord:
    """Force the model back to auto-generated (e.g. on change_impact reset)."""
    meta = _read_meta(_meta_path(registry_root, model_name, version))
    current = ApprovalState(meta.get("approval_state", ApprovalState.AUTO.value))
    if current == ApprovalState.AUTO:
        raise PromotionError("already at auto-generated")
    meta["approval_state"] = ApprovalState.AUTO.value
    _write_meta(_meta_path(registry_root, model_name, version), meta)
    record = PromotionRecord(
        model_name=model_name, version=version,
        from_state=current.value, to_state=ApprovalState.AUTO.value,
        reviewer=reviewer, timestamp=_now_iso(), rationale=rationale,
    )
    _append_audit(_audit_path(registry_root, model_name, version), record)
    return record
