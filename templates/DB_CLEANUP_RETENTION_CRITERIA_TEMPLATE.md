# Cleanup and Retention Criteria Template

**Purpose:** Define when temporary database objects, backup artifacts,
operational data, and legacy fallback systems may be cleaned up or pruned.
No cleanup occurs before all criteria are met and explicitly approved.

---

## 1. Temporary restore database cleanup

| Criterion | Detail |
|-----------|--------|
| Target | `<project>_restore_<operator>_<yyyymmddhhmmss>` |
| Precondition | Validation evidence is recorded in the restore packet |
| Precondition | No active connections to the restore database |
| Precondition | The original production database is confirmed healthy |
| Precondition | Drop command is reviewed and exact |
| Command | `sudo -n -u postgres dropdb <temp_db_name>` |
| Post-validation | Verify temp DB no longer exists: `psql -lqt | grep <temp_db_name>` |
| Required approval | Buddy approval for each dropdb invocation |

## 2. Legacy SQLite / fallback cleanup

| Criterion | Detail |
|-----------|--------|
| Target | `<legacy_db_path>` |
| Precondition | PostgreSQL has completed N successful scheduled runs (N >= 14) |
| Precondition | Backup and restore have been proven |
| Precondition | Rollback no longer depends on the legacy system |
| Precondition | Archive copy exists and is verified (checksum match) |
| Precondition | Documented approval from Buddy |
| Post-validation | Legacy path removed; no running process references it |

## 3. Backup artifact retention

| Criterion | Detail |
|-----------|--------|
| VPS retention | Keep last 14 daily dumps |
| Archive transfer | Copy to Mac archive after N days |
| Archive verification | Checksum match between VPS and Mac copies |
| Prune eligibility | VPS artifact can be pruned after archive verification and retention window |
| Prune approval | Buddy or automated retention policy |
| Prune command | `rm <dump_file> <manifest_file> <checksum_file>` (exact paths) |

## 4. Operational data retention

| Data class | VPS retention | Archive destination | Prune trigger |
|------------|--------------|---------------------|---------------|
| Application data | Indefinite (active) | N/A | Application retirement |
| Health records | 90 days | Mac archive | After archive verified |
| Run logs | 30 days | Mac archive | After archive verified |
| Migration history | Indefinite | N/A | N/A |
| Temporary restore DBs | Hours (per drill) | N/A | After validation recorded |

## 5. Cleanup stop conditions

- Target database or file is ambiguous.
- Any running process or timer references the target.
- Archive copy is missing or checksum does not match.
- Deletion target is the production database.
- Active writer depends on the target.
- Buddy approval has not been explicitly obtained.
