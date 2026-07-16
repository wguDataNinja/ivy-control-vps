# Isolated Restore Checklist Template

**Purpose:** Step-by-step checklist for an isolated PostgreSQL restore drill.
Create a temporary database, restore a backup, validate, record evidence,
and clean up.

---

## 1. Prerequisites

- [ ] Backup dump file exists and checksum matches.
- [ ] `pg_restore --list` validates the dump.
- [ ] Target PostgreSQL 16 is running.
- [ ] Required roles exist in the target instance.
- [ ] Required extensions exist (e.g. `pgcrypto`).
- [ ] Sufficient disk space for the restore database.

## 2. Temporary database name

```
{project}_restore_{operator}_{yyyymmddhhmmss}
```

## 3. Restore procedure

```bash
# Create temporary database (as postgres user)
sudo -n -u postgres createdb -O {project}_owner {project}_restore_{operator}_{yyyymmddhhmmss}

# Restore from dump (as postgres user)
sudo -n -u postgres pg_restore -d {project}_restore_{operator}_{yyyymmddhhmmss} \
  --no-owner --role={project}_owner <dump_file>

# Verify roles and grants
sudo -n -u postgres psql -d {project}_restore_{operator}_{yyyymmddhhmmss} \
  -c "\du+ {project}_*"
```

## 4. Validation queries

```sql
-- Schema existence
SELECT schema_name FROM information_schema.schemata
WHERE schema_name IN ('app', 'archive', 'health');

-- Migration version
SELECT version, name, checksum_sha256, applied_at
FROM {schema}.{project}_migrations ORDER BY version;

-- Key row counts
SELECT 'posts' AS entity, COUNT(*) FROM app.posts
UNION ALL
SELECT 'observations', COUNT(*) FROM app.observations;

-- Role permissions
SELECT r.rolname, r.rolcanlogin,
       ARRAY(SELECT p.privilege_type FROM information_schema.role_table_grants p
             WHERE p.grantee = r.rolname LIMIT 5) AS sample_grants
FROM pg_roles r WHERE r.rolname LIKE '{project}_%';
```

## 5. Positive and negative role tests

```sql
-- Reader can SELECT but not INSERT
SET ROLE {project}_reader;
SELECT COUNT(*) FROM app.posts;  -- must succeed
INSERT INTO app.posts DEFAULT VALUES;  -- must fail

-- Backup can read all tables
SET ROLE {project}_backup;
SELECT COUNT(*) FROM app.posts;  -- must succeed
```

## 6. Cleanup procedure

```bash
# Verify no active connections to restore DB
sudo -n -u postgres psql -c "SELECT datname, pid, state FROM pg_stat_activity WHERE datname LIKE '%_restore_%';"

# Drop the temporary database
sudo -n -u postgres dropdb {project}_restore_{operator}_{yyyymmddhhmmss}
```

## 7. Evidence record

```yaml
restore_evidence:
  dump_file: <dump_file>
  checksum: <sha256>
  temp_database: <temp_db_name>
  created_at: <timestamp>
  validated_by: <operator>
  validation_passed: true/false
  cleanup_packet_ready: true/false
  cleanup_completed_at: <timestamp>
  issues:
    - description: "Missing extension pgcrypto required manual install"
      resolution: "Installed before restore"
```

## 8. Stop conditions

- `pg_restore` exits non-zero.
- Row counts do not match expected values.
- Role permissions are incorrect.
- Cleanup fails (temp database remains).
- Disk space is insufficient.
