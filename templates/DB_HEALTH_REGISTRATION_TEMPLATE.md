# Health Registration Template

**Purpose:** Register a database-backed or file-backed health producer with the
portfolio health contract. Satisfies the health fixture validation gate.

---

## 1. Workload identity

```yaml
health_registration:
  workflow_id: <project_slug>/<workflow_name>
  producer_type: <db-backed | file-backed | adapter>
  producer_path: scripts/<health_producer>.py
  output_path: /home/scraper/health/<project>_health.json
  cadence: daily
```

## 2. Health field mapping

Map producer output to the canonical v2 health contract fields:

| Canonical field | Source | Transform |
|----------------|--------|-----------|
| `project` | static | `project_slug` |
| `workflow` | static | `workflow_name` |
| `run_id` | DB run record | UUID |
| `status` | computed | From run success + freshness |
| `started_at` | DB run record | Timestamptz |
| `finished_at` | DB run record | Timestamptz |
| `last_success_at` | DB run record | Timestamptz |
| `deployed_revision` | SHA or None | From package or env |
| `incident_state` | computed | none, active, resolved |

## 3. DB-backed health configuration

```yaml
db_backed:
  schema: health
  run_table: <project>_runs
  health_view: <project>_health
  health_connection: ${<PROJECT>_PG_MONITOR_URL}
```

## 4. File-backed or adapter configuration

```yaml
file_backed:
  input_path: /home/scraper/health/<source>_raw.json
  adapter: scripts/health_adapter_<workload>.py
  output_contract_version: "2.0.0"
```

## 5. Freshness and backup thresholds

```yaml
thresholds:
  freshness_hours: 26
  backup_stale_hours: 48
  consecutive_failures_warn: 3
  consecutive_failures_critical: 10
```

## 6. Sanitization rules

Must exclude: IP addresses, filesystem paths, credentials, private repo names,
raw error messages or stack traces, sensitive source names, approval details,
reviewer identities, private backlog contents.
