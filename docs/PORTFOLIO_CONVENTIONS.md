# Portfolio Conventions

**Status:** Current authority.
**Purpose:** Durable cross-repo conventions and VPS admission requirements for PostgreSQL, systemd, health, migration, environment variables, deployment, backup, restore, retention, and recovery. Repository-specific deviations must be documented in the repo CONTROL.md.

---

## VPS admission requirements

A repository is eligible for production deployment to Ivy VPS only when the following requirements are satisfied or an explicit exception is recorded in `repos/<repo>/CONTROL.md`.

### Repository and source authority

- GitHub is the authoritative source for reviewed code and durable repository state.
- The deployed revision is an approved commit, tag, or release identified by exact SHA.
- The repository has a clear owner and production purpose.
- The expected GitHub remote, branch policy, and deployment path are documented.
- The deployed checkout is clean and drift can be detected.
- Runtime data, generated files, secrets, logs, backups, and mutable state live outside the Git checkout.
- The repository includes safe setup, deployment, health, rollback, and recovery instructions.

### Runtime contract

- Every production workload has one clear runtime owner.
- Every recurring workload has one authoritative scheduler.
- Duplicate schedulers and duplicate writers are disabled before activation.
- Services use approved systemd naming and are disabled until Scheduler Gate approval.
- The service entrypoint, working directory, environment files, user, restart policy, timeout, and resource expectations are documented.
- Long-running work is bounded, observable, cancellable, and safe to retry.
- Runs are idempotent or use explicit deduplication and checkpointing.
- A failed, cancelled, partial, skipped, or successful run has unambiguous terminal semantics.
- Process exit codes and systemd result semantics agree with the application health contract.

### Configuration and secrets

- Production secrets are outside Git.
- A safe `.env.example` documents required variable names without live values.
- Production environment files live under `/home/scraper/config/` with least-privilege ownership and permissions.
- Required variables are validated at startup.
- Missing or invalid configuration fails closed rather than silently selecting an unsafe fallback.
- Logs, health exports, documentation, and reports do not expose credentials or connection strings.

### Database readiness

A repository that owns or writes PostgreSQL data must satisfy all of the following:

- Database, schema, role, and ownership boundaries are documented.
- Applications do not use the `postgres` superuser.
- Separate owner, migrator, writer, reader, monitor, and backup roles exist where applicable.
- Least-privilege positive and negative permission tests pass.
- Forward migrations, rollback SQL or irreversibility statements, validation SQL, and migration-version tracking exist.
- Migrations have been applied and validated in the target environment.
- Canonical data, mutable observations, project-specific state, archive state, and derived outputs are separated where appropriate.
- Import or backfill tooling is read-only against legacy sources and idempotent against the target.
- Backup tooling works with the dedicated backup role.
- A dump has been validated with `pg_restore --list`.
- A full restore drill has passed before the database is considered production-complete.
- Retention, archive, prune eligibility, and recovery authority are documented.

### Health and observability

- The repository implements the portfolio health contract or a documented compatible equivalent.
- Health exposes current run state, last success, freshness, backlog, error class, deployed revision, schema version, and backup state.
- A running job exposes heartbeat and stage or target progress when applicable.
- Stale `running` work is detected and recovered safely.
- Concurrent execution is prevented where duplicate work would be unsafe.
- Expected partial or skipped conditions are explicitly enumerated and distinguishable from real failures.
- Monitoring thresholds exist for service state, schedule freshness, run duration, heartbeat age, database health, backup age, disk growth, and resource use.
- Sanitized public health output excludes sensitive operational detail.

### Backup, restore, retention, and recovery

- Automated backups exist for durable production state.
- Backup artifacts are timestamped, checksummed, validated, and copied to the designated archive authority.
- Backup age and archive lag are monitored.
- Restore prerequisites, commands, validation steps, and ownership are documented.
- At least one restore drill has been completed before the workload is considered fully stabilized.
- Retention distinguishes operational data, archive data, application history, regenerable data, and rollback artifacts.
- Destructive pruning occurs only after archive verification and explicit prune eligibility.
- Host rebuild and emergency recovery procedures identify the required code revision, configuration, database state, services, and validation steps.

### Deployment and rollback

- Preflight checks pass.
- The exact deployment artifact list is known.
- Dependency and migration changes are identified before deployment.
- Service impact and scheduler ownership are known.
- A rollback SHA and rollback procedure exist.
- Rollback preserves evidence and does not delete durable target data unless explicitly approved.
- Production activation includes bounded validation, explicit success gates, explicit failure gates, and automatic rollback where practical.
- A reboot or service-restart recovery check is completed during stabilization.

### Documentation and control evidence

The repository-specific control sheet at `repos/<repo>/CONTROL.md` must record:

- current lifecycle state;
- production authority;
- deployed SHA;
- database and schema ownership;
- service and timer names;
- environment-file locations;
- backup and restore status;
- health implementation status;
- rollback readiness;
- unresolved blockers;
- approved exceptions;
- evidence links under `_internal/` where applicable.

Admission states are:

| State | Meaning |
|---|---|
| `not-ready` | Required architecture, runtime, database, or operational work is incomplete. |
| `ready-for-proof` | Implementation is complete enough for bounded VPS validation, but production authority has not moved. |
| `ready-for-cutover` | Proof passed and scheduler, rollback, monitoring, backup, and authority gates are satisfied. |
| `production-stabilizing` | Production authority has moved, but scheduled-run, backup, restore, reboot, or retention gates remain open. |
| `production-complete` | The workload is authoritative, observable, recoverable, documented, and no longer dependent on a legacy runtime for normal recovery. |

---

## PostgreSQL naming

One PostgreSQL 16 server on the Ivy VPS is the target production database platform. Mac PostgreSQL instances may be used for development, restore verification, backup/archive work, and emergency recovery, but they are not the target production authority. Database per project. Roles per project:

| Role | Purpose | Permissions |
|------|---------|-------------|
| `{project}_owner` | Schema ownership | NOLOGIN, NOINHERIT. Owns schemas and objects. |
| `{project}_writer` | Application writes | CONNECT, INSERT/UPDATE/DELETE on app tables. Used by ingestion. |
| `{project}_reader` | Read-only queries | CONNECT, SELECT on non-sensitive views. Used by dashboards. |
| `{project}_monitor` | Health checks | CONNECT, SELECT on health views only. Used by Hermes. |
| `{project}_migrator` | Schema changes | CONNECT, CREATE/ALTER/DROP during migration windows. SET ROLE to owner. |
| `{project}_backup` | pg_dump | CONNECT, SELECT on all tables. |

No application uses `postgres` superuser. No pooling yet. Standard schemas: `app`, `archive`, `health`.

---

## Migration layout

Each repository with a PostgreSQL database follows this migration structure:

```
db/
  migrations/
    YYYYMMDD_NNN_description.sql
    rollback/
      YYYYMMDD_NNN_description_down.sql
    validation/
      YYYYMMDD_NNN_description_check.sql
  fixtures/
  README.md
```

File naming format: `YYYYMMDD_NNN_description.sql` where `NNN` is a zero-padded sequence number (001, 002...).

Every migration MUST provide:
1. **Forward SQL** — the schema change, idempotent where practical
2. **Rollback SQL** (or a documented statement of irreversibility with rationale)
3. **Validation query** — row-count check, constraint check, or invariant assertion
4. **Version record** — INSERT into the project's `_migrations` tracking table

Schema version tracking table:

```sql
CREATE TABLE {schema}.{project}_migrations (
  version integer PRIMARY KEY,
  name text NOT NULL,
  checksum_sha256 text NOT NULL,
  applied_at timestamptz NOT NULL DEFAULT now(),
  applied_by text NOT NULL DEFAULT current_user,
  duration_ms integer NOT NULL CHECK (duration_ms >= 0)
);
```

Migration SQL files must NOT contain production credentials, data dumps, environment-specific paths, or secrets of any kind.

---

## Bounded privileged execution

The portfolio uses bounded privileged execution for repeatable VPS deployment and database onboarding tasks. This is not a grant of broad shell authority.

### Current implemented boundary

Session evidence shows a migration-phase boundary currently exists:

- `/usr/local/sbin/ivy-systemd-deploy` is a root-owned helper used for allowlisted systemd deployment actions.
- `/etc/sudoers.d/ivy-migration` allows selected `ivy-systemd-deploy` actions as root, `/usr/sbin/reboot`, and PostgreSQL `psql`, `createdb`, and `dropdb` as the `postgres` user.
- helper actions are logged to `/var/log/ivy-systemd-deploy.log`.
- arbitrary shell access, arbitrary `systemctl`, arbitrary root file writes, unknown projects, unknown helper actions, and extra helper arguments were denied in Session 3 validation.
- broad sudo still requires a password.
- the installed helper is root-owned, is not yet version-controlled, and cannot update itself through the current NOPASSWD boundary.

Supporting evidence is recorded in `_internal/outbox/session3/agent-6-portfolio-vps-operations-discovery.md`, `_internal/outbox/session3/codex-7-operations-access-and-traderie-cutover.md`, and `_internal/outbox/session4/agent-1-traderie-cutover-unblock-audit.md`.

This boundary is current session evidence and current deployment practice. It is not yet a reusable platform product. Reuse requires an explicit Strong Codex packet until the productization gate passes.

### Productization requirements

Before the helper/sudo workflow becomes a reusable portfolio capability, it must have:

- version-controlled helper source or template;
- reviewed installation/update mechanism;
- scoped sudo allowlist with exact commands and arguments;
- command and argument validation inside the helper;
- repository or workload allowlisting;
- exact-SHA enforcement for deployable repositories;
- action logging that records timestamp, actor, project, action, source SHA, and result without secrets;
- validation that the installed root-owned helper hash matches reviewed source;
- rollback procedure for helper and sudo-policy changes;
- negative tests proving denied arbitrary shell access, secret management, destructive cleanup, non-allowlisted projects, non-allowlisted actions, and broad root commands;
- explicit statement that reboot remains production-affecting and requires Buddy-approved timing.

### Prohibited capabilities

The reusable bounded helper must not:

- provide arbitrary root shell access;
- manage secrets or print live secret values;
- edit arbitrary files;
- perform destructive cleanup without a separate exact-target approval;
- bypass Git publication or exact-SHA review;
- deploy dirty or unapproved checkouts;
- install packages unless a separate package-management packet is approved;
- treat reboot authority as automatically approved.

### Installation packet requirements

A later privileged helper/sudo-policy installation packet must include:

- reviewed helper source path and checksum;
- reviewed sudoers policy text;
- install paths, owners, and modes;
- `visudo -c` validation plan;
- current installed helper/policy backup or capture;
- update and rollback commands;
- allowlist matrix for each project/workload;
- positive and negative validation commands;
- log inspection command;
- stop conditions for hash mismatch, denied expected command, allowed unexpected command, missing logs, or policy parse failure.

Medium agents may prepare the source, packet, validation matrix, and evidence template. Strong Codex performs any root-owned installation or sudo-policy update only when separately authorized.

---


## Systemd naming

Pattern: `{project}-{role}-{action}.service` / `.timer`

Approved action verbs: `ingest`, `process`, `validate`, `export`, `notify`, `check`, `backup`, `retain`, `recover`.

Services and timers must remain disabled until Scheduler Gate approval. Exact SHA deployment required before activation.

---

## Environment variable naming

Pattern: `{PROJECT}_{VARIABLE}` — uppercase, project prefix.

| Variable pattern | Purpose | Secret? |
|-----------------|---------|---------|
| `{PROJECT}_PG_URL` | Full PostgreSQL connection URL | Yes (contains password) |
| `{PROJECT}_PG_DATABASE` | Database name | No |
| `{PROJECT}_PG_WRITER_USER` | Writer role name | No |
| `{PROJECT}_PG_READER_USER` | Reader role name | No |
| `{PROJECT}_PG_MONITOR_USER` | Monitor role name | No |
| `{PROJECT}_PG_MIGRATOR_USER` | Migrator role name | No |
| `{PROJECT}_PG_BACKUP_USER` | Backup role name | No |
| `{PROJECT}_DATA_ROOT` | VPS data directory | No |
| `{PROJECT}_RAW_ROOT` | VPS raw capture directory | No |
| `{PROJECT}_EXPORT_ROOT` | VPS export directory | No |
| `{PROJECT}_HEALTH_OUTPUT` | Health JSON output path | No |
| `{PROJECT}_BACKUP_ROOT` | Backup directory | No |

VPS config files live at `/home/scraper/config/{project}.env` (outside Git). Repositories keep safe `.env.example` with variable names and placeholders only.

---

## Health contract

The canonical portfolio health contract is now defined in `docs/HEALTH_CONTRACT.md` (v2.0.0).

This section is superseded. The old 18-field model below is retained as historical context but is no longer authoritative. All new health work must follow `docs/HEALTH_CONTRACT.md`.

### Historical field set (v1, superseded)

| Field | Type | Description |
|-------|------|-------------|
| `project` | text | Project slug |
| `workflow` | text | Workflow name |
| `run_id` | uuid | Unique run identifier |
| `status` | text | ok, warn, fail, skip |
| `started_at` | timestamptz | Run start |
| `finished_at` | timestamptz | Run finish |
| `last_success_at` | timestamptz | Last successful run |
| `expected_cadence` | interval | Expected time between runs |
| `freshness_age` | interval | Time since last run |
| `records_read` | integer | Input records processed |
| `records_written` | integer | Output records produced |
| `records_rejected` | integer | Records rejected or failed |
| `backlog` | integer | Pending items |
| `retry_count` | integer | Current retry attempt |
| `error_class` | text | Error type if failed |
| `deployed_revision` | text | Git commit hash |
| `schema_version` | integer | DB migration version |
| `backup_state` | text | ok, stale, fail |
| `incident_state` | text | none, active, resolved |

Sanitized public export MUST exclude: IP addresses, filesystem paths, credentials, private repo names, raw error messages or stack traces, sensitive source names, approval details or reviewer identities, private backlog contents.

---

## Deployment preflight

Before any VPS checkout update, verify:
- Correct repo path and remote origin (GitHub)
- Correct branch or detached SHA
- Clean working tree with no modified tracked files
- Untracked files are expected and acceptable (runtime data outside Git)
- Secrets are outside Git checkout
- Sufficient disk headroom (below 85% or above 1 GB free)
- Approved target SHA matches deployment registry
- Approved pull request number recorded
- No unexpected local commits
- Dependency-change flag set if requirements changed
- Migration-change flag set if migration files changed
- Service impact assessed
- Rollback SHA recorded

---

Backup retention, restore-proof requirements, and backup versus application-history distinction are defined in `docs/DATA_LIFECYCLE_STANDARD.md`.

---

## Deployment stop conditions

Deployment must stop immediately if:
- Dirty checkout — `git status` shows modified tracked files
- Unknown remote — `origin` does not match expected GitHub URL
- Unapproved SHA — commit SHA not in deployment registry
- Insufficient disk — >85% or < 1 GB free
- Runtime data mixed inside Git working tree
- Secret files tracked in Git
- Pending migration without Database Authority Gate approval
- Unresolved merge or divergent branches
- Detached HEAD inconsistent with registered SHA
- Service mapping unknown — cannot determine which services to restart
- Rollback SHA not recorded
