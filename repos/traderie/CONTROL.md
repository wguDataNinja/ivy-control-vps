---
control_model_version: "1.0"
repository:
  slug: traderie
  purpose: "Active governance authority for Traderie within IvyControlVPS."
  remote: "git@github.com:wguDataNinja/d2-market-helper.git"
  default_branch: master
  approved_sha: "e5ebd0f6dd41bcb4e1d8a88f272be89b225cfd40"
  local_path: "/Users/buddy/projects/traderie"
  vps_path: "/home/scraper/apps/traderie"
lifecycle:
  admission_gate: 5
  state: "production-runtime"
github:
  visibility: public
  publication_gate: 3
  clean_history: true
vps:
  clone_state: cloned
  runtime_location: "/home/scraper/apps/traderie"
scheduler:
  active: "traderie-ingest-snapshot.timer"
  writer: "VPS systemd service (sole writer)"
  legacy: "Mac launchd — inactive/unloaded for production authority"
database:
  present: true
  name: "traderie"
  schemas: ["app", "archive", "health"]
  migrations: "001-017"
data_locations:
  archive: null
  backup: "/home/scraper/backups/postgres/traderie"
  source_only: false
health:
  state: degraded
roadmap:
  gates: [1, 2, 3, 4, 5]
  blockers: ["pc_hc_nl timeout on 2026-07-16 natural run"]
  next_task: "Session 5 §7A — Traderie production recovery"
hermes:
  scope: "read-only"
codex_stops:
  - "Service unit not found"
  - "Timer inactive/unexpected state"
  - "pc_hc_nl timeout recurrence"
  - "Deployed SHA mismatch"
  - "Disk >85%"
  - "Backup dump missing or zero-size"
  - "Restore validation failure"
  - "Conflicting health run/service state evidence"
buddy_decisions: []
last_verified: "2026-07-16"
evidence_basis: "_internal/outbox/session-9/21-live-discovery.md"
---

# Traderie — Repository Control

**Purpose:** Active governance authority for Traderie within IvyControlVPS.
**Canonical remote:** `github.com/wguDataNinja/d2-market-helper`
**Default branch:** `master`
**Approved production SHA:** `e5ebd0f6dd41bcb4e1d8a88f272be89b225cfd40`
**Local path:** `/Users/buddy/projects/traderie`
**VPS path:** `/home/scraper/apps/traderie`
**Detailed gate evidence:** `repos/traderie/RELEASE_GATES.md`

---

## Portfolio Admission State

| Gate | State | Notes |
|------|-------|-------|
| 1 — Portfolio Admission | PASS | Repository is recognized as managed. Identity, remote, SHA documented. |
| 2 — Public Repository Readiness | PASS | GitHub-published. Secrets cleared from Git history. |
| 3 — GitHub Publication | PASS | Published at approved SHA `e5ebd0f6`. |
| 4 — Deployment Readiness | PASS | VPS PostgreSQL, roles, migrations, backup/restore, systemd units, and scheduler proven. |
| 5 — VPS Deployment | PASS | Bounded one-shot deployment proven; VPS systemd is sole scheduler/writer. |
| 6 — Operational Activation | BLOCKED | First natural scheduled generation partially failed. See Current Blocker. |

---

## Production Authority

| Component | Current state |
|---|---|
| Runtime host | Ivy VPS |
| Runtime user | `scraper` |
| Active scheduler | `traderie-ingest-snapshot.timer` enabled, active, waiting |
| Active writer | VPS systemd service path only |
| Legacy Mac launchd | Inactive/unloaded for production authority |
| Production database | PostgreSQL database `traderie` on VPS |
| Schemas | `app`, `archive`, `health` |
| Migrations | 001-017 applied |
| Health | DB-backed `health.health_runs` exists; file-export path behavior unresolved |
| Backup | Latest known dump: `traderie_20260709T090253Z.dump`; freshness threshold now defined by `docs/HEALTH_CONTRACT.md` default unless repo sets stricter policy |

---

## Applicable Standards Matrix

| Standard | Applicability | Compliance | Notes |
|---|---|---|---|
| Git workflow | REQUIRED | PASS | `master` branch is accepted deviation (see Deviations section). Production deployment uses exact SHA. |
| Public/private boundary | REQUIRED | PASS | Secrets and runtime data remain outside Git. |
| Runtime logging | REQUIRED | PASS WITH CONDITION | Objective progress evidence must include file mtime/size and process state, not only journal silence. |
| LLM tenets | NOT APPLICABLE | PASS | No operational LLM stage. |
| PostgreSQL naming | REQUIRED | PASS | Project database and role model are implemented on VPS. |
| Backup/restore | REQUIRED | PASS WITH CONDITION | Backup and isolated restore were proven; explicit backup freshness threshold has been added. |
| Systemd naming | REQUIRED | PASS | Units are installed from reviewed source. |
| Health contract | REQUIRED | PASS WITH CONDITION | DB health records exist; file-based export behavior must be reconciled. |
| Repository control model | REQUIRED | PASS | This file and `RELEASE_GATES.md` are current authority. |
| Data lifecycle | REQUIRED | PASS WITH CONDITION | Growth and retention evidence continue through stabilization. |

---

## Accepted Deviations

| Deviation | Justification |
|-----------|---------------|
| Default branch `master` instead of `main` | Legacy naming; production deployment uses exact SHA, not branch name. No operational impact. |

---

## Current Blocker

The first genuine natural scheduled generation after segmented cutover partially failed on 2026-07-11 at 18:01:46 UTC. Segments `pc_sc_nl`, `pc_sc_l`, and `pc_hc_l` completed; `pc_hc_nl` reached its 480-second bound and timed out. Overall service exit was `1`.

Do not increase the timeout without direct runtime, retry, volume, latency, and progress evidence.

---

## Next Authorized Phase

Session 5 `§7A` Traderie production recovery:

1. Investigate the `pc_hc_nl` natural-run timeout.
2. Verify DB-backed and file-based health behavior.
3. Confirm or refine backup freshness policy in the repo contract.
4. Apply source correction and tests if required.
5. Publish through git-steward if source changes are made.
6. Strong Codex deploys exact published SHA, proves bounded generation, then proves one genuine natural scheduled generation.
7. Controlled reboot proof occurs only after natural scheduled generation succeeds.

---

## Hermes Scope

Hermes may perform read-only inspection: health run freshness, timer/service status, backup age, deployed SHA drift check, and PostgreSQL connectivity. Hermes must not restart services, modify timers, mutate databases, or deploy code.

### Stop conditions

Abort and escalate to Strong Codex or Buddy on: service unit not found, timer inactive/unexpected state, `pc_hc_nl` timeout recurrence, deployed SHA mismatch, disk >85%, backup dump missing or zero-size, restore validation failure, conflicting evidence between health run and service state.

---

## Cross-Repository Gate Authority

Gate decisions for Traderie are owned by IvyControlVPS and recorded in:

- `repos/traderie/CONTROL.md` — active governance authority
- `repos/traderie/RELEASE_GATES.md` — detailed gate evidence

Traderie-local `STATUS.md`, `SESSION.md`, and `LOG.md` are historical evidence, not current gate authority.
