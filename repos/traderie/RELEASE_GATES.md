# Traderie — Release Gates

**Authority:** ivy-control-vps — this file is the single source of gate decisions for Traderie.
**Approved SHA:** `b3b70a01426694d06d6c07a09f0c33427f530f0d`
**Date:** 2026-07-07

---

## Gate framework

Each gate produces `PASS`, `PASS WITH CONDITIONS`, `BLOCKED`, or `NOT APPLICABLE`. Gates are sequential: a later gate cannot pass until the previous gate has passed. A passing gate does not automatically invoke the next — each requires explicit Buddy dispatch.

---

## 1. Portfolio Admission Gate

**Status: ✅ PASS**

Determines whether Traderie is recognized as a managed repository in the ivy-control-vps portfolio.

| Criterion | Result | Evidence |
|-----------|--------|----------|
| STATUS.md exists in `repos/traderie/` | ✅ PASS | `ivy-control-vps/repos/traderie/STATUS.md` |
| Canonical remote registered | ✅ PASS | `github.com/wguDataNinja/d2-market-helper` |
| Local path known | ✅ PASS | `/Users/buddy/projects/traderie` |
| Repo classification recorded | ✅ PASS | active-dev (implicit — has code, docs, tests, CI) |
| Initial phase/gate/blocker recorded | ✅ PASS | STATUS.md §Phase, §Gates, §Known blockers |

**Conditions:** None.

---

## 2. Public Repository Readiness Gate

**Status: ✅ PASS WITH CONDITIONS**

Determines whether the repository is safe and coherent for public publication on GitHub.

| Criterion | Standard | Traderie evidence | Result |
|-----------|----------|-------------------|--------|
| Public/private boundary | No secrets, no internal paths in tracked files. `.gitignore` covers `.env`, keys, secrets. | `.gitignore` covers `.env`, `*.har`, `logs/`, `runtime/`, private data paths, local workspace files. No `.env` tracked. | **PASS** |
| Secrets in history | `git log --all -S` scan clean | CI workflow includes `! git grep -l 'password\s*='` check. No secret file history found. | **PASS** |
| No `.db`/`.sqlite` files | No committed database files | Zero `.db`, `.sqlite`, `.sqlite3` files exist in repo. | **PASS** |
| No large tracked files (>10 MB) | No files exceed 10 MB | CI checks for >10 MB files. None found. | **PASS** |
| README describes purpose, status, usage | README exists and is current | `README.md` — scope, current state (Phase A), validation commands, deployment note. | **PASS** |
| AGENTS.md is current | AGENTS.md exists and routes work | `AGENTS.md` — 35 lines, routes to worker/git-steward/roadmap-planner/task-reviewer/agent-manager. | **PASS** |
| License | MUST NOT be missing without documentation | No license. **DOCUMENTED EXCEPTION** — README line 52: "No license is granted at this time." Accepted decision per SESSION.md. | **PASS WITH CONDITIONS** |
| No generated/runtime data tracked | `data/raw/`, `data/history/`, `data/snapshots/`, `logs/` gitignored | All correctly gitignored. Product JSONs in `data/products/` are intentionally tracked source artifacts. | **PASS** |
| CI present | GitHub Actions or equivalent | `.github/workflows/ci.yml` — syntax check, tests, migration order, secret scan, large file check. | **PASS** |
| Fresh-clone reproducible | `pip install -r requirements.txt && pytest` works | Verified at `b3b70a0` — 57/57 tests pass, `collection_status.py --json` succeeds. | **PASS** |
| No internal `/Users/buddy/` paths | No local filesystem paths in tracked code | Env vars parameterize paths. No hardcoded local paths in committed source. | **PASS** |

**Conditions:**
1. No license — documented in README. Accepted.
2. Set `TRADERIE_SCHEMA_VERSION` in `deploy/env.example` from 9 to 17 (not a publication blocker, deploy config is future).

---

## 3. GitHub Publication Gate

**Status: ✅ PASS**

Confirms the exact published commit reached the canonical remote successfully.

| Criterion | Result | Evidence |
|-----------|--------|----------|
| Remote URL matches canonical | ✅ PASS | `git@github.com:wguDataNinja/d2-market-helper.git` |
| Pushed commit exists on remote | ✅ PASS | `b3b70a0` at `origin/master`, `git ls-remote origin HEAD` confirms |
| Fresh clone compiles and tests pass | ✅ PASS | Verified at push time — `pip install`, `pytest`, `collection_status.py --json` all pass |
| Published author identity correct | ✅ PASS | All commits authored `wguDataNinja <jowe160@wgu.edu>` |
| Push auth identity matches owner | ✅ PASS | `ssh -T git@github.com` returns `Hi wguDataNinja!` |
| No private material in published commit | ✅ PASS | Diff reviewed before push. No `_internal/`, `.env`, keys, or secrets. |

**Retrospective finding: The original Traderie GitHub push was justified.** At the time of publication, the repo had passed the tests, secret scans, fresh-clone proof, and pre-push backup. Publication Gate standards were not yet formally documented, but the ad hoc review satisfied the same criteria. No conditions were violated.

---

## 4. Deployment Readiness Gate

**Status: ⛔ BLOCKED**

Determines whether Traderie can be deployed to a VPS. Does not authorize deployment — only confirms readiness.

| Criterion | Standard | Traderie evidence | Result |
|-----------|----------|-------------------|--------|
| VPS Capacity Gate | PASS before any deployment | **FAILED** — 91% disk (3.3 GB free), no passwordless sudo, no PostgreSQL. | **BLOCKED** |
| Exact SHA recorded | Approved SHA documented | `b3b70a0` recorded in this file. | **PASS** |
| Systemd units defined | Units follow naming convention | 6 service/timer pairs under `deploy/systemd/`. Names follow `{project}-{role}-{action}`. | **PASS** |
| Wrapper scripts exist | All referenced scripts present | `run_traderie_snapshot.sh`, `run_traderie_backup.sh`, `run_traderie_validate.sh`, `regenerate_products.sh` all present. | **PASS** |
| Environment template exists | `deploy/env.example` | Present, documents all required env vars, no secrets. | **PASS** |
| Rollback plan | Documented | `deploy/ROLLBACK.md` — 9 sections covering service disable, revert, unit removal, env restore, data recovery. | **PASS** |
| Backup/restore procedure | Documented | `docs/backup-restore.md` present. Pre-push backup evidenced. | **PASS** |
| Retention policy | Documented | `docs/retention.md` present — 5 retention classes, cadence, Gates. | **PASS** |
| Health export defined | Script exists, schema documented | `scripts/traderie_health_export.py` with `--pg` and file modes. Health schema at `health.health_runs`, `health.workflow_status`. | **PASS** |
| PostgreSQL adapter available | Real adapter or documented fallback | `scripts/traderie_pg_adapter.py` — env-gated real PG, defaults to file fallback. | **PASS** |
| Deploy docs reference current ivy-control-vps paths | No stale `ivy-control/vps/` references | `deploy/README.md` references `ivy-control/vps/worker-control/reports/` paths (historical). Should reference `ivy-control-vps/docs/PORTFOLIO_CONVENTIONS.md`. | **PASS WITH CONDITIONS** |
| Configuration/env contract documented | Env var names, defaults, secrets policy | `deploy/env.example` covers all vars. `TRADERIE_SCHEMA_VERSION=9` is stale (should be 17). VPS-specific values use placeholder paths. | **PASS WITH CONDITIONS** |

**Conditions:**
1. VPS Capacity Gate must pass before deployment can proceed.
2. `deploy/README.md` stale path references should be updated from `ivy-control/vps/` to `ivy-control-vps/docs/PORTFOLIO_CONVENTIONS.md`.
3. `deploy/env.example` `TRADERIE_SCHEMA_VERSION` should be updated from 9 to 17, and `TRADERIE_MIGRATION_VERSION` should be updated to `20260706_017_grant_reader_health_select`.
4. Deploy docs reference architecture documents in old `ivy-control/vps/` — these should point to `docs/PORTFOLIO_CONVENTIONS.md` where promoted or noted as historical where not.

**Blocking gap:** VPS Capacity Gate.

---

## 5. VPS Deployment Gate

**Status: ⛔ BLOCKED**

Authorizes the bounded Phase B deployment proof. Not reached because Deployment Readiness Gate is BLOCKED.

| Criterion | Standard | Traderie | Result |
|-----------|----------|----------|--------|
| VPS Capacity Gate | ✅ PASS | ❌ FAIL | **BLOCKED** |
| Exact SHA verified on remote | ✅ PASS | `b3b70a0` confirmed | **PASS** |
| Pre-deployment backup/restore | Fresh backup + restore drill | Must be run immediately before deployment | **NOT YET RUN** |
| Scheduler Gate bypass | Not required for one-shot proof | Deployment proof is bounded — no timers enabled | **NOT APPLICABLE** |
| Services/timers remain disabled | No timer enabled during proof | Per Phase B packet requirements | **PLANNED** |
| Rollback proven | `deploy/ROLLBACK.md` executable | Plan exists, not executed on VPS | **NOT YET PROVEN** |
| Health export verified | Sanitized, no private data | Script exists, verified locally | **PASS** |

---

## 6. Operational Activation Gate

**Status: 🔲 NOT APPLICABLE**

Authorizes continuous collection and production authority transfer. Cannot be reached until VPS Deployment Gate passes and a stabilization period completes.

---

## Accepted repository-specific deviations

| Standard | Traderie deviation | Rationale | Authority |
|----------|-------------------|-----------|-----------|
| PORTFOLIO_CONVENTIONS.md systemd action verbs | Uses 6 verbs (ingest, process, validate, check, backup, retain) — all in approved list | Compliant | — |
| PORTFOLIO_CONVENTIONS.md | No license | Documented in README. Not a portfolio requirement — decision is per-repo. | Buddy (SESSION.md) |
| PORTFOLIO_CONVENTIONS.md restore proof requires `LOG.md` entry | Traderie uses its own logging conventions | Traderie AGENTS.md defines orchestrator-owned files. LOG.md is present but not required by ivy-control-vps. | Portfolio conventions §5: "Each repository should document its own retention policy." Applies analogously to logging. |
| Branch base | Traderie uses `master`, not `main` | ivy-control-vps does not mandate a branch name. Both conventions exist across the ecosystem. | — |

---

## Current blocker

**VPS Capacity Gate** — `ih-market-vps` at 91% disk (3.3 GB free, 2026-07-07). No passwordless sudo. No PostgreSQL installed. Gates 4, 5, and 6 cannot proceed until this passes.

---

## Approved SHA

```
b3b70a01426694d06d6c07a09f0c33427f530f0d
```

This SHA is the current authoritative published version. Any future deployment must use this SHA or a later reviewed and recorded replacement.
