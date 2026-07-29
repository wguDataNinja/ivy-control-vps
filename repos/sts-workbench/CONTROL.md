---
control_model_version: "1.0"
repository:
  slug: sts-workbench
  purpose: "V1 Palworld Nitewing voice assistant — typed/audio interaction, STT/TTS, evidence/citation browser, OpenCode communication, and Palworld CLI integration."
  remote: null
  default_branch: master
  approved_sha: "9782dfb7093471bc6dc19cc21a912849574228ec"
  local_path: "/Users/buddy/projects/sts-workbench"
  vps_path: null
lifecycle:
  admission_gate: 1
  state: "source-only"
github:
  visibility: null
  publication_gate: 1
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
backup:
  importance: important
  sensitivity: public
  strategy: git_remote
  priority: P4
  exclude_groups:
    - cache
    - virtualenv
    - git_objects
  evidence_max_age_days: 90
health:
  state: unknown
roadmap:
  gates: [1]
  blockers: ["19 dirty tracked files and 3 untracked files pending STS-V1-01 classification and Buddy preservation decision"]
  next_task: "STS-V1-01 — Dirty-State Preservation and Reconciliation"
continuity:
  current_focus: "V1 finish-line completion — dirty-state preservation, lifecycle repair, acceptance, and release packaging."
  recent_milestone: "HITL acceptance in progress (2/8 checklist items); backend 365+p tests, frontend typecheck/unit/build passing (with one backend communication-repair failure)."
  recent_reference: "docs/V1_FINISH_LINE_ROADMAP.md (Buddy-approved 2026-07-27); docs/HITL_ACCEPTANCE_2026-07-24.md"
  long_horizon: "V1 completion for bounded Nitewing voice assistant, then evaluate follow-on scope."
hermes:
  scope: "read-only"
codex_stops:
  - "No runtime or database work possible for a source-only repository"
  - "VPS clone requires separate admission gate"
buddy_decisions:
  - "Approve STS Workbench managed-repository admission — APPROVED 2026-07-29"
  - "Approve STS-V1-01 as H4 supervised-cycle pilot — APPROVED 2026-07-29"
last_verified: "2026-07-29"
evidence_basis: "docs/V1_FINISH_LINE_ROADMAP.md"
---

# STS Workbench — Repository Control

**Purpose:** Active governance authority for STS Workbench within IvyControlVPS.
**Canonical remote:** Not yet published — no GitHub remote configured
**Default branch:** `master`
**Approved SHA:** `9782dfb7093471bc6dc19cc21a912849574228ec`
**Local path:** `/Users/buddy/projects/sts-workbench`
**Lifecycle state:** `source-only` — V1 finish-line admission; no service, DB, or runtime
**Detailed gate evidence:** `repos/sts-workbench/RELEASE_GATES.md` (pending creation)

---

## Portfolio Admission State

| Gate | State | Notes |
|------|-------|-------|
| Gate 1 — Portfolio Admission | PASS | Repository recognized; CONTROL.md created |
| Gate 2 — Public Repository Readiness | NOT APPLICABLE | No GitHub remote configured; publication deferred |
| Gate 3 — GitHub Publication | NOT APPLICABLE | Not published on GitHub |
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
| Git workflow | REQUIRED | PASS WITH CONDITION | Local `master` branch; no remotes; dirty tracked state pending classification |
| Public/private boundary | REQUIRED | PASS WITH CONDITION | `_internal/` excluded via `.gitignore`; publication not yet configured |
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

1. No GitHub remote configured — publication deferred to V1 completion.
2. Default branch is `master` rather than `main` — preserves existing convention.

---

## Hermes Scope

| Action | Permitted | Notes |
|--------|-----------|-------|
| Read-only inspection | YES | Inspect repository, check SHA, verify cleanliness |
| Test execution | YES | Run tests; report results |
| Dirty-state classification | YES | STS-V1-01 pilot: classify paths, record preservation options |
| Branch creation | Requires per-repo Buddy approval | Future gated stage |
| Pull request preparation | Requires per-repo Buddy approval | Future gated stage |
| VPS operations | NO | Not applicable — no runtime |
| Database operations | NO | Not applicable — no database |

**Stop conditions:** Do not stage, commit, reset, stash, or clean Git state. Do not modify `v1/**`, `docs/**`, `HANDOFF.md`, or `TODO.md`. Classification is read-only.

---

## Strong Codex Stop Conditions

None — no runtime or database work is possible for a source-only repository. Codex escalation is available under the standard capability registry for architecture review.

---

## Current Blocker

The STS Workbench checkout has 19 dirty tracked files and 3 untracked files from prior completed work. These must be classified and preserved through an approved non-destructive route (STS-V1-01) before sustained V1 progression can begin.

**Depends on:** H4 supervised-cycle pilot completion and Buddy preservation strategy decision.

---

## Next Authorized Work

1. **Immediate:** STS-V1-01 — Dirty-State Preservation and Reconciliation (H4 supervised-cycle pilot).
2. **After V1-01:** STS-V1-02 — Current Validation and Compatibility Baseline (requires Buddy gate).
3. **After baseline:** STS-V1-03 through STS-V1-08 per `docs/V1_FINISH_LINE_ROADMAP.md`.

---

## Cross-Repository Gate Authority

Gate decisions for STS Workbench are owned by IvyControlVPS and recorded in:

- `repos/sts-workbench/CONTROL.md` — this file
- `repos/sts-workbench/RELEASE_GATES.md` — detailed gate evidence (pending creation)

STS Workbench source code remains at its canonical local path. This repository tracks only governance and admission evidence.
