# Producer Registry Model

## Purpose

Track all registered health producers (workflows) so the aggregator knows:
- which workflows are expected;
- their expected cadence and freshness thresholds;
- their adapter type;
- whether they are enabled/disabled.

## Fields

| Field | Type | Description |
|---|---|---|
| `producer_id` | UUID | Stable unique identifier for the producer registration |
| `workflow_id` | text | `{project}/{workflow}` — stable across environments |
| `project` | text | Portfolio project slug |
| `workflow` | text | Workflow name |
| `environment` | text | `production`, `staging`, `development` |
| `expected_cadence_seconds` | integer | Expected interval between runs |
| `freshness_grace_seconds` | integer | Additional grace before stale detection (default 0) |
| `enabled` | boolean | Whether this producer is actively expected to report |
| `owner` | text | Responsible person or team |
| `adapter_type` | text | `canonical`, `shared-003`, `divergent`, or null for canonical |
| `contract_version` | integer | Highest contract version this producer supports |
| `visibility` | text | `operator` (private) or `public` |
| `registered_at` | timestamptz | When first observed |
| `retired_at` | timestamptz | When decommissioned (null if active) |
| `metadata` | jsonb | Reserved for producer-specific extension metadata |

## Lifecycle

1. **Discovery** — The aggregator discovers a new `workflow_id` from an incoming payload and creates a registry entry with defaults.
2. **Registration** — A producer may pre-register by writing to the registry table directly (Codex or admin).
3. **Active** — The producer sends regular payloads. The registry `expected_cadence_seconds` may be updated by the producer's latest payload.
4. **Disabled** — Setting `enabled = false` suppresses stale/failure alerts for planned downtime or retirement.
5. **Retired** — Setting `retired_at` removes the producer from active monitoring. No alerting.

## Default values on discovery

```sql
expected_cadence_seconds = payload.expected_cadence_seconds
freshness_grace_seconds = 0
enabled = true
adapter_type = 'canonical'
contract_version = payload.contract_version
visibility = 'operator'
```

---

## Registered producers

### Traderie

| workflow_id | Project | Workflow | Cadence | Adapter | Contract | Status |
|---|---|---|---|---|---|---|
| `traderie/snapshot` | traderie | snapshot | 21600 (6h) | canonical | v2 | Ready for VPS deployment |
| `traderie/health_export` | traderie | health_export | 1800 (30 min) | canonical | v2 | Ready for VPS deployment |

Both producers share the same exporter (`scripts/traderie_health_export.py`, updated 2026-07-09, `producer_version: traderie_health_export.py/2.0.0`). The `snapshot` workflow represents the main ingestion pipeline; `health_export` is the health monitoring workflow that reports on snapshot health.

### Reddit Ops

(TBD — see `codex-2-reddit-ops-health-producer.md` in `_internal/outbox/session3/`.)

---

## Registration notes

- Producers should be pre-registered before the aggregator's first collection cycle to prevent false "missing observation" alerts during initial deployment.
- `contract_version` must match the producer's claimed version. The aggregator validates every incoming payload against the schema for that version.
- When a producer updates its `contract_version`, the aggregator should accept both old and new versions during a 30-day migration window.
