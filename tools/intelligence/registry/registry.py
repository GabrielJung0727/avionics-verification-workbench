"""Local MLflow-style model registry.

Stores frozen models with the full metadata bundle required by Phase A's
dataset contract (dataset_hash + label_version + approval_state). The
adapter is intentionally tiny so it can be swapped for ``mlflow``,
``databricks-feature-engineering``, ``azureml-mlflow``, or SageMaker Model
Registry without changing predictor code.
"""
from __future__ import annotations
import hashlib
import json
import pickle
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DRAFT_BANNER = (
    "DRAFT - human-in-the-loop. This learned component is frozen, "
    "verification-only, and never closes a control loop."
)


def _git_sha(repo: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL, text=True,
        ).strip()
    except Exception:
        return "unknown"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class DatasetMeta:
    dataset_version: str
    dataset_hash: str
    n_train: int
    n_holdout: int
    split_strategy: str           # 'campaign-family' | 'date' | 'hw-rev'
    split_key: str
    feature_columns: list[str]
    label_column: str
    label_version: str


@dataclass
class ModelMeta:
    model_name: str
    version: str
    intended_use: str
    out_of_scope: list[str]
    training_seed: int
    frozen: bool = True
    approval_state: str = "auto-generated"   # -> reviewer-confirmed -> board-approved
    created_at: str = field(default_factory=_now_iso)
    git_sha: str = "unknown"


@dataclass
class ModelRecord:
    meta: ModelMeta
    dataset: DatasetMeta
    metrics: dict[str, Any]
    card_extra: dict[str, Any] = field(default_factory=dict)
    artifact_path: Path | None = None    # set after registration


def dataset_hash_for(matrix_bytes: bytes) -> str:
    return hashlib.sha256(matrix_bytes).hexdigest()


@dataclass
class LocalRegistry:
    root: Path

    def _model_dir(self, name: str, version: str) -> Path:
        return self.root / name / version

    def register(self, *, model_obj: Any, record: ModelRecord,
                 repo: Path | None = None) -> Path:
        """Write the artifact + every metadata file. Returns the version dir."""
        d = self._model_dir(record.meta.model_name, record.meta.version)
        d.mkdir(parents=True, exist_ok=True)

        if repo is not None:
            record.meta.git_sha = _git_sha(repo)

        artifact = d / "model.pkl"
        with artifact.open("wb") as fh:
            pickle.dump(model_obj, fh)
        record.artifact_path = artifact

        (d / "meta.json").write_text(
            json.dumps({**asdict(record.meta), "_draft_banner": DRAFT_BANNER},
                       indent=2, sort_keys=True),
            encoding="utf-8",
        )
        (d / "dataset.json").write_text(
            json.dumps(asdict(record.dataset), indent=2, sort_keys=True),
            encoding="utf-8",
        )
        (d / "metrics.json").write_text(
            json.dumps({**record.metrics, "_draft": True},
                       indent=2, sort_keys=True),
            encoding="utf-8",
        )
        (d / "model_card.json").write_text(
            json.dumps({
                "name": record.meta.model_name,
                "version": record.meta.version,
                "intended_use": record.meta.intended_use,
                "out_of_scope": record.meta.out_of_scope,
                "training_seed": record.meta.training_seed,
                "approval_state": record.meta.approval_state,
                "_draft_banner": DRAFT_BANNER,
                **record.card_extra,
            }, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        (d / "assurance_stub.md").write_text(
            self._assurance_stub_template(record),
            encoding="utf-8",
        )

        # update top-level manifest
        manifest = self.root / "manifest.json"
        idx: dict = {}
        if manifest.exists():
            try:
                idx = json.loads(manifest.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                pass
        models = idx.setdefault("models", {})
        versions = models.setdefault(record.meta.model_name, [])
        if record.meta.version not in versions:
            versions.append(record.meta.version)
        idx["last_registered_at"] = _now_iso()
        manifest.write_text(json.dumps(idx, indent=2, sort_keys=True),
                            encoding="utf-8")
        return d

    @staticmethod
    def _assurance_stub_template(rec: ModelRecord) -> str:
        return (
            f"# Assurance stub: {rec.meta.model_name} {rec.meta.version}\n\n"
            f"> {DRAFT_BANNER}\n\n"
            f"## Intended use\n{rec.meta.intended_use}\n\n"
            f"## Out of scope\n"
            + "\n".join(f"- {o}" for o in rec.meta.out_of_scope)
            + "\n\n"
            f"## Training data pedigree\n"
            f"- dataset_version: `{rec.dataset.dataset_version}`\n"
            f"- dataset_hash:    `{rec.dataset.dataset_hash[:16]}...`\n"
            f"- label_version:   `{rec.dataset.label_version}`\n"
            f"- split_strategy:  `{rec.dataset.split_strategy}` "
            f"(NOT random)\n"
            f"- n_train / n_holdout: {rec.dataset.n_train} / {rec.dataset.n_holdout}\n\n"
            f"## Failure modes (TODO Phase C)\n"
            f"- See assurance case in Phase C; this stub seeds the discussion.\n\n"
            f"## Fallback behavior\n"
            f"- The deterministic verification pipeline runs whether this model "
            f"is present or not; predictions are advisory only.\n\n"
            f"## Human override path\n"
            f"- Every prediction surfaces with the DRAFT banner; a reviewer "
            f"must promote `approval_state` from `auto-generated` to "
            f"`reviewer-confirmed` before any downstream tool acts on it.\n"
        )

    def load(self, name: str, version: str) -> tuple[Any, ModelRecord]:
        d = self._model_dir(name, version)
        with (d / "model.pkl").open("rb") as fh:
            obj = pickle.load(fh)
        meta = ModelMeta(**{
            k: v for k, v in
            json.loads((d / "meta.json").read_text(encoding="utf-8")).items()
            if k != "_draft_banner"
        })
        ds = DatasetMeta(**json.loads((d / "dataset.json").read_text(encoding="utf-8")))
        metrics = json.loads((d / "metrics.json").read_text(encoding="utf-8"))
        metrics.pop("_draft", None)
        rec = ModelRecord(meta=meta, dataset=ds, metrics=metrics)
        rec.artifact_path = d / "model.pkl"
        return obj, rec

    def list_models(self) -> dict[str, list[str]]:
        manifest = self.root / "manifest.json"
        if not manifest.exists():
            return {}
        return json.loads(manifest.read_text(encoding="utf-8")).get("models", {})
