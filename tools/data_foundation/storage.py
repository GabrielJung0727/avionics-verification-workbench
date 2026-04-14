"""Filesystem layout for the local lakehouse.

Designed to mirror the cloud object-store layout one-for-one so that
swapping in S3/ADLS/GCS later means changing only the path resolver.
"""
from __future__ import annotations
import hashlib
from dataclasses import dataclass
from pathlib import Path


@dataclass
class LakehouseLayout:
    root: Path

    @property
    def bronze(self) -> Path:
        return self.root / "bronze" / "runs"

    @property
    def silver_db(self) -> Path:
        return self.root / "silver" / "catalog.sqlite"

    @property
    def gold_dir(self) -> Path:
        return self.root / "gold"

    @property
    def drift_dir(self) -> Path:
        return self.root / "drift"

    @property
    def manifest(self) -> Path:
        return self.root / "manifest.json"

    def ensure(self) -> None:
        for p in (self.bronze, self.silver_db.parent, self.gold_dir, self.drift_dir):
            p.mkdir(parents=True, exist_ok=True)


def sha256_of_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def content_address(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()
