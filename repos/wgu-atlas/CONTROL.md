---
control_model_version: "1.0"
repository:
  slug: wgu-atlas
  purpose: "WGU Atlas — downstream LLM consumer for WGU program lineage and course analysis."
  remote: "git@github.com:wguDataNinja/wgu-atlas.git"
  default_branch: homepage-redesign
  approved_sha: "d0265926fbea2f8b96a67dfb7e4ae56f792f26b3"
  local_path: "/Users/buddy/projects/wgu-atlas"
  vps_path: null
lifecycle:
  admission_gate: null
  state: "downstream"
github:
  visibility: public
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
  blockers: ["Boundary, configuration/cost, and source-path remediation needed", "Downstream LLM system — hold behind boundary/LLM gates"]
  next_task: "Gate 1 admission — resolve boundary gates"
hermes:
  scope: "none"
codex_stops:
  - "No runtime, no database"
  - "Boundary gates unresolved"
  - "LLM cost and configuration gates unresolved"
buddy_decisions: []
last_verified: "2026-07-16"
evidence_basis: "_internal/outbox/session-9/21-live-discovery.md"
---

# WGU Atlas — Repository Control

**Purpose:** Active governance authority for WGU Atlas within IvyControlVPS.
**Canonical remote:** `git@github.com:wguDataNinja/wgu-atlas.git`
**Default branch:** `homepage-redesign`
**Approved SHA:** `d0265926fbea2f8b96a67dfb7e4ae56f792f26b3` (local HEAD on `homepage-redesign`, ahead 9)
**Local path:** `/Users/buddy/projects/wgu-atlas`
**VPS lane:** None
**Detailed gate evidence:** Not yet created.

---

## Portfolio Admission State

| Gate | State | Notes |
|------|-------|-------|
| 1 — Portfolio Admission | NOT YET ADMITTED | Control record created as part of portfolio batch 2. |
| 2 — Public Repository Readiness | NOT YET ASSESSED | Published on GitHub but not reviewed under admission criteria. |
| 3 — GitHub Publication | NOT YET ASSESSED | |
| 4 — Deployment Readiness | NOT APPLICABLE | Downstream LLM consumer. No service, DB, or scheduler scope. |
| 5 — VPS Deployment | NOT APPLICABLE | No VPS runtime. |
| 6 — Operational Activation | NOT APPLICABLE | No service, timer, or scheduler. |

---

## Applicable Standards Matrix

| Standard | Applicability | Compliance | Notes |
|----------|--------------|------------|-------|
| Git workflow | REQUIRED | NOT YET ASSESSED | |
| Public/private boundary | REQUIRED | NOT YET ASSESSED | |
| Runtime logging | NOT APPLICABLE | PASS | No runtime |
| LLM tenets | REQUIRED | NOT YET ASSESSED | Downstream LLM system — LLM tenets must be evaluated before admission |
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

Boundary, configuration/cost, and source-path remediation needed. Downstream LLM system — hold behind boundary/LLM gates per report 21.

---

## Next Authorized Work

Per report 21: WGU Atlas remains deferred behind boundary, configuration/cost, and source-path remediation gates.

1. Resolve boundary gates and LLM cost/configuration.
2. Prepare Gate 1 admission packet after boundary resolution.

---

## Hermes Scope

None — deferred. Hermes may not inspect this repository until boundary gates are resolved.

### Stop conditions

No Hermes authority until boundary gates pass.

---

## Cross-Repository Gate Authority

Gate decisions for WGU Atlas are owned by IvyControlVPS and recorded in:

- `repos/wgu-atlas/CONTROL.md` — this file
