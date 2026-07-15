# Portfolio Health Conformance Matrix

**Date:** 2026-07-08
**Contract version:** 2.0.0

## Legend

| Code | Meaning |
|---|---|
| ✓ | Available / Conforming |
| ≡ | Derivable via adapter |
| ± | Partial — requires some changes |
| ✗ | Missing / Not applicable |
| N/A | Workflow does not produce this type of data |

## Per-project assessment

### Reddit Ops

| Criterion | Status | Notes |
|---|---|---|
| Health source | `tools/check_reddit_ops_pg_health.py` + operational SQL queries | No dedicated health table yet |
| Health table | `reddit_core.ingestion_runs` | Operational table, not a health table |
| Canonical field set | ≡ | All fields derivable from ingestion_runs + system queries |
| Exporter exists | ± | CHECK script exists, but no canonical exporter |
| Scheduler metadata | ✓ | systemctl reports |
| Deployed SHA | ✗ | VPS not a Git checkout — needs manual SHA tracking |
| Drift detection | ✗ | Not implemented |
| Backup/restore metrics | ✓ | Backup service + timer active |
| Storage metrics | ± | `pg_database_size()` available; disk via `df` |
| Tests | ✗ | No health export tests |
| **Conformance** | **Adapter-compatible** | Need canonical exporter |

**Recommended action:** Implement `tools/reddit_ops_health_exporter.py` as first canonical producer.

---

### Traderie

| Criterion | Status | Notes |
|---|---|---|
| Health source | `scripts/traderie_health_export.py` | Updated to v2, ~490 lines. Updated 2026-07-09. |
| Health table | `health.health_runs`, `health.workflow_status` | SHARED-003 compliant; v2 payload via adapter layer |
| Canonical field set | ✓ | All 16 required core + 19 optional + 2 operator-only supported |
| Exporter exists | ✓ | Working, `--pg` and `--json` and fixture modes; contract_version=2 |
| Scheduler metadata | ✓ | `scheduler_state` field present |
| Deployed SHA | ✓ | `deployed_revision` field present |
| Drift detection | ✗ | Not yet implemented (planned) |
| Backup/restore metrics | ✓ | `backup_state`, `backup_age_seconds`, `prune_status` |
| Storage metrics | ✓ | `database_size_bytes`, `data_directory_size_bytes`, `disk_free_bytes`, `disk_usage_pct` |
| Tests | ✓ | 57/57 passing; health export tests verify v2 output |
| **Conformance** | **Canonical** | Updated to v2 contract. All required fields present. |

**Recommended action:** None — exporter is v2-compatible. Next step: VPS deployment, health collector activation.

---

### SJC Intel

| Criterion | Status | Notes |
|---|---|---|
| Health source | `scripts/health_export.py` | Inert, dry-run mode |
| Health table | `health.health_runs`, `health.workflow_status` | SHARED-003 compliant |
| Canonical field set | ✓ | Same schema as Traderie |
| Exporter exists | ± | Inert, needs activation + v2 update |
| Tests | ✓ | 3 test fixtures, 11 tests |
| **Conformance** | **Canonical-compatible** | Inert — activate when repo is deployed |

**Recommended action:** Update exporter to v2 when SJC Intel deployment begins.

---

### IH Market Companion

| Criterion | Status | Notes |
|---|---|---|
| Health source | `scripts/health_export.py` | Inert, 130 lines |
| Health table | `health.private_status` | Divergent schema |
| Canonical field set | ≡ | Requires adapter: status mapping, field renames |
| Exporter exists | ± | Custom schema, not SHARED-003 or v2 |
| Tests | ✗ | No health export tests |
| **Conformance** | **Adapter-required** | Needs repository-local adapter |

**Recommended action:** Create `scripts/health_adapter.py` that reads `health.private_status` and produces canonical v2 JSON. Keep existing table.

---

### Idle Hacking KB

| Criterion | Status | Notes |
|---|---|---|
| Health source | Live natural-run health output (44 successful exports) | Health endpoint exists but reports incorrectly — treats cumulative historical failure count as current failure |
| Health table | PostgreSQL metadata schema + filesystem generation state | No dedicated health table in PostgreSQL |
| Canonical field set | ± | Health output exists but does not conform to v2 contract — needs adapter for status semantics correction |
| Exporter exists | ± | Health reporting is live but semantically incorrect — cumulative failures treated as current failures |
| Tests | ✗ | No health export tests |
| **Conformance** | **Divergent — live but semantically incorrect** | Needs adapter + failure-semantics correction |

**Recommended action:** Correct the health reporter to distinguish consecutive from cumulative failures per HEALTH_CONTRACT.md §4.8. Then create a repository-local adapter that reads the private health output and produces canonical v2 JSON.

---

### Reckless Ben

| Criterion | Status | Notes |
|---|---|---|
| Health source | `scripts/health_export.py` | Inert, 123 lines |
| Health table | `health.observations` | SHARED-003 compatible |
| Canonical field set | ≡ | Requires adapter: field mapping (freshness as text, etc.) |
| Exporter exists | ± | SHARED-003 compatible, needs v2 update |
| Tests | ± | Fixtures exist |
| **Conformance** | **Adapter-compatible** | Minor adapter needed |

**Recommended action:** Update exporter to v2 when RB deployment is authorized.

---

## Summary

| Repository | Conformance | Exporter | Tests | Next action |
|---|---|---|---|---|
| Reddit Ops | Adapter-compatible | Need to create | Need to create | Implement canonical exporter |
| Traderie | Canonical-compatible | ✓ Existing (update) | ✓ Update | Update exporter fields, test, deploy |
| SJC Intel | Canonical-compatible | ± Inert | ✓ | Activate when deploying |
| IH Market Companion | Adapter-required | ± Divergent | ✗ | Create adapter when deploying |
| Idle Hacking KB | Divergent — live but semantically incorrect | ± (live, wrong semantics) | ✗ | Correct failure semantics; then add adapter |
| Reckless Ben | Adapter-compatible | ± Inert | ± | Update when deployment authorized |
