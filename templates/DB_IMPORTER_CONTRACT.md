# Importer Contract Template

**Purpose:** Define the contract for a read-only, idempotent PostgreSQL import
or backfill from a legacy source.

---

## 1. Source identity

```yaml
source:
  type: <sqlite|postgres|csv|json>
  path: /path/to/legacy/source
  access: read-only
  format_version: <version_or_null>
```

## 2. Target database

```yaml
target:
  database: <project>
  schema: app
  migration_prerequisite: <last_migration_before_import>
```

## 3. Import contract

```yaml
import:
  idempotent: true
  read_only_source: true
  insert_strategy: <INSERT ON CONFLICT DO NOTHING | MERGE | TRUNCATE + INSERT>
  batch_size: 1000
  error_handling: log_and_continue_or_abort
  max_errors_before_abort: 10
  progress_logging: every N records
  rollback_strategy: re-run from clean database (no in-place rollback)
```

## 4. Record mapping

| Target table | Source table | Field mapping | Transform |
|-------------|--------------|---------------|-----------|
| `app.posts` | `legacy_posts` | `id` → `id`, `title` → `title` | Trim whitespace |
| `app.posts` | `legacy_posts` | `created` → `created_utc` | Convert to timestamptz |

## 5. Idempotency proof

- Run the importer once against a fresh database.
- Run the importer a second time against the same database.
- Verify that row counts match and no duplicate records exist.

## 6. Validation

```yaml
validation:
  row_count_match:
    source_table: legacy_posts
    target_table: app.posts
    expected_count: <N>
  sample_checks:
    - SELECT * FROM app.posts LIMIT 5
  null_checks:
    - "No NULL in app.posts.id"
```

## 7. Prohibitions

- Importer must not write to the legacy source.
- Importer must not create, alter, or drop schemas or tables.
- Importer must not run as a superuser or the owner role.
