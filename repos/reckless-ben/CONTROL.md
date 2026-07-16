---
control_model_version: "1.0"
repository:
  slug: reckless-ben
  purpose: "Reckless Ben — preserved NO_LAUNCH; no admission work."
  remote: null
  default_branch: null
  approved_sha: null
  local_path: null
  vps_path: null
lifecycle:
  admission_gate: null
  state: "restricted"
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
  blockers: ["NO_LAUNCH — restricted; no admission work authorized"]
  next_task: "No admission work; preserved restricted status"
hermes:
  scope: "none"
codex_stops:
  - "Restricted — no inspection, no admission, no VPS work"
  - "NO_LAUNCH preserved"
buddy_decisions:
  - "NO_LAUNCH preserved — APPROVED"
last_verified: "2026-07-16"
evidence_basis: "_internal/outbox/session-9/21-live-discovery.md"
---

# Reckless Ben — Repository Control

**Purpose:** Preserved `NO_LAUNCH` record for Reckless Ben within IvyControlVPS.
**Canonical remote:** UNKNOWN — no remote discovered.
**Default branch:** UNKNOWN
**Approved SHA:** None
**Local path:** UNKNOWN — not found at expected `/Users/buddy/projects/reckless-ben`
**VPS lane:** None
**Detailed gate evidence:** Not yet created.

---

## Portfolio Admission State

| Gate | State | Notes |
|------|-------|-------|
| 1 — Portfolio Admission | NOT YET ADMITTED | Control record created as part of portfolio batch 2. NO_LAUNCH preserved. |
| 2 — Public Repository Readiness | UNKNOWN | No path or remote discovered. |
| 3 — GitHub Publication | UNKNOWN | |
| 4 — Deployment Readiness | NOT APPLICABLE | Restricted — no deployment scope. |
| 5 — VPS Deployment | NOT APPLICABLE | No VPS runtime. |
| 6 — Operational Activation | NOT APPLICABLE | No service, timer, or scheduler. |

---

## Applicable Standards Matrix

| Standard | Applicability | Compliance | Notes |
|----------|--------------|------------|-------|
| Git workflow | NOT YET ASSESSED | UNDEFINED | |
| Public/private boundary | NOT YET ASSESSED | UNDEFINED | |
| Runtime logging | NOT APPLICABLE | PASS | No runtime |
| LLM tenets | NOT APPLICABLE | PASS | No LLM scope |
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

`NO_LAUNCH` — restricted. No admission work authorized until Buddy lifts restriction.

---

## Next Authorized Work

No admission work. Reckless Ben remains restricted per report 21 finding: "no local path discovered at expected location".

---

## Hermes Scope

None — restricted. Hermes may not inspect this repository.

### Stop conditions

Restricted — no inspection, no admission, no VPS work.

---

## Cross-Repository Gate Authority

Gate decisions for Reckless Ben are owned by IvyControlVPS and recorded in:

- `repos/reckless-ben/CONTROL.md` — this file
