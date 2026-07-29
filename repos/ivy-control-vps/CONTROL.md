---
control_model_version: "1.0"
repository:
  slug: ivy-control-vps
  purpose: "Portfolio control plane for repository governance, evidence, continuity, and bounded agent coordination."
  remote: "https://github.com/wguDataNinja/ivy-control-vps.git"
  default_branch: main
  approved_sha: "12ca8c22d9d5078828c50b25981b2d4cda4fd73a"
  local_path: null
  vps_path: "/home/scraper/apps/ivy-control-vps"
lifecycle:
  admission_gate: 3
  state: "admitted"
github:
  visibility: public
  publication_gate: 3
  clean_history: null
vps:
  clone_state: cloned
  runtime_location: "/home/scraper/apps/ivy-control-vps"
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
  gates: [1, 2, 3]
  blockers: ["H4 supervised-cycle pilot (STS-V1-01) in progress — pending Buddy preservation decision"]
  next_task: "Session 14: execute H4 STS-V1-01 supervised-cycle pilot on STS Workbench"
continuity:
  current_focus: "VPS engineering-workspace residency and bounded Hermes orchestration foundations."
  recent_milestone: "Clean public VPS workspace refreshed to the approved published SHA without private material."
  recent_reference: "docs/VPS_INVENTORY.md"
  long_horizon: "A trustworthy portfolio control plane that helps humans and agents operate independent repositories safely."
hermes:
  scope: "read-only"
  artifact_paths:
    - "agent/reports/"
    - "logs/"
codex_stops:
  - "Do not treat the engineering workspace as production activation."
  - "Do not transfer _internal, credentials, private evidence, or raw agent material to the VPS checkout."
  - "Do not grant branch, PR, deployment, service, database, or credential authority without a separate approved gate."
buddy_decisions:
  - "Approve per-repository Hermes artifact-only or branch/PR scope — PENDING"
last_verified: "2026-07-29"
evidence_basis: "docs/VPS_INVENTORY.md"
---

# Ivy Control VPS — Repository Control

**Purpose:** Active governance authority for the portfolio control plane itself.
**Canonical remote:** `https://github.com/wguDataNinja/ivy-control-vps.git`
**Default branch:** `main`
**Approved SHA:** `12ca8c22d9d5078828c50b25981b2d4cda4fd73a`
**VPS engineering workspace:** `/home/scraper/apps/ivy-control-vps`

## Portfolio Admission State

| Gate | State | Notes |
|---|---|---|
| Gate 1 — Portfolio Admission | PASS | Control plane is a managed portfolio asset. |
| Gate 2 — Public Repository Readiness | PASS WITH CONDITION | The resident workspace excludes the obsolete tracked root `TODO.md`; broader public cleanup/publishing remains pending. |
| Gate 3 — GitHub Publication | PASS | Merged at `12ca8c2`. Approved head `f847045` is second parent. Full Gate 3 procedure formalized in `docs/GIT_WORKFLOW.md`. |
| Gate 4 — Deployment Readiness | NOT APPLICABLE | Engineering workspace only; no runtime or authority transfer. |
| Gate 5 — VPS Deployment | NOT APPLICABLE | Workspace residency is not service deployment. |
| Gate 6 — Operational Activation | NOT APPLICABLE | No service, timer, database, or production writer. |

## Workspace Boundary

The VPS copy is a clean public engineering workspace. It may support
inspection, status generation, and later explicitly delegated branch work. It
does not contain `_internal/`, credentials, private prompts/evidence, runtime
data, or a production service. Its obsolete tracked root `TODO.md` is
deliberately omitted through a sparse profile rather than replaced with private
planning. The checkout is disposable and recoverable from the approved SHA;
disabling the sparse profile restores the full tracked tree.

## Hermes Scope

Hermes is currently **read-only** for this repository. The global Mode 0
artifact-only contract does not itself grant a target repository scope. A
separate reviewed delegation envelope is required before Hermes creates any
workflow artifact, and branch/PR authority remains a later gate.

## Current Blocker

The H4 supervised-cycle pilot (STS-V1-01 — Dirty-State Preservation and Reconciliation) is in progress. Hermes is executing the first bounded supervised cycle on STS Workbench under the Alori harness framework. Completion requires Buddy preservation strategy decision after the result report.

## Next Authorized Work

1. **Immediate:** Execute STS-V1-01 dirty-state classification on STS Workbench via isolated worktree. Maker: OpenCode. Checker: Hermes.
2. **After H4 completion:** Progression through STS-V1-02 through STS-V1-08 per `docs/V1_FINISH_LINE_ROADMAP.md` (each requires separate Buddy gate).
3. **After STS V1 completion:** Evidence-backed capability demonstration for broader autonomous orchestration.
