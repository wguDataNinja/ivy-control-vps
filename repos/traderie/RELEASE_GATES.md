# Traderie — Release Gates

**Authority:** IvyControlVPS.
**Active governance authority:** `repos/traderie/CONTROL.md`
**Approved production SHA:** `e5ebd0f6dd41bcb4e1d8a88f272be89b225cfd40`
**Last reconciled:** 2026-07-12

---

## Gate Framework

Each gate produces `PASS`, `PASS WITH CONDITIONS`, `BLOCKED`, or `NOT APPLICABLE`. A later gate cannot pass until earlier required gates have passed. Operational activation remains conditional until scheduled-run, health, backup-freshness, and reboot evidence are complete.

### Mapping to the portfolio 6-gate model

This repository predates the standardized six-gate model (`docs/REPOSITORY_CONTROL_MODEL.md`). Gates 1–5 here correspond to the portfolio Gates 1–5. The portfolio's Gate 6 (Operational Activation) is split into two sub-gates here: **Gate 6 (Scheduler)** and **Gate 7 (Operational Activation)** — both must pass for the portfolio Gate 6 to pass. The `repos/traderie/CONTROL.md` Gate table records the consolidated portfolio state.

---

## 1. Portfolio Admission Gate

**Status: PASS**

Traderie is admitted as a managed deterministic ingestion repository. Canonical remote, local path, portfolio purpose, public/private boundary, and detailed control path are recorded.

---

## 2. Public Repository Readiness Gate

**Status: PASS WITH CONDITIONS**

Publication, tests, CI, `.gitignore`, no-secret posture, generated-data boundaries, and no-license exception were accepted during the original publication path.

**Continuing conditions**

- Public source changes must still pass tests and secret scans.
- No production data, dumps, logs, or private files may enter Git.

---

## 3. GitHub Publication Gate

**Status: PASS**

Traderie has an approved GitHub source path. Later production fixes were published by exact SHA, with current deployed production SHA `e5ebd0f6dd41bcb4e1d8a88f272be89b225cfd40`.

---

## 4. Deployment Readiness Gate

**Status: PASS**

PostgreSQL roles/database, migration validation, deployment docs, systemd source, environment boundary, health tooling, backup tooling, and rollback path are sufficient for VPS deployment.

---

## 5. VPS Deployment Gate

**Status: PASS**

Traderie is deployed on the VPS by exact approved SHA. The checkout, helper pin, deployed revision metadata, systemd unit source, and segmented orchestrator have matched the approved SHA in Session 4 evidence.

---

## 6. Scheduler Gate

**Status: PASS WITH CONDITIONS**

VPS systemd is the sole scheduler and writer. Mac launchd is inactive. `traderie-ingest-snapshot.timer` is enabled and active.

**Condition**

The first genuine natural scheduled generation partially failed when `pc_hc_nl` timed out at 480 seconds. Scheduler authority remains established, but production is degraded until the natural scheduled run completes successfully.

---

## 7. Operational Activation Gate

**Status: BLOCKED**

Operational completion is blocked by:

1. `pc_hc_nl` natural-run timeout root cause unresolved.
2. File-based health export path is empty while DB-backed health records exist; behavior must be reconciled.
3. Backup freshness threshold must be applied to Traderie health/control evidence.
4. One genuine natural scheduled generation must pass with all four segments.
5. Controlled reboot proof must pass after natural-run success.

---

## Current Stop Conditions

- Bounded generation fails.
- Natural scheduled run fails.
- Duplicate scheduler or writer appears.
- Health cannot distinguish DB-backed, file-backed, stale, failed, and backup-stale states.
- Backup freshness exceeds the accepted threshold without explicit incident state.
- Controlled reboot fails to recover timer, service, database, and health.
