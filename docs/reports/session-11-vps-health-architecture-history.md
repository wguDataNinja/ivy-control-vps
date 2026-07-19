# VPS Health Architecture History Report

**Session:** 11 — Task 2
**Date:** 2026-07-19
**Status:** Evidence only — no files modified
**Author:** OpenCode agent (deep historical investigation)

---

## Executive Summary

The current VPS health architecture is the product of six sessions of deliberate evolution, not accidental accretion. Every apparent inconsistency (hardcoded dashboard checks, distributed CONTROL.md authority, private inventory prose, aspirational health schemas, missing adapters, stale references) has a traceable reason:

1. **The centralized health aggregator was explicitly rejected in Session 9** as premature (only 2 repos with health output).
2. **The dashboard was built in Session 8** because the Phase 0 CLI (Session 5-7) was recognized as a "control-document renderer, not an independent health view."
3. **The producer pattern was established in Session 9** — 6 producer contracts in `tools/producers/` emit canonical v2 health format.
4. **CONTROL.md became policy truth** in the Session 9 knowledge hierarchy (live evidence > CONTROL.md > registry > dashboard > roadmap > session reports).
5. **The private VPS inventory** was last consolidated on 2026-07-07 — before the dashboard, before the producer contracts, before the knowledge hierarchy — and is now partially stale.
6. **No single declarative VPS inventory exists** because the project deliberately deferred it: the CONTROL.md-per-repo pattern was sufficient at 10 repos, and TODO.md only added it as a P1 task in Session 11.

---

## Timeline

| Date | Session | Change | Reason | Current status |
|---|---|---|---|---|
| 2026-07-06 | Pre-1 | VPS provisioned (Hetzner CX23) | Need autonomous infrastructure | Active |
| 2026-07-06 | 1-3 | Traderie PostgreSQL onboarded | Data pipeline migration | Active, degraded (pc_hc_nl timeout) |
| 2026-07-07 | ~3 | `_internal/vps-inventory-and-runbook.md` consolidated | Consolidate old-tree VPS docs into private authority | Stale — timer listing wrong |
| 2026-07-07 | ~4 | Health contract v1 in PORTFOLIO_CONVENTIONS.md | Need standard health format | Superseded by v2 |
| 2026-07-08 | 4 | Reddit Ops cutover history begins | PostgreSQL migration | Active, backup unit drifted |
| 2026-07-08 | 4 | Health contract v2 (docs/HEALTH_CONTRACT.md) | Codify 46-field canonical model | Design reference — aggregator rejected |
| 2026-07-08 | ~4 | Producer registry (docs/health/producer-registry.md) | Track who produces what | Only Traderie registered |
| 2026-07-08 | ~4 | Adapter interface (docs/health/adapter-interface.md) | Bridge divergent health formats | Current — not implemented for IH |
| 2026-07-08 | 4 | Reddit Ops: first failed cutover (no frontier) | Root cause: missing per-subreddit frontier check | Fixed in run 23/24 |
| 2026-07-08 | 4 | Reddit Ops: successful final cutover | wgu-reddit-postgres-run.timer enabled | Production active |
| 2026-07-09~14 | 5-7 | Phase 0 CLI (portfolio_phase0_status.py) | "Keep it small: no dashboard, API, alerting, live SSH" | Superseded by dashboard |
| 2026-07-15 | 8 | Session 8 reconciliation — Phase 0 CLI recognized as insufficient | "The present Phase 0 CLI is a control-document renderer, not an independent health view" | Led to dashboard |
| 2026-07-15 | 8 | Minimal ingestion dashboard built (ingestion_dashboard.py) | Need live evidence, not prose-parsed health | Current live tool |
| 2026-07-15 | 8 | Dashboard evidence levels established | Must distinguish live from stale from missing | Current authority |
| 2026-07-15~16 | 9 | Live VPS discovery (fresh systemd, backup failures, helper state) | Verify what's actually running | Evidence captured |
| 2026-07-16 | 9 | 6 producer contracts created (tools/producers/) | Timestamped runtime evidence | Current — most missing_producer |
| 2026-07-16 | 9 | Knowledge hierarchy formalized | Live evidence > CONTROL.md > registry > dashboard > roadmap | Current authority |
| 2026-07-16 | 9 | **Centralized health aggregator rejected** | Only 2 repos have health output; premature | HEALTH_CONTRACT.md demoted |
| 2026-07-16 | 9 | Explicit Do-Not-Build list created | No health API, no normalized DB, no persistent registry | Current constraint |
| 2026-07-16 | 9 | Dashboard prose fallback removed | Must NOT derive RED from CONTROL.md prose | Done |
| 2026-07-16 | 9 | 10x CONTROL.md records completed | Per-repo policy truth | Current authority |
| 2026-07-19 | 10 | Session journals established | Required control-plane artifact | Current — only session 10 filled |
| 2026-07-19 | 11 | Healthcheck investigation (this report) | Verify claimed drift before fixing | Claimed drift does not exist |

---

## WGU Reddit Migration History

### Original architecture

Pre-migration: SQLite-based WGU Reddit collector on the Mac, triggered by Mac launchd (`com.buddy.wgu-reddit.dailyupdate`). Data in `/home/scraper/data/wgu-reddit/WGU-Reddit.db`. No PostgreSQL, no VPS systemd timer.

### Intended migration path

1. PostgreSQL 16 on VPS, database `reddit_ops` with schemas `reddit_core`, `wgu_reddit`, `bsda_courses`
2. Per-subreddit frontier tracking, per-target commits, advisory lock, stale-run recovery
3. `wgu-reddit-postgres-run.timer` as sole scheduler, `wgu-reddit-shadow-run.timer` as rollback
4. Mac launchd disabled. SQLite preserved as immutable fallback.

### Completed steps

- PostgreSQL setup, migrations 0001-0006 (cutover history §1, §3)
- Frontier fix (cutover history §3, §6)
- Advisory lock, stale-run recovery (cutover history §4)
- Three consecutive systemd-triggered runs (STABILIZATION.md gate 3)
- Approved-partial exit semantics (STABILIZATION.md gate 1)
- Production timer enabled, shadow timer disabled (cutover history §8)
- Automated backup timer at 08:00 UTC (STABILIZATION.md gate 4)
- Full restore drill to isolated DB (STABILIZATION.md gate 6)
- Backup copied to Mac archive (STABILIZATION.md gate 5)

### Incomplete steps

- Reboot recovery (blocked — requires Buddy-approved timing; STABILIZATION.md gate 7)
- Deployed SHA recorded in health (blocked — not a Git checkout; STABILIZATION.md gate 10)
- Drift detection (STABILIZATION.md gate 11)
- Rebuild reproducibility (STABILIZATION.md gate 12)

### Abandoned plans

- SQLite retirement — explicitly changed to "preserved as immutable historical artifact"
- Git-based deployment — vps is SCP-managed because credential-bearing commit blocks publication
- Centralized health aggregator — rejected in Session 9

### Remaining legacy artifacts

- `wgu-reddit-shadow-run.timer` preserved as disabled rollback
- SQLite at `/home/scraper/data/wgu-reddit/WGU-Reddit.db`
- Mac launchd `com.buddy.wgu-reddit.dailyupdate` disabled
- Backup unit `wgu-reddit-backup.service` references wrong script (`backup_reddit_ops.sh` not `backup_reddit_ops_pg.sh`)

---

## Health System Evolution

### Phase 0 CLI (Session 5-7)

The first health tool was `tools/portfolio_phase0_status.py`. It read CONTROL.md YAML front matter and placeholder files. It was deliberately scoped:

- No dashboard
- No live SSH
- No live database queries
- No API
- No alerting

It rendered control-document state (lifecycle, admission gates, blockers) as text output. It was explicitly "useful scaffolding only."

### Minimal dashboard (Session 8)

Session 8 live discovery found the Phase 0 CLI couldn't answer basic operational questions. The health dashboard (`tools/ingestion_dashboard.py`) was built in one session to fill the gap. Key design constraints:

- Safe read-only SSH only (no secrets, browser profiles, DB credentials)
- Evidence levels label every cell (live / evidence_card / stale / missing_producer / unsupported_field / doc_fallback / unresolved_authority)
- Never infers health from absent data — preserves UNKNOWN
- Never mutates production state
- Roadmap coverage verified via explicit registry (not fragile Markdown parsing)

The dashboard was **never intended to be permanent**. It was the transitional Phase 0 view, and its own documentation labels it as such.

### Producer contracts (Session 9)

Six producer contracts created in `tools/producers/`:
1. `traderie_live_export.py` — canonical v2 health for Traderie
2. `reddit_backup_evidence.py` — backup/restore evidence for Reddit
3. `reddit_canonicality_placeholder.py` — placeholder (every dimension = unresolved)
4. `ih_ack_replay_contract.py` — IH acknowledgement/replay template
5. `control_plane_revision.py` — deployed revision tracking
6. `vps_capacity_snapshot.py` — VPS capacity evidence

Each emits canonical v2 16-field core health format. Only Traderie has a working live producer. The rest report `missing_producer` or placeholders.

### Centralized aggregator rejected (Session 9)

The most important architectural decision: HEALTH_CONTRACT.md v2 defined a 46-field model with aggregator database, read-only API, alert semantics, and producer registry. Session 9 Codex assessment explicitly rejected building it:

- Only 2 repos (Traderie + Reddit Ops) have any health output
- No consumer exists beyond the local dashboard
- No pager/push infrastructure exists

HEALTH_CONTRACT.md was demoted from "current contract" to "design reference." The centralized aggregator schema, API spec, and alert semantics were stripped. The project kept the lightweight evidence-projection model.

### Current architecture (Simplest Credible Target)

From Session 9 closeout assessment (§16):

```
repos/<repo>/CONTROL.md           ← policy truth
  → portfolio_registry.py         ← aggregated policy view (in-memory)
  → tools/producers/*             ← runtime truth (timestamped live probes)
  → ingestion_dashboard.py        ← evidence projection (never policy)
  → Hermes (read-only, bounded)   ← prioritization only
  → Buddy decision → execution
```

---

## Inventory Evolution

### Artifact map

| Artifact | Created | Purpose | Authority level | Owns | Insufficiency |
|---|---|---|---|---|---|
| `_internal/vps-inventory-and-runbook.md` | 2026-07-07 | Private VPS operations reference (SSH, workloads, systemd, filesystem, interaction modes) | ⚠️ Stale — last consolidated before dashboard/producer era | Host identity, SSH config, interaction modes, protected data rules, minimum evidence set | Prose-based, not structured; timer listing wrong (shadow vs postgres-run); no freshness thresholds, no ownership |
| `repos/*/CONTROL.md` (10 files) | 2026-07-08~16 | Per-repo governance (lifecycle, scheduler, database, VPS path, Hermes scope) | ✅ Current policy truth | Scheduler active/writer/legacy, database schemas, backup config, health state, blockers | Distributed — no single VPS deployment view; no cross-workload relationships; hard to answer "what runs on the VPS?" |
| `ROADMAP.md §0` | 2026-07-15 | High-level workload classification and immediate issues | ✅ Current | 5-workload table with classification, issue, evidence | No service/timer names, data locations, or freshness |
| `tools/ingestion_dashboard.py ROADMAP_WORKLOADS` | 2026-07-15 | Dashboard workload-to-roadmap mapping | ✅ Current | 6-workload mapping to ROADMAP § labels | Hardcoded in Python; no data locations, ownership, or timers |
| `tools/portfolio_registry.py` | 2026-07-08 | 10-repo baseline list with lifecycle + runtime | ✅ Current — ephemeral (in-memory only) | YAML-derived repo list | No service/timer names; no data locations; ephemeral by design |
| `docs/PORTFOLIO_UNIVERSE.md` | 2026-07-19 | 18-asset portfolio-wide asset inventory | ✅ Current (DISCOVERY_INCOMPLETE) | Asset classification, portfolio relationships | Not VPS-specific; no operational detail |
| `docs/PORTFOLIO_BASELINE.md` | 2026-07-05 | Dated 8-repo assessment | ❌ Stale | Historical LLM stages, repo status | Explicitly dated — superseded by CONTROL.md files |
| `docs/health/producer-registry.md` | 2026-07-08 | Canonical health producer registration | ✅ Partial | workflow_id, cadence, adapter_type, contract_version | Only Traderie registered; Reddit Ops TBD |
| `docs/health/portfolio-conformance-matrix.md` | 2026-07-08 | Per-repo v2 contract conformance | ✅ Current | Conformance level, gaps, recommended actions | Not an inventory; references nonexistent `check_reddit_ops_pg_health.py` |

### Why no single inventory exists

1. **The per-repo CONTROL.md pattern was deliberately chosen** as the source of policy truth in Session 9. A cross-cutting inventory was considered unnecessary at 10 repos.
2. **The private inventory** was created before the dashboard, before the producer contracts, before the knowledge hierarchy — it captured what was known at the time (2026-07-07) and was never updated.
3. **A declarative VPS inventory was not prioritized** until TODO.md P1 in Session 11 — it was deferred because the distributed CONTROL.md pattern worked for current scale.
4. **The project deliberately avoided new artifact creation** (Session 9 Do-Not-Build list) — the inventory wasn't on the do-not-build list, but it wasn't prioritized either.

---

## Existing Decisions

### Made and documented

| Decision | Source | Date |
|---|---|---|
| Phase 0 CLI is scaffolding only, not a health view | `session-8/codex-1-current-state-and-roadmap-reconciliation.md` | 2026-07-15 |
| Dashboard must preserve UNKNOWN for absent adapters | `session-8/codex-3-minimal-ingestion-dashboard.md` | 2026-07-15 |
| Dashboard is transitional — not a health platform | `session-8/codex-3-minimal-ingestion-dashboard.md` | 2026-07-15 |
| No prose fallback in dashboard — route to UNKNOWN | `session-9/39-codex-assessment-proposal.md` | 2026-07-16 |
| CONTROL.md is policy truth; live evidence is runtime truth | `session-9/40-control-model-hermes-and-closeout-assessment.md` | 2026-07-16 |
| Knowledge hierarchy: live > CONTROL.md > registry > dashboard > roadmap > session reports | `session-9/39-codex-assessment-proposal.md` | 2026-07-16 |
| Centralized health aggregator is premature — do not build | `session-9/39-codex-assessment-proposal.md` | 2026-07-16 |
| Do-Not-Build list: no health API, no normalized DB, no persistent registry, no alert delivery | `session-9/40-control-model-hermes-and-closeout-assessment.md` | 2026-07-16 |
| Adapter pattern for divergent health (IH repos) | `session-6/idlehacker-postgres-onboarding-and-lifecycle.md` | ~2026-07-14 |
| Producers emit canonical v2 format; 42 tests | `session-9/23-phase-c-dashboard-and-producers.md` | 2026-07-16 |
| Hermes is read-only, bounded; never writes production | `session-8/codex-4-hermes-readiness-and-palworld-pilot.md` | 2026-07-15 |
| Session journals required for control-plane continuity | `session-10` closeout | 2026-07-19 |
| Backup unit drift exists and needs Strong Codex packet | `repos/reddit-ops/CONTROL.md:197` | Ongoing |

### Deferred

| Decision | Source | Why deferred |
|---|---|---|
| Reddit Ops Git publication strategy | `repos/reddit-ops/CONTROL.md` | Credential-bearing commit blocks; Buddy must choose history remediation or replacement repo |
| IH userscript source authority | `ROADMAP.md §7` | Buddy must decide canonical source and duplicate disposition |
| IH acknowledgement destination | `ROADMAP.md §7` | Buddy must decide durable archive path |
| idle-hacker governance (managed or dev sandbox) | `session-9/39-codex-assessment-proposal.md` | Buddy decision |
| Hermes PR/branch creation | `session-9/40-control-model-hermes-and-closeout-assessment.md` | Awaiting Palworld pilot |
| VPS deployment automation | `session-9/40-control-model-hermes-and-closeout-assessment.md` | Awaiting Git publication resolution for WGU Reddit |
| Centralized health aggregator | `session-9/39-codex-assessment-proposal.md` | Only 2 repos have health output |

### Open questions

| Question | Implication for inventory |
|---|---|
| Should the missing `tools/check_reddit_ops_pg_health.py` be created or all docs updated? | Controls whether inventory references a health script path |
| Should `_internal/vps-inventory-and-runbook.md` be updated or superseded by `docs/VPS_INVENTORY.md`? | Controls whether the private doc remains an authority |
| What is the correct timer listing for the private inventory? | Currently shows `wgu-reddit-shadow-run.timer` as active (wrong) |

---

## Current Architecture Gap

### Why we have hardcoded dashboard checks

The dashboard was built in one session (Session 8) to solve an immediate problem. Hardcoded service/timer names were the fastest path to a working tool. The dashboard's `ROADMAP_WORKLOADS` dictionary and `collect_reddit()` function embed timer names directly because no machine-readable inventory existed to read them from. This was a deliberate tradeoff: working tool now vs. generalized solution later.

### Why we have distributed CONTROL.md authority

The per-repo CONTROL.md pattern was the result of Session 7-9 normalization. It was designed for per-repo governance (lifecycle, blockers, scheduler, backup). It was not designed as a VPS operations catalog. The question "what runs on the VPS?" requires reading 10 files. This is correct by design for policy authority — but it creates friction for operational queries.

### Why we have private inventory prose

The private inventory (`_internal/vps-inventory-and-runbook.md`) consolidated old-tree VPS documents on 2026-07-07. It captured host identity, SSH configuration, interaction modes, and workload descriptions. It was never updated after the dashboard, producer contracts, and knowledge hierarchy were created because:
- It's in `_internal/` (gitignored, off the main workflow)
- Its interaction-mode documentation is still valuable and not duplicated elsewhere
- Updating it wasn't prioritized over more urgent work

### Why we have aspirational health schemas

HEALTH_CONTRACT.md v2 (46-field model, aggregator database, read-only API, alert semantics) was created in Session 4 as the target architecture. Session 9 Codex assessment explicitly recognized it as premature but did not delete it — it was demoted to "design reference." The schema files, API boundaries, and producer registry remain as reference for when the project grows enough to need them.

### Why we have missing adapters

The gap between aspirational schema and implemented producers is the central tension of the current architecture. 17 missing adapters are tracked in the dashboard's `missing_live_adapters` list (ingestion_dashboard.py:591-608). Each represents a producer that emits `missing_producer` until someone builds it. This is intentional — the dashboard was designed to make gaps visible rather than inferring health from absent data.

### Why we have stale references

1. **TODO.md line 39**: The claimed `wgu-reddit.service` → `wgu-reddit-postgres-run.service` drift was never verified against code. The healthcheck code already uses the correct names.
2. **`tools/check_reddit_ops_pg_health.py`** referenced in 4 documents but never created. The references were likely written when this script was planned but implementation never followed.
3. **Private inventory timer listing** was correct on 2026-07-07 (when `wgu-reddit-shadow-run.timer` was the active production timer) but became stale after the cutover to `wgu-reddit-postgres-run.timer` on 2026-07-08.

---

## Recommendations

1. **Acknowledge the claimed drift is non-existent.** The TODO.md entry should be corrected to match reality. No healthcheck code needs patching for the `wgu-reddit.service` name.

2. **Create `docs/VPS_INVENTORY.md`** as the declarative VPS service/lane inventory. Schema proposed in Task 1 evidence report. This fills the gap between per-repo CONTROL.md files and the operational question "what runs on the VPS?"

3. **Update `_internal/vps-inventory-and-runbook.md`** to correct the timer listing. Consider marking it as partially superseded by `docs/VPS_INVENTORY.md` for the workload table while keeping the interaction-mode and SSH documentation.

4. **Resolve the missing health script.** Either create `tools/check_reddit_ops_pg_health.py` or update all 4 documentation references to point to `ingestion_dashboard.py` as the Reddit health tooling.

5. **Continue the producer buildout.** The 6 producer contracts establish the pattern. The next step is making them live — starting with Traderie (has working exporter, needs VPS deployment) then Reddit (needs backup unit fix + canonical exporter).

6. **Revisit HEALTH_CONTRACT.md when 3+ repos have live producers.** The design reference is valid — it's just premature. The knowledge hierarchy and dashboard are sufficient at current scale.

---

## Evidence Sources

| Source | Path | Used for |
|---|---|---|
| WGU Reddit cutover history | `repos/reddit-ops/CUTOVER_HISTORY.md` | Migration timeline, rollback events |
| WGU Reddit stabilization | `repos/reddit-ops/STABILIZATION.md` | Completed/incomplete gates, blockers |
| Reddit Ops CONTROL.md | `repos/reddit-ops/CONTROL.md` | Scheduler state, backup drift, health tooling reference |
| Traderie CONTROL.md | `repos/traderie/CONTROL.md` | Scheduler state, health contract status |
| Docker health contract v2 | `docs/HEALTH_CONTRACT.md` | Target architecture, field schema, aggregator design |
| Health producer registry | `docs/health/producer-registry.md` | Registered producers, cadence, adapter types |
| Health conformance matrix | `docs/health/portfolio-conformance-matrix.md` | Per-repo v2 conformance assessment |
| Adapter interface | `docs/health/adapter-interface.md` | Adapter pattern, field mapping rules |
| API/alert boundaries | `docs/health/api-alert-boundaries.md` | Deferred API design |
| Session 8 codex 1 | `_internal/outbox/session-8/codex-1-current-state-and-roadmap-reconciliation.md` | Phase 0 CLI insufficiency, dashboard creation rationale |
| Session 8 codex 3 | `_internal/outbox/session-8/codex-3-minimal-ingestion-dashboard.md` | Dashboard design, evidence levels, transitional nature |
| Session 9 codex 39 | `_internal/outbox/session-9/39-codex-assessment-proposal.md` | Aggregator rejection, knowledge hierarchy, stale-claim fixes |
| Session 9 codex 40 | `_internal/outbox/session-9/40-control-model-hermes-and-closeout-assessment.md` | Simplest Credible Target, Do-Not-Build list, work splits |
| Session 9 phase C | `_internal/outbox/session-9/23-phase-c-dashboard-and-producers.md` | Producer contracts, 42 tests |
| Session 9 live discovery | `_internal/outbox/session-9/21-live-discovery.md` | Fresh systemd state, backup failure, helper state |
| Session 5 health registration | `_internal/outbox/session-5/codex-production-health-registration.md` | Producer pattern, deferred registration |
| Portfolio registry | `tools/portfolio_registry.py` | 10-repo baseline, lifecycle types |
| Ingestion dashboard | `tools/ingestion_dashboard.py` | Current healthcheck code, evidence levels, missing adapters |
| Private VPS inventory | `_internal/vps-inventory-and-runbook.md` | Timer listing (stale), interaction modes, SSH config |
| Session journal | `_internal/logs/sessions/SESSION_JOURNAL.md` | Cross-session navigation (Session 10 only) |
| Task 1 evidence report | `_internal/outbox/session-11/01-vps-healthcheck-hardening-evidence-report.md` | Component inventory, drift analysis, inventory schema proposal |
| Git log | `git log --oneline --all -80` | Commit history, session boundaries |
| PORTFOLIO_CONVENTIONS.md | `docs/PORTFOLIO_CONVENTIONS.md` | Systemd naming pattern |
| VPS_ORCHESTRATION.md | `agents/VPS_ORCHESTRATION.md` | VPS interaction modes |
| HERMES_AGENT_CONTRACT.md | `agents/HERMES_AGENT_CONTRACT.md` | Hermes scope, task discovery |
| OPERATING_MODEL.md | `docs/OPERATING_MODEL.md` | VPS classification, filesystem layout |
