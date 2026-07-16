# Conditional Role Applicability Table

**Purpose:** Determine which PostgreSQL roles a project requires based on its
workload type. Mark roles `applies: false` when the condition is not met.

---

## Decision table

| Role | Required when | May be omitted when |
|------|---------------|---------------------|
| `owner` | Any PostgreSQL schema exists | No PostgreSQL database is used |
| `migrator` | Migrations or schema changes are applied | Read-only consumer of another database |
| `writer` | Workload writes database rows | File/export-only batch, static site, or read-only consumer |
| `reader` | Human/reporting queries or local validation need read access | No read-only SQL surface exists |
| `monitor` | Health producer reads DB-backed health or current-state views | Health is file/export-only |
| `backup` | Database backups are required | Non-database workload with manifest/checksum archive |

## Workload type mapping

| Workload type | owner | migrator | writer | reader | monitor | backup | Example |
|---------------|-------|----------|--------|--------|---------|--------|---------|
| Full PostgreSQL app | required | required | required | required | required | required | Traderie, Idle Hacking KB |
| Shared-platform schema | required | required | required | required | required | required | Reddit Ops (per schema) |
| Read-only consumer | N/A | N/A | N/A | required | optional | N/A | Dashboard queries |
| File/export-only batch | N/A | N/A | N/A | N/A | optional | N/A | WGU Catalog |
| File-only with archive | N/A | N/A | N/A | N/A | N/A | N/A | Static site |

## Manifest representation

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
    applies: false
    note: "Read-only consumer of reddit_ops"
  # ...
```

## Validation rule

Every role with `applies: true` must have a positive permission test in the
privilege matrix. Every role with `applies: false` must have a documented
reason in the manifest or CONTROL.md.
