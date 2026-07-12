# Ivy Control VPS Roadmap

**Status:** Active ingestion-first portfolio roadmap, refined 2026-07-12.
**Scope:** Portfolio-wide ingestion admission, reusable VPS/PostgreSQL platform products, health visibility, repository readiness packets, and controlled cutover waves.

This roadmap separates two goals:

1. **Ingestion operational readiness** - the evidence required to move authoritative collection to the VPS safely.
2. **Full public repository maturity** - broader documentation, CI, UI, LLM maturity, public polish, automation, and long-term hardening.

The immediate goal is to get appropriate ingestion workloads under one VPS authority and visible health monitoring without forcing unrelated maturity work to block safe ingestion cutovers.

## §1 Strategy and Authority

### §1A Operating Strategy

**Outcome**

The portfolio moves from repeated one-off discovery to reusable admission packets and bounded privileged execution.

**Principles**

- Treat Traderie and Reddit Ops as evidence for reusable platform products.
- Prepare eligible repositories in parallel where file ownership and authority do not conflict.
- Cut over in small waves after a narrow Platform Confidence Gate passes.
- Reserve Strong Codex for privileged VPS/PostgreSQL execution, production cutovers, rollback/recovery, cross-repository architecture, and stateful gate reviews.
- Use medium OpenCode agents for source readiness, documentation, tests, local validation, health adapters, backup scripts, runbooks, control sheets, and handoff packets.
- Keep one authoritative scheduler and one authoritative writer per production workflow.
- Make Phase 0 health visibility a prerequisite for new waves; do not make polished dashboard UI a prerequisite.

**Authority set**

- `docs/OPERATING_MODEL.md` - operating model and execution classes.
- `docs/REPOSITORY_CONTROL_MODEL.md` - repository gates and control-sheet authority.
- `docs/PORTFOLIO_CONVENTIONS.md` - deployment, PostgreSQL, systemd, backup, rollback, and admission conventions.
- `docs/HEALTH_CONTRACT.md` - canonical health payloads and health storage/API boundaries.
- `docs/DATA_LIFECYCLE_STANDARD.md` - retention, backup, restore, archive, and deletion rules.
- `docs/DATABASE.md` - consolidated database architecture and operations reference.
- `docs/PORTFOLIO_BASELINE.md` - roster and baseline classification; current operational status is reconciled here and in `repos/<repo>/CONTROL.md`.

### §1B Execution Classes

| Class | Owner | Examples |
|---|---|---|
| Medium OpenCode | Low-risk implementation and evidence | Admission audits, source fixes, docs, tests, unit templates, health adapters, backup scripts, runbooks, gate packets |
| Strong Codex | Privileged or broad-context execution | VPS provisioning, PostgreSQL roles, production deployment, migration, scheduler cutover, rollback, reboot proof, cross-repo architecture |
| git-steward | Authorized Git writes | Exact-file staging, commits, pushes, branch publication, clean-tree verification |
| Buddy | Risk and authority decisions | Publication strategy approval, destructive approval, license choices, privileged/reboot timing, sensitive review |

## §2 Current Portfolio State

### §2A Repository and Workload Roster

| Repository or workload | Owns ingestion? | Current state | Intended VPS ingestion scope | Next gate |
|---|---:|---|---|---|
| Traderie | Yes | `PRODUCTION_DEGRADED`: VPS sole scheduler/writer; natural run timed out in `pc_hc_nl` | Restore healthy scheduled generation, health/export clarity, backup freshness, reboot proof | `§7A-G1` Traderie Recovery Gate |
| Reddit Ops | Yes | `production-stabilizing`: VPS systemd user timer is sole collector; publication/drift/reboot remain open | Publish clean source, repair backup unit source/deploy, prove backup freshness and recovery | `§7B-G1` Publication Strategy Gate |
| SJC Intel | Yes | Mac development; inert systemd units and migrations exist | Early deterministic Wave 1 candidate | `§4C-G1` Readiness Packet Gate |
| IH Market Companion | Yes | Mixed Mac/VPS helper context; public/private and browser/runtime boundary need normalization | Later deterministic/browser runtime candidate | `§4D-G1` Authority Normalization Gate |
| WGU Catalog | Yes, low-frequency batch | Mac CLI/file-export workflow; no daemon required by current evidence | Event-driven or monthly-check catalog ingestion/export | `§4E-G1` Batch Source Authority Gate |
| WGU-derived Reddit workloads | Unclear | Reddit Ops is the collector authority; WGU-Reddit/catalog/analysis/LLM ownership split is unresolved | Deferred behind boundary reconciliation | `§4F-G1` WGU Boundary Reconciliation Gate |
| BSDA Courses | No, consumer | Mac development; consumes Reddit/WGU data | Consumer-only LLM pipeline after upstream contracts | `§4G-G1` Consumer Boundary Gate |
| WGU Atlas | No, downstream/static | GitHub Pages/static site; catalog dependency active | Catalog consumer and later LLM QA reference | `§4H-G1` Catalog Contract Gate |
| Idle Hacking KB | Yes, sensitive | Mac development; complex LLM and Discord capture | Only a safe ingestion subset may be prepared near term | `§4I-G1` Sensitive Ingestion Boundary Gate |
| Reckless Ben | Restricted | `NO_LAUNCH` | No production ingestion unless reclassified | `§4J-G1` Restricted Repository Gate |
| ivy-control-vps | Platform | Local control plane | Standards, health view, templates, readiness review | `§3` platform gates |

### §2B Reconciled Current Facts

**Traderie**

- Deployed production SHA: `e5ebd0f6dd41bcb4e1d8a88f272be89b225cfd40`.
- VPS systemd is sole scheduler and writer. Mac launchd is inactive.
- Segmented runtime is deployed with per-segment bounds: `pc_sc_nl=180s`, `pc_sc_l=240s`, `pc_hc_l=360s`, `pc_hc_nl=480s`.
- Manual bounded generation and Persistent catch-up generation passed.
- The first genuine natural scheduled generation on 2026-07-11 18:01:46 UTC partially failed because `pc_hc_nl` hit the 480s bound.
- DB-backed health records exist; file-export behavior is unresolved.
- Backup freshness now has a portfolio default in `docs/HEALTH_CONTRACT.md`; Traderie still needs evidence that the threshold is applied correctly.
- Controlled reboot proof is deferred until natural scheduled generation succeeds.

**Reddit Ops**

- VPS systemd user timer `wgu-reddit-postgres-run.timer` is the sole ingestion scheduler.
- Database `reddit_ops` runs on VPS PostgreSQL 16 with migrations `0001` through `0006`.
- Approved-partial exit semantics and three systemd-triggered runs are proven.
- Backup source is reviewed, but the installed backup service has referenced the wrong script name in prior evidence; publication and deployment of reviewed source are still required.
- Backup/restore evidence exists with remaining exact-SHA, drift, alerting, and reboot gaps.
- Git publication is blocked because local unpublished history contains credential-bearing commit `e4acae0`; normal push is forbidden.

### §2C WGU-Derived Boundary Status

**Known from current evidence**

- `repos/reddit-ops/CONTROL.md` governs Reddit Ops as the WGU subreddit PostgreSQL collector.
- `_internal/outbox/session4/agent-3-portfolio-ingestion-admission-matrix.md` identifies `/Users/buddy/Desktop/WGU-Reddit` as the Reddit Ops producer code and `/Users/buddy/projects/WGU-Reddit` as an empty placeholder.
- Reddit Ops currently owns production ingestion into `reddit_ops`.
- BSDA Courses is a downstream consumer in current planning.
- WGU Catalog is a separate WGU course catalog source authority, not proven to be the same boundary as Reddit Ops.

**Unresolved ownership questions**

- Which repository owns future Reddit catalog, catalog-like exports, or shared Reddit data contracts.
- Which WGU-Reddit code paths are ingestion, catalog, analysis, LLM, benchmark, or historical tools.
- Which future roadmap sections belong under Reddit Ops versus WGU-Reddit Operations versus consumer repositories.
- Which publication strategy safely represents production collector code without credential-bearing history.

**Planning rule**

Do not plan production LLM, downstream WGU-Reddit, Reddit catalog, or derived Reddit workload admission until `§4F-G1` passes. This ambiguity does not block unrelated deterministic ingestion work such as SJC Intel or WGU Catalog batch readiness.

### §2D Ingestion Readiness Versus Full Maturity

| Dimension | Required for ingestion cutover | Can wait for full maturity |
|---|---|---|
| Source authority | Reviewed source and exact deployment SHA, or explicit temporary exception | Branch protection, release automation |
| Scheduler/trigger | Exactly one production scheduler or trigger | Scheduler UI and long-term automation |
| Writer | Exactly one production writer | Legacy cleanup after stabilization |
| Health | Phase 0 visibility plus contract-compatible producer or adapter | Polished dashboard and alert delivery |
| Backup/recovery | Backup, checksum, manifest, restore or equivalent recovery proof | Monthly restore automation |
| Documentation | Operator procedure, rollback, control/gate evidence | Public tutorials and presentation polish |
| Tests | Focused validation for changed operational paths | Broad CI expansion |

## §3 Shared Platform Workstreams

### §3A Canonical Ingestion-Admission Gate

**Outcome**

Every ingestion workload satisfies one reusable gate before production authority can move, unless a documented workload-specific exception is recorded in its control sheet.

**Gate ID**

`§3A-G1` Canonical Ingestion-Admission Gate.

**Required evidence**

- Collector authority.
- Scheduler or trigger authority.
- Writer authority.
- Canonical data authority.
- Reviewed source and exact deployment SHA.
- Secrets and runtime configuration.
- Deterministic entry point.
- Locking or concurrent-run protection.
- Idempotency or duplicate prevention.
- Bounded runtime and timeout behavior.
- Retry and terminal failure behavior.
- Schema and migration state where applicable.
- Health output.
- Freshness.
- Counts, backlog, or output manifest where applicable.
- Backup.
- Checksum and manifest.
- Isolated restore or equivalent recovery proof.
- Rollback.
- Mac fallback, archive, or recovery role.
- Legacy scheduler shutdown.
- Successful manual run.
- Successful natural scheduled or event-triggered run.
- Exactly one active production writer.

Repository-specific gates may add requirements, but they must not silently omit this common gate.

### §3B PostgreSQL Reusable Products

**Outcome**

PostgreSQL onboarding becomes a set of reusable products prepared mostly by medium agents, with Strong Codex performing bounded privileged execution.

**Current bounded-privilege evidence**

Session evidence shows the workflow changed from repeated interactive password entry to a migration-phase scoped model:

- Earlier state: `_internal/vps-inventory-and-runbook.md` and early Session 3 evidence recorded no broad passwordless sudo and interactive sudo requirements.
- Session 3 evidence: `_internal/outbox/session3/agent-6-portfolio-vps-operations-discovery.md` found PostgreSQL admin already worked through `sudo -n -u postgres` for `psql`, `createdb`, and `dropdb`.
- Session 3 Codex evidence: `_internal/outbox/session3/codex-7-operations-access-and-traderie-cutover.md` recorded durable migration-phase policy at `/usr/local/sbin/ivy-systemd-deploy`, `/etc/sudoers.d/ivy-migration`, and `/var/log/ivy-systemd-deploy.log`.
- Session 4 evidence: `_internal/outbox/session4/agent-1-traderie-cutover-unblock-audit.md` recorded the current boundary as allowlisted `ivy-systemd-deploy` actions for Traderie, `/usr/sbin/reboot`, PostgreSQL `psql/createdb/dropdb` as `postgres`, and password-required broad sudo.
- The helper is root-owned, not version-controlled, and cannot update itself through the current NOPASSWD boundary. A repository-hosted helper template plus scoped update command is still planned, not complete.

**Current authority assessment**

This is current session evidence and current deployment practice, not yet a fully promoted public platform standard. It is safe to reuse only through explicit Strong Codex packets that cite the helper and sudo boundary. Promotion and hardening are required before treating it as a general-purpose platform product.

**Reusable product plan**

| Product | Status | Current location or evidence | Prepare | Execute | Completion evidence |
|---|---|---|---|---|---|
| Project database provisioning packet | Existing as task evidence; needs promotion | Traderie/Reddit Ops Codex packets; `docs/DATABASE.md` | Medium OpenCode | Strong Codex | DB exists, roles exist, grants verified |
| Role and privilege matrix | Existing but dispersed | `docs/PORTFOLIO_CONVENTIONS.md`, `docs/DATABASE.md`, repo migrations | Medium OpenCode | Strong Codex validates | Positive and negative role tests |
| Standard role naming with conditional applicability | Existing | `docs/PORTFOLIO_CONVENTIONS.md` | Medium OpenCode | Strong Codex validates | Control sheet records applicable roles |
| Database onboarding manifest | Planned and required | New template under future `docs/templates/` or `repos/<repo>/` packet | Medium OpenCode | Strong Codex consumes | Manifest lists DB, schemas, roles, env vars, migrations, validation |
| Environment/configuration template | Existing per repo, inconsistent | `.env.example`, deploy env examples | Medium OpenCode | Strong Codex installs live config | Safe example exists; live env outside Git |
| Migration execution and validation packet | Existing per repo, needs standardization | Traderie migrations/validation; Reddit Ops migrations | Medium OpenCode | Strong Codex | Migration ledger and validation SQL pass |
| Negative privilege-test procedure | Existing as evidence, needs template | Traderie role tests; Reddit Ops gates | Medium OpenCode | Strong Codex | Writer cannot read/alter outside scope; reader cannot write |
| Isolated restore helper or packet | Existing as packets, needs helper | Traderie/Reddit Ops restore evidence | Medium OpenCode | Strong Codex | Restore DB validated and cleaned up |
| Backup/checksum/manifest wrapper | Existing per repo, needs common wrapper | Traderie and Reddit Ops scripts | Medium OpenCode | Strong Codex or scheduler | Dump, SHA-256, manifest, `pg_restore --list` |
| Health registration procedure | Planned and required | `docs/HEALTH_CONTRACT.md`, `docs/health/producer-registry.md` | Medium OpenCode | Strong Codex for production registration | Producer listed, Phase 0 view shows it |
| Temporary restore cleanup procedure | Existing in packets, needs template | Traderie/Reddit Ops restore packets | Medium OpenCode | Strong Codex | No restore DB remains after proof |
| Bounded privileged execution workflow | Existing but needs promotion/hardening | `ivy-systemd-deploy`, `/etc/sudoers.d/ivy-migration`, session logs | Strong Codex designs, Medium documents | Strong Codex | Helper actions logged; no broad sudo used |
| PostgreSQL admission evidence template | Planned and required | This roadmap `§3B`, `§3A` | Medium OpenCode | Review by Strong Codex | Packet sufficient for execution without rediscovery |

**Deliberate non-capabilities**

- The current helper is not a general shell.
- It does not permit arbitrary root file edits.
- It does not manage secrets.
- It does not update itself.
- It does not authorize destructive data deletion.
- It does not replace Buddy approval for reboot timing, publication strategy, or destructive cleanup.

**Gate**

`§3B-G1` PostgreSQL Productization Gate.

### §3C Deployment and Exact-SHA Tooling

**Outcome**

Every deployable repository can be installed and verified by exact SHA.

**Products**

- Exact-SHA deployment template - existing but needs promotion from Traderie packets.
- Deployment registry entry - planned and required.
- Drift checker - planned and required.
- Helper update mechanism - planned and required because current `ivy-systemd-deploy` hardcodes a SHA.

**Gate**

`§3C-G1` Exact-SHA Deployment Gate.

### §3D Systemd and Scheduler Standards

**Outcome**

Schedulers are bounded, observable, and never duplicated.

**Products**

- Systemd service/timer templates - existing per repo, need portfolio templates.
- Unit validation procedure - existing through `systemd-analyze verify`, needs template.
- Natural-run acceptance template - existing in Traderie evidence, needs promotion.
- Rollback packet template - existing per repo, needs promotion.

**Gate**

`§3D-G1` Scheduler Gate.

### §3E Phase 0 Health View

**Outcome**

Buddy can inspect ingestion status through a quick read-only operator view before new cutovers.

**Product**

`Phase 0 operator view`: a CLI-generated table or simple internal HTML page. Initial implementation should be a CLI report because it can be validated fastest.

**Planned command path**

`tools/portfolio_phase0_status.py --format table`

**Source data**

- Repository health exporters or adapters where available.
- `repos/<repo>/CONTROL.md` for expected scheduler/writer authority and approved SHA.
- Read-only systemd state for local/VPS jobs where a producer is not yet registered.
- Backup artifact age from repo health or documented backup path.
- Drift evidence from Git SHA, health `deployed_revision`, and unit hash where available.

**Required output columns**

- Repository or workload.
- Ingestion workflow.
- Last attempt.
- Last successful run.
- Freshness.
- Scheduler or trigger state.
- Current writer authority.
- Deployed revision.
- Backup age.
- Current failure.
- Drift.
- Active incident or approval requirement.

**Completion proof**

One generated report includes Traderie, Reddit Ops, SJC Intel readiness placeholder, and WGU Catalog batch placeholder without exposing secrets, connection strings, private paths, raw error bodies, or credentials.

**Gate**

`§3E-G1` Phase 0 Health Visibility Gate.

### §3F Backup, Restore, and Retention

**Outcome**

Every authoritative data store has a verified recovery path before cutover.

**Products**

- Backup/checksum/manifest wrapper - existing per repo, needs promotion.
- Isolated restore packet - existing per repo, needs template.
- File/export recovery equivalent - planned for WGU Catalog and other non-DB workloads.
- Backup freshness threshold - default added in `docs/HEALTH_CONTRACT.md`, repo-specific thresholds still required where stricter.

**Gate**

`§3F-G1` Backup/Restore Gate.

### §3G Drift and Deployed-Revision Verification

**Outcome**

Unapproved code, dirty checkouts, stale units, missing revision metadata, and schema drift are visible.

**Products**

- Drift checker - planned and required.
- Deployment registry - planned and required.
- Unit hash verification - existing in Traderie evidence, needs template.

**Gate**

`§3G-G1` Drift Detection Gate.

### §3H Reusable Onboarding Artifacts

| Artifact | Status |
|---|---|
| PostgreSQL onboarding packet/helper | Existing but needing promotion |
| Role matrix | Existing and reusable |
| Exact-SHA deployment template | Existing but needing promotion |
| Deployment registry entry | Planned and required |
| Systemd service and timer templates | Existing but needing promotion |
| Unit validation | Existing but needing promotion |
| Health exporter or adapter template | Planned and required |
| Health producer registration | Existing registry doc, needs operational procedure |
| Backup and restore wrapper | Existing per repo, needs promotion |
| Cutover packet template | Existing but needing promotion |
| Rollback packet template | Existing but needing promotion |
| Natural-run acceptance template | Existing but needing promotion |
| Drift checker | Planned and required |
| Readiness review template | Planned and required |
| Platform-confidence checklist | Planned in `§6A`, required before Wave 1 |

**Gate**

`§3H-G1` Reusable Artifact Gate.

### §3I Hermes Staged Authority

Hermes remains read-only until Phase 0 health and deterministic workflow contracts are proven.

**Gate**

`§3I-G1` Hermes Read-Only Gate.

## §4 Repository Readiness Campaign

### §4A Campaign Model

Prepare eligible ingestion repositories in parallel, but cut over in controlled waves. WGU-derived downstream ambiguity is deferred behind `§4F-G1` and must not block SJC Intel, WGU Catalog batch readiness, or other unrelated deterministic readiness work.

### §4B Common Medium-Agent Packet Shape

Every readiness packet must specify:

- roadmap section and gate;
- exact repository scope;
- required reading;
- allowed writes and prohibited actions;
- expected source or documentation outputs;
- local validation;
- dry-run or staging proof;
- evidence files;
- stop conditions;
- escalation conditions;
- privileged handoff requirements;
- completion gate.

### §4C SJC Intel Readiness Packet

**Task artifact**

`_internal/outbox/session5/agent-sjc-intel-ingestion-readiness.md`

**Repository scope**

`/Users/buddy/projects/sjc_intel`; control-plane outputs under `repos/sjc-intel/`.

**Required reading**

Root `AGENTS.md`, `TODO.md`, `docs/OPERATING_MODEL.md`, `docs/REPOSITORY_CONTROL_MODEL.md`, `docs/PORTFOLIO_CONVENTIONS.md`, `docs/DATA_LIFECYCLE_STANDARD.md`, `docs/HEALTH_CONTRACT.md`, `docs/DATABASE.md`, SJC Intel README/AGENTS/deploy/systemd/db/health docs.

**Expected outputs**

Create `repos/sjc-intel/CONTROL.md` and `repos/sjc-intel/RELEASE_GATES.md`; update only SJC Intel source/docs if required for readiness.

**Local validation**

Run repository tests, migration validation, health exporter dry run, unit static validation if systemd files exist, `.env.example` check, no-secret/path scan.

**Dry-run or staging proof**

No VPS mutation. Produce a bounded command plan for Strong Codex.

**Stop conditions**

Secrets, unclear writer authority, missing deterministic entrypoint, failed tests, destructive cleanup need, or private data exposure risk.

**Escalation**

Strong Codex for database provisioning, config installation, systemd installation, production deploy, and scheduler activation.

**Completion gate**

`§4C-G1` SJC Intel Readiness Packet Gate.

### §4D IH Market Companion Readiness Packet

**Task artifact**

`_internal/outbox/session5/agent-ih-market-authority-readiness.md`

**Repository scope**

`/Users/buddy/projects/ih_market_companion`; control-plane outputs under `repos/ih-market-companion/`.

**Required reading**

Control-plane standards, IH Market README/AGENTS/deploy/systemd/db/health/runtime docs, and any public/private boundary document in the repo.

**Expected outputs**

Authority map, public/private boundary assessment, service/timer inventory, data-boundary scan, migration/health review, rollback packet, and control/gate drafts.

**Local validation**

Run tests or targeted validations available locally; verify unit source syntax; scan for private trading/chat paths in publishable docs.

**Dry-run or staging proof**

No live runtime or trading-adjacent action. Evidence only.

**Stop conditions**

Trading authority ambiguity, private data exposure, active dirty tree that prevents safe classification, or unclear VPS helper ownership.

**Escalation**

Strong Codex for any VPS helper change, browser/runtime service activation, PostgreSQL provisioning, or trading-adjacent authority.

**Completion gate**

`§4D-G1` IH Market Authority Normalization Gate.

### §4E WGU Catalog Batch Readiness Packet

**Classification**

Low-frequency event-driven or scheduled batch ingestion workload. It is not a continuous collector.

**Task artifact**

`_internal/outbox/session5/agent-wgu-catalog-batch-readiness.md`

**Repository scope**

`/Users/buddy/projects/wgu-catalog`; control-plane outputs under `repos/wgu-catalog/`.

**Required reading**

Control-plane standards, WGU Catalog README/docs/scripts/export fixtures, and any current operator notes.

**Expected outputs**

Control/gate files that define source authority, deterministic commands, release-detection or monthly-check mechanism, output validation, archive/rollback, health/freshness visibility, exact source revision, and operator procedure.

**Workload requirements**

- Detect or confirm a new WGU catalog release.
- Run established ingestion, parsing, validation, and export.
- Record source version and acquisition date.
- Validate outputs.
- Publish checksums or manifests.
- Expose freshness and last-success health.
- Preserve prior catalog versions.
- Notify when a new release requires review or ingestion.
- Decide whether activation is automatic, approval-gated, or manually triggered.

**Non-goals**

Do not create unnecessary database, daemon, or continuous scheduler work if the existing file/export architecture is sufficient.

**Local validation**

Run existing ingest/parse/validate/export commands on fixtures or dry-run data; verify manifests/checksums and prior-version preservation.

**Stop conditions**

Unclear source authority, inability to validate output, missing archive/rollback, or release-detection ambiguity that cannot be resolved locally.

**Escalation**

Strong Codex only if VPS scheduling or production storage activation is selected.

**Completion gate**

`§4E-G1` WGU Catalog Batch Source Authority Gate.

### §4F WGU-Derived Boundary Reconciliation

**Task artifact**

`_internal/outbox/session5/agent-wgu-reddit-boundary-reconciliation.md`

**Scope**

Read-only reconciliation across Reddit Ops controls, `/Users/buddy/Desktop/WGU-Reddit`, `/Users/buddy/projects/WGU-Reddit`, relevant Reddit catalog or derived workload evidence if present, BSDA consumer references, and `docs/DATABASE.md`.

**Outcome**

Resolve enough repository/workload ownership to decide which future roadmap sections belong to Reddit Ops, WGU-Reddit, a Reddit catalog boundary, BSDA Courses, or another derived workload.

**Work**

- Identify current authorities.
- Separate ingestion, catalog, analysis, LLM, benchmark, and historical-tool responsibilities.
- Resolve publication blockers at the correct repository boundary.
- Define future roadmap sections and control-sheet owners.

**Deferred**

No production LLM, downstream WGU-Reddit, Reddit catalog, or derived Reddit workload admission until this gate passes.

**Completion gate**

`§4F-G1` WGU Boundary Reconciliation Gate.

### §4G BSDA Courses Consumer Readiness

Deferred until `§4F-G1` and WGU Catalog contract evidence are available. BSDA remains consumer-only and must not gain independent Reddit ingestion authority.

### §4H WGU Atlas Readiness

Deferred until WGU Catalog contract evidence is available. Atlas remains downstream/static unless a later gate adds production LLM authority.

### §4I Idle Hacking Safe Ingestion Packet

**Task artifact**

`_internal/outbox/session5/agent-idlehacking-safe-ingestion-boundary.md`

**Repository scope**

`/Users/buddy/projects/idlehacking_kb`; control-plane outputs under `repos/idlehacking-kb/`.

**Expected outputs**

Define a safe ingestion subset if one exists; inventory Discord capture authority, migration/health status, credential coupling, and LLM exclusion boundary.

**Local validation**

Read-only/source-only checks; no Discord capture, no production LLM execution, no credential use.

**Stop conditions**

Sensitive-source ambiguity, cross-repo credential dependency, unclear capture authority, or any required live service interaction.

**Escalation**

Strong Codex for production database provisioning, Discord capture deployment, or LLM production authority.

**Completion gate**

`§4I-G1` Idle Hacking Sensitive Ingestion Boundary Gate.

### §4J Reckless Ben Restricted Path

Reckless Ben remains `NO_LAUNCH`. It contributes approval and evidence patterns only unless Buddy explicitly reclassifies it.

## §5 Schedulable Execution Groups

### §5A Shared Platform Foundation

**Hard dependencies:** Current roadmap authority, no production mutation.
**Concurrent work:** PostgreSQL product templates, deployment registry design, reusable packet templates.
**Owner:** Medium OpenCode prepares; Strong Codex reviews privileged design.
**Completion evidence:** Reusable artifact list reaches `existing reusable` or `planned with owner`; no ambiguous helper/sudo boundary remains.
**Next gate:** `§3B-G1`, `§3H-G1`.

### §5B Repository-Specific Medium-Agent Readiness Packets

**Hard dependencies:** `§3A` gate model.
**Concurrent work:** SJC Intel, WGU Catalog, IH Market, Idle Hacking safe subset. WGU-derived workloads wait for `§4F-G1`.
**Owner:** Medium OpenCode.
**Completion evidence:** Required outbox report, control/gate drafts, validation output, privileged handoff packet.
**Next gate:** repository readiness gate.

### §5C Minimum Health Visibility

**Hard dependencies:** Phase 0 source list and control-sheet fields.
**Concurrent work:** Health adapter review can run with readiness packets.
**Owner:** Medium OpenCode; Strong Codex only for live health registration.
**Completion evidence:** Phase 0 report shows required columns for existing and candidate workloads.
**Next gate:** `§3E-G1`.

### §5D Platform Confidence Review

**Hard dependencies:** Existing workload status, Phase 0 health, capacity check, backup freshness.
**Owner:** Strong Codex or high-reasoning review from a compact evidence packet.
**Completion evidence:** `§6A-G1` pass/fail with conditions.
**Next gate:** Wave 1 authorization.

### §5E Wave 1 Privileged Cutover

**Hard dependencies:** Platform Confidence Gate, repository readiness gate, exact approved SHA, backup/rollback packet.
**Owner:** Strong Codex.
**Completion evidence:** Bounded manual run, health, backup, restore/recovery proof, scheduler activation.
**Next gate:** Natural-run acceptance.

### §5F Natural-Run Acceptance

**Hard dependencies:** Scheduler active and no manual start substituted for proof.
**Owner:** OpenCode read-only evidence, Strong Codex only if remediation is needed.
**Completion evidence:** Genuine scheduled or event-triggered run succeeds and is distinguished from manual or Persistent catch-up.
**Next gate:** Stabilization.

### §5G Stabilization

**Hard dependencies:** Natural-run acceptance.
**Owner:** OpenCode evidence review; Strong Codex for recovery/reboot if needed.
**Completion evidence:** Health current, backup fresh, rollback available, drift clean, incidents absent or documented.
**Next gate:** next readiness/cutover wave.

### §5H Next Readiness and Cutover Wave

**Hard dependencies:** Prior wave stabilized or explicitly accepted with conditions.
**Owner:** Medium OpenCode prepares; Strong Codex executes.
**Completion evidence:** Same as Wave 1, adjusted by workload risk.

## §6 Cutover Strategy and Platform Confidence

### §6A Platform Confidence Gate

**Gate ID**

`§6A-G1` Platform Confidence Gate.

**Minimum conditions before first new ingestion cutover wave**

- No unresolved critical production incident.
- Traderie and Reddit Ops each have exactly one authoritative scheduler/trigger and writer, or any exception is documented and not relevant to the candidate wave.
- Current health is visible in Phase 0 view or equivalent evidence.
- Backup freshness is passing or explicitly waived for a non-database candidate with equivalent recovery proof.
- Rollback is available for existing production workloads.
- PostgreSQL service is healthy.
- Disk/capacity is below stop thresholds.
- No known duplicate-writer condition.
- No active recovery operation would make another cutover unsafe.

**Not required for this gate**

- Full repository maturity.
- Polished dashboard UI.
- Every reboot proof.
- Every remaining Traderie or Reddit Ops maturity task, unless the unresolved item is a genuine hard dependency for the candidate cutover.

### §6B Recommended Batching

| Wave | Scope | Rationale |
|---|---|---|
| Wave 0 | Traderie recovery and Reddit Ops recovery/publication as separate sessions | Existing workloads must not hide critical incidents |
| Wave 1 | SJC Intel; WGU Catalog only if it selects VPS batch trigger | Low-risk deterministic and batch workloads |
| Wave 2 | IH Market or Idle Hacking safe subset | Higher runtime/privacy complexity |
| Wave 3 | LLM/downstream production stages | Requires boundary, budget, prompt, audit, and review gates |

### §6C Rollback Rules

- Bounded generation failure stops activation.
- Natural scheduled or event-triggered run failure produces one focused remediation task.
- Duplicate scheduler/writer risk triggers rollback to last known single authority.
- Backup/restore failure blocks production-complete status.
- Reboot failure requires documented fallback authority where applicable.

## §7 Active Recovery Workstreams

### §7A Traderie Production Recovery

**Outcome**

Traderie returns from `PRODUCTION_DEGRADED` to `production-complete` or a clearly narrower blocked state.

**Work**

- Investigate `pc_hc_nl` timeout using runtime, retry, volume, latency, progress, file mtime/size, and process evidence.
- Verify DB-backed and file-based health behavior.
- Apply backup freshness threshold to Traderie evidence.
- Apply source correction and tests if needed.
- Deploy exact published SHA, prove bounded generation, prove one genuine natural scheduled generation, then perform controlled reboot proof if the Platform Confidence Gate does not require deferral.

**Gate**

`§7A-G1` Traderie Recovery Gate.

### §7B Reddit Ops Publication Strategy

**Outcome**

Publishable Reddit Ops source path is approved without exposing credential-bearing history.

**Work**

- Reconstruct clean publishable history excluding `e4acae0`, or choose another Buddy-approved publication strategy.
- Add reviewed backup unit source and tests.
- Run secret scan and present strategy for Buddy approval before any push.

**Gate**

`§7B-G1` Reddit Ops Publication Strategy Gate.

### §7C Reddit Ops Production Recovery

**Outcome**

Backup service, backup freshness, exact-SHA deployment, restore evidence, drift, and reboot/persistence gaps are reconciled after publication or explicit rsync exception.

**Gate**

`§7C-G1` Reddit Ops Recovery Gate.

## §8 Evidence and Completion Proofs

### §8A Standard Gate IDs

| Gate | Meaning |
|---|---|
| `ADMISSION` | Control sheet, gate file, source boundary, current authority, next phase |
| `INGESTION` | Canonical ingestion-admission gate from `§3A` |
| `SOURCE` | Publishable source, `.env.example`, tests, docs, no secret/private blockers |
| `PG` | Database, roles, migrations, validation, privilege proof |
| `HEALTH` | Contract-compatible health, freshness, backup state, deployed revision |
| `BACKUP` | Dump or export, checksum, manifest, restore or equivalent recovery proof |
| `DEPLOY` | Exact SHA deployed, config installed, checkout clean, smoke proof |
| `SCHEDULER` | One scheduler/trigger active, duplicate writers disabled, exit semantics correct |
| `NATURAL` | Genuine scheduled or event-triggered run passes |
| `REBOOT` | Post-reboot service/timer/database recovery passes where required |
| `MATURITY` | Broader CI, docs, dashboard polish, LLM budgets, public presentation |

### §8B Required Evidence Per Ingestion Workload

Every ingestion readiness review must answer:

- What data is collected or acquired.
- Current and future collector.
- Current and future scheduler or trigger.
- Current and future writer.
- Canonical data store or export authority.
- Exact source revision.
- Health/freshness surface.
- Backup/recovery surface.
- Duplicate-writer risk.
- Publication blocker.
- Privileged execution requirements.
- Deferred maturity work.
- Next gate.

## §9 Near-Term Session Sequence

### §9A Roadmap and Authority Reconciliation

**Scope:** This refinement pass.
**Risk profile:** Documentation/control only.
**Completion:** Roadmap, affected authority docs, private log, validation.

### §9B Traderie Recovery Session

**Scope:** `§7A` only.
**Risk profile:** Existing production recovery.
**Owner:** OpenCode evidence/source prep, git-steward if source changes, Strong Codex for production deployment/reboot.
**Dependency:** None from WGU boundary work.

### §9C Reddit Ops Publication Strategy Session

**Scope:** `§7B` only.
**Risk profile:** Git/history/publication.
**Owner:** OpenCode prepares clean branch and scan; Buddy approves strategy; git-steward performs authorized writes.
**Dependency:** No production mutation.

### §9D Reddit Ops Production Recovery Session

**Scope:** `§7C` only.
**Risk profile:** Live backup/service/restore/reboot work.
**Owner:** Strong Codex after publication or explicit rsync exception.
**Dependency:** `§9C` or Buddy-approved deployment exception.

### §9E PostgreSQL Platform Products Session

**Scope:** `§3B`, `§3H`.
**Risk profile:** Productization and bounded privilege design; no live changes unless separately authorized.
**Owner:** Medium OpenCode prepares templates and packets; Strong Codex reviews privilege model and later executes only bounded privileged packets.
**Current product outputs:** `docs/DATABASE.md` reusable PostgreSQL onboarding system, `docs/PORTFOLIO_CONVENTIONS.md` bounded privileged execution requirements, `_internal/templates/SESSION5_REUSABLE_TASK_TEMPLATES.md`, and Session 5 PostgreSQL/helper packets under `_internal/outbox/session5/`.

### §9F Phase 0 Health Session

**Scope:** `§3E`.
**Risk profile:** Read-only status surface.
**Owner:** Medium OpenCode; Strong Codex only if live health registration is needed.
**Current product output:** `docs/HEALTH_CONTRACT.md` §4A and `_internal/outbox/session5/agent-phase0-health-implementation.md`.

### §9G SJC Intel Readiness Session

**Scope:** `§4C`.
**Risk profile:** Source/readiness only.
**Owner:** Medium OpenCode.
**Dependency:** Canonical gate model.

### §9H Platform Confidence Review

**Scope:** `§6A`.
**Risk profile:** Cross-workload readiness decision.
**Owner:** Strong Codex or high-reasoning gate review.
**Dependency:** Phase 0 health plus current production evidence.

### §9I Wave 1 Privileged Cutover

**Scope:** First candidate that passes readiness, likely SJC Intel.
**Risk profile:** Live VPS/PostgreSQL/scheduler work.
**Owner:** Strong Codex.
**Dependency:** `§6A-G1` and repository readiness gate.

## §10 Reference Migration

Historical logs and outbox packets keep their old references. Current authority documents should use the new references below. `TODO.md` still contains old roadmap references but is protected task input and must not be edited by agents.

| Old reference | New reference |
|---|---|
| Old `§2A` admission | `§3A`, `§4`, `§8` |
| Old `§3A` VPS capacity | `§6A`, `§5D` |
| Old `§3B` PostgreSQL foundation | `§3B`, `docs/DATABASE.md` |
| Old `§3C` backup/restore | `§3F`, `§8A BACKUP` |
| Old `§4A` deployment contract | `§3C`, `§3G`, `§8A DEPLOY` |
| Old `§5A` authority transfer | `§3A`, `§6C`, `§8A SCHEDULER` |
| Old `§6A` health | `§3E`, `docs/HEALTH_CONTRACT.md` |
| Old `§7A` Traderie current state | `§2B`, `§7A` |
| Old `§7G` Traderie scheduler | `§7A`, `§8A SCHEDULER` |
| Old `§7H` Traderie acceptance | `§7A`, `§5G` |
| Old `§8` Hermes | `§3I` |
| Old `§9A` WGU-Reddit ingestion inspection | `§2C`, `§4F` |
| Old `§9B` WGU-Reddit LLM | Deferred behind `§4F-G1` |
| Old `§10A` SJC Intel | `§4C`, `§9G` |
| Old `§11` WGU Catalog | `§4E`, `§9G` or later batch readiness session |
| Old `§12` BSDA Courses | `§4G` |
| Old `§13` WGU Atlas | `§4H` |
| Old `§14` Idle Hacking KB | `§4I` |
| Old `§15` IH Market Companion | `§4D` |
| Old `§16` Reckless Ben | `§4J` |
| Old `§17` rebuild/incident response | `§3F`, `§3G`, `§6C` |
| Old `§18` sequencing | `§5`, `§6`, `§9` |
| Old `§19` standards loop | `§3H`, `§9A` |
| Old `§20` next work | `§11` |

**Unmigrated safely**

- `TODO.md` roadmap references: left unchanged because `TODO.md` is protected task input.
- Historical `_internal/outbox/` and agent logs: left unchanged as evidence.
- Private VPS runbook stale privilege statements: not edited in this task because `_internal/` is protected; later workflow maintenance should reconcile it with Session 3/4 evidence.
- `repos/traderie/PHASE_B_CODEX_PACKET.md`: marked superseded because it is a historical phase packet, not current execution authority.
- `repos/traderie/STATUS.md`: already marked deprecated and historical, so its old blocker list was left unchanged.

## §11 Current Next Work

1. Run the medium-agent packets prepared under `_internal/outbox/session5/` for `§9E`, `§9F`, `§9G`, and bounded repository readiness.
2. Run `§9B` Traderie recovery as a separate production recovery session.
3. Run `§9C` Reddit Ops publication strategy as a separate Git/history session.
4. Implement `§9E` PostgreSQL reusable platform products and `§9F` Phase 0 health in parallel with source-only readiness work.
5. Run `§9G` SJC Intel readiness after the reusable gate model is accepted.
6. Run `§9H` Platform Confidence Review before any Wave 1 cutover.

## §12 Decisions Requiring Buddy

| Decision | Why Buddy is required |
|---|---|
| Reddit Ops publication strategy | Credential-bearing history blocks normal push |
| Reboot timing and privilege path | Reboot affects production workloads |
| WGU-derived repository/workload ownership | Current split is unresolved and should not be inferred |
| WGU Catalog activation mode | Automatic monthly check, approval-gated trigger, or manual operator run |
| License choices | Several repositories lack licenses |
| Destructive cleanup or legacy data deletion | Requires exact target approval |
