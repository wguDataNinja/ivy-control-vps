# Health Adapter Interface

## Purpose

Define a deterministic adapter interface that transforms existing divergent health implementations to the canonical v2 contract format.

## Interface

Every adapter is a callable (script or function) that:

**Input:** Source data (varies by repository):
- File path to existing health JSON (e.g., SHARED-003 format).
- Database query result from existing health table.
- Inert/fixture mode for testing.

**Output:** Canonical v2 JSON payload (validates against `portfolio_health_schema.json`).

**Behavior:**

| Condition | Adapter action |
|---|---|
| Source field maps directly | Copy with or without rename |
| Source field needs type conversion | Convert (e.g., interval -> integer seconds) |
| Source field missing | Set to `null` |
| Source field has no canonical equivalent | Include in `metadata` object |
| Source has unknown fields | Pass through in `metadata` |
| Source cannot be read | Emit `status: stale` with `error_class: AdapterError` |

## Field mapping rules

### Timestamp normalization

All timestamps MUST be ISO 8601 strings with timezone (Z suffix).

### Status mapping

| Source status | Canonical status |
|---|---|
| `ok` | `ok` |
| `warn`, `degraded` | `warn` |
| `fail`, `failed` | `fail` |
| `skip`, `not_applicable` | `skip` |
| `running`, `in_progress` | `running` |
| `unknown`, null | `stale` |
| `healthy` | `ok` |

### Freshness normalization

| Source type | Conversion |
|---|---|
| `interval` | `EXTRACT(EPOCH FROM interval)` |
| `integer` seconds | Direct pass-through |
| `text` like `"300"` | `CAST(text AS integer)` |
| `text` like `"5m"` | Parse and convert to seconds |
| Missing/null | Computed: `now() - last_success_at` |

### Cadence normalization

Same rules as freshness normalization.

## Test requirements

Every adapter must have:

1. A test with a valid source payload producing a valid canonical output.
2. A test with a missing-optional-field source producing valid output with nulls.
3. A test with a missing-required-field source producing a validation error.
4. A test with an unknown-field source passing through to `metadata`.

## Reference adapter

A reference adapter `traderie_to_canonical.py` exists in the Traderie repository. It maps SHARED-003 format to v2 format and serves as the implementation template for all other adapters.
