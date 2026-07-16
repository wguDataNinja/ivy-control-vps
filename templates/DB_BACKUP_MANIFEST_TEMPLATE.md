# Backup Manifest Template

**Purpose:** Standard manifest schema for PostgreSQL backup artifacts. Every
backup must produce a machine-readable manifest alongside the dump file.

---

## 1. Manifest schema

```yaml
backup_manifest:
  project: <project_slug>
  database: <database_name>
  dump_file: <project>_<yyyymmddThhmmssZ>.dump
  dump_format: custom
  created_at: <yyyymmddThhmmssZ>
  created_by: <project>_backup
  checksum:
    algorithm: sha256
    value: <hex_digest>
  file_size_bytes: <N>
  pg_version: 16
  pg_restore_list_validated: true/false
  retention:
    policy: keep_last_N
    value: 14
    expires_at: <yyyymmdd>
  archive:
    copied_to: <user>@<host>:<path>
    archive_verified: true/false
```

## 2. Validation commands

```bash
# Verify dump is readable
pg_restore --list <dump_file> > /dev/null 2>&1 && echo "VALID" || echo "CORRUPT"

# Verify checksum
sha256sum --check <checksum_file>

# Verify backup role ownership
ls -la <dump_file>  # should show <project>_backup or root-only
```

## 3. Retention rules

- Keep the last 14 daily dumps by default.
- Retain at least one passing restore drill per project.
- Archive to Mac after retention window on VPS.
- Prune VPS dumps only after archive verification and explicit approval.

## 4. Backup failure detection

```yaml
failure_conditions:
  - dump_file_size == 0
  - pg_restore --list exits non-zero
  - checksum mismatch
  - manifest missing required fields
  - backup role connection failure
```
