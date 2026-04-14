"""SQLite-backed Silver/Gold catalog. ANSI SQL only so the same DDL maps to
Databricks/BigQuery/Athena."""
from __future__ import annotations
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

SCHEMA_VERSION = "1.0.0"

_SILVER_DDL = """
CREATE TABLE IF NOT EXISTS run_manifest (
    run_id              TEXT PRIMARY KEY,
    ingested_at         TEXT NOT NULL,
    git_sha             TEXT,
    git_dirty           INTEGER NOT NULL DEFAULT 0,
    workbench_version   TEXT,
    seed                INTEGER,
    bench_id            TEXT,
    operator            TEXT,
    env_profile         TEXT,
    sensor_bus_config   TEXT,
    time_sync_state     TEXT NOT NULL DEFAULT 'sim_clock',
    bronze_path         TEXT NOT NULL,
    bronze_sha256       TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS verification_outcome (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id              TEXT NOT NULL REFERENCES run_manifest(run_id),
    tc_id               TEXT NOT NULL,
    req_id              TEXT NOT NULL,
    result              TEXT NOT NULL,
    dal_context         TEXT,
    evidence_pointer    TEXT,
    coverage_pointer    TEXT,
    waiver              INTEGER NOT NULL DEFAULT 0,
    failures            TEXT
);
CREATE INDEX IF NOT EXISTS ix_vo_req ON verification_outcome(req_id);
CREATE INDEX IF NOT EXISTS ix_vo_tc  ON verification_outcome(tc_id);

CREATE TABLE IF NOT EXISTS fault_injection_case (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id                  TEXT NOT NULL REFERENCES run_manifest(run_id),
    campaign_id             TEXT NOT NULL,
    classification          TEXT NOT NULL,
    fcc_mode_terminal       TEXT,
    hm_event_total          INTEGER,
    expected_pass           INTEGER NOT NULL,
    parameters_json         TEXT,
    detection_latency_us    INTEGER,
    mitigation_latency_us   INTEGER,
    recorder_sha256         TEXT
);
CREATE INDEX IF NOT EXISTS ix_fic_camp ON fault_injection_case(campaign_id);

CREATE TABLE IF NOT EXISTS telemetry_event (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id          TEXT NOT NULL REFERENCES run_manifest(run_id),
    ts_us           INTEGER NOT NULL,
    bus             TEXT NOT NULL,
    msg_id          TEXT NOT NULL,
    payload_sha256  TEXT NOT NULL,
    payload_len     INTEGER NOT NULL,
    source_clock    TEXT NOT NULL DEFAULT 'sim_clock'
);
CREATE INDEX IF NOT EXISTS ix_tel_run_ts ON telemetry_event(run_id, ts_us);

CREATE TABLE IF NOT EXISTS derived_health_window (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id          TEXT NOT NULL REFERENCES run_manifest(run_id),
    window_id       INTEGER NOT NULL,
    phase           TEXT NOT NULL,
    start_us        INTEGER NOT NULL,
    end_us          INTEGER NOT NULL,
    summary_json    TEXT
);

CREATE TABLE IF NOT EXISTS human_review (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id                  TEXT NOT NULL REFERENCES run_manifest(run_id),
    target_kind             TEXT NOT NULL,
    target_id               INTEGER NOT NULL,
    reviewer_role           TEXT NOT NULL,
    adjudication            TEXT NOT NULL,
    rationale               TEXT,
    confidence              REAL,
    disagreement            INTEGER NOT NULL DEFAULT 0,
    relabel_history_json    TEXT,
    state                   TEXT NOT NULL DEFAULT 'auto-generated'
);

CREATE TABLE IF NOT EXISTS artifact_index (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id          TEXT NOT NULL REFERENCES run_manifest(run_id),
    kind            TEXT NOT NULL,
    uri             TEXT NOT NULL,
    sha256          TEXT NOT NULL,
    size_bytes      INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_ai_kind ON artifact_index(kind);

CREATE TABLE IF NOT EXISTS mcdc_sample (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id              TEXT NOT NULL REFERENCES run_manifest(run_id),
    decision            TEXT NOT NULL,
    conditions          INTEGER NOT NULL,
    covered_conditions  INTEGER NOT NULL,
    pct                 REAL NOT NULL,
    samples             INTEGER NOT NULL,
    unique_rows         INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS hil_measurement (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id              TEXT NOT NULL REFERENCES run_manifest(run_id),
    config_name         TEXT NOT NULL,
    cycles              INTEGER NOT NULL,
    latency_mean_us     REAL NOT NULL,
    latency_max_us      INTEGER NOT NULL,
    jitter_stddev_us    REAL NOT NULL,
    drops               INTEGER NOT NULL,
    reboots             INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS hf_finding (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id          TEXT NOT NULL REFERENCES run_manifest(run_id),
    hf_id           TEXT NOT NULL,
    title           TEXT,
    passed          INTEGER NOT NULL,
    detail          TEXT,
    ac_ref          TEXT
);

CREATE TABLE IF NOT EXISTS lakehouse_meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""

_GOLD_VIEWS = """
DROP VIEW IF EXISTS daily_coverage;
CREATE VIEW daily_coverage AS
SELECT
    substr(rm.ingested_at, 1, 10) AS day,
    COUNT(DISTINCT rm.run_id)     AS runs,
    AVG(ms.pct)                   AS mean_mcdc_pct
FROM run_manifest rm
LEFT JOIN mcdc_sample ms USING (run_id)
GROUP BY day
ORDER BY day DESC;

DROP VIEW IF EXISTS weekly_escape_rate;
CREATE VIEW weekly_escape_rate AS
SELECT
    strftime('%Y-W%W', rm.ingested_at) AS iso_week,
    COUNT(*) AS campaigns_total,
    SUM(CASE WHEN fic.classification = 'escaped' THEN 1 ELSE 0 END) AS escapes,
    1.0 * SUM(CASE WHEN fic.classification = 'escaped' THEN 1 ELSE 0 END)
        / NULLIF(COUNT(*), 0) AS escape_rate
FROM fault_injection_case fic
JOIN run_manifest rm USING (run_id)
GROUP BY iso_week
ORDER BY iso_week DESC;

DROP VIEW IF EXISTS req_pass_rate;
CREATE VIEW req_pass_rate AS
SELECT
    req_id,
    COUNT(*) AS attempts,
    SUM(CASE WHEN result = 'PASS' THEN 1 ELSE 0 END) AS passes,
    1.0 * SUM(CASE WHEN result = 'PASS' THEN 1 ELSE 0 END)
        / NULLIF(COUNT(*), 0) AS pass_rate,
    MAX(rm.ingested_at) AS last_seen
FROM verification_outcome vo
JOIN run_manifest rm USING (run_id)
GROUP BY req_id
ORDER BY pass_rate ASC, attempts DESC;

DROP VIEW IF EXISTS hil_latency_distribution;
CREATE VIEW hil_latency_distribution AS
SELECT
    config_name,
    COUNT(*) AS runs,
    AVG(latency_mean_us) AS mean_us,
    MAX(latency_max_us)  AS max_us,
    AVG(jitter_stddev_us) AS mean_jitter_us,
    SUM(drops) AS total_drops,
    SUM(reboots) AS total_reboots
FROM hil_measurement
GROUP BY config_name
ORDER BY config_name;
"""


def create_silver_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(_SILVER_DDL)
    conn.execute(
        "INSERT OR REPLACE INTO lakehouse_meta(key, value) VALUES (?, ?)",
        ("schema_version", SCHEMA_VERSION),
    )
    conn.commit()


def create_gold_views(conn: sqlite3.Connection) -> None:
    conn.executescript(_GOLD_VIEWS)
    conn.commit()


@dataclass
class Catalog:
    db_path: Path

    @contextmanager
    def connect(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
        finally:
            conn.close()

    def initialize(self) -> None:
        with self.connect() as conn:
            create_silver_schema(conn)
            create_gold_views(conn)

    def schema_version(self) -> str | None:
        with self.connect() as conn:
            try:
                row = conn.execute(
                    "SELECT value FROM lakehouse_meta WHERE key='schema_version'"
                ).fetchone()
            except sqlite3.OperationalError:
                return None
            return row[0] if row else None
