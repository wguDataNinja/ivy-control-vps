# Database Onboarding Manifest Template

**Purpose:** Declare a PostgreSQL candidate's identity, schema contract, role model,
environment bindings, migration plan, backup/restore contract, health registration,
rollback plan, and evidence destination before privileged execution.

---

## 1. Project identity

```yaml
project_slug: <project_slug>
repository:
  local_path: /Users/buddy/projects/<repo>
  remote: <github_remote_url_or_null>
  branch: <default_branch>
  reviewed_sha: <full_commit_sha_or_null>
database:
  name: <project_slug>
  owner_role: <project_slug>_owner
  schemas:
    - name: app
      owner_role: <project_slug>_owner
    - name: archive
      owner_role: <project_slug>_owner
    - name: health
      owner_role: <project_slug>_owner
```

## 2. Role matrix

```yaml
roles:
  owner:
    name: <project_slug>_owner
    login: false
    applies: true
    note: null
  migrator:
    name: <project_slug>_migrator
    login: true
    applies: true
    note: null
  writer:
    name: <project_slug>_writer
    login: true
    applies: true
    note: null
  reader:
    name: <project_slug>_reader
    login: true
    applies: true
    note: null
  monitor:
    name: <project_slug>_monitor
    login: true
    applies: true
    note: null
  backup:
    name: <project_slug>_backup
    login: true
    applies: true
    note: null
```

## 3. Environment contract

```yaml
environment:
  env_example: deploy/env.example
  vps_env_path: /home/scraper/config/<project>.env
  required_variables:
    - <PROJECT>_PG_URL
    - <PROJECT>_PG_MIGRATOR_URL
    - <PROJECT>_PG_WRITER_URL
    - <PROJECT>_PG_READER_URL
    - <PROJECT>_PG_MONITOR_URL
    - <PROJECT>_PG_BACKUP_URL
    - <PROJECT>_HEALTH_OUTPUT
```

## 4. Migration plan

```yaml
migrations:
  directory: db/migrations
  expected_count: <N>
  validation_directory: db/migrations/validation
  rollback_directory: db/migrations/rollback
  migration_file_pattern: "YYYYMMDD_NNN_description.sql"
  rollback_file_pattern: "YYYYMMDD_NNN_description_down.sql"
  validation_file_pattern: "YYYYMMDD_NNN_description_check.sql"
```

## 5. Backup contract

```yaml
backup:
  command: scripts/<project>_backup.sh
  output_root: /home/scraper/backups/postgres/<project>
  dump_format: custom
  retention_count: 14
  manifest_required: true
  checksum_required: true
```

## 6. Health registration

```yaml
health:
  workflow_id: <project_slug>/<workflow_name>
  producer_or_adapter: scripts/health_export.py
  output_path: /home/scraper/health/<project>_health.json
  freshness_threshold_hours: 26
```

## 7. Rollback plan

```yaml
rollback:
  source_authority_fallback: <legacy_system_or_service>
  database_rollback: rollback SQL from migrations
  scheduler_rollback: <previous_timer_service_name>
  evidence_preservation: all run logs and health snapshots retained
```

## 8. Evidence destination

```yaml
evidence:
  output_dir: _internal/outbox/session-<N>/<packet-evidence-dir>
  required_items:
    - onboarding_manifest
    - reviewed_sha_or_blocker_statement
    - migration_file_list_and_checksums
    - role_and_privilege_matrix
    - positive_and_negative_privilege_test_output
    - command_transcript_summaries
    - backup_artifact_checksum_manifest
    - isolated_restore_proof
    - health_producer_or_adapter_output
    - rollback_procedure_and_stop_gates
    - cleanup_evidence
    - single_writer_authority_statement
```
