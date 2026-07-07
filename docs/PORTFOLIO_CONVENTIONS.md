# Portfolio Conventions

**Status:** Current authority — promoted from `ivy-control/vps/` historical material.
**Purpose:** Durable cross-repo conventions for PostgreSQL, systemd, health, gates, and deployment. Repository-specific deviations must be documented in the repo STATUS file.

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

## Backup format

```bash
pg_dump -h 127.0.0.1 -p 5432 -U {project}_backup -Fc -Z 9 -f {file}
sha256sum {file} > {file}.sha256
```

Manifest includes: database name, timestamp, PG version, dump size, SHA-256, schema version, source commit, restore database name, restore/validation/cleanup status.

Retention: latest + pre-migration baseline kept on Mac under `/Users/buddy/projects/backups/postgres/{project}/`.

---

## Restore proof

Before any real-data operation or destructive change: restore drill must pass. Procedure:
1. Create restore database: `{db}_restore_verify_{timestamp}`
2. pg_restore the latest baseline dump
3. Run `db/validation/999_full_validation.sql`
4. Verify schema ownership, table ownership, and row counts
5. Drop restore database
6. Record evidence in project LOG.md

---

## Systemd naming

Pattern: `{project}-{role}-{action}.service` / `.timer`

Approved action verbs: `ingest`, `process`, `validate`, `export`, `notify`, `check`, `backup`, `retain`, `recover`.

Services and timers must remain disabled until Scheduler Gate approval. Exact SHA deployment required before activation.

---

## Health contract

Each project maintains a `health` schema with:
- `health_status` or `health_runs` table — records per-run health data
- `workflow_status` table — current workflow state per workflow

Sanitized JSON export excludes: IP addresses, filesystem paths, credentials, private repo names, raw error messages, sensitive source names.

---

## Gate definitions

| Gate | Controls | Minimum evidence | Authority |
|------|----------|-----------------|-----------|
| Database Authority | Creating DBs/roles, migrations, PG connections | DB names/roles, capacity evidence, migration plan, rollback path | Buddy |
| Backup/Restore | Live backups, restore drills, destructive/cutover work | Dump file + SHA-256, restore target, successful restore + validation | Buddy |
| GitHub Push | Remote writes, PR creation, workflow pushes | GitHub readiness checklist, clean secrets/history, target branch | Buddy |
| VPS Capacity | Host inspection, provisioning, shadow services | CPU/RAM/disk/process metrics, forecast, safe threshold, rollback | Buddy |

---

## Deployment stop conditions

Deployment must stop immediately if:
- Dirty checkout: `git status` shows modified tracked files
- Unknown remote: `origin` does not match expected GitHub URL
- Unapproved SHA: commit SHA not in deployment registry
- Insufficient disk: >85% or <1 GB free
- Runtime data inside Git tree
- Secrets tracked in Git
- Pending migration without Database Authority Gate approval
- Unresolved merge or divergent branches
- Detached HEAD inconsistent with registry
- Service mapping unknown
- Rollback SHA unavailable
