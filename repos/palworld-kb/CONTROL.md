---
control_model_version: "1.0"
repository:
  slug: palworld-kb
  purpose: "Provenance-backed Palworld gameplay knowledge base with human-gated canonical promotion."
  remote: "https://github.com/wguDataNinja/palworld-kb.git"
  default_branch: main
  approved_sha: "1c8d411406ce45cf948390e82f1e8494ca0352b6"
  local_path: "/Users/buddy/projects/palworld-kb"
  vps_path: null
lifecycle:
  admission_gate: 3
  state: "source-only"
github:
  visibility: public
  publication_gate: 3
  clean_history: true
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
backup:
  importance: important
  sensitivity: public
  strategy: git_remote
  priority: P3
  exclude_groups:
    - cache
    - virtualenv
    - git_objects
  evidence_max_age_days: 90
health:
  state: unknown
roadmap:
  gates: [1, 2, 3]
  blockers: []
  next_task: "ROADMAP.md §6F — footprint review, Hermes admission packet, source-only VPS clone"
continuity:
  current_focus: "Workflow remediation and bounded source-only admission preparation; content quality remains the main product work."
  recent_milestone: "Promotion foundation is implemented and a workflow-readiness audit identified remaining lifecycle remediation."
  recent_reference: "Local commit 004e996 and agent-reports/SESSION_JOURNAL.md; review acceptance remains pending."
  long_horizon: "A provenance-backed, agent-ready Palworld knowledge base with human-gated canonical promotion."
hermes:
  scope: "read-only"
codex_stops:
  - "No runtime or database work possible for a source-only repository"
buddy_decisions:
  - "Approve VPS source-only clone timing and path — PENDING"
  - "Authorize Hermes branch/PR creation when that gate is designed — PENDING"
last_verified: "2026-07-16"
evidence_basis: "_internal/outbox/session-9/21-live-discovery.md"
---

# Palworld KB — Repository Control

**Purpose:** Active governance authority for Palworld KB within IvyControlVPS.
**Canonical remote:** `https://github.com/wguDataNinja/palworld-kb.git`
**Default branch:** `main`
**Approved production SHA:** `1c8d411406ce45cf948390e82f1e8494ca0352b6`
**Local path:** `/Users/buddy/projects/palworld-kb`
**Lifecycle state:** `source-only` — source-only admission candidate; no service, DB, or runtime
**Detailed gate evidence:** `repos/palworld-kb/RELEASE_GATES.md`

---

## Portfolio Admission State

| Gate | State | Notes |
|------|-------|-------|
| Gate 1 — Portfolio Admission | PASS | Repository recognized; CONTROL.md created |
| Gate 2 — Public Repository Readiness | PASS | Published; publicly accessible |
| Gate 3 — GitHub Publication | PASS | SHA `1c8d411` published on `main` |
| Gate 4 — Deployment Readiness | NOT APPLICABLE | Source-only repository; no deployment scope |
| Gate 5 — VPS Deployment | NOT APPLICABLE | No VPS runtime; source-only clone possible later |
| Gate 6 — Operational Activation | NOT APPLICABLE | No service, timer, or scheduler |

---

## Production Authority

| Component | State |
|-----------|-------|
| Runtime host | Not applicable — source-only |
| Runtime user | Not applicable |
| Active scheduler | Not applicable |
| Active writer | Not applicable |
| Production database | Not applicable |
| Backup | Not applicable |

---

## Applicable Standards Matrix

| Standard | Applicability | Compliance | Notes |
|----------|--------------|------------|-------|
| Git workflow | REQUIRED | PASS | Published; branch is `main` |
| Public/private boundary | REQUIRED | PASS | No secrets tracked |
| Runtime logging | NOT APPLICABLE | PASS | No runtime |
| LLM tenets | NOT APPLICABLE | PASS | No operational LLM stage |
| PostgreSQL naming | NOT APPLICABLE | PASS | No database |
| Backup/restore | NOT APPLICABLE | PASS | No database |
| Systemd naming | NOT APPLICABLE | PASS | No services |
| Health contract | NOT APPLICABLE | PASS | No runtime health to report |
| Repository control model | REQUIRED | PASS | This file created |
| Data lifecycle | NOT APPLICABLE | PASS | No archived data |

---

## Accepted Deviations

None.

---

## Hermes Scope

| Action | Permitted | Notes |
|--------|-----------|-------|
| Read-only inspection | YES | Inspect repository, check SHA, verify cleanliness |
| Test execution | YES | Run tests; report results |
| Source-size review | YES | Footprint audit for VPS clone suitability |
| Branch creation | Requires per-repo Buddy approval | Future gated stage |
| Pull request preparation | Requires per-repo Buddy approval | Future gated stage |
| VPS operations | NO | Not applicable — no runtime |
| Database operations | NO | Not applicable — no database |

**Stop conditions:** Do not create branches or PRs without Buddy approval. Do not modify tracked content. Do not make claims about deployed state (no runtime).

---

## Strong Codex Stop Conditions

None — no runtime or database work is possible for a source-only repository.

---

## Decisions Requiring Buddy

1. Approve VPS source-only clone timing and path.
2. Authorize Hermes branch/PR creation when that gate is designed.

---

## Current Blocker

None. Palworld KB is published and suitable for source-only admission after footprint review.

---

## Next Authorized Work

Per ROADMAP.md §6F:

1. Footprint review — checkout size, largest tracked files, object history.
2. Hermes admission packet preparation.
3. Source-only VPS clone after admission gate passes.
4. Content development (main workstream — not infrastructure-blocked).

---

## Cross-Repository Gate Authority

Gate decisions for Palworld KB are owned by IvyControlVPS and recorded in:

- `repos/palworld-kb/CONTROL.md` — this file
- `repos/palworld-kb/RELEASE_GATES.md` — detailed gate evidence

Palworld KB source code remains at its canonical remote. This repository tracks only governance and admission evidence.
