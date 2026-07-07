# Traderie — Repository Control

**Purpose:** Active governance authority for Traderie. One-stop for current state, applicable standards, compliance, blockers, and next work.
**Canonical remote:** `github.com/wguDataNinja/d2-market-helper`
**Default branch:** `master`
**Approved SHA:** `b3b70a01426694d06d6c07a09f0c33427f530f0d`
**Local path:** `/Users/buddy/projects/traderie`
**Portfolio admission:** ✅ PASS
**Detailed gate evidence:** `repos/traderie/RELEASE_GATES.md`

---

## Applicable standards matrix

| Standard | Source | Applicability | Compliance | Notes |
|----------|--------|---------------|------------|-------|
| Git workflow | `docs/GIT_WORKFLOW.md` | REQUIRED | ✅ PASS | `master` branch — accepted deviation. SSH remote, git-steward delegation. |
| Public/private boundary | `docs/OPERATING_MODEL.md`, `docs/GIT_WORKFLOW.md` | REQUIRED | ✅ PASS | No secrets tracked. `.gitignore` covers `.env`, keys, private data paths. |
| Logging (agent work) | `docs/LOGGING_STANDARD.md` | REQUIRED | ✅ PASS WITH CONDITION | AGENTS.md routes to orchestrator-owned files. Private agent logs under `_internal/`. Historical SESSION.md/LOG.md exist but are not current authority. |
| Logging (runtime) | `docs/LOGGING_STANDARD.md` | NOT YET ASSESSED | UNDEFINED | No VPS runtime yet. Will be assessed at Deployment Readiness. |
| LLM tenets | `docs/LLM_TENETS.md` | NOT APPLICABLE | — | Traderie has no operational LLM stage. Classification, extraction, or summarization may be added later. |
| PostgreSQL naming | `docs/PORTFOLIO_CONVENTIONS.md` | REQUIRED | ✅ PASS | 6 roles match convention. Schemas: `app`, `archive`, `health`. Database `traderie`. |
| Backup format | `docs/PORTFOLIO_CONVENTIONS.md` | REQUIRED | ✅ PASS | `pg_dump -Fc -Z 9`. SHA-256 checksums. Manifests recorded. |
| Restore proof | `docs/PORTFOLIO_CONVENTIONS.md` | REQUIRED | ✅ PASS | Restore drill passed 2026-07-06. Pre-push backup verified. |
| Systemd naming | `docs/PORTFOLIO_CONVENTIONS.md` | REQUIRED | ✅ PASS | 6 service/timer pairs follow `{project}-{role}-{action}`. All action verbs in approved list. |
| Health contract | `docs/PORTFOLIO_CONVENTIONS.md` | REQUIRED | ✅ PASS | `health.health_runs` + `health.workflow_status`. Sanitized export exists. |
| Gate definitions | `docs/PORTFOLIO_CONVENTIONS.md` | REQUIRED | ✅ PASS | Gates recorded in `RELEASE_GATES.md`. Sequential framework defined. |
| Deployment stop conditions | `docs/PORTFOLIO_CONVENTIONS.md` | REQUIRED | ✅ PASS | Conditions documented. VPS deployment not yet attempted. |
| Repository control model | `docs/REPOSITORY_CONTROL_MODEL.md` | REQUIRED | ✅ PASS | This file. |
| Data lifecycle | `docs/DATA_LIFECYCLE_STANDARD.md` | REQUIRED | ✅ PASS WITH CONDITION | Retention policy exists but references historical reports. See data-lifecycle assessment below. |
| CI and fresh-clone | Portfolio expectation | REQUIRED | ✅ PASS | GitHub Actions CI. 57/57 tests. Fresh-clone proven at `b3b70a0`. |
| Secrets and credentials | Portfolio expectation | REQUIRED | ✅ PASS | `.env` gitignored. No tracked secrets. CI includes secret scan. |
| Generated/runtime data | Portfolio expectation | REQUIRED | ✅ PASS | `data/raw/`, `data/history/`, `data/snapshots/`, `logs/` gitignored. |

---

## Accepted deviations

| Standard | Deviation | Rationale | Authority |
|----------|-----------|-----------|-----------|
| Branch name | `master` instead of `main` | No portfolio requirement for branch name. Both conventions exist. | Portfolio conventions §none. |
| License | No license | Documented in README. Per-repo decision. | Buddy. |
| Restore proof recording | Traderie uses its own logging conventions | Portfolio conventions §5 analogously allows repo-specific logging. | Portfolio conventions §5. |

---

## Data-lifecycle assessment

| Criterion | Evidence | Result |
|-----------|----------|--------|
| Current database size | 9.7 MB | ✅ Well within minimal footprint. |
| Current product file size | ~529 KB (4 JSON files) | ✅ Trivial. |
| Raw snapshot retention | 14 days after PG parity (per `docs/retention.md`) | ✅ Policy defined. Not yet enforced (no VPS continuous collection). |
| Normalized snapshot retention | 30 days after PG parity | ✅ Policy defined. |
| History JSONL retention | Indefinite compressed archive with 365-day review boundary | ⚠️ PASS WITH CONDITION — accept 365-day default review cycle. Archive age, size, growth, and prune evidence must be confirmed before Operational Activation (Gate 6). |
| Backup retention (VPS) | 7 daily + 4 weekly | ✅ Per portfolio standard. |
| Backup retention (Mac) | 14→7 daily + 4 weekly + monthly | ✅ Per portfolio standard. |
| Prune behavior | Script exists (`scripts/traderie_prune.py`). Pilot prune executed — 50 prune_audit rows, 25 archive_audit rows. | ✅ Prune mechanism implemented and tested. Not configured for continuous scheduled execution (correct — VPS not deployed). |
| Archive behavior | `archive.prune_archive_audit` table. Migration 012 created prune_archive_audit. | ✅ Archive schema exists. Migration applied. |
| Growth measurement | Not yet instrumented in health export. No continuous collection on VPS. | ⚠️ Need to add `database_size`, `data_directory_size`, and `growth_rate` to health export before VPS deployment. Not a deployment blocker — growth is currently zero. |
| Disk thresholds | Portfolio thresholds apply. No repo-specific thresholds defined. | ⚠️ Should document repo-specific data-directory thresholds before VPS deployment. |
| Expected daily growth | ~22K rows/day, ~12 MB/day (file-based history). PG growth unknown (no continuous collection yet). | ⚠️ Cannot measure PG daily growth until VPS collection runs. Acceptable — will be measured during Phase B. |
| Hot/current vs archival | `app` schema is current operational data. `archive` schema is retention-audit records. History JSONL is cold compressed archive. | ✅ Lifecycle separation implemented. |
| UI data consumed | `data/products/*.json` (~529 KB total) — product prices, rune values. No database queries in current UI. | ✅ UI footprint is trivially small. |
| High-resolution history beyond UI needs | Raw snapshots retained 14 days, normalized 30 days. Product JSONs are the UI surface. | ✅ Raw/normalized retention aligns with re-derivation window, not UI needs. |

**Conclusion:** Traderie meets minimal-footprint expectations. No data-lifecycle issue blocks deployment readiness. Before operational activation (Gate 6), the following must be confirmed:
1. Archive age, size, growth rate, and prune evidence for the history JSONL archive.
2. `database_size`, `data_directory_size`, and `growth_rate` added to health export.
3. Repo-specific data-directory thresholds documented.
4. 365-day history JSONL review boundary observed (provisional default).

---

## Current blocker

**VPS Capacity Gate** — `ih-market-vps` at 91% disk (3.3 GB free, 2026-07-07). No passwordless sudo. No PostgreSQL installed. No traderie checkout. Gates 4, 5, and 6 cannot proceed until this passes.

---

## Next authorized phase

**Phase B — VPS capacity remediation and bounded deployment proof.** Scope defined in `repos/traderie/PHASE_B_CODEX_PACKET.md`. VPS Capacity Gate must pass before deployment work begins.

---

## Cross-repository gate authority

Gate decisions for Traderie are owned by ivy-control-vps and recorded in:
- `repos/traderie/CONTROL.md` (this file) — active governance authority
- `repos/traderie/RELEASE_GATES.md` — detailed gate evidence

Traderie-local documents (STATUS.md, SESSION.md, LOG.md) are historical evidence, not current gate authority. A new agent should read CONTROL.md first to determine current state.
