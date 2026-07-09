-- ============================================================
-- Infra Health — Normalized Aggregator Schema (Design Only)
-- Schema: observation (producer observations, registry, views)
-- Schema: health     (aggregator self-health)
-- ============================================================
-- This SQL is DESIGN-ONLY. It will be provisioned by Codex
-- after the Database Authority Gate passes.
-- ============================================================

-- Schemas
CREATE SCHEMA IF NOT EXISTS observation;
CREATE SCHEMA IF NOT EXISTS health;

-- ============================================================
-- Producer Registry
-- ============================================================
CREATE TABLE IF NOT EXISTS observation.producer_registry (
    producer_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id         TEXT NOT NULL UNIQUE,               -- {project}/{workflow}
    project             TEXT NOT NULL,
    workflow            TEXT NOT NULL,
    environment         TEXT NOT NULL DEFAULT 'production',
    expected_cadence_seconds INTEGER NOT NULL,
    freshness_grace_seconds INTEGER NOT NULL DEFAULT 0,
    enabled             BOOLEAN NOT NULL DEFAULT TRUE,
    owner               TEXT,
    adapter_type        TEXT,                              -- 'canonical', 'shared-003', 'divergent'
    contract_version    INTEGER NOT NULL DEFAULT 2,
    visibility          TEXT NOT NULL DEFAULT 'operator',  -- 'operator', 'public'
    registered_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    retired_at          TIMESTAMPTZ,
    metadata            JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_registry_project ON observation.producer_registry(project);
CREATE INDEX IF NOT EXISTS idx_registry_enabled ON observation.producer_registry(enabled);

COMMENT ON TABLE observation.producer_registry IS
  'Producer registry. One row per registered workflow. Upsert on first observation.';

-- ============================================================
-- Health Observations (append-only time-series)
-- ============================================================
CREATE TABLE IF NOT EXISTS observation.health_observations (
    observation_id          BIGSERIAL PRIMARY KEY,
    workflow_id             TEXT NOT NULL,                 -- FK to producer_registry
    run_id                  UUID NOT NULL,
    status                  TEXT NOT NULL CHECK (status IN ('ok','warn','fail','skip','stale','running')),
    started_at              TIMESTAMPTZ,
    finished_at             TIMESTAMPTZ,
    last_success_at         TIMESTAMPTZ,
    expected_cadence_seconds INTEGER NOT NULL,
    freshness_seconds       INTEGER NOT NULL DEFAULT 0,
    records_read            INTEGER,
    records_written         INTEGER,
    records_rejected        INTEGER,
    backlog                 INTEGER,
    retry_count             INTEGER,
    error_class             TEXT,
    error_code              TEXT,
    deployed_revision       TEXT,
    schema_version          INTEGER,
    migration_version       TEXT,
    scheduler_state         TEXT,
    backup_state            TEXT,
    backup_age_seconds      INTEGER,
    storage_bytes           BIGINT,
    storage_growth_bytes_24h BIGINT,
    database_size_bytes     BIGINT,
    data_directory_size_bytes BIGINT,
    prune_status            TEXT,
    incident_state          TEXT NOT NULL DEFAULT 'none',
    degraded_reason_code    TEXT,
    heartbeat_at            TIMESTAMPTZ,
    heartbeat_age_seconds   INTEGER,
    volume_24h              INTEGER,
    growth_rate_24h         BIGINT,
    growth_rate_7d          BIGINT,
    retention_boundary_proximity TEXT,
    last_failure_at         TIMESTAMPTZ,
    failure_count           INTEGER,
    drift_state             TEXT,
    disk_free_bytes         BIGINT,
    disk_usage_pct          NUMERIC(5,2),
    producer_version        TEXT,
    project_environment     TEXT,
    contract_version        INTEGER NOT NULL DEFAULT 2,
    generated_at            TIMESTAMPTZ NOT NULL,          -- original producer timestamp
    observed_at             TIMESTAMPTZ NOT NULL DEFAULT now(),  -- aggregator receive time
    metadata                JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_obs_workflow_time ON observation.health_observations(workflow_id, observed_at DESC);
CREATE INDEX IF NOT EXISTS idx_obs_status ON observation.health_observations(status);
CREATE INDEX IF NOT EXISTS idx_obs_project ON observation.health_observations(workflow_id text_pattern_ops);
CREATE INDEX IF NOT EXISTS idx_obs_generated ON observation.health_observations(generated_at);

COMMENT ON TABLE observation.health_observations IS
  'Append-only health observations. 90-day rolling retention. Partition by month.';

-- ============================================================
-- Current State View
-- ============================================================
CREATE OR REPLACE VIEW observation.current_state AS
SELECT DISTINCT ON (ho.workflow_id)
    ho.workflow_id,
    pr.project,
    pr.workflow,
    pr.environment,
    ho.status,
    ho.generated_at,
    ho.observed_at,
    ho.last_success_at,
    ho.expected_cadence_seconds,
    ho.freshness_seconds,
    CASE
        WHEN ho.status = 'skip' THEN 'skip'
        WHEN ho.freshness_seconds > ho.expected_cadence_seconds * 2 THEN 'stale'
        WHEN ho.freshness_seconds > ho.expected_cadence_seconds * 1 THEN 'warn'
        ELSE ho.status
    END AS effective_status,
    ho.records_written,
    ho.records_rejected,
    ho.backlog,
    ho.error_class,
    ho.deployed_revision,
    ho.schema_version,
    ho.migration_version,
    ho.scheduler_state,
    ho.backup_state,
    ho.backup_age_seconds,
    ho.storage_bytes,
    ho.database_size_bytes,
    ho.data_directory_size_bytes,
    ho.prune_status,
    ho.incident_state,
    ho.degraded_reason_code,
    CASE
        WHEN ho.heartbeat_at IS NULL THEN NULL
        ELSE GREATEST(0, EXTRACT(EPOCH FROM (now() - ho.heartbeat_at))::integer)
    END AS heartbeat_age_seconds,
    ho.volume_24h,
    ho.growth_rate_24h,
    ho.growth_rate_7d,
    ho.retention_boundary_proximity,
    ho.last_failure_at,
    ho.failure_count,
    ho.drift_state,
    ho.disk_free_bytes,
    ho.disk_usage_pct,
    ho.contract_version,
    pr.enabled AS producer_enabled,
    pr.visibility,
    CASE
        WHEN ho.incident_state = 'active' THEN TRUE
        ELSE FALSE
    END AS active_incident
FROM observation.health_observations ho
JOIN observation.producer_registry pr ON ho.workflow_id = pr.workflow_id
ORDER BY ho.workflow_id, ho.observed_at DESC;

COMMENT ON VIEW observation.current_state IS
  'Latest health observation per workflow, with effective status and producer metadata.';

-- ============================================================
-- Portfolio Summary View
-- ============================================================
CREATE OR REPLACE VIEW observation.portfolio_summary AS
SELECT
    COUNT(*) AS total_workflows,
    COUNT(*) FILTER (WHERE effective_status = 'ok') AS healthy,
    COUNT(*) FILTER (WHERE effective_status = 'warn') AS warning,
    COUNT(*) FILTER (WHERE effective_status = 'stale') AS stale,
    COUNT(*) FILTER (WHERE effective_status = 'fail') AS failed,
    COUNT(*) FILTER (WHERE effective_status = 'skip') AS skipped,
    COUNT(*) FILTER (WHERE effective_status = 'running') AS running,
    COUNT(*) FILTER (WHERE active_incident) AS active_incidents,
    COUNT(*) FILTER (WHERE backup_state = 'stale' OR backup_state = 'fail') AS backup_issues,
    COUNT(*) FILTER (WHERE disk_usage_pct >= 85 OR disk_usage_pct IS NULL AND disk_free_bytes IS NOT NULL) AS disk_critical,
    now()::TIMESTAMPTZ AS computed_at
FROM observation.current_state
WHERE producer_enabled = TRUE;

COMMENT ON VIEW observation.portfolio_summary IS
  'Aggregate portfolio health counts. Designed for dashboard top-level display.';

-- ============================================================
-- Aggregator Self-Health
-- ============================================================
CREATE TABLE IF NOT EXISTS health.ingest_log (
    ingest_id           BIGSERIAL PRIMARY KEY,
    source_project      TEXT NOT NULL,
    records_received    INTEGER NOT NULL DEFAULT 0,
    records_rejected    INTEGER NOT NULL DEFAULT 0,
    rejection_reason    TEXT,
    checksum_sha256     TEXT,
    ingest_timestamp    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_ingest_project ON health.ingest_log(source_project);
CREATE INDEX IF NOT EXISTS idx_ingest_time ON health.ingest_log(ingest_timestamp DESC);

COMMENT ON TABLE health.ingest_log IS
  'Aggregator ingest log. 30-day retention.';

-- ============================================================
-- Retention Hooks (to be implemented by scheduled job)
-- ============================================================
-- -- Delete observations older than 90 days
-- DELETE FROM observation.health_observations
-- WHERE observed_at < now() - INTERVAL '90 days';
--
-- -- Delete ingest log older than 30 days
-- DELETE FROM health.ingest_log
-- WHERE ingest_timestamp < now() - INTERVAL '30 days';

-- ============================================================
-- Migration Tracking
-- ============================================================
-- Each migration must INSERT into app.infra_health_migrations:
-- CREATE TABLE IF NOT EXISTS app.infra_health_migrations (
--     version integer PRIMARY KEY,
--     name text NOT NULL,
--     checksum_sha256 text NOT NULL,
--     applied_at timestamptz NOT NULL DEFAULT now(),
--     applied_by text NOT NULL DEFAULT current_user,
--     duration_ms integer NOT NULL CHECK (duration_ms >= 0)
-- );
