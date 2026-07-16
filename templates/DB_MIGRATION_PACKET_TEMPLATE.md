# Migration Packet Template

**Purpose:** Prepare an ordered migration execution packet with forward SQL,
rollback SQL, validation SQL, checksums, and an execution plan for Strong Codex.

---

## 1. Migration inventory

| # | File | Checksum (SHA-256) | Rollback exists? | Validation exists? | Irreversible? |
|---|------|--------------------|------------------|-------------------|---------------|
| 1 | `YYYYMMDD_NNN_description.sql` | `<sha256>` | Yes/No | Yes/No | No — rollback exists |
| 2 | `YYYYMMDD_NNN_description.sql` | `<sha256>` | Yes/No | Yes/No | Yes — reason: `...` |

## 2. Checksum generation

```bash
sha256sum db/migrations/*.sql db/migrations/rollback/*.sql db/migrations/validation/*.sql
```

## 3. Migration execution plan

```yaml
execution:
  target_database: <project>
  migrator_role: <project>_migrator
  ordered_steps:
    - step: 1
      file: YYYYMMDD_NNN_description.sql
      rollback: YYYYMMDD_NNN_description_down.sql
      validation: YYYYMMDD_NNN_description_check.sql
    - step: 2
      file: YYYYMMDD_NNN_description.sql
      rollback: null
      validation: YYYYMMDD_NNN_description_check.sql
      irreversible: true
      rationale: "Data transform cannot be reversed"
```

## 4. Execution commands (for Strong Codex)

```bash
# Apply migration N
PGPASSWORD=... psql -h <host> -U <project>_migrator -d <project> \
  -f db/migrations/YYYYMMDD_NNN_description.sql

# Run validation
PGPASSWORD=... psql -h <host> -U <project>_migrator -d <project> \
  -f db/migrations/validation/YYYYMMDD_NNN_description_check.sql

# Rollback (if needed)
PGPASSWORD=... psql -h <host> -U <project>_migrator -d <project> \
  -f db/migrations/rollback/YYYYMMDD_NNN_description_down.sql
```

## 5. Stop conditions

- Missing checksum for any migration file
- Rollback missing without documented irreversible rationale
- Validation SQL fails
- Migration produces superuser-only operations
- Migration references credentials or host-specific paths
