-- Phase A Silver layer DDL
-- ANSI SQL subset; works in SQLite, Databricks SQL, BigQuery, Athena.
-- Every row in every table is reachable via run_id (lineage anchor).

PRAGMA foreign_keys = ON;

-- ==========================================================================
-- run_manifest : 1 row per verification run; the lineage anchor
-- ==========================================================================
CREATE TABLE IF NOT EXISTS run_manifest (
    run_id              TEXT PRIMARY KEY,
    ingested_at         TEXT NOT NULL,            -- ISO-8601
    git_sha             TEXT,
    git_dirty           INTEGER NOT NULL DEFAULT 0,
    workbench_version   TEXT,
    seed                INTEGER,
    bench_id            TEXT,                     -- e.g. 'sim-localhost'
    operator            TEXT,                     -- e.g. CI user
    env_profile         TEXT,                     -- e.g. 'github-actions-ubuntu-2204'
    sensor_bus_config   TEXT,                     -- path or content hash
    time_sync_state     TEXT NOT NULL DEFAULT 'sim_clock',
    bronze_path         TEXT NOT NULL,
    bronze_sha256       TEXT NOT NULL
);

-- ==========================================================================
-- verification_outcome : per-test result with req link + DAL context
-- ==========================================================================
CREATE TABLE IF NOT EXISTS verification_outcome (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id              TEXT NOT NULL REFERENCES run_manifest(run_id),
    tc_id               TEXT NOT NULL,
    req_id              TEXT NOT NULL,
    result              TEXT NOT NULL CHECK (result IN ('PASS','FAIL','ERROR','FLAKY')),
    dal_context         TEXT,                     -- e.g. 'B'
    evidence_pointer    TEXT,                     -- bundle path
    coverage_pointer    TEXT,
    waiver              INTEGER NOT NULL DEFAULT 0,
    failures            TEXT                      -- JSON list
);
CREATE INDEX IF NOT EXISTS ix_vo_req ON verification_outcome(req_id);
CREATE INDEX IF NOT EXISTS ix_vo_tc  ON verification_outcome(tc_id);

-- ==========================================================================
-- fault_injection_case : per-campaign run + classification
-- ==========================================================================
CREATE TABLE IF NOT EXISTS fault_injection_case (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id                  TEXT NOT NULL REFERENCES run_manifest(run_id),
    campaign_id             TEXT NOT NULL,
    classification          TEXT NOT NULL,        -- detected/mitigated/...
    fcc_mode_terminal       TEXT,
    hm_event_total          INTEGER,
    expected_pass           INTEGER NOT NULL,
    parameters_json         TEXT,                 -- raw fault list
    detection_latency_us    INTEGER,
    mitigation_latency_us   INTEGER,
    recorder_sha256         TEXT
);
CREATE INDEX IF NOT EXISTS ix_fic_camp ON fault_injection_case(campaign_id);

-- ==========================================================================
-- telemetry_event : parsed bus_recording.bin rows
-- ==========================================================================
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

-- ==========================================================================
-- derived_health_window : HM event grouped into phase windows
-- ==========================================================================
CREATE TABLE IF NOT EXISTS derived_health_window (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id          TEXT NOT NULL REFERENCES run_manifest(run_id),
    window_id       INTEGER NOT NULL,
    phase           TEXT NOT NULL CHECK (phase IN
                       ('pre_fault','onset','latch','post_fault','recovery')),
    start_us        INTEGER NOT NULL,
    end_us          INTEGER NOT NULL,
    summary_json    TEXT
);

-- ==========================================================================
-- human_review : reviewer adjudication state machine
-- ==========================================================================
CREATE TABLE IF NOT EXISTS human_review (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id                  TEXT NOT NULL REFERENCES run_manifest(run_id),
    target_kind             TEXT NOT NULL,        -- 'verification_outcome', etc.
    target_id               INTEGER NOT NULL,
    reviewer_role           TEXT NOT NULL,
    adjudication            TEXT NOT NULL,        -- accept/reject/needs-info
    rationale               TEXT,
    confidence              REAL,
    disagreement            INTEGER NOT NULL DEFAULT 0,
    relabel_history_json    TEXT,
    state                   TEXT NOT NULL DEFAULT 'auto-generated'
                            CHECK (state IN
                              ('auto-generated','reviewer-confirmed',
                               'label-board-approved'))
);

-- ==========================================================================
-- artifact_index : every file shipped in the bundle, hash-indexed
-- ==========================================================================
CREATE TABLE IF NOT EXISTS artifact_index (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id          TEXT NOT NULL REFERENCES run_manifest(run_id),
    kind            TEXT NOT NULL,                -- bus_recording, hm_log, ...
    uri             TEXT NOT NULL,
    sha256          TEXT NOT NULL,
    size_bytes      INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_ai_kind ON artifact_index(kind);

-- ==========================================================================
-- mcdc_sample : per-decision MC/DC coverage snapshot
-- ==========================================================================
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

-- ==========================================================================
-- hil_measurement : per-config HIL run summary
-- ==========================================================================
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

-- ==========================================================================
-- hf_finding : per-evaluator HF outcome
-- ==========================================================================
CREATE TABLE IF NOT EXISTS hf_finding (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id          TEXT NOT NULL REFERENCES run_manifest(run_id),
    hf_id           TEXT NOT NULL,
    title           TEXT,
    passed          INTEGER NOT NULL,
    detail          TEXT,
    ac_ref          TEXT
);
