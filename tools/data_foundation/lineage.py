"""Full lineage walk for a given run_id."""
from __future__ import annotations
from pathlib import Path
from .catalog import Catalog


def lineage_for_run(db_path: Path, run_id: str) -> dict:
    catalog = Catalog(db_path=db_path)
    with catalog.connect() as conn:
        manifest = conn.execute(
            """SELECT run_id, ingested_at, git_sha, git_dirty,
                      workbench_version, bench_id, operator, env_profile,
                      bronze_path, bronze_sha256
               FROM run_manifest WHERE run_id = ?""",
            (run_id,),
        ).fetchone()
        if not manifest:
            return {"run_id": run_id, "found": False}

        outcomes = conn.execute(
            """SELECT tc_id, req_id, result, dal_context, failures
               FROM verification_outcome WHERE run_id = ?
               ORDER BY tc_id, req_id""",
            (run_id,),
        ).fetchall()

        campaigns = conn.execute(
            """SELECT campaign_id, classification, fcc_mode_terminal,
                      hm_event_total, expected_pass, recorder_sha256
               FROM fault_injection_case WHERE run_id = ?""",
            (run_id,),
        ).fetchall()

        artifacts = conn.execute(
            """SELECT kind, uri, sha256, size_bytes
               FROM artifact_index WHERE run_id = ?""",
            (run_id,),
        ).fetchall()

        mcdc = conn.execute(
            """SELECT decision, conditions, covered_conditions, pct, samples
               FROM mcdc_sample WHERE run_id = ?""",
            (run_id,),
        ).fetchall()

        telemetry_count = conn.execute(
            "SELECT COUNT(*) FROM telemetry_event WHERE run_id = ?",
            (run_id,),
        ).fetchone()[0]

        reviews = conn.execute(
            """SELECT target_kind, target_id, reviewer_role,
                      adjudication, state FROM human_review WHERE run_id = ?""",
            (run_id,),
        ).fetchall()

    return {
        "found": True,
        "run_id": run_id,
        "manifest": {
            "ingested_at": manifest[1],
            "git_sha": manifest[2],
            "git_dirty": bool(manifest[3]),
            "workbench_version": manifest[4],
            "bench_id": manifest[5],
            "operator": manifest[6],
            "env_profile": manifest[7],
            "bronze_path": manifest[8],
            "bronze_sha256": manifest[9],
        },
        "verification_outcomes": [
            {"tc_id": r[0], "req_id": r[1], "result": r[2],
             "dal": r[3], "failures": r[4]} for r in outcomes
        ],
        "campaigns": [
            {"id": r[0], "classification": r[1], "fcc_mode": r[2],
             "hm_events": r[3], "expected_pass": bool(r[4]),
             "recorder_sha256": r[5]} for r in campaigns
        ],
        "artifacts": [
            {"kind": r[0], "uri": r[1], "sha256": r[2], "bytes": r[3]}
            for r in artifacts
        ],
        "mcdc": [
            {"decision": r[0], "conditions": r[1],
             "covered": r[2], "pct": r[3], "samples": r[4]}
            for r in mcdc
        ],
        "telemetry_event_count": telemetry_count,
        "human_reviews": [
            {"target": f"{r[0]}#{r[1]}", "reviewer": r[2],
             "adjudication": r[3], "state": r[4]} for r in reviews
        ],
    }
