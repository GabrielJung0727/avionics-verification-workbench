-- Phase A Gold layer materialized views.
-- These are deterministic SQL aggregations on Silver tables.

-- daily_coverage : avg / min line coverage by ingestion day
CREATE VIEW IF NOT EXISTS daily_coverage AS
SELECT
    substr(rm.ingested_at, 1, 10) AS day,
    COUNT(DISTINCT rm.run_id)     AS runs,
    AVG(ms.pct)                   AS mean_mcdc_pct
FROM run_manifest rm
LEFT JOIN mcdc_sample ms USING (run_id)
GROUP BY day
ORDER BY day DESC;

-- weekly_escape_rate : campaign escape rate per ISO week
CREATE VIEW IF NOT EXISTS weekly_escape_rate AS
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

-- req_pass_rate : per-requirement test outcome trend
CREATE VIEW IF NOT EXISTS req_pass_rate AS
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

-- hil_latency_distribution : per-config latency distribution snapshot
CREATE VIEW IF NOT EXISTS hil_latency_distribution AS
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
