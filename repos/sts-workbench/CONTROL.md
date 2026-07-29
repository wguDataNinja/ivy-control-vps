---
control_model_version: "1.0"
repository:
  slug: sts-workbench
  purpose: "V1 Palworld Nitewing voice assistant — typed/audio interaction, STT/TTS, evidence/citation browser, OpenCode communication, and Palworld CLI integration."
  remote: null
  default_branch: master
  approved_sha: "d60c3d51b5cb76ff8b011da5a348be3ba96da1d2"
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
  blockers: ["H4.1 custody pilot in progress — bounded local-commit validation on STS Workbench. STS-V1-02 pending Buddy deferral decision."]
  next_task: "H4.1 custody pilot: validate supervised local git commit on V1_FINISH_LINE_ROADMAP.md"
continuity:
  current_focus: "V1 finish-line completion — STS-V1-02 validation baseline, lifecycle repair, acceptance, and release packaging."
  recent_milestone: "STS-V1-01 complete: 19 dirty paths preserved at d60c3d5. H4 supervised-cycle pilot proven (maker/checker cycle). Backend 363p/2f/1s, frontend typecheck/unit/build passing."
  recent_reference: "docs/V1_FINISH_LINE_ROADMAP.md; ivy-control-vps _internal/outbox/runs/session-14-sts-h4/"
  long_horizon: "V1 completion for bounded Nitewing voice assistant, then evaluate follow-on scope."
hermes:
  scope: "read-only"
git_custody:
  inspect: true
  local_commit: true
  push_branch: false
  create_pr: false
  merge: false
  update_approved_sha: false
  protected_paths:
    - "_internal/**"
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
**Approved SHA:** `d60c3d51b5cb76ff8b011da5a348be3ba96da1d2`
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
| Git workflow | REQUIRED | PASS WITH CONDITION | Local `master` branch; no remotes; STS-V1-01 preserved at approved SHA `d60c3d5` |
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
| Local commit (via custody) | YES | H4.1 custody pilot: one bounded dispatch with accepted manifest. `local_commit: true` enabled for STS. |
| Branch creation | Requires per-repo Buddy approval | Future gated stage |
| Pull request preparation | Requires per-repo Buddy approval | Future gated stage |
| VPS operations | NO | Not applicable — no runtime |
| Database operations | NO | Not applicable — no database |

**Stop conditions:** Do not stage, commit (outside custody pilot), reset, stash, or clean Git state. Do not modify `v1/**`, `docs/**`, `HANDOFF.md`, or `TODO.md`. Classification is read-only. Custody pilot limited to one accepted manifest, no remote, no push, no PR, no merge.

---

## Strong Codex Stop Conditions

None — no runtime or database work is possible for a source-only repository. Codex escalation is available under the standard capability registry for architecture review.

---

## Current Blocker

STS-V1-01 complete — all 19 dirty paths classified as completed V1 work and preserved at `d60c3d5`. Pre-existing conditions:
- Backend: 2 Whisper-adapter test failures (environment-dependent fixture issue)
- Contract validator exits 1 (36 "Other errs" — schema fixture behavior)
These were not introduced by the preservation commit.

**Next:** STS-V1-02 — Current Validation and Compatibility Baseline requires Buddy gate for deferral or fix decisions on pre-existing failures.

---

## Next Authorized Work

1. **Immediate:** H4.1 custody pilot — one bounded local commit via supervised custody cycle (update V1_FINISH_LINE_ROADMAP.md to mark STS-V1-01 complete).
2. **After H4.1:** STS-V1-02 — Current Validation and Compatibility Baseline (requires Buddy gate for pre-existing failure deferrals).
3. **After baseline:** STS-V1-03 through STS-V1-08 per `docs/V1_FINISH_LINE_ROADMAP.md`.

---

## Cross-Repository Gate Authority

Gate decisions for STS Workbench are owned by IvyControlVPS and recorded in:

- `repos/sts-workbench/CONTROL.md` — this file
- `repos/sts-workbench/RELEASE_GATES.md` — detailed gate evidence (pending creation)

STS Workbench source code remains at its canonical local path. This repository tracks only governance and admission evidence.
