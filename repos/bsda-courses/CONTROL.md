---
control_model_version: "1.0"
repository:
  slug: bsda-courses
  purpose: "BSDA course data — program definitions, course lineage, and comparison artifacts for WGU BSDA degree."
  remote: null
  default_branch: null
  approved_sha: null
  local_path: null
  vps_path: null
lifecycle:
  admission_gate: null
  state: "downstream"
github:
  visibility: null
  publication_gate: null
  clean_history: null
vps:
  clone_state: not-cloned
  runtime_location: null
scheduler:
  active: null
  writer: null
  legacy: null
database:
  present: false
  name: null
  schemas: []
  migrations: null
data_locations:
  archive: null
  backup: null
  source_only: true
health:
  state: unknown
roadmap:
  gates: []
  blockers: ["Boundary, configuration/cost, and source-path remediation needed", "Local path not found at expected /Users/buddy/projects/bsda-courses"]
  next_task: "Gate 1 admission — resolve path, remote, and boundary gates"
hermes:
  scope: "none"
codex_stops:
  - "No runtime, no database, path undiscovered"
  - "Boundary gates unresolved"
  - "Do not invent path or remote"
buddy_decisions: []
last_verified: "2026-07-16"
evidence_basis: "_internal/outbox/session-9/21-live-discovery.md"
---

# BSDA Courses — Repository Control

**Purpose:** Active governance authority for BSDA Courses within IvyControlVPS.
**Canonical remote:** UNKNOWN — no remote discovered.
**Default branch:** UNKNOWN
**Approved SHA:** None
**Local path:** UNKNOWN — not found at expected `/Users/buddy/projects/bsda-courses`
**VPS lane:** None
**Detailed gate evidence:** Not yet created.

---

## Portfolio Admission State

| Gate | State | Notes |
|------|-------|-------|
| 1 — Portfolio Admission | NOT YET ADMITTED | Control record created as part of portfolio batch 2. |
| 2 — Public Repository Readiness | UNKNOWN | No path or remote discovered. |
| 3 — GitHub Publication | UNKNOWN | |
| 4 — Deployment Readiness | NOT APPLICABLE | No deployment scope. |
| 5 — VPS Deployment | NOT APPLICABLE | No VPS runtime. |
| 6 — Operational Activation | NOT APPLICABLE | No service, timer, or scheduler. |

---

## Applicable Standards Matrix

| Standard | Applicability | Compliance | Notes |
|----------|--------------|------------|-------|
| Git workflow | NOT YET ASSESSED | UNDEFINED | |
| Public/private boundary | NOT YET ASSESSED | UNDEFINED | |
| Runtime logging | NOT APPLICABLE | PASS | No runtime |
| LLM tenets | NOT YET ASSESSED | UNDEFINED | Likely downstream LLM consumer — requires boundary gate |
| PostgreSQL naming | NOT APPLICABLE | PASS | No database |
| Backup/restore | NOT APPLICABLE | PASS | No runtime state |
| Systemd naming | NOT APPLICABLE | PASS | No services |
| Health contract | NOT APPLICABLE | PASS | No runtime health |
| Repository control model | REQUIRED | PASS | This file created |
| Data lifecycle | NOT APPLICABLE | PASS | No data |

---

## Accepted Deviations

None.

---

## Current Blocker

Local path not found at expected location `/Users/buddy/projects/bsda-courses`. Boundary, configuration/cost, and source-path remediation needed before Gate 1. Deferred downstream LLM system per report 21.

---

## Next Authorized Work

Per report 21: BSDA Courses remains deferred behind boundary, configuration/cost, and source-path remediation gates.

1. Resolve source path and remote.
2. Prepare Gate 1 admission packet after path is established.

---

## Hermes Scope

None — deferred. Hermes may not inspect this repository until boundary gates are resolved.

### Stop conditions

No Hermes authority until boundary gates pass.

---

## Cross-Repository Gate Authority

Gate decisions for BSDA Courses are owned by IvyControlVPS and recorded in:

- `repos/bsda-courses/CONTROL.md` — this file
