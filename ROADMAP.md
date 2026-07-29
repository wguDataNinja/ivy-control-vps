# Ivy Control VPS Roadmap

**Status:** Portfolio-wide strategic direction. Defines where the portfolio is
investing, what phases each major workstream follows, and what gates govern
progression. Implementation detail lives in `TODO.md` and per-repo ROADMAP.md
files.

**Architectural decisions:** See `docs/STRATEGIC_ARCHITECTURE.md` for durable
architectural decisions, portfolio thesis, and sequencing rationale. This roadmap
references that document rather than duplicating all rationale.

**Updated:** 2026-07-29

---

## §0 Operator Summary

### Current observation surface

```sh
./tools/open_ingestion_dashboard.sh
```

For a read-only terminal summary suitable for a future Hermes healthcheck, run:

```sh
python3 tools/ingestion_dashboard.py --no-live --summary --stdout-only
```

Evidence precedence: live measurement, validated producer payload, read-only
database/service inspection, control document, roadmap, placeholder, then
unknown. A control- or roadmap-only claim can never be green; missing evidence
is **UNKNOWN**, not healthy.

### Current workload truth

| Workload | Current classification | Immediate issue | Evidence |
|---|---|---|---|
| Reddit Ops | `CANDIDATE_CANONICAL` | Backup recovery proven; canonicality review pending | Live dashboard + `repos/reddit-ops/CONTROL.md` |
| Idle Hacking chat | `CAPTURING_BUT_NOT_DURABLE` | Acknowledgement, replay, archive continuity open | Live dashboard |
| Idle Hacking market | `CAPTURING_BUT_NOT_DURABLE` | Same durability gap | Live dashboard |
| Traderie | `DEGRADED_BUT_BOUNDED` | Focused `pc_hc_nl` recovery | `repos/traderie/CONTROL.md` |
| VPS capacity | `CURRENTLY_ACCEPTABLE` | Ongoing monitoring | Live dashboard |

### Immediate P0 priorities

1. Progress Reddit Ops canonicality review toward Buddy gate decision.
2. Prove recent completeness, archive-to-VPS continuity, single-writer canonicality.
3. Make Idle Hacking chat and market health truthful, separate, acknowledged, replayable.
4. Add missing dashboard adapters before claiming portfolio ingestion is trustworthy.
5. Keep Traderie in focused recovery; do not reopen architecture.

---

## §1 Portfolio Direction

### North star

A portfolio of independently governed repositories, each with:
- a clear purpose and owner-approved direction (ROADMAP.md);
- bounded agent execution with controlled strong-model handoffs;
- operational evidence that distinguishes known from unknown;
- autonomous VPS infrastructure where warranted.

### Strategic priorities

1. **Prototype capability** — Demonstrate reusable application architecture (Palworld KB / STS).
2. **Research pipeline** — Demonstrate extraction/classification at scale (Adult Research Ontology).
3. **Infrastructure baseline** — All active repos operating from autonomous VPS infrastructure.
4. **Automation** — Reduce manual toil through scheduled autonomous collection and intelligence generation.
5. **Completeness** — Finish and publish what exists (WGU Atlas, BSDA Courses).

### Repo ownership map

| Repository | Lifecycle | Portfolio role |
|---|---|---|
| palworld-kb | `source-only` | Capability prototype |
| reddit-ops | `production-runtime` | Data pipeline |
| traderie | `production-runtime` | Data pipeline |
| idlehacking-kb | `browser-dependent` | Knowledge system |
| ih-market-companion | `browser-dependent` | Market collection |
| sjc-intel | `source-only` | Intelligence research |
| sts-workbench | `source-only` | V1 finish-line (Nitewing voice assistant) |
| wgu-catalog | `batch` | Data source |
| wgu-atlas | `downstream` | LLM consumer |
| bsda-courses | `downstream` | LLM consumer |
| reckless-ben | `restricted` | Governance reference |

---

## §2 Active Initiatives

### §2A Reddit Ops canonicality — `§7B-G1`

**State:** `CANDIDATE_CANONICAL` / **BLOCKED BY GATE** for legacy retirement.

Backup recovery is proven (natural timer run at 2026-07-16 08:00:14 UTC produced
valid artifact). Canonicality adapters needed before `VERIFIED_CANONICAL`
declaration. Git publication blocked by credential-bearing commit.

**Completion unlocks:** `VERIFIED_CANONICAL` review and legacy retirement decision.

### §2B Idle Hacking durability

**State:** `CAPTURING_BUT_NOT_DURABLE`.

Chat and market capture are operational but lack acknowledgement, replay,
archive continuity, and truthful current-failure health semantics. IH ownership
and acknowledgement destination pending Buddy decision.

### §2C Traderie bounded recovery — `§7A-G1`

**State:** `DEGRADED_BUT_BOUNDED`.

First natural scheduled generation (2026-07-11) partially failed — `pc_hc_nl`
segment timed out at 480 seconds. Focused recovery only: timeout investigation,
health reconciliation, natural-run proof, reboot proof.

### §2D Dashboard and adapters

**State:** Transitional local dashboard implemented (`open_ingestion_dashboard.sh`).
Missing adapters: Reddit canonicality, Traderie live exporter, IH verification,
IH acknowledgement/backlog, VPS capacity.

### §2E Per-repo roadmaps

Repositories with sufficient complexity should have their own ROADMAP.md with
phased execution detail, dependency maps, and implementation chunks. See
`docs/REPOSITORY_CONTROL_MODEL.md` §Per-repo roadmap for the contract.

---

## §3 Shared Platform Gates

### §3A Canonical Ingestion-Admission

Every ingestion workload must evidence collector, scheduler, writer, SHA,
entrypoint, lock, health, backup, restore, rollback, archive role, legacy
scheduler status, manual and natural run success, and exactly one production
writer.

### §3B PostgreSQL onboarding

Shared products: onboarding guide, migration templates, role matrix, importer
contract, backup/restore process, restore drill checklist. Not every repo needs
PostgreSQL.

### §3C Deployment and exact SHA

Exact-SHA deployment, checkout cleanliness, source hash verification, drift
detection, rollback SHA tracking.

### §3D Scheduler and natural-run

Systemd unit validation, one-scheduler/one-writer evidence, locking,
timeout/progress evidence, timer acceptance, reboot recovery.

### §3E Health, backup, capacity

Health producers with v2 evidence, capacity monitoring (disk, inodes, memory,
PostgreSQL, WAL, backup staging), browser hardening products.

### §3F Platform Confidence

Before a new production wave: dashboard exposes current evidence, capacity
within threshold, backup/restore works, one-writer demonstrable, bounded
privileged execution sufficient.

---

## §4 Repository Advancement Model

### §4A Independent advancement

Repositories advance independently through: local completion → tests + docs →
GitHub readiness → VPS footprint review → source-only clone → optional DB →
optional production activation.

### §4B Placement

- Git: code, schemas, migrations, tests, docs, small fixtures.
- VPS: approved clone, recent operational data, bounded runtime, logs outside checkout.
- Mac: large/private corpus, raw archives, long retention, browser backups.
- Never Git: live DBs, dumps, profiles, raw archives, secrets, mutable runtime.

### §4C Per-repo status

| Repo | Code | GitHub | VPS | Runtime | Archive | Hermes |
|---|---|---|---|---|---|---|
| Reddit Ops | Mac | blocked | deployed | VPS PG + collector | Mac | read-only |
| Traderie | Mac | published | deployed | VPS PG + systemd | Mac | read-only |
| IH Market Companion | Mac | published | helper | browser + helper | Mac | read-only |
| Idle Hacking KB | Mac | privacy | metadata DB | VPS metadata | Mac | read-only |
| SJC Intel | Mac | prepare | none | none | Mac | read-only |
| Palworld KB | Mac | published | none | none | none | read-only |
| STS Workbench | Mac | none | none | none | none | read-only |
| WGU Catalog | Mac | published | none | none | none | read-only |
| WGU Atlas | Mac | published | none | none | none | none |
| BSDA Courses | unknown | unknown | none | none | none | none |
| Reckless Ben | unknown | unknown | none | none | none | none |

---

## §5 Completed Milestones

Completed work is historical evidence, not active execution:

- Traderie: PostgreSQL schema/roles/migrations, backup/isolated restore,
  segmented runtime, sole VPS authority. Natural-run recovery remains open.
- Reddit Ops: migration, roles, locking, frontier/idempotence, approved-partial
  semantics. Backup unit drift and canonicality remain open.
- Idle Hacking KB: metadata onboarding, idempotent reconciliation, isolated
  restore, archive verification. Health semantics and archive ack remain open.
- IH Market: bounded retention, helper deployment, publication. Archive and PG
  reconciliation remain open.
- Dashboard: transitional CLI implemented. Missing named adapters.

---

## §6 Hermes Evolution

**Current:** read-only inspection, health comparison, status reports, drift
detection, bounded evidence requests. Not a production controller.

**Next stage:** After clean clone, scoped credential/audit design, test/secret-
scan checks, and per-repo Buddy approval: inspect VPS clones, identify bounded
work, create isolated branches, run tests, prepare PRs.

**Still prohibited:** self-merge, autonomous deployment, database mutation,
broad secrets access, destructive operations, unrestricted service control.

---

## §6A Autonomous Branch-to-PR Pilot — Completed

**Status:** COMPLETED — Session 13 executed the complete branch-to-PR pilot
on Palworld KB. Git Steward MVP was implemented, the Palworld baseline was
published, a draft PR was created, reviewed for Gate 3 readiness, and merged.

The pilot demonstrated:
- Git Steward MVP (53 tests, three-gate model: validate, publish-branch, create-draft-pr)
- Controlled publication with explicit per-gate Buddy approval
- PR creation, review, and merge under three-gate authority
- Approval consumption and cryptographic authority digest
- Portfolio-view creation and Hermes-to-OpenCode delegation contract

### What was proven

1. Branch-to-PR-to-merge delivery loop on one repository (palworld-kb)
2. Independent Gate 1, Gate 2, Gate 3 approvals
3. Git Steward secret/absolute-path/protected-path/large-file validation
4. Approval authority digest binding approval state to execution evidence
5. Deterministic evidence and sanitized reporting
6. Read-only PR review and merge-readiness assessment

### What remains unproven

1. Hermes-first orchestration (delegation contract defined, pilot not executed)
2. Multi-repository orchestration (envelope design not yet attempted)
3. Hermes-per-repo credential model
4. VPS workspace management and deterministic gates for non-Palworld repos
5. STS Workbench managed-repository admission
6. Cross-repository dependency orchestration (Palworld-to-STS)

### Deferred

- General autonomous orchestration service
- STS reusable adapter extraction
- Provider abstraction framework
- Idle Hacker consolidation
- Automated deployment
- Broad portfolio-scale generalization

---

## §6B Hermes Continuous Orchestration — In Progress

**Status:** IN PROGRESS — Phase 4 (two delegation cycles completed and validated). Hermes is evolving from a guided task-executor
toward a continuous orchestration layer that selects bounded work, delegates
to execution agents, reviews evidence, updates continuity, and proceeds
without requiring Buddy to approve every routine step.

### Phases

**Phase 1: Complete the repository governance baseline**
- The Branch Integration Workflow, preflight gate, terminology, and
  command-plan self-review are now documented in `docs/GIT_WORKFLOW.md`.
- All Hermes governance contracts are canonical in the repository.
- The repository is authoritative for all operating rules; Hermes memory is
  a compact runtime summary derived from it.

**Phase 2: Establish the standard delegation cycle**
- The repeatable process is documented in `agents/HERMES_AGENT_CONTRACT.md`
  §3.5f: preflight, isolation, numbering, packet creation, OpenCode
  delegation, result reporting, Hermes review, evidence reconciliation, and
  human publication gate.
- Validate and fill remaining gaps during trials rather than pre-building.

✅ **Phase 3: Complete**
- Ran one complete trial on a bounded real task. Hermes oriented, inspected Git state,
  isolated, numbered, created the packet, delegated to OpenCode, received
  the report, inspected the result, reconciled evidence, and stopped at the
  human gate.
- The trial validated the delegation contract and identified documentation
  gaps before broader use.

✅ **Phase 4: Complete**
- H0–H3 supervised-cycle contracts, decision-packet schemas, isolated worktree tests, and maker/checker cycle implemented and merged (31 passing tests). Session 13 Palworld pilot artifacts preserved as canonical reference.
- `docs/HERMES_ORCHESTRATION_CONTRACTS.md`, `schemas/hermes_orchestration/decision-packet.schema.json`, `schemas/hermes_orchestration/supervised-cycle.schema.json` merged.

**Phase 5: Begin normal roadmap execution** — ⬆️ In progress
- Hermes works through properly sized roadmap tasks one at a time.
- OpenCode remains the default executor unless demonstrated otherwise.
- Hermes may propose the next task without requiring Buddy to choose
  every work item individually.

**Phase 6: Expand autonomy after proven reliability**
- Only after repeated reliable operation should the project consider:
  portfolio task selection, automatic task decomposition, alternative
  executors, concurrency, or broader autonomy.
- This is a later design review, not an assumed destination.

### Dependencies
- Human operator provides plain-language trial objectives and selects
  initial tasks.
- Documentation and repository governance are complete.
- No infrastructure, deployment, database, or production changes required.

### Risks
- Hermes may attempt to implement rather than delegate (mitigated by
  role-separation rule and governance contracts in
  `agents/HERMES_AGENT_CONTRACT.md` §3.5f).
- OpenCode unavailability would block the trial.
- Trial may reveal documentation gaps requiring iteration.

---

## §6C H4 Supervised-Cycle Pilot — STS Workbench Dirty-State Preservation

**Status:** COMPLETED — H4 accepted and H4.1 local-custody pilot completed 2026-07-29.

**Pilot repository:** STS Workbench (`/Users/buddy/projects/sts-workbench`)
**Roadmap item:** `STS-V1-01` — Dirty-State Preservation and Reconciliation (per `docs/V1_FINISH_LINE_ROADMAP.md`)

**Scope:** Classify every dirty tracked/untracked path in the STS Workbench checkout, record non-destructive preservation options, and produce a path-to-classification table. Allowed files: `agent/inbox/`, `agent/reports/`, `agent/INDEX.md` in isolated worktree only. Denied: `v1/**`, `docs/**`, `HANDOFF.md`, `TODO.md`, Git staging/commit/reset/stash/clean, `_internal/**`, all network/runtime paths.

**Boundaries:** No product/runtime/credential/publishing scope. No Git mutation. Human gate: Buddy chooses preservation strategy.

**Preconditions:** STS Workbench admitted as managed repository (`repos/sts-workbench/CONTROL.md` created). ivy-control-vps baseline clean and authoritative.

**Outcome:** H4 accepted; H4.1 committed one accepted manifest in an isolated
STS branch at `cd36e36`, found/fixed porcelain-output handling, and reset
`local_commit` to false. Canonical report:
`_internal/orchestration/repos/sts-workbench/tasks/h4-sts-h4-1-summary/final-report.md`.

---

## §6D Managed-Repository Admission: STS Workbench

**Status:** ADMITTED — source-only control record established 2026-07-29.

**Activities:**
- `repos/sts-workbench/CONTROL.md` established; source-only and no remote.
- STS-V1-02 remains gated by its existing Buddy decision packet.

1. Reddit Ops clean publication/history strategy.
2. Reddit Ops legacy fallback retirement (after canonicality proven).
3. Canonical Idle Hacking userscript source and duplicate disposition.
4. Chat/market archive acknowledgement destination and authority.
5. Browser-profile inspection/recovery/install-verification procedure.
6. Controlled reboot timing.
7. Hermes PR credentials and scope per repo.
8. Palworld KB VPS source-only clone timing.
9. Per-repo ROADMAP.md creation priority and timing.
10. Palworld 36-commit publication audit disposition.
11. First pilot credential model (fine-grained PAT vs GitHub App).
12. ✅ STS Workbench managed-repository admission timing — Buddy approved 2026-07-29. CONTROL.md creation in progress.
