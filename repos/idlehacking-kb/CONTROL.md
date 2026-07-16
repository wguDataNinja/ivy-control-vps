---
control_model_version: "1.0"
repository:
  slug: idlehacking-kb
  purpose: "Idle Hacking knowledge base — chat archive, market metadata, userscript source, and LLM/agent framework."
  remote: "https://github.com/wguDataNinja/idlehacking-kb.git"
  default_branch: main
  approved_sha: "61379d38220d10196661c6ee0e58ecc32521385e"
  local_path: "/Users/buddy/projects/idlehacking_kb"
  vps_path: "/home/scraper/apps/idlehacking-kb-metadata"
lifecycle:
  admission_gate: null
  state: "browser-dependent"
github:
  visibility: public
  publication_gate: null
  clean_history: null
vps:
  clone_state: pending
  runtime_location: "/home/scraper/apps/idlehacking-kb-metadata"
scheduler:
  active: "ih-collector-helper.service (shared with IH Market Companion)"
  writer: "VPS shared helper (collector_helper.py)"
  legacy: null
database:
  present: true
  name: "idlehacking_kb"
  schemas: ["chat", "archive", "provenance", "claims", "qa", "llm", "health"]
  migrations: "001-010"
data_locations:
  archive: null
  backup: null
  source_only: false
health:
  state: degraded
roadmap:
  gates: []
  blockers: ["Privacy/publication and userscript authority gating issues", "IH ownership and acknowledgement decisions UNRESOLVED"]
  next_task: "Resolve IH ownership and acknowledgement decisions"
hermes:
  scope: "read-only"
codex_stops:
  - "Browser profile access or recovery required"
  - "Privacy boundary violation"
  - "Userscript authority unresolved"
  - "Chat archive replay unproven"
  - "Acknowledgement receipt unresolved"
  - "Data size exceeding safe thresholds"
buddy_decisions:
  - "Canonical tracked userscript and acknowledgement destination — PENDING"
  - "IH ownership decision — PENDING"
last_verified: "2026-07-16"
evidence_basis: "_internal/outbox/session-9/21-live-discovery.md"
---

# Idle Hacking KB — Repository Control

**Purpose:** Active governance authority for Idle Hacking KB within IvyControlVPS.
**Canonical remote:** `https://github.com/wguDataNinja/idlehacking-kb.git`
**Default branch:** `main`
**Approved SHA:** `61379d38220d10196661c6ee0e58ecc32521385e` (local HEAD; not yet published as approved)
**Local path:** `/Users/buddy/projects/idlehacking_kb`
**VPS lane:** Metadata checkout at `/home/scraper/apps/idlehacking-kb-metadata`; raw bodies remain protected filesystem/archive material
**Detailed gate evidence:** Not yet created.

---

## Portfolio Admission State

| Gate | State | Notes |
|------|-------|-------|
| 1 — Portfolio Admission | NOT YET ADMITTED | Control record created as part of portfolio batch 2. Identity, remote, SHA documented. |
| 2 — Public Repository Readiness | NOT YET ASSESSED | Privacy/publication and userscript authority remain gating issues. |
| 3 — GitHub Publication | NOT YET ASSESSED | Published on GitHub but not yet reviewed under admission criteria. |
| 4 — Deployment Readiness | NOT YET ASSESSED | Metadata runtime exists on VPS; full admission requires source authority resolution. |
| 5 — VPS Deployment | NOT YET ASSESSED | Metadata checkout present; full deployment not reviewed. |
| 6 — Operational Activation | UNDEFINED | Not assessed. |

---

## Applicable Standards Matrix

| Standard | Applicability | Compliance | Notes |
|----------|--------------|------------|-------|
| Git workflow | REQUIRED | NOT YET ASSESSED | |
| Public/private boundary | REQUIRED | NOT YET ASSESSED | Privacy/publication gates unresolved |
| Runtime logging | REQUIRED | NOT YET ASSESSED | |
| LLM tenets | REQUIRED | NOT YET ASSESSED | KB includes LLM/agent framework |
| PostgreSQL naming | REQUIRED | NOT YET ASSESSED | Database `idlehacking_kb` exists on VPS |
| Backup/restore | REQUIRED | NOT YET ASSESSED | |
| Systemd naming | REQUIRED | NOT YET ASSESSED | |
| Health contract | REQUIRED | NOT YET ASSESSED | |
| Repository control model | REQUIRED | PASS | This file created |
| Data lifecycle | REQUIRED | NOT YET ASSESSED | 139 GB local; requires retention plan |

---

## IH Ownership and Acknowledgement

**UNRESOLVED — pending Buddy decision.**

Chat health reports `indexeddb_write_failure` with pending archive acknowledgement. Market capture reports OK but acknowledgement, replay, archive freshness, and PostgreSQL reconciliation are unproven. IH source ownership and the canonical tracked userscript remain undecided. See `repos/ih-market-companion/CONTROL.md` for the companion decision.

---

## Current Blocker

Privacy/publication and userscript authority remain gating issues. IH ownership and acknowledgement decisions are unresolved.

---

## Next Authorized Work

1. Buddy decides IH ownership and acknowledgement destination.
2. Resolve privacy/publication gates.
3. Resolve canonical userscript source authority (linked with IH Market Companion).
4. Prepare Gate 1 admission packet.

---

## Hermes Scope

Hermes may perform read-only inspection: metadata checkout state, database schema check, file sizes, source registry health. Hermes must not modify files, access Chrome/Tampermonkey profile, run collectors, or deploy.

### Stop conditions

Abort on: browser profile access required, privacy boundary violation, untracked private data in working tree, data growth exceeding safe bounds, evidence of unintended automation.

---

## Cross-Repository Gate Authority

Gate decisions for Idle Hacking KB are owned by IvyControlVPS and recorded in:

- `repos/idlehacking-kb/CONTROL.md` — active governance authority
- `repos/ih-market-companion/CONTROL.md` — companion authority for IH-wide decisions
