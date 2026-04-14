"""Turn a verification-report.json (and optionally the matching bundle zip)
into Bronze + Silver rows under ``evidence/lakehouse/``.
"""
from __future__ import annotations
import json
import sqlite3
import uuid
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .bus_parser import parse_bus_recording
from .catalog import Catalog
from .storage import LakehouseLayout, content_address


@dataclass
class IngestSummary:
    run_id: str
    bronze_path: Path
    rows_per_table: dict[str, int]
    bundle_used: Path | None


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _insert_run_manifest(conn: sqlite3.Connection, run_id: str,
                         payload: dict, bronze_path: Path,
                         bronze_sha256: str) -> None:
    build = payload.get("summary_build", {}) or {}
    # build info isn't always in the report (it lives in the bundle manifest).
    seed_guess = None
    for r in payload.get("results", []):
        seed_guess = seed_guess or r.get("recorder_sha256")
    conn.execute(
        """
        INSERT OR REPLACE INTO run_manifest(
            run_id, ingested_at, git_sha, git_dirty, workbench_version,
            seed, bench_id, operator, env_profile, sensor_bus_config,
            time_sync_state, bronze_path, bronze_sha256
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            run_id,
            _now_iso(),
            build.get("git_sha"),
            int(bool(build.get("git_dirty", False))),
            payload.get("workbench_version", ""),
            None,
            "sim-localhost",
            "ci",
            "local-python",
            "config/partitions/default.txt",
            "sim_clock",
            str(bronze_path),
            bronze_sha256,
        ),
    )


def _insert_outcomes(conn, run_id, payload) -> int:
    rows = []
    for r in payload.get("results", []):
        for req in r.get("req", []) or [None]:
            rows.append((
                run_id,
                r.get("id"),
                req,
                r.get("result", "ERROR"),
                None,
                None,
                None,
                0,
                json.dumps(r.get("failures", []), ensure_ascii=False),
            ))
    if rows:
        conn.executemany(
            """INSERT INTO verification_outcome(
                 run_id, tc_id, req_id, result, dal_context,
                 evidence_pointer, coverage_pointer, waiver, failures
               ) VALUES (?,?,?,?,?,?,?,?,?)""",
            rows,
        )
    return len(rows)


def _insert_campaigns(conn, run_id, payload) -> int:
    rows = []
    for c in payload.get("campaigns", []):
        rows.append((
            run_id,
            c.get("id"),
            c.get("classification", "unknown"),
            c.get("fcc_mode_terminal"),
            int(c.get("hm_event_total", 0) or 0),
            1 if c.get("pass") else 0,
            json.dumps(c.get("hm_event_counts", {}), ensure_ascii=False),
            None,
            None,
            c.get("recorder_sha256"),
        ))
    if rows:
        conn.executemany(
            """INSERT INTO fault_injection_case(
                 run_id, campaign_id, classification, fcc_mode_terminal,
                 hm_event_total, expected_pass, parameters_json,
                 detection_latency_us, mitigation_latency_us, recorder_sha256
               ) VALUES (?,?,?,?,?,?,?,?,?,?)""",
            rows,
        )
    return len(rows)


def _insert_mcdc(conn, run_id, payload) -> int:
    rows = []
    for name, info in (payload.get("mcdc") or {}).items():
        rows.append((
            run_id, name,
            int(info.get("conditions", 0)),
            int(info.get("covered_conditions", 0)),
            float(info.get("pct", 0.0)),
            int(info.get("samples", 0)),
            int(info.get("unique_rows", 0)),
        ))
    if rows:
        conn.executemany(
            """INSERT INTO mcdc_sample(
                 run_id, decision, conditions, covered_conditions,
                 pct, samples, unique_rows
               ) VALUES (?,?,?,?,?,?,?)""",
            rows,
        )
    return len(rows)


def _insert_hil(conn, run_id, payload) -> int:
    rows = []
    for r in payload.get("hil_runs", []):
        rows.append((
            run_id,
            r.get("name", "?"),
            int(r.get("cycles", 0)),
            float(r.get("latency_mean_us", 0.0)),
            int(r.get("latency_max_us", 0)),
            float(r.get("jitter_stddev_us", 0.0)),
            int(r.get("drops", 0)),
            int(r.get("reboots", 0)),
        ))
    if rows:
        conn.executemany(
            """INSERT INTO hil_measurement(
                 run_id, config_name, cycles, latency_mean_us,
                 latency_max_us, jitter_stddev_us, drops, reboots
               ) VALUES (?,?,?,?,?,?,?,?)""",
            rows,
        )
    return len(rows)


def _insert_hf(conn, run_id, payload) -> int:
    rows = []
    for f in payload.get("hf_findings", []):
        rows.append((
            run_id,
            f.get("hf_id"),
            f.get("title"),
            1 if f.get("passed") else 0,
            f.get("detail"),
            f.get("ac_ref"),
        ))
    if rows:
        conn.executemany(
            """INSERT INTO hf_finding(
                 run_id, hf_id, title, passed, detail, ac_ref
               ) VALUES (?,?,?,?,?,?)""",
            rows,
        )
    return len(rows)


def _ingest_bundle_artifacts(conn, run_id, bundle_path: Path) -> tuple[int, int]:
    """Return (artifact_rows, telemetry_rows)."""
    artifact_rows = 0
    telemetry_rows = 0
    with zipfile.ZipFile(bundle_path, "r") as zf:
        manifest = json.loads(zf.read("manifest.json"))
        for entry in manifest.get("files", []):
            conn.execute(
                """INSERT INTO artifact_index(run_id, kind, uri, sha256, size_bytes)
                   VALUES (?,?,?,?,?)""",
                (run_id, entry["path"].split("/")[0], entry["path"],
                 entry["sha256"], entry["size"]),
            )
            artifact_rows += 1
        # parse bus_recording.bin if present
        for name in zf.namelist():
            if name.endswith("bus_recording.bin"):
                rows = []
                for ev in parse_bus_recording(zf.read(name)):
                    rows.append((run_id, ev.ts_us, ev.bus, ev.msg_id,
                                 ev.payload_sha256, ev.payload_len, "sim_clock"))
                if rows:
                    conn.executemany(
                        """INSERT INTO telemetry_event(
                             run_id, ts_us, bus, msg_id,
                             payload_sha256, payload_len, source_clock
                           ) VALUES (?,?,?,?,?,?,?)""",
                        rows,
                    )
                    telemetry_rows += len(rows)
    return artifact_rows, telemetry_rows


def ingest_report(report_path: Path, lakehouse_root: Path,
                  bundle_path: Path | None = None) -> IngestSummary:
    layout = LakehouseLayout(root=lakehouse_root)
    layout.ensure()
    catalog = Catalog(db_path=layout.silver_db)
    catalog.initialize()

    payload_text = Path(report_path).read_text(encoding="utf-8")
    payload = json.loads(payload_text)
    run_id = str(uuid.uuid4())
    bronze_path = layout.bronze / f"{run_id}.json"
    bronze_path.write_text(payload_text, encoding="utf-8")
    bronze_sha = content_address(payload_text.encode("utf-8"))

    rows_per: dict[str, int] = {}
    with catalog.connect() as conn:
        _insert_run_manifest(conn, run_id, payload, bronze_path, bronze_sha)
        rows_per["verification_outcome"] = _insert_outcomes(conn, run_id, payload)
        rows_per["fault_injection_case"] = _insert_campaigns(conn, run_id, payload)
        rows_per["mcdc_sample"] = _insert_mcdc(conn, run_id, payload)
        rows_per["hil_measurement"] = _insert_hil(conn, run_id, payload)
        rows_per["hf_finding"] = _insert_hf(conn, run_id, payload)
        if bundle_path and Path(bundle_path).exists():
            arts, tel = _ingest_bundle_artifacts(conn, run_id, Path(bundle_path))
            rows_per["artifact_index"] = arts
            rows_per["telemetry_event"] = tel
        conn.commit()

    # update lakehouse manifest
    manifest_path = layout.manifest
    manifest = {"schema_version": catalog.schema_version() or "0.0.0", "runs": 0}
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    manifest["runs"] = int(manifest.get("runs", 0)) + 1
    manifest["last_run_id"] = run_id
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    return IngestSummary(
        run_id=run_id,
        bronze_path=bronze_path,
        rows_per_table=rows_per,
        bundle_used=Path(bundle_path) if bundle_path else None,
    )
