---
control_model_version: "1.0"
repository:
  slug: wgu-catalog
  purpose: "WGU academic catalog data — canonical degree program, course, and requirement definitions."
  remote: "git@github.com:wguDataNinja/wgu-catalog.git"
  default_branch: main
  approved_sha: "6b27a92d268e99fac5885caa104acb5fcdd3b9d2"
  local_path: "/Users/buddy/projects/wgu-catalog"
  vps_path: null
lifecycle:
  admission_gate: null
  state: "batch"
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
  blockers: ["Not yet admitted — needs source/version/manifest/retention procedure"]
  next_task: "Source/version/manifest/retention procedure; Gate 1 admission packet"
hermes:
  scope: "read-only"
codex_stops:
  - "No VPS runtime, no database, no scheduler"
  - "No service activation without Gate 1 passage"
buddy_decisions: []
last_verified: "2026-07-16"
evidence_basis: "_internal/outbox/session-9/21-live-discovery.md"
---

# WGU Catalog — Repository Control

**Purpose:** Active governance authority for WGU Catalog within IvyControlVPS.
**Canonical remote:** `git@github.com:wguDataNinja/wgu-catalog.git`
**Default branch:** `main`
**Approved SHA:** `6b27a92d268e99fac5885caa104acb5fcdd3b9d2` (local HEAD; not yet published as approved)
**Local path:** `/Users/buddy/projects/wgu-catalog`
**VPS lane:** No VPS runtime discovered.
**Detailed gate evidence:** Not yet created.

---

## Portfolio Admission State

| Gate | State | Notes |
|------|-------|-------|
| 1 — Portfolio Admission | NOT YET ADMITTED | Control record created as part of portfolio batch 2. |
| 2 — Public Repository Readiness | NOT YET ASSESSED | Published on GitHub but not reviewed under admission criteria. |
| 3 — GitHub Publication | NOT YET ASSESSED | |
| 4 — Deployment Readiness | NOT APPLICABLE | Low-frequency batch candidate per report 21. No database or continuous service justified from present evidence. |
| 5 — VPS Deployment | NOT APPLICABLE | No VPS runtime. Source-only VPS clone possible after admission. |
| 6 — Operational Activation | NOT APPLICABLE | No service, timer, or scheduler. |

---

## Applicable Standards Matrix

| Standard | Applicability | Compliance | Notes |
|----------|--------------|------------|-------|
| Git workflow | REQUIRED | NOT YET ASSESSED | |
| Public/private boundary | REQUIRED | NOT YET ASSESSED | |
| Runtime logging | NOT APPLICABLE | PASS | No runtime |
| LLM tenets | NOT APPLICABLE | PASS | No operational LLM stage |
| PostgreSQL naming | NOT APPLICABLE | PASS | No database |
| Backup/restore | NOT APPLICABLE | PASS | No database or runtime state |
| Systemd naming | NOT APPLICABLE | PASS | No services |
| Health contract | NOT APPLICABLE | PASS | No runtime health |
| Repository control model | REQUIRED | PASS | This file created |
| Data lifecycle | NOT YET ASSESSED | UNDEFINED | |

---

## Accepted Deviations

None.

---

## Current Blocker

Not yet admitted. Needs source/version/manifest/retention procedure before Gate 1.

---

## Next Authorized Work

Per report 21 guidance: low-frequency batch candidate. After source/version/manifest/retention procedure:

1. Prepare Gate 1 admission packet.
2. Footprint review.
3. Source-only VPS clone after admission.

---

## Hermes Scope

Hermes may perform read-only inspection: repository structure, file sizes, `.gitignore` compliance. Hermes must not modify files, run workflows, or deploy.

### Stop conditions

Abort on: tracked secrets or credentials found, untracked private data in working tree, evidence of unintended automation.

---

## Cross-Repository Gate Authority

Gate decisions for WGU Catalog are owned by IvyControlVPS and recorded in:

- `repos/wgu-catalog/CONTROL.md` — this file
