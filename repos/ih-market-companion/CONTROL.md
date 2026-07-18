---
control_model_version: "1.0"
repository:
  slug: ih-market-companion
  purpose: "Public market site, VPS/cloud collector, market publishing, health checks, and ecosystem docs for IdleHacker."
  remote: "https://github.com/wguDataNinja/ih-market-companion.git"
  default_branch: main
  approved_sha: "ae50fd47b49c13016a98034677e16151b337c871"
  local_path: "/Users/buddy/projects/ih_market_companion"
  vps_path: null
lifecycle:
  admission_gate: null
  state: "browser-dependent"
github:
  visibility: public
  publication_gate: 3
  clean_history: true
vps:
  clone_state: not-cloned
  runtime_location: "/home/scraper/vps_helper/collector_helper.py"
scheduler:
  active: "ih-collector-helper.service"
  writer: "VPS systemd service (shared helper — collector_helper.py)"
  legacy: null
database:
  present: false
  name: null
  schemas: []
  migrations: null
data_locations:
  archive: null
  backup: null
  source_only: false
backup:
  importance: important
  sensitivity: private
  strategy: file_archive
  priority: P1
  include_groups:
    - private_state
  exclude_groups:
    - cache
    - virtualenv
    - build_output
    - git_objects
  evidence_max_age_days: 60
health:
  state: unknown
roadmap:
  gates: [1]
  blockers: ["Userscript source authority unresolved (pending Buddy decision)"]
  next_task: "Buddy decides canonical userscript source; resolve acknowledgement destination and archive authority"
continuity:
  current_focus: "Resolve the canonical userscript, acknowledgement destination, and archive authority before market durability work."
  recent_milestone: "Bounded collector manifest metadata was added; public market-site and private collection boundaries remain separate."
  recent_reference: "Local commit ae50fd47; use the public README health checks only within their documented limits."
  long_horizon: "A trustworthy public Idle Hacking market companion backed by explicit source, freshness, and archive contracts."
hermes:
  scope: "read-only"
codex_stops:
  - "Tracked secrets or credentials found"
  - "Browser profile paths exposed"
  - "Untracked private data in working tree"
  - "_internal/ not properly git-ignored"
  - "Health adapter returning raw exception messages"
  - "Evidence of unintended automation"
buddy_decisions:
  - "Canonical userscript source (Option A — IH Market Companion, or alternative) — PENDING"
  - "IH acknowledgement destination and archive authority — PENDING"
  - "IH ownership decision — PENDING"
last_verified: "2026-07-16"
evidence_basis: "_internal/outbox/session-9/21-live-discovery.md"
---

# IH Market Companion — Repository Control

**Purpose:** Public market site, VPS/cloud collector, market publishing, health checks, and ecosystem docs for IdleHacker.
**Canonical remote:** `github.com/wguDataNinja/ih-market-companion`
**Default branch:** `main`
**Approved SHA:** `ae50fd47b49c13016a98034677e16151b337c871` (published — bounded collector manifest metadata)
**Local path:** `/Users/buddy/projects/ih_market_companion`
**VPS lane:** Collector helper deployed on `ih-market-vps`; shared-helper normalization pending.
**Detailed gate evidence:** Not yet created. See `repos/ih-market-companion/RELEASE_GATES.md` when created.

---

## Portfolio Admission State

| Gate | State | Notes |
|------|-------|-------|
| 1 — Portfolio Admission | NOT YET ADMITTED | Control record created as part of portfolio batch 1. |
| 2 — Public Repository Readiness | PASS | GitHub-published. Public-only content. `.env.example` present. |
| 3 — GitHub Publication | PASS | Published at SHA `ae50fd47`. |
| 4 — Deployment Readiness | NOT YET ASSESSED | Collector helper deployed on VPS as transitional shared-helper; not yet reviewed under Gate 4 standards. Canonical Ingestion-Admission subgate evidence absent. |
| 5 — VPS Deployment | NOT YET ASSESSED | Collector helper is running on VPS as transitional arrangement. Not reviewed under Gate 5. |
| 6 — Operational Activation | UNDEFINED | Not assessed. Scheduler activation would require Buddy approval. |

---

## Applicable Standards Matrix

| Standard | Applicability | Compliance | Notes |
|---|---|---|---|
| Git workflow | REQUIRED | PASS | Conventional commits. Clean published history. |
| Public/private boundary | REQUIRED | PASS WITH CONDITION | Public content only in tracked files. `_internal/` contains private trading scripts (git-ignored). `.env.example` present. |
| Runtime logging | REQUIRED | PASS | Collector helper logs to systemd journal. No gap identified. |
| LLM tenets | NOT APPLICABLE | PASS | Zero LLM imports. All execution paths deterministic. `prompts/` are planning artifacts — no runtime consumption. |
| PostgreSQL naming | NOT APPLICABLE | PASS | No production PostgreSQL authority established. Proposal exists but not deployed. |
| Backup/restore | NOT APPLICABLE | PASS | No database or runtime state requiring backup. Mac archives verified but not VPS scope. |
| Systemd naming | REQUIRED | NOT YET ASSESSED | Collector helper uses shared-helper service name; normalization pending. |
| Health contract | REQUIRED | PASS WITH CONDITION | Health adapters created (G2). `deployed_revision` unresolved. Source authority unresolved. |
| Repository control model | REQUIRED | PASS | This file is current authority. |
| Data lifecycle | NOT YET ASSESSED | UNDEFINED | Bounded snapshot/receipt retention deployed. Growth thresholds not formally documented. |

---

## Accepted Deviations

| Deviation | Justification |
|-----------|---------------|
| `_internal/` git-ignored with private trading scripts | Trading-agent infrastructure is private by nature. `.gitignore` blocks `_internal/*`. Approved by AGENTS.md policy. |

---

## Userscript Source Authority

**UNRESOLVED — pending Buddy decision.**

The Wave 1 investigation (G3) recommends IH Market Companion (`_internal/scripts/idle_hacking_collector.js`) as the single tracked canonical userscript source, with the Idle Hacking KB copy becoming a provenance mirror. This recommendation is **NOT yet approved**. Until Buddy decides:

- The tracked source in `idlehacking_kb/` remains the de facto tracked copy (committed at SHA `5ea49eb`).
- The IH Market Companion copy remains git-ignored.
- `deployed_revision` in health output must be `None` (unresolved).
- No deployment drift claim can be made from either copy.

---

## Current Blocker

Userscript source authority unresolved (pending Buddy decision). Health adapter `deployed_revision` cannot be populated until source authority and deployment drift detection are resolved.

---

## Next Authorized Phase

1. Buddy decides canonical userscript source (Option A — IH Market Companion, or alternative).
2. After decision: implement tracked canonical path, update `.gitignore`, add provenance header to KB mirror copy.
3. Resolve acknowledgement destination and archive authority.
4. Prepare idempotent PostgreSQL import/reconciliation pilot.
5. Source-only VPS clone after footprint review.

---

## Hermes Scope

Hermes may perform read-only inspection: repository structure, file sizes, `.gitignore` compliance, health adapter output format, public market data freshness, GitHub Pages deployment status. Hermes must not modify files, run collectors, access VPS, or deploy.

### Stop conditions

Abort on: tracked secrets or credentials found, browser profile paths exposed, untracked private data in working tree, `_internal/` not properly git-ignored, health adapter returning raw exception messages, or any evidence of unintended automation.
