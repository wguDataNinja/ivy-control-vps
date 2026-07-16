# Pilot Gate Template

**Purpose:** Define the gate criteria for a pilot (first non-production or
limited-production PostgreSQL onboarding). Record prerequisites, execution
packet, validation, and pass/fail decision.

---

## 1. Pilot identity

```yaml
pilot:
  project: <project_slug>
  description: <brief_purpose>
  database: <database_name>
  host: <vps_hostname>
  runtime_user: <user>
  packeted_by: <agent>
  executed_by: <Strong Codex | OpenCode>
  buddy_approval_required: true/false
```

## 2. Prerequisites

- [ ] Onboarding manifest is complete and reviewed.
- [ ] Naming follows `docs/PORTFOLIO_CONVENTIONS.md`.
- [ ] Migration files exist with forward, rollback, and validation.
- [ ] Role applicability matrix is complete.
- [ ] Privilege matrix with positive and negative tests is documented.
- [ ] Backup command and manifest schema are defined.
- [ ] Health producer or adapter is implemented.
- [ ] Rollback plan is documented.
- [ ] Evidence bundle index is prepared.
- [ ] No superuser references in any SQL.
- [ ] No secrets or host-specific paths in migration files.

## 3. Execution sequence

| Step | Action | Owner |
|------|--------|-------|
| 1 | Provision database, schemas, roles, grants | Strong Codex |
| 2 | Apply migrations | Strong Codex |
| 3 | Run validation SQL | Strong Codex |
| 4 | Run role positive and negative tests | Strong Codex |
| 5 | Execute backup proof | Strong Codex |
| 6 | Execute isolated restore proof | Strong Codex |
| 7 | Run health producer check | Strong Codex |
| 8 | Record evidence bundle | Medium agent |

## 4. Validation criteria

```yaml
validation:
  schemas_exist:
    - app
    - archive
    - health
  roles_exist:
    - <project>_owner
    - <project>_migrator
    - <project>_writer
    - <project>_reader
    - <project>_monitor
    - <project>_backup
  migrations_applied:
    count: <N>
    last_version: <version>
  backup_validated:
    dump_non_zero: true
    checksum_matches: true
    pg_restore_list_valid: true
  restore_proved:
    temp_db_created: true
    row_counts_match: true
    cleanup_completed: true
  health_output: valid_json
  no_superuser_usage: true
```

## 5. Pass/fail

```yaml
pilot_result:
  date: <yyyymmdd>
  passed: true/false
  blocker: <description or null>
  conditions:
    - condition: <description>
      owner: <agent>
      deadline: <date_or_null>
  buddy_approved: true/false
  next_step: <cutover | remediation | extended_pilot>
```
