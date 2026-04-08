"""M6 evidence bundle exporter + verifier.

Produces a self-contained ``bundle-<run_id>-<sha_short>.zip`` containing:

    manifest.json
    inputs/          scenario + partition + campaign configs
    env/             git_sha, tool_versions, build_info
    results/         bus_recording.bin, hm_log.csv, test_results.json,
                     mcdc_report.json, escape_report.json
    trace/           req_to_test.json, gap_report.json

``build_bundle(payload, out_dir)`` takes the dict produced by
``run_verification.py`` plus the root of the repo, materializes the files,
writes a manifest with per-file sha256, and zips the whole thing.

``verify_bundle(zip_path)`` re-opens the bundle, recomputes hashes, and
returns a list of mismatches (empty on success). This is the foundation of
the "replay from archive" guarantee (SYS-024).
"""
from __future__ import annotations
import hashlib
import json
import shutil
import subprocess
import sys
import uuid
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


SCHEMA_VERSION = "1.0"


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _sha256_of_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def manifest_for_files(bundle_root: Path) -> list[dict]:
    """Return sorted [{path, sha256, size}] for every file under ``bundle_root``,
    excluding the manifest itself (which is written last)."""
    files: list[dict] = []
    for p in sorted(bundle_root.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(bundle_root).as_posix()
        if rel == "manifest.json":
            continue
        files.append({
            "path": rel,
            "sha256": sha256_of_file(p),
            "size": p.stat().st_size,
        })
    return files


def _git_sha(repo: Path) -> tuple[str, bool]:
    try:
        sha = subprocess.check_output(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL, text=True,
        ).strip()
        dirty = bool(subprocess.check_output(
            ["git", "-C", str(repo), "status", "--porcelain"],
            stderr=subprocess.DEVNULL, text=True,
        ).strip())
        return sha, dirty
    except Exception:
        return "unknown", False


def _tool_versions() -> dict:
    return {
        "python": sys.version.split()[0],
        "platform": sys.platform,
    }


@dataclass
class _Files:
    inputs: dict[str, bytes]   # rel path -> bytes
    results: dict[str, bytes]
    trace: dict[str, bytes]
    env: dict[str, bytes]


def _collect_files(payload: dict, repo: Path) -> _Files:
    """Materialize all payload content into in-memory bytes so the bundle is
    hermetic. Small files only, so in-memory is fine."""
    def j(obj) -> bytes:
        return json.dumps(obj, indent=2, sort_keys=True, default=str).encode("utf-8")

    inputs: dict[str, bytes] = {}
    # include partition table, test cases, campaign configs
    pt = repo / "config" / "partitions" / "default.txt"
    if pt.exists():
        inputs["partition_table.txt"] = pt.read_bytes()
    for p in sorted((repo / "tools" / "runner" / "test_cases").glob("*.json")):
        inputs[f"test_cases/{p.name}"] = p.read_bytes()
    for p in sorted((repo / "tools" / "fault_injector" / "campaigns").glob("*.json")):
        inputs[f"campaigns/{p.name}"] = p.read_bytes()

    results: dict[str, bytes] = {
        "test_results.json": j(payload.get("results", [])),
        "campaigns.json": j(payload.get("campaigns", [])),
        "mcdc_report.json": j(payload.get("mcdc", {})),
        "coverage.json": j(payload.get("coverage", {})),
        "hf_findings.json": j(payload.get("hf_findings", [])),
        "mode_confusion.json": j(payload.get("mode_confusion", [])),
        "hil_runs.json": j(payload.get("hil_runs", [])),
    }

    trace: dict[str, bytes] = {
        "req_to_test.json": j(payload.get("trace", {})),
        "gap_report.json": j(payload.get("gap", {})),
    }

    git_sha, dirty = _git_sha(repo)
    env: dict[str, bytes] = {
        "git_sha.txt": f"{git_sha}{' (dirty)' if dirty else ''}\n".encode("utf-8"),
        "tool_versions.json": j(_tool_versions()),
    }
    return _Files(inputs=inputs, results=results, trace=trace, env=env)


def build_bundle(payload: dict, repo: Path, out_dir: Path) -> Path:
    """Write ``bundle-<run_id_short>-<sha_short>.zip`` under ``out_dir`` and
    return its path."""
    out_dir.mkdir(parents=True, exist_ok=True)
    run_id = str(uuid.uuid4())
    run_id_short = run_id.split("-", 1)[0]
    git_sha, dirty = _git_sha(repo)
    sha_short = git_sha[:8] if git_sha != "unknown" else "nogit"

    files = _collect_files(payload, repo)
    summary = payload.get("summary", {})

    # Stage to a scratch dir so sha256 is stable and deterministic
    scratch = out_dir / f".stage-{run_id_short}"
    if scratch.exists():
        shutil.rmtree(scratch)
    scratch.mkdir(parents=True)

    def write_group(group: dict[str, bytes], sub: str) -> None:
        for rel, data in group.items():
            dest = scratch / sub / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)

    write_group(files.inputs, "inputs")
    write_group(files.results, "results")
    write_group(files.trace, "trace")
    write_group(files.env, "env")

    file_entries = manifest_for_files(scratch)

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "workbench_version": "0.6.0",
        "build": {
            "git_sha": git_sha,
            "git_dirty": dirty,
            "tool_versions": _tool_versions(),
        },
        "summary": summary,
        "files": file_entries,
        "dal_assumptions": [
            {"module": "fcc_cmd_lane", "dal": "B"},
            {"module": "fcc_mon_lane", "dal": "B"},
            {"module": "health_monitor", "dal": "B"},
            {"module": "engine_interface", "dal": "C"},
            {"module": "display_computer", "dal": "C"},
            {"module": "data_concentrator", "dal": "C"},
        ],
        "disclaimer": (
            "Learning-grade workbench. DAL ratings are assumptions and not "
            "certified. Bundle replays are byte-level integrity checks, not "
            "an equivalent of a DER-approved verification record."
        ),
    }
    (scratch / "manifest.json").write_bytes(
        json.dumps(manifest, indent=2, sort_keys=True).encode("utf-8")
    )

    # Zip it. Deterministic date so re-builds produce matching archives.
    zip_path = out_dir / f"bundle-{run_id_short}-{sha_short}.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(scratch.rglob("*")):
            if p.is_file():
                zi = zipfile.ZipInfo(p.relative_to(scratch).as_posix())
                zi.date_time = (2026, 1, 1, 0, 0, 0)
                zi.compress_type = zipfile.ZIP_DEFLATED
                zf.writestr(zi, p.read_bytes())

    shutil.rmtree(scratch, ignore_errors=True)
    return zip_path


def verify_bundle(zip_path: Path) -> dict:
    """Open a bundle, recompute every file's sha256, and compare against the
    manifest. Returns {'ok': bool, 'mismatches': [...], 'manifest': {...}}."""
    with zipfile.ZipFile(zip_path, "r") as zf:
        manifest_bytes = zf.read("manifest.json")
        manifest = json.loads(manifest_bytes)
        mismatches: list[str] = []
        for entry in manifest["files"]:
            try:
                data = zf.read(entry["path"])
            except KeyError:
                mismatches.append(f"missing: {entry['path']}")
                continue
            actual = _sha256_of_bytes(data)
            if actual != entry["sha256"]:
                mismatches.append(
                    f"hash mismatch: {entry['path']} "
                    f"expected={entry['sha256'][:12]}.. got={actual[:12]}.."
                )
            if len(data) != entry["size"]:
                mismatches.append(
                    f"size mismatch: {entry['path']} "
                    f"expected={entry['size']} got={len(data)}"
                )
    return {
        "ok": not mismatches,
        "mismatches": mismatches,
        "manifest": manifest,
    }
