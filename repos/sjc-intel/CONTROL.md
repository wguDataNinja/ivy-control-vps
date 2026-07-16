---
control_model_version: "1.0"
repository:
  slug: sjc-intel
  purpose: "AI-assisted local intelligence/reporting for St. Johns County, Florida. Discovers, monitors, classifies, verifies, and organizes public information."
  remote: null
  default_branch: master
  approved_sha: "35a0246f530f2ace77d9f93d07ddf78431c31667"
  local_path: "/Users/buddy/projects/sjc_intel"
  vps_path: null
lifecycle:
  admission_gate: 1
  state: "source-only"
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
  gates: [1]
  blockers: ["No remote configured for local checkout"]
  next_task: "Establish canonical remote and publication-readiness review; prepare Gate 4 readiness packet"
hermes:
  scope: "read-only"
codex_stops:
  - "Tracked secrets or credentials found"
  - "Untracked private data in working tree"
  - "Unexpected runtime state (scheduled tasks, daemons)"
  - "Untracked _outbox/ contains unassessed private content"
  - "Data growth exceeds safe bounds"
  - "Evidence of unintended automation"
buddy_decisions: []
last_verified: "2026-07-16"
evidence_basis: "_internal/outbox/session-9/21-live-discovery.md"
---

# SJC Intel — Repository Control

**Purpose:** AI-assisted local intelligence/reporting for St. Johns County, Florida. Discovers, monitors, classifies, verifies, and organizes public information.
**Canonical remote:** UNKNOWN — no remote configured in local checkout.
**Default branch:** `master`
**Approved SHA:** `35a0246f530f2ace77d9f93d07ddf78431c31667` (latest local HEAD; not published)
**Local path:** `/Users/buddy/projects/sjc_intel`
**Detailed gate evidence:** Not yet created. See `repos/sjc-intel/RELEASE_GATES.md` when created.

---

## Portfolio Admission State

| Gate | State | Notes |
|------|-------|-------|
| 1 — Portfolio Admission | NOT YET ADMITTED | Control record created as part of portfolio batch 1. |
| 2 — Public Repository Readiness | UNKNOWN | No remote configured. Cannot assess GitHub readiness. |
| 3 — GitHub Publication | BLOCKED | No remote configured. Not published. |
| 4 — Deployment Readiness | NOT YET ASSESSED | No service, timer, or production runtime. Operator-mode only — no scheduled automation. |
| 5 — VPS Deployment | NOT APPLICABLE | Not admitted to VPS. No deployment scope. |
| 6 — Operational Activation | NOT APPLICABLE | No production runtime to activate. |

---

## Applicable Standards Matrix

| Standard | Applicability | Compliance | Notes |
|---|---|---|---|
| Git workflow | REQUIRED | PASS | Conventional commit prefixes used. Agent Git policy documented in `AGENTS.md`. |
| Public/private boundary | REQUIRED | PASS | `.env.example` present. No tracked secrets identified. Untracked `_outbox/` and `data/` are local-only. |
| Runtime logging | REQUIRED | PASS | Best-in-portfolio three-tier logging model (agent logs, run logs, conversation logs). |
| LLM tenets | NOT APPLICABLE | PASS | Zero LLM imports. All workflows use HTTP fetch + HTML parse + regex. |
| PostgreSQL naming | NOT APPLICABLE | PASS | No PostgreSQL requirement identified. |
| Backup/restore | NOT APPLICABLE | PASS | No database, runtime state, or generated data requiring backup. `data/` contains curated intel items — no backup contract defined. |
| Systemd naming | NOT APPLICABLE | PASS | No systemd units. Operator mode — no scheduled automation. |
| Health contract | NOT APPLICABLE | PASS | No health producer. No scheduled runtime. |
| Repository control model | REQUIRED | PASS | This file is current authority. |
| Data lifecycle | NOT YET ASSESSED | UNDEFINED | `data/intel_items/`, `data/source_events/`, `data/search_runs/` growth not assessed. |

---

## Accepted Deviations

| Deviation | Justification |
|-----------|---------------|
| Default branch `master` instead of `main` | Legacy naming. No operational impact; no publication dependency. |
| No canonical remote configured | Repository is in pre-publication state. Remote must be set before GitHub publication. |

---

## Current Blocker

No remote configured for the local checkout. Repository cannot be published or cloned until a remote is established and a publication-readiness review is completed.

---

## Next Authorized Phase

1. Establish canonical remote and publication-readiness review.
2. Prepare Gate 4 readiness packet: source authority, scheduler/writer boundary, migrations/roles (if applicable), health adapter, backup/restore and rollback packet, exact-SHA/footprint review, and tests.
3. No production cutover without Gate 4/5 packet.

---

## Hermes Scope

Hermes may perform read-only inspection: repository structure, file sizes, source registry health, `.gitignore` compliance, cadence review, monitor spec review. Hermes must not modify files, run workflows, or deploy.

### Stop conditions

Abort on: tracked secrets or credentials found, untracked private data in working tree, unexpected runtime state (scheduled tasks, daemons), untracked `_outbox/` contains unassessed private content, data growth exceeds safe bounds, or any evidence of unintended automation.
