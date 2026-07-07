# Portfolio Conventions

**Status:** Current authority.
**Purpose:** Durable cross-repo conventions for PostgreSQL, systemd, health, migration, environment variables, and deployment. Repository-specific deviations must be documented in the repo CONTROL.md.

---

## PostgreSQL naming

One PostgreSQL 16 server on Mac (`localhost:5432`). Database per project. Roles per project:

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

Each project maintains a health schema with a per-run health table containing at minimum:

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
