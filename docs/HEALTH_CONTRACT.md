# Portfolio Health Contract

**Version:** 2.0.0
**Status:** Current authority. Supersedes the health contract section of `docs/PORTFOLIO_CONVENTIONS.md` §Health contract.
**Date:** 2026-07-08

---

## 1. Purpose and Scope

### 1.1 Goals

- Every production Ivy workflow emits deterministic health signals.
- Health data is machine-readable, versioned, and sanitized.
- A central aggregator can normalize payloads from diverse producers.
- Aggregated health supports a read-only API, operator dashboard, and Hermes read-only assistance.
- Deterministic production operation never depends on Hermes.

### 1.2 Non-goals

- This document does not define the dashboard UI, the API implementation, or the alert delivery channel.
- It does not define Hermes workflow contracts.
- It does not define per-repository retention policies (those remain in each repo's control docs).

### 1.3 Authority and precedence

| Source | Authority |
|---|---|
| This document (HEALTH_CONTRACT.md) | Highest — canonical architecture authority |
| PORTFOLIO_CONVENTIONS.md (outside §Health) | Equal — complementary conventions |
| SHARED-003_HEALTH_CONTRACT.md | Historical reference — superseded by this document |
| INFRA_HEALTH_DESIGN_PACKAGE.md | Historical reference — design direction superseded by this document |
| Repo-specific CONTROL.md | Repository-specific compliance, must not contradict this contract |

---

## 2. Architecture

```
deterministic producer (repository)
  -> local health exporter script
  -> canonical sanitized JSON payload
  -> aggregator (validates + normalizes + stores)
  -> infra_health PostgreSQL (append-only observations + current-state views)
  -> read-only API (private operator + optional sanitized public)
  -> dashboard (reads API, not databases directly)
  -> Hermes read-only assistance (reads API or monitor role)
```

### 2.1 Producer responsibilities

Every production repository owns:

- A deterministic health exporter that emits canonical JSON.
- A documented workflow registry (what workflows exist, their expected cadence).
- Deployed revision reporting (exact SHA or `unknown`).
- Safe failure behavior — exporter failure must not cascade; a failed producer emits a `skip` heartbeat.
- Tests and fixtures for the exporter.

### 2.2 Aggregator responsibilities

The central health service owns:

- Producer registration and discovery.
- Payload validation against the canonical JSON Schema.
- Adapter normalization for non-conforming producers.
- Current-state computation (latest per workflow per project).
- Freshness evaluation (compare observation time + status to expected cadence).
- Overdue and missing-observation detection.
- Incident-state derivation.
- Historical retention (90-day rolling).
- Portfolio summary queries.
- Read-only API output.
- Dashboard-ready views.
- Alert event generation.
- Self-health reporting.

### 2.3 Distinction of failure layers

The aggregator must distinguish:

| Layer | Signal | Example |
|---|---|---|
| Producer failure | No payload received within expected window + grace | Workflow silent for 3 hours |
| Exporter failure | Payload received but missing core fields | Missing `deployed_revision` |
| Collector failure | Payload contains `status: fail` with error | Database unreachable |
| Aggregator failure | Aggregator self-health fails | Aggregator cannot write |
| API failure | API returns 5xx | Dashboard shows error |
| Stale observation | Payload received but `status: stale` | Workflow stopped reporting success |
| Intentionally disabled | Payload contains `scheduler_state: paused` | Maintenance window |

---

## 3. Canonical Field Set

### 3.1 Field classification

| Code | Meaning |
|---|---|
| **Required core** | Must be present in every producer payload. Aggregator rejects payloads missing these. |
| **Optional producer** | Producer may include if available. Aggregator fills with `null`. |
| **Derived aggregator** | Computed by aggregator from observation history or multiple payloads. |
| **Operator-only** | Present in private payload, stripped from public projection. |
| **Deprecated** | Still accepted but will be removed in next major version. |
| **Postponed** | Defined for future contract version; not yet required. |

The canonical v2 model has exactly 46 current fields:

| Classification | Count | Payload ownership |
|---|---:|---|
| Required core | 16 | Producer payload, keys required; nullable where specified |
| Optional producer | 19 | Producer payload when available; aggregator stores `null` when absent |
| Operator-only | 2 | Private producer payload only; stripped from public projection |
| Derived aggregator | 9 | Aggregator/current-state fields; not emitted by producers |
| Deprecated | 0 | Legacy aliases are accepted by adapters but are not v2 fields |
| Postponed | 0 | Future fields are named in §3.5 but are not v2 fields |

Producer payloads therefore contain 37 contract fields at most
(16 required core + 19 optional producer + 2 operator-only), plus optional
`metadata`. The normalized/current-state model contains all 46 fields. This
distinction prevents double-counting aggregator-derived fields as producer
fields.

### 3.2 Canonical field table

| # | Field | Type | Nullable | Classification | Owner | Description |
|---|---|---|---|---|---|---|
| 1 | `contract_version` | integer | no | Required core | Producer | This contract's version number (currently 2) |
| 2 | `generated_at` | timestamptz | no | Required core | Producer | When this payload was generated (ISO 8601) |
| 3 | `project` | text | no | Required core | Producer | Portfolio project slug (`traderie`, `reddit_ops`, etc.) |
| 4 | `workflow` | text | no | Required core | Producer | Workflow name within project (`daily_ingest`, `snapshot`, etc.) |
| 5 | `workflow_id` | text | no | Required core | Producer | Stable unique workflow identifier (`{project}/{workflow}`) |
| 6 | `run_id` | uuid | no | Required core | Producer | Unique run identifier |
| 7 | `status` | text | no | Required core | Producer | One of: `ok`, `warn`, `fail`, `skip`, `stale`, `running` |
| 8 | `started_at` | timestamptz | yes | Required core | Producer | Run start timestamp |
| 9 | `finished_at` | timestamptz | yes | Required core | Producer | Run finish timestamp; `null` if still running |
| 10 | `last_success_at` | timestamptz | yes | Required core | Producer | Timestamp of last `ok` run for this workflow |
| 11 | `expected_cadence_seconds` | integer | no | Required core | Producer | Expected interval between runs in seconds |
| 12 | `freshness_seconds` | integer | no | Required core | Producer | Seconds since `last_success_at` (or `generated_at` if never succeeded) |
| 13 | `records_read` | integer | yes | Optional producer | Producer | Input records processed |
| 14 | `records_written` | integer | yes | Optional producer | Producer | Output records produced |
| 15 | `records_rejected` | integer | yes | Optional producer | Producer | Records rejected or failed |
| 16 | `backlog` | integer | yes | Optional producer | Producer | Pending items count |
| 17 | `retry_count` | integer | yes | Optional producer | Producer | Current retry attempt |
| 18 | `error_class` | text | yes | Optional producer | Producer | Error type if failed (`NetworkError`, `TimeoutError`, etc.) |
| 19 | `error_code` | text | yes | Operator-only | Producer | Machine-readable error code; stripped from public output |
| 20 | `error_message_private` | text | yes | Operator-only | Producer | Raw error detail; NEVER in public output |
| 21 | `deployed_revision` | text | yes | Required core | Producer | Git commit SHA of deployed code; `null` if not tracked |
| 22 | `schema_version` | integer | yes | Optional producer | Producer | Project schema migration version |
| 23 | `migration_version` | text | yes | Optional producer | Producer | Migration filename stem of latest applied migration |
| 24 | `scheduler_state` | text | yes | Required core | Producer | `active`, `paused`, `unknown`, `unmanaged` |
| 25 | `backup_state` | text | yes | Required core | Producer | `ok`, `stale`, `fail`, `not_applicable` |
| 26 | `backup_age_seconds` | integer | yes | Optional producer | Producer | Age of latest backup in seconds |
| 27 | `storage_bytes` | bigint | yes | Optional producer | Producer | Total bytes consumed by project data |
| 28 | `storage_growth_bytes_24h` | bigint | yes | Optional producer | Producer | Byte change in last 24 hours |
| 29 | `database_size_bytes` | bigint | yes | Optional producer | Producer | PostgreSQL database size in bytes |
| 30 | `data_directory_size_bytes` | bigint | yes | Optional producer | Producer | Data/export directory size in bytes |
| 31 | `prune_status` | text | yes | Optional producer | Producer | `ok`, `stale`, `fail`, `not_applicable` |
| 32 | `incident_state` | text | yes | Required core | Producer | `none`, `active`, `resolved` |
| 33 | `degraded_reason_code` | text | yes | Derived aggregator | Aggregator | Machine-readable reason for non-ok status |
| 34 | `heartbeat_at` | timestamptz | yes | Optional producer | Producer | Timestamp of last progress during a run |
| 35 | `heartbeat_age_seconds` | integer | yes | Derived aggregator | Aggregator | Seconds since `heartbeat_at` |
| 36 | `volume_24h` | integer | yes | Derived aggregator | Aggregator | Records written in the last 24 hours |
| 37 | `growth_rate_24h` | bigint | yes | Derived aggregator | Aggregator | Storage growth in last 24 hours |
| 38 | `growth_rate_7d` | bigint | yes | Derived aggregator | Aggregator | Storage growth in last 7 days |
| 39 | `retention_boundary_proximity` | text | yes | Derived aggregator | Aggregator | `ok`, `warning`, `critical` based on retention policy |
| 40 | `last_failure_at` | timestamptz | yes | Derived aggregator | Aggregator | Timestamp of last non-ok run |
| 41 | `failure_count` | integer | yes | Derived aggregator | Aggregator | Consecutive failure count |
| 42 | `drift_state` | text | yes | Derived aggregator | Aggregator | `clean`, `dirty`, `unknown` based on deployed_revision |
| 43 | `disk_free_bytes` | bigint | yes | Optional producer | Producer | Free disk space on host |
| 44 | `disk_usage_pct` | numeric(5,2) | yes | Optional producer | Producer | Disk usage percentage |
| 45 | `producer_version` | text | yes | Optional producer | Producer | Health exporter version |
| 46 | `project_environment` | text | yes | Optional producer | Producer | `production`, `staging`, `development` |

### 3.3 Required core fields for v2.0.0

Every producer payload MUST include:

`contract_version`, `generated_at`, `project`, `workflow`, `workflow_id`, `run_id`, `status`, `started_at`, `finished_at`, `last_success_at`, `expected_cadence_seconds`, `freshness_seconds`, `deployed_revision`, `scheduler_state`, `backup_state`, `incident_state`

The aggregator MUST reject payloads missing any required core field.

`started_at`, `finished_at`, and `last_success_at` are required (the keys must be present) but may be null (e.g., `finished_at` is null while a run is in progress). The JSON Schema enforces both presence and nullability.

### 3.4 Ownership inventory

| Classification | Fields |
|---|---|
| Required core | `contract_version`, `generated_at`, `project`, `workflow`, `workflow_id`, `run_id`, `status`, `started_at`, `finished_at`, `last_success_at`, `expected_cadence_seconds`, `freshness_seconds`, `deployed_revision`, `scheduler_state`, `backup_state`, `incident_state` |
| Optional producer | `records_read`, `records_written`, `records_rejected`, `backlog`, `retry_count`, `error_class`, `schema_version`, `migration_version`, `backup_age_seconds`, `storage_bytes`, `storage_growth_bytes_24h`, `database_size_bytes`, `data_directory_size_bytes`, `prune_status`, `heartbeat_at`, `disk_free_bytes`, `disk_usage_pct`, `producer_version`, `project_environment` |
| Operator-only | `error_code`, `error_message_private` |
| Derived aggregator | `degraded_reason_code`, `heartbeat_age_seconds`, `volume_24h`, `growth_rate_24h`, `growth_rate_7d`, `retention_boundary_proximity`, `last_failure_at`, `failure_count`, `drift_state` |

Each current v2 field appears in exactly one ownership classification.

### 3.5 Deprecated aliases accepted by adapters

The following legacy aliases are accepted for backward compatibility and mapped
to canonical fields by adapters. They are not part of the 46-field v2 canonical
inventory.

| Legacy field | Maps to | Deprecation |
|---|---|---|
| `schema_version` (used as contract version) | `contract_version` | Removed in v3 |
| `freshness_age` (interval type) | `freshness_seconds` (integer) | Removed in v3 |
| `service_slug` | `project` | Removed in v3 |
| `component` | `workflow` | Removed in v3 |

### 3.6 Postponed fields (planned for v3)

- `cost_per_run` (integer, cents) — LLM stage cost accounting
- `token_count` (integer) — LLM stage token usage
- `upstream_workflow_id` (text) — dependency tracking between workflows
- `run_duration_seconds` (integer) — already derivable from started_at/finished_at

Postponed fields are not part of the 46-field v2 canonical inventory.

---

## 4. Freshness Semantics

### 4.1 Freshness computation

```
freshness_seconds = now() - COALESCE(last_success_at, created_at, generated_at)
```

### 4.2 Status interpretation

| `status` value | Meaning | Freshness evaluation |
|---|---|---|
| `ok` | Run completed successfully | Compare `freshness_seconds` to `expected_cadence_seconds` |
| `warn` | Run completed with warnings | Compare `freshness_seconds` to `expected_cadence_seconds` |
| `fail` | Run failed | Immediate alert-worthy unless within grace |
| `skip` | Run intentionally skipped | No freshness evaluation — `expected_cadence` is paused |
| `stale` | Last known run has exceeded thresholds | Set by aggregator when producer is silent |
| `running` | Run is in progress | Track `heartbeat_age_seconds` instead |

### 4.3 Freshness thresholds

| Level | Condition | `status` |
|---|---|---|
| Healthy | `freshness_seconds <= expected_cadence_seconds * 1` | Produced status |
| Warning | `expected_cadence_seconds * 1 < freshness_seconds <= expected_cadence_seconds * 2` | `warn` (aggregator may override) |
| Degraded | `freshness_seconds > expected_cadence_seconds * 2` | `stale` (aggregator sets) |
| Failed | Producer explicitly reports `fail` | `fail` (producer authority) |

### 4.4 Grace periods

- A `running` workflow that exceeds `expected_cadence_seconds * 1` without a heartbeat is treated as potentially stale.
- A `running` workflow that exceeds `expected_cadence_seconds * 2` without a heartbeat is treated as stale.
- New workflows (first run) have a 24-hour grace before being flagged stale.

### 4.5 Missing observations

If no payload is received for a registered workflow within `expected_cadence_seconds * 3`, the aggregator records a synthetic observation with `status: stale` and `degraded_reason_code: no_observation_received`.

If the aggregator itself cannot write, it reports `aggregator_unreachable` through its self-health endpoint.

### 4.6 Maintenance windows

A producer may set `scheduler_state: paused` during maintenance. The aggregator must not flag paused workflows as stale. Health dashboards show paused workflows with a distinct visual state.

### 4.7 Backup freshness semantics

Every workflow with `backup_state` other than `not_applicable` MUST document an expected backup cadence in its repository control sheet or producer registry entry.

Default evaluation when a repository has not defined stricter thresholds:

| Level | Condition |
|---|---|
| `ok` | `backup_age_seconds <= expected_backup_cadence_seconds * 1.5` |
| `stale` | `expected_backup_cadence_seconds * 1.5 < backup_age_seconds <= expected_backup_cadence_seconds * 3` |
| `fail` | latest backup attempt failed, no validated backup exists, or `backup_age_seconds > expected_backup_cadence_seconds * 3` |

Daily backups therefore default to `ok` through 36 hours, `stale` after 36 hours, and `fail` after 72 hours or on explicit backup failure. Repository control sheets may set stricter thresholds when the data source or recovery objective requires it.

### 4.8 Failure semantics

Current health must distinguish these failure dimensions:

| Dimension | Definition | Computation |
|-----------|------------|-------------|
| Current active failure | Is the most recent run in a terminal error state? | `status IN ('fail', 'stale')` for the latest observation |
| Latest run result | What did the most recent run report? | Raw `status` from the latest producer payload |
| Bounded recent-run history | Have the last N runs (e.g., 10) completed within policy? | Count of `ok`/`warn` versus `fail`/`stale` in the rolling window |
| Consecutive failures | How many uninterrupted failures since the last success? | Increment on each `fail` or `stale`; reset to 0 on `ok` or `warn` |
| Cumulative historical failures | Total failures recorded since deployment or counter reset | Monotonic counter; never reset by a successful run |
| Recovery state | Is the workload actively recovering after a known failure? | `last_failure_at < last_success_at` AND consecutive failures === 0 after a prior non-zero peak |

Rules:

1. **Cumulative counts remain visible.** Historical failure totals are preserved as evidence. They must not be hidden, reset on success, or removed from the data model.
2. **A successful run resets consecutive failure state.** `failure_count` (field #41) tracks consecutive failures, not cumulative total.
3. **Current status must not remain down solely because cumulative historical failures are nonzero.** A workload with a successful current run, recent bounded evidence of reliability, and no active failure must report a healthy current status.
4. **Status computation uses:** current run state, freshness, active failures, recent bounded evidence, and recovery state. Cumulative historical failures are evidence for trend analysis and incident review — they are not a direct input to current health status.
5. **Recovery state** is `recovered` when the most recent run is successful, consecutive failures are zero, and a prior failure peak existed. The aggregator may record the recovery timestamp.

Example: 44 recent successful exports with zero consecutive failures produce a healthy current state even if cumulative historical failures are nonzero. The historical failures remain available for review but do not keep the health indicator in a `fail` or `stale` state.

---

## 4A. Phase 0 Operator Status View

Phase 0 is the first portfolio health deliverable. It is a small read-only CLI report, not a dashboard, API, alerting system, or production health aggregator.

### Command

Initial implementation:

```bash
python3 tools/portfolio_phase0_status.py --format table
```

Optional machine output:

```bash
python3 tools/portfolio_phase0_status.py --format json
```

### Initial workload coverage

The first implementation must include:

- Traderie production workload;
- Reddit Ops production workload;
- SJC Intel readiness placeholder;
- WGU Catalog low-frequency batch placeholder.

### Data sources

The CLI reads only local files and explicitly supplied read-only evidence snapshots. It must not SSH to the VPS, query production databases, read live secrets, or modify any scheduler.

Allowed sources:

- `repos/<repo>/CONTROL.md` for lifecycle state, production authority, deployed SHA, scheduler/writer names, backup/restore status, blockers, and next authorized work;
- `repos/<repo>/RELEASE_GATES.md` when present for gate-specific status;
- repo-specific health JSON fixtures or sanitized evidence files produced by prior authorized tasks;
- an optional local phase0 evidence directory supplied by `--evidence-dir`;
- documented backup path classes, ages, or summaries from control sheets or sanitized evidence;
- deployment registry or exact-SHA evidence when that artifact exists;
- static placeholder metadata for readiness candidates.

### Normalized internal model

Each row normalizes to:

| Field | Meaning |
|---|---|
| `workload_id` | Stable slug, usually `{repo}/{workflow}` |
| `repository` | Managed repo or workload name |
| `workflow` | Ingestion workflow or batch trigger |
| `classification` | `production`, `production_degraded`, `readiness_placeholder`, or `batch_placeholder` |
| `last_attempt_at` | Latest known attempt timestamp or `unknown` |
| `last_success_at` | Latest known success timestamp or `unknown` |
| `freshness_state` | `ok`, `stale`, `fail`, `not_applicable`, or `unknown` |
| `scheduler_state` | `active`, `paused`, `unmanaged`, `not_applicable`, or `unknown` |
| `writer_authority` | Current writer authority summarized without private paths |
| `deployed_revision` | Exact SHA, short SHA, `pending-publication`, `not_applicable`, or `unknown` |
| `backup_age` | Human-readable age, `not_applicable`, or `unknown` |
| `current_failure` | Short sanitized failure code or `none` |
| `drift_state` | `clean`, `dirty`, `not_evaluated`, or `unknown` |
| `incident_or_approval` | Active incident, required approval, or `none` |
| `source` | Control/evidence source used to populate the row |

### Workload identity rules

- Use existing `workflow_id` when a producer supplies one.
- Otherwise use `{repo_slug}/{workflow_slug}`.
- WGU Catalog uses `wgu_catalog/catalog_release_batch` until a repo-specific producer exists.
- SJC Intel uses `sjc_intel/ingestion_readiness` until production workflow names are accepted.
- WGU-derived Reddit workloads other than Reddit Ops are not added until the WGU-derived boundary reconciliation gate resolves ownership.

### Control-sheet fields consumed

The parser may consume headings and tables for:

- lifecycle state;
- approved production SHA or deployment status;
- production authority;
- active scheduler/timer;
- active writer;
- database and schema status;
- health status;
- backup status;
- current blocker;
- unresolved gates;
- next authorized work.

If a field is missing, the CLI reports `unknown` and records the missing field in JSON output.

### Health producer and adapter interface

The CLI may read canonical health JSON or adapter output that follows the v2 field names in this contract. Adapter functions should return the normalized model above and preserve a `source` pointer to the file or control sheet they used.

Missing producers are allowed for placeholders. They must appear as `readiness_placeholder` or `batch_placeholder`, not as production failures.

### Systemd inspection boundary

Phase 0 must not inspect live systemd state by default. If a later task provides a sanitized `systemctl show` snapshot, the CLI may parse that snapshot from `--evidence-dir`. Live systemd inspection, SSH, timer activation, service restart, or daemon reload is outside Phase 0.

### Deployed revision and drift

Deployed revision priority:

1. canonical health payload `deployed_revision`;
2. repo control sheet deployed or approved SHA;
3. sanitized deployment evidence file;
4. `unknown`.

Drift is `clean` only when a row has both expected and observed revision evidence and they match. It is `dirty` when both are present and differ. It is `not_evaluated` for placeholders and `unknown` when production evidence is incomplete.

### Freshness and backup evaluation

Freshness uses §4 semantics when `last_success_at` and `expected_cadence_seconds` are available. Otherwise it uses control-sheet status text. WGU Catalog freshness is evaluated against the latest known catalog release/check cadence once a release-detection packet defines it; before then it reports `unknown` with `approval_required` if activation mode is undecided.

Backup age uses canonical health `backup_age_seconds` first, then sanitized evidence summaries, then control-sheet text. It must not scan private backup directories by default.

### Incident and approval state

Represent production issues and human approvals as short codes:

- `incident:critical`;
- `incident:degraded`;
- `approval:publication`;
- `approval:cutover`;
- `approval:reboot`;
- `approval:activation-mode`;
- `none`.

Do not include reviewer identities, private notes, full stack traces, hostnames, IP addresses, filesystem paths, credentials, or raw error bodies.

### Missing and contradictory data

- Missing non-critical data renders as `unknown`, not as a failure.
- Missing required production authority data renders `current_failure=missing_authority`.
- Contradictory current-authority data renders `current_failure=contradictory_authority` and `incident_or_approval=approval:review`.
- Placeholder candidates must be visibly marked so they are not mistaken for live production health.

### CLI options

Required:

- `--format table|json`

Recommended:

- `--repo <slug>` filter rows;
- `--evidence-dir <path>` read sanitized local evidence snapshots;
- `--include-placeholders` default true for Phase 0;
- `--strict` exit non-zero on contradictory production authority;
- `--no-color` deterministic output for tests.

### Table output

Table columns:

```text
WORKLOAD  WORKFLOW  LAST_ATTEMPT  LAST_SUCCESS  FRESHNESS  SCHEDULER  WRITER  REVISION  BACKUP_AGE  FAILURE  DRIFT  INCIDENT/APPROVAL
```

Sample:

```text
WORKLOAD     WORKFLOW                 LAST_ATTEMPT       LAST_SUCCESS       FRESHNESS  SCHEDULER  WRITER      REVISION      BACKUP_AGE  FAILURE              DRIFT          INCIDENT/APPROVAL
traderie     ingest_snapshot          2026-07-11 18:01Z  2026-07-11 18:01Z  fail       active     vps         e5ebd0f      stale       pc_hc_nl_timeout     not_evaluated  incident:degraded
reddit_ops   daily_wgu_collection     unknown            unknown            unknown    active     vps         pending-pub  unknown     publication_blocker  unknown        approval:publication
sjc_intel    ingestion_readiness       not_applicable     not_applicable     unknown    unmanaged  none        unknown      unknown     readiness_pending    not_evaluated  approval:cutover
wgu_catalog  catalog_release_batch     not_applicable     not_applicable     unknown    manual     file-export unknown      not_app     activation_mode     not_evaluated  approval:activation-mode
```

### Fixtures, tests, and validation

The implementation packet must include:

- fixtures for Traderie degraded production, Reddit Ops publication-blocked production, SJC readiness placeholder, and WGU Catalog batch placeholder;
- parser tests for missing and contradictory fields;
- table snapshot or golden-output test;
- JSON schema or key-set test for machine output;
- redaction tests for private paths, credentials, hostnames, IP addresses, and raw error messages.

Validation commands:

```bash
python3 -m pytest tests/test_portfolio_phase0_status.py
python3 tools/portfolio_phase0_status.py --format table --no-color
python3 tools/portfolio_phase0_status.py --format json
```

### Completion proof

`§3E-G1` passes when the command prints all four required rows, tests pass, no private or secret values are emitted, placeholder rows are clearly marked, and contradictory production authority is surfaced without making live changes.

---

## 5. Identifier and Versioning Model

### 5.1 Identifiers

| Concept | Pattern | Example | Notes |
|---|---|---|---|
| `project` | `{slug}` | `traderie`, `reddit_ops` | Lowercase, underscore-separated |
| `workflow` | `{action}` | `daily_ingest`, `snapshot` | Lowercase, underscore-separated |
| `workflow_id` | `{project}/{workflow}` | `traderie/snapshot` | Stable across environments |
| `run_id` | UUID v4 | `a1b2c3d4-...` | Generated per run |
| `contract_version` | integer | `2` | This document's version |
| `schema_version` | integer | `17` | Per-project migration count |
| `migration_version` | text | `20260705_017_grant_reader_health_select` | Migration filename stem |

### 5.2 Contract versioning

| Version change | Rule |
|---|---|
| Adding optional fields | Minor — aggregator must accept |
| Adding required fields | Major — producer + aggregator must coordinate migration window |
| Removing fields | Major — 30-day deprecation notice |
| Renaming fields | Major — old name accepted for one version |
| Changing enum values | Major — old value accepted for one version |

### 5.3 Producer compatibility

- Producers must declare `contract_version` in every payload.
- Aggregator must accept the current and immediately previous major version.
- Producers SHOULD support the latest major version within 30 days of release.

---

## 6. Storage Model

### 6.1 Canonical normalized schema

The central aggregator stores observations in a dedicated `infra_health` database:

```
infra_health/
  schema: observation/
    TABLE health_observations       -- append-only time-series
    TABLE producer_registry         -- current producer identities
    VIEW  current_state             -- latest observation per workflow
    VIEW  portfolio_summary         -- aggregated portfolio state
  schema: health/
    TABLE ingest_log                -- aggregator self-health
```

### 6.2 `observation.health_observations`

This is the canonical normalized table that all producer payloads map into. Schema is detailed in `docs/health/database/normalized_health_schema.sql`.

### 6.3 `observation.current_state` view

A view that returns the latest observation per `(workflow_id)` using `DISTINCT ON`. This is the primary query target for dashboards and API.

### 6.4 `observation.producer_registry`

Contains one row per registered producer workflow. See `docs/health/producer-registry.md`.

### 6.5 Retention

| Table | Retention |
|---|---|
| `observation.health_observations` | 90-day rolling; monthly archive to Mac |
| `observation.producer_registry` | Indefinite (upsert on registration) |
| `health.ingest_log` | 30-day rolling |
| Current-state view | No retention — always derived from observations |

### 6.6 No live provisioning

This schema is design-only in this repository. It will be provisioned by Codex after the Database Authority Gate passes.

---

## 7. Producer/Adapter Model

### 7.1 Producer types

| Type | Description | Example |
|---|---|---|
| **Canonical** | Emits the exact v2 contract fields | Future Reddit Ops exporter, updated Traderie exporter |
| **Adapter-compatible** | Emits a known variant; aggregator can normalize | Current Traderie exporter (SHARED-003) |
| **Divergent** | Uses different schema/field names; requires adapter | IHMC `private_status`, IHK `private_status` |
| **Not yet instrumented** | No health exporter exists | BSDA Courses, WGU Atlas |

### 7.2 Adapter strategy

- Do not force existing repositories to rename mature tables.
- Existing health tables keep their names.
- Each divergent producer gets a repository-local adapter script that reads the existing table and produces canonical JSON.
- The aggregator may also maintain a server-side normalization map for known divergent fields.
- Adapter code lives in the producer's repository, not in the aggregator.

See `docs/health/adapter-interface.md` for the formal interface.

---

## 8. API and Public/Private Boundary

### 8.1 Private operator API (authenticated)

Exposes all fields except `error_message_private`, raw stack traces, and secrets. Used by the operator dashboard.

### 8.2 Sanitized public/read-only API

Excludes `error_code`, `error_message_private`, `storage_bytes` (exact), `deployed_revision` (optional), `disk_free_bytes`, `disk_usage_pct`, `project_environment` unless production. Includes summary health status, freshness, cadence, and incident flag.

### 8.3 Fields excluded from all API output

- `error_message_private`
- Any field matching the prohibited patterns list (see §13)
- Connection strings, credentials, tokens
- Filesystem paths
- IP addresses
- User/seller identities

### 8.4 Authentication

- Private API: Bearer token or SSH-based auth.
- Public API: No auth required, but rate-limited.
- Dashboard: Reads private API.

---

## 9. Alert Semantics

### 9.1 Event types

| Event | Severity | Description |
|---|---|---|
| Workflow stale | warning | `freshness_seconds > expected_cadence_seconds * 2` |
| Workflow failed | critical | `status: fail` |
| Service down | critical | Producer has not reported for `expected_cadence * 3` |
| Heartbeat lost | warning | `status: running` but heartbeat exceeds threshold |
| Backup overdue | warning | `backup_state: stale` |
| Backup failed | critical | `backup_state: fail` |
| Disk warning | warning | `disk_usage_pct >= 75` |
| Disk critical | critical | `disk_usage_pct >= 85` |
| Drift detected | warning | `drift_state: dirty` |
| Aggregator unhealthy | critical | Aggregator self-health check fails |
| Observability gap | info | Expected producer not yet registered |

### 9.2 Severity levels

| Level | Action |
|---|---|
| info | No notification. Visible in dashboard. |
| warning | Dashboard highlight. Optional notification. |
| critical | Immediate notification. Escalation if not acknowledged. |

### 9.3 Deduplication

- Same `workflow_id` + same event type within cooldown period (15 min by default) suppresses duplicate.
- Recovery notification sent when condition clears.

### 9.4 Recovery semantics

- A subsequent `status: ok` from the same `workflow_id` auto-resolves all active alerts for that workflow.
- Alerts for different workflows are independent.

### 9.5 Delivery

Alert delivery channel is a later concern. This document defines what events exist and their semantics. Implementation (email, push, webhook) is deferred.

---

## 10. Traderie Compatibility

Traderie's existing `health.health_runs` table is the closest to the canonical schema. Mappings:

| Canonical field | Traderie field | Status |
|---|---|---|
| `project` | `project` (default `traderie`) | Direct |
| `workflow` | `workflow` | Direct |
| `workflow_id` | `{project}/{workflow}` | Derived |
| `run_id` | `run_id` | Direct |
| `status` | `status` | Direct — uses same enum |
| `started_at` | `started_at` | Direct |
| `finished_at` | `finished_at` | Direct |
| `last_success_at` | `last_success_at` | Direct |
| `expected_cadence_seconds` | `expected_cadence` (interval → extract epoch) | Derived |
| `freshness_seconds` | `freshness_age` (interval → extract epoch) | Derived |
| `records_read` | `records_read` | Direct |
| `records_written` | `records_written` | Direct |
| `records_rejected` | `records_rejected` | Direct |
| `backlog` | `backlog` | Direct |
| `retry_count` | `retry_count` | Direct |
| `error_class` | `error_class` | Direct |
| `error_code` | `error_code` | Direct |
| `deployed_revision` | `deployed_revision` | Direct |
| `schema_version` | `schema_version` | Direct |
| `migration_version` | `migration_version` | Direct |
| `scheduler_state` | `scheduler_state` | Direct |
| `backup_state` | `backup_state` | Direct |
| `storage_bytes` | `storage_bytes` | Direct |
| `storage_growth_bytes_24h` | `storage_growth_bytes_24h` | Direct |
| `incident_state` | `incident_state` | Direct |
| `database_size_bytes` | New field | Add to exporter |
| `data_directory_size_bytes` | New field | Add to exporter |
| `prune_status` | New field | Derive from prune_audit |
| `disk_free_bytes`, `disk_usage_pct` | New field | Add to exporter (VPS only) |
| `heartbeat_at` | Not needed | Traderie runs are bounded |

Traderie's existing exporter is already SHARED-003 compliant and can be updated to v2 in one task.

---

## 11. Reddit Ops First-Producer Role

Reddit Ops will be the first canonical producer. See the precise implementation specification in `repos/reddit-ops/` (this task's companion outputs).

---

## 12. Codex-Only Deployment Boundary

The following work is Codex-only and must NOT be performed by OpenCode:

- Provisioning `infra_health` database and roles
- Applying central health migrations on VPS
- Deploying the aggregator service
- Deploying producer exporters to VPS
- Configuring health output directories and permissions
- Installing systemd health timers
- Activating health collection on VPS
- Deploying the read-only API
- Deploying the dashboard
- Configuring alert delivery
- Performing production cutover

---

## 13. Prohibited Fields (Public Output)

These field names are banned from all sanitized public output by exact match:

`error_message_private`, `error_message`, `raw_payload`, `source_url`, `filesystem_path`, `credential`, `api_key`, `token`, `cookie`, `session_id`, `browser_profile`, `private_notes`, `reviewer`, `approval_detail`, `backlog_detail`, `ip_address`, `hostname`, `local_path`, `stack_trace`, `sql_error`, `chat_body`, `reddit_body`, `raw_html`, `raw_response`

---

## 14. References and Superseded Sources

| Source | Status |
|---|---|
| SHARED-003_HEALTH_CONTRACT.md | Superseded by this document. Its field-level detail informed this contract. |
| INFRA_HEALTH_DESIGN_PACKAGE.md | Superseded by this document. Its storage model was adopted with modifications. |
| PORTFOLIO_CONVENTIONS.md §Health contract | Superseded by this document. |
| SHARED_HEALTH_INPUT_SYNTHESIS.md | Historical evidence. Fully superseded. |
