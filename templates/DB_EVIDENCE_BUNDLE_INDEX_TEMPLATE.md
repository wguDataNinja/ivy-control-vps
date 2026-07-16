# Evidence Bundle Index Template

**Purpose:** Index all evidence artifacts produced during a PostgreSQL
onboarding. Used as the table of contents for the private outbox packet.

---

## 1. Onboarding overview

```yaml
onboarding:
  project: <project_slug>
  database: <database_name>
  date_completed: <yyyymmdd>
  executed_by: <Strong Codex | OpenCode>
  buddy_approval: <optional_approval_ref>
  outbox_directory: _internal/outbox/session-<N>/<packet-evidence-dir>
```

## 2. Evidence index

| # | Artifact | Description | Format | Verified |
|---|----------|-------------|--------|----------|
| 1 | `manifest.yaml` | Onboarding manifest (project identity, roles, env, migrations, backup, health) | YAML | ✅ |
| 2 | `reviewed_sha.txt` | Exact reviewed source SHA or publication blocker statement | Text | ✅ |
| 3 | `migration_checksums.txt` | SHA-256 checksums of all migration files | Text | ✅ |
| 4 | `role_matrix.yaml` | Role applicability and privilege matrix | YAML | ✅ |
| 5 | `privilege_tests.log` | Positive and negative role test output | Text | ✅ |
| 6 | `provisioning_commands.log` | Command transcript (secrets redacted) | Text | ✅ |
| 7 | `backup_manifest.yaml` | Backup artifact path, checksum, manifest | YAML | ✅ |
| 8 | `restore_evidence.yaml` | Isolated restore proof (temp DB name, validation, cleanup) | YAML | ✅ |
| 9 | `health_output.json` | Health producer or adapter output (sanitized) | JSON | ✅ |
| 10 | `rollback_procedure.md` | Rollback steps and stop gates | Markdown | ✅ |
| 11 | `cleanup_evidence.yaml` | Cleanup of temp restore databases | YAML | ✅ |
| 12 | `natural_run_proof.yaml` | Natural scheduled run evidence | YAML | ✅ |
| 13 | `authority_statement.md` | Final single-writer/scheduler authority statement | Markdown | ✅ |

## 3. Artifact location convention

```
_internal/outbox/session-<N>/<packet-evidence-dir>/
  manifest.yaml
  reviewed_sha.txt
  migration_checksums.txt
  role_matrix.yaml
  privilege_tests.log
  provisioning_commands.log
  backup_manifest.yaml
  restore_evidence.yaml
  health_output.json
  rollback_procedure.md
  cleanup_evidence.yaml
  natural_run_proof.yaml
  authority_statement.md
```

## 4. Required checks per artifact

- Every artifact must exist at the expected path.
- YAML files must parse without errors.
- JSON files must parse and contain expected fields.
- SHA checksums must match file contents.
- No artifact may contain credentials, private IPs, or filesystem paths.
