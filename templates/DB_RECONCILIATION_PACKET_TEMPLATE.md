# Reconciliation Packet Template

**Purpose:** Compare source-of-truth records (legacy, archive, or canonical data
source) against the target PostgreSQL database to verify completeness and
correctness after import, migration, or cutover.

---

## 1. Scope

```yaml
reconciliation:
  source: <legacy_db | archive_export | canonical_source>
  target: <project>.<schema>
  entity_type: <posts | identities | records>
  batch_id: <optional batch identifier>
```

## 2. Reconciliation queries

```sql
-- Row count comparison
SELECT COUNT(*) FROM legacy.{table};
SELECT COUNT(*) FROM {project}.{schema}.{table};

-- Missing records in target
SELECT l.id FROM legacy.{table} l
LEFT JOIN {project}.{schema}.{table} t ON l.id = t.id
WHERE t.id IS NULL;

-- Extra records in target (not in legacy — may be valid new data)
SELECT t.id FROM {project}.{schema}.{table} t
LEFT JOIN legacy.{table} l ON t.id = l.id
WHERE l.id IS NULL;

-- Field-level sample comparison
SELECT l.field, t.field
FROM legacy.{table} l
JOIN {project}.{schema}.{table} t ON l.id = t.id
WHERE l.field IS DISTINCT FROM t.field
LIMIT 100;
```

## 3. Acceptance criteria

| Criterion | Expected | Actual |
|-----------|----------|--------|
| Row count match | `N` | `N` |
| Missing records | `0` | `<count>` |
| Field-level divergence | `<tolerance>` | `<actual>` |

## 4. Resolution of divergence

- New records in target only: acceptable if created by post-import operations.
- Missing records: must be re-imported or flagged as accepted.
- Field-level divergence: investigate and document root cause.

## 5. Evidence record

```yaml
reconciliation_result:
  date: <yyyymmdd>
  operator: <name>
  row_count_match: true/false
  missing_records: <count>
  extra_records: <count>
  field_divergences: <count>
  accepted_divergences:
    - entity: <id>
      reason: "Post-import update"
  blocked_items:
    - entity: <id>
      reason: "Legacy data corruption"
  passed: true/false
```
