---
control_model_version: "1.0"
repository:
  slug: "<repo-slug>"
  purpose: "<one-line-purpose>"
  remote: "<canonical-remote-url>"
  default_branch: "<branch>"
  approved_sha: "<full-commit-sha-or-null>"
  local_path: "<mac-development-path>"
  vps_path: "<vps-checkout-path-or-null>"
lifecycle:
  admission_gate: <1-6-or-null>
  state: "<classification>"
github:
  visibility: "<public|private|null>"
  publication_gate: <1-6-or-null>
  clean_history: <true|false|null>
vps:
  clone_state: "<cloned|not-cloned|pending>"
  runtime_location: "<vps-path-or-null>"
scheduler:
  active: "<systemd-timer-or-other>"
  writer: "<writer-description>"
  legacy: "<description-of-disabled-predecessor>"
database:
  present: <true|false>
  name: "<db-name-or-null>"
  schemas: []
  migrations: "<range-or-null>"
data_locations:
  archive: "<mac-archive-path-or-null>"
  backup: "<vps-backup-path-or-null>"
  source_only: <true|false>
health:
  state: "<healthy|degraded|unknown>"
roadmap:
  gates: []
  blockers: []
  next_task: "<next-authorized-work-reference>"
hermes:
  scope: "<read-only|read-only-with-pr|none>"
codex_stops: []
buddy_decisions: []
last_verified: "<yyyy-mm-dd>"
evidence_basis: "<path-to-gate-evidence>"
---

# <Repository Name> — Repository Control

**Purpose:** Active governance authority for <Repository Name> within IvyControlVPS.

---

## Production Authority

| Component | Current state |
|-----------|---------------|
| Runtime host | Ivy VPS |
| Runtime user | `<user>` |
| Active scheduler | `<systemd-timer>` |
| Active writer | `<writer-description>` |
| Legacy authority | `<description-of-disabled-predecessor>` |
| Production database | PostgreSQL database `<db-name>` on VPS (or `None`) |
| Schemas | `<schema-list>` (or `N/A`) |
| Migrations | `<migration-range>` (or `N/A`) |
| Health | `<health-description>` |
| Backup | `<backup-description>` |

---

## Applicable Standards Matrix

| Standard | Applicability | Compliance | Notes |
|----------|---------------|------------|-------|
| Git workflow | REQUIRED / NOT APPLICABLE / REQUIRED WITH EXCEPTION / NOT YET ASSESSED | PASS / PASS WITH CONDITION / BLOCKED / UNDEFINED | |
| Public/private boundary | | | |
| Runtime logging | | | |
| LLM tenets | | | |
| PostgreSQL naming | | | |
| Backup/restore | | | |
| Systemd naming | | | |
| Health contract | | | |
| Repository control model | | | |
| Data lifecycle | | | |

---

## Current Blocker

<Describe the single current blocker, or "None.">

---

## Next Authorized Work

<Reference to roadmap section or phase packet.>

---

## Cross-Repository Gate Authority

Gate decisions for this repository are owned by IvyControlVPS and recorded in:

- `repos/<repo>/CONTROL.md` — active governance authority
- `repos/<repo>/RELEASE_GATES.md` — detailed gate evidence

---

## Repository-specific notes

<Accepted deviations, known inaccessible targets, unique operational constraints.>

---
