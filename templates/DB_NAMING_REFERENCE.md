# Database Naming Reference

**Purpose:** Single authoritative reference for database, schema, role, and restore
database naming across the portfolio.

---

## 1. Databases

| Component | Pattern | Example |
|-----------|---------|---------|
| Database name | `{project_slug}` | `traderie`, `reddit_ops`, `sjc_intel` |

Rules:

- Lowercase snake case.
- Match the stable project slug unless a documented legacy exception exists in
  `repos/<repo>/CONTROL.md`.
- One database per project unless shared-platform justification is documented.

## 2. Schemas

| Schema | Purpose | Default owner |
|--------|---------|---------------|
| `app` | Application tables, views, indexes | `{project}_owner` |
| `archive` | Export lineage, archive records, prune metadata | `{project}_owner` |
| `health` | Run records, health state, operational views | `{project}_owner` |

Rules:

- Standard set is `app`, `archive`, `health`.
- Additional schemas require a documented reason in `repos/<repo>/CONTROL.md`.
- Shared platform services (e.g. `reddit_ops`) use named project schemas
  (`reddit_core`, `wgu_reddit`, `bsda_courses`).

## 3. Roles

| Role class | Pattern | Login | Purpose |
|------------|---------|-------|---------|
| owner | `{project}_owner` | NOLOGIN | Schema ownership, no app login |
| migrator | `{project}_migrator` | LOGIN | Migration-time DDL |
| writer | `{project}_writer` | LOGIN | Application DML |
| reader | `{project}_reader` | LOGIN | Read-only queries |
| monitor | `{project}_monitor` | LOGIN | Health/observability |
| backup | `{project}_backup` | LOGIN | pg_dump |

Rules:

- Use lowercase snake case.
- Prefix with the project slug.
- Owner is always `NOLOGIN`.
- `applies: false` when the role is not needed (see role applicability table).

## 4. Temporary restore databases

| Pattern | Example |
|---------|---------|
| `{project}_restore_{operator}_{yyyymmddhhmmss}` | `traderie_restore_buddy_20260709120000` |

Rules:

- Must be created only by an approved restore packet.
- Must be dropped only by an approved cleanup packet after validation is recorded.
- Operator is the person or agent running the restore.

## 5. Migration files

| File type | Pattern |
|-----------|---------|
| Forward | `YYYYMMDD_NNN_description.sql` |
| Rollback | `YYYYMMDD_NNN_description_down.sql` |
| Validation | `YYYYMMDD_NNN_description_check.sql` |

Directory structure:

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

## 6. Environment variables

| Variable pattern | Secret? |
|-----------------|---------|
| `{PROJECT}_PG_URL` | Yes |
| `{PROJECT}_PG_MIGRATOR_URL` | Yes |
| `{PROJECT}_PG_WRITER_URL` | Yes |
| `{PROJECT}_PG_READER_URL` | Yes |
| `{PROJECT}_PG_MONITOR_URL` | Yes |
| `{PROJECT}_PG_BACKUP_URL` | Yes |
| `{PROJECT}_PG_DATABASE` | No |
| `{PROJECT}_PG_WRITER_USER` | No |
| `{PROJECT}_PG_READER_USER` | No |
| `{PROJECT}_PG_MONITOR_USER` | No |
| `{PROJECT}_PG_MIGRATOR_USER` | No |
| `{PROJECT}_PG_BACKUP_USER` | No |
| `{PROJECT}_HEALTH_OUTPUT` | No |
| `{PROJECT}_BACKUP_ROOT` | No |
| `{PROJECT}_DATA_ROOT` | No |
| `{PROJECT}_RAW_ROOT` | No |
| `{PROJECT}_EXPORT_ROOT` | No |

## 7. Systemd units

| Component | Pattern |
|-----------|---------|
| Service | `{project}-{role}-{action}.service` |
| Timer | `{project}-{role}-{action}.timer` |

Approved action verbs: `ingest`, `process`, `validate`, `export`, `notify`,
`check`, `backup`, `retain`, `recover`.
