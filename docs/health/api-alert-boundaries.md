# API and Alert Boundaries

## API Design (Deferred Implementation)

### Private Operator API

Fields exposed (authenticated, operator dashboard):

- All `observation.current_state` view columns.
- Historical observations filtered by `workflow_id` and time range.
- Producer registry entries.
- Portfolio summary.
- Excludes: `error_message_private`, raw stack traces, secrets.

### Public Read-Only API

Fields exposed (rate-limited, no auth):

| Field | Source |
|---|---|
| `contract_version` | current_state |
| `generated_at` | current_state |
| `project` | current_state |
| `workflow` | current_state |
| `status` | current_state.effective_status |
| `last_success_at` | current_state |
| `expected_cadence_seconds` | current_state |
| `freshness_seconds` | current_state |
| `volume_24h` | current_state |
| `incident` | current_state.active_incident |
| `backup_state` | current_state |
| `migration_version` | current_state |

Removed from public: `deployed_revision`, `storage_bytes`, `database_size_bytes`, `disk_free_bytes`, `disk_usage_pct`, `error_code`, `incident_state` (replaced by boolean `incident`), `producer_version`, `project_environment` (unless production).

Public projection is intentionally not the producer payload. It is a sanitized
view over aggregator current state and must exclude every operator-only field,
private error detail, exact host/resource metric, secret-like field, and raw
payload field named in `HEALTH_CONTRACT.md` §13.

### Endpoints (suggested, not implemented)

```
GET /api/v2/health/summary          -> portfolio_summary
GET /api/v2/health/workflows        -> current_state (all)
GET /api/v2/health/workflows/:id    -> current_state (single)
GET /api/v2/health/workflows/:id/history  -> health_observations (time-range)
GET /api/v2/health/registry          -> producer_registry
```

### Authentication

- Private API: TLS + Bearer token or SSH tunnel.
- Public API: No auth, rate-limited.
- Dashboard: Reads private API via server-side proxy.

---

## Alert Semantics

### Events

| Event | Trigger | Severity | Dedup key |
|---|---|---|---|
| Workflow stale | `effective_status = 'stale'` | warning | `{workflow_id}/stale` |
| Workflow failed | `status = 'fail'` | critical | `{workflow_id}/fail` |
| Producer silent | No observation for `cadence * 3` | critical | `{workflow_id}/silent` |
| Backup overdue | `backup_state = 'stale'` | warning | `{workflow_id}/backup_stale` |
| Backup failed | `backup_state = 'fail'` | critical | `{workflow_id}/backup_fail` |
| Disk warning | `disk_usage_pct >= 75` | warning | `{host}/disk_warn` |
| Disk critical | `disk_usage_pct >= 85` or `disk_free_bytes < 1GB` | critical | `{host}/disk_crit` |
| Drift detected | `deployed_revision != expected` | warning | `{workflow_id}/drift` |
| Aggregator down | Self-health check fails | critical | `aggregator/down` |

### Cooldowns

- Same dedup key within 15 minutes suppresses duplicate.
- Recovery notification sent when condition clears.

### Severity action

| Severity | Dashboard | Notification | Escalation |
|---|---|---|---|
| info | Show | None | None |
| warning | Highlight | Optional (email) | None |
| critical | Flashing | Required (email/push) | 30 min if unacked |

### Alert state lifecycle

```
Condition detected -> Alert CREATED (open)
Operator acknowledges -> Alert ACKNOWLEDGED
Condition clears -> Alert RESOLVED (auto)
Manual override -> Alert SUPPRESSED
```

### Delivery implementation

Alert delivery channel (email, push, webhook) is deferred. This document defines what events exist.

---

## Dashboard Requirements (Deferred)

The future dashboard must display:

1. Overall portfolio state (healthy/warning/stale/failed counts).
2. Per-project drill-down.
3. Per-workflow detail (latest observation, history, incident state).
4. Stale/failed workflow list (sorted by severity).
5. Backup age summary.
6. Disk/resource pressure summary.
7. Deployed revision drift indicators.
8. Recent incidents timeline.
9. Historical trend views (optional).
10. Maintenance window indication.

Dashboard MUST NOT be implemented in this task.
