# Documentation Index

This index is the operational map for agents and maintainers working with IvyControlVPS. It lists every document in the repository and serves as the entry point for understanding the repo's structure and purpose.

## Documents

### Active authority — read first

| Document | Purpose |
|----------|---------|
| [`README.md`](../README.md) | Public repository overview — purpose, current stage, design principles |
| [`PORTFOLIO.md`](PORTFOLIO.md) | Human portfolio working view — Buddy's all-project surface for priorities, notes, direction, and decisions |
| [`PORTFOLIO_INTENT.md`](PORTFOLIO_INTENT.md) | Buddy Intent Layer — what Buddy cares about, current priorities, Hermes alignment target |
| [`ROADMAP.md`](../ROADMAP.md) | Portfolio-wide strategic direction — investment priorities, active initiatives, shared gates |
| [`OPERATING_MODEL.md`](OPERATING_MODEL.md) | Operating model — public/private boundary, living standards, Git, deployment, agents, documentation maintenance |
| [`PORTFOLIO_UNIVERSE.md`](PORTFOLIO_UNIVERSE.md) | Curated known portfolio universe — asset relationship, classification, value context, and discovery confidence; not live operational status |
| [`REPOSITORY_CONTROL_MODEL.md`](REPOSITORY_CONTROL_MODEL.md) | Portfolio repository-control model — governance mechanism, standards applicability, gate framework, approved SHA tracking, per-repo roadmap contract |
| [`REPOSITORY_WORK_PROTOCOL.md`](REPOSITORY_WORK_PROTOCOL.md) | Work-continuity protocol — task identity, result reports, logs, journals, review, and promotion into canonical documentation |
| [`GIT_WORKFLOW.md`](GIT_WORKFLOW.md) | Git workflow — branch naming, commits, PRs, agents, VPS provisional rules, git-steward delegation |
| [`HEALTH_CONTRACT.md`](HEALTH_CONTRACT.md) | Canonical health/evidence semantics for operational workloads |

### Supporting technical reference — read when the task needs it

| Document | Purpose |
|----------|---------|
| [`PORTFOLIO_CONVENTIONS.md`](PORTFOLIO_CONVENTIONS.md) | Cross-repo conventions and VPS admission requirements — PostgreSQL naming, backup/restore, systemd, health contract, deployment prerequisites, gates, and stop conditions |
| [`DATA_LIFECYCLE_STANDARD.md`](DATA_LIFECYCLE_STANDARD.md) | Portfolio data-lifecycle principles — data classes, retention, growth measurement, disk thresholds, health metrics |
| [`LOGGING_STANDARD.md`](LOGGING_STANDARD.md) | Three-layer logging standard — machine/runtime, agent work, and GPT/planning logs |
| [`LLM_TENETS.md`](LLM_TENETS.md) | Design tenets for auditable, constrained, portable, and data-efficient LLM systems |
| [`RESIDENT_AGENT_MODEL.md`](RESIDENT_AGENT_MODEL.md) | Resident Agent Interface architecture — **redirect**; content merged into `OPERATING_MODEL.md` §Hermes and agents |

### Operations and access

| Document | Purpose |
|----------|---------|
| [`VPS_ACCESS.md`](VPS_ACCESS.md) | VPS access procedures — SSH, SCP, desktop access, identity key management |
| [`VPS_ADMISSION_CHECKLIST.md`](VPS_ADMISSION_CHECKLIST.md) | VPS repository admission evidence checklist — supporting checklist for the deployment requirements in `PORTFOLIO_CONVENTIONS.md` |
| [`DATABASE.md`](DATABASE.md) | Database architecture and operations — PostgreSQL topology, schema ownership, migrations, backup/restore, and operation history |
| [`HERMES_OPERATOR_GUIDE.md`](HERMES_OPERATOR_GUIDE.md) | Hermes operator guide — bridge protocol, orientation, independent verification, file-based communication loop |

### Agent contracts

| Document | Purpose |
|----------|---------|
| [`../agents/VPS_ORCHESTRATION.md`](../agents/VPS_ORCHESTRATION.md) | VPS/Hermes orchestration contract — interaction modes (read-only inspection, bounded mutation, full production), approval boundaries, logging |
| [`../agents/orchestrator-task-packet-template.md`](../agents/orchestrator-task-packet-template.md) | Reusable Mode 0 task-packet template — execution aid, not authority |
| [`../agents/LOCAL_IMPLEMENTATION.md`](../agents/LOCAL_IMPLEMENTATION.md) | Local implementation agent contract — rules for OpenCode, Codex, and similar agents operating from this repository |

### Health subsystem

| Document | Purpose |
|----------|---------|
| [`health/adapter-interface.md`](health/adapter-interface.md) | Health adapter interface contract — required schema for producer registration, normalized health fields |
| [`health/api-alert-boundaries.md`](health/api-alert-boundaries.md) | API alert boundary definitions — thresholds for freshness, failure counts, disk, memory, and database growth |
| [`health/portfolio-conformance-matrix.md`](health/portfolio-conformance-matrix.md) | Portfolio-wide health conformance matrix — which producers are registered, their current health semantic alignment, and gaps to v2 contract compliance |
| [`health/producer-registry.md`](health/producer-registry.md) | Registered health producers — exact producer-ids, current schema versions, and registration metadata |
| [`health/schemas/portfolio_health_schema.json`](health/schemas/portfolio_health_schema.json) | JSON Schema for portfolio health reports — validation target for all adapters |
| [`health/database/normalized_health_schema.sql`](health/database/normalized_health_schema.sql) | Normalized PostgreSQL schema for aggregated portfolio health |

### Traderie governance

| Document | Purpose |
|----------|---------|
| [`repos/traderie/CONTROL.md`](../repos/traderie/CONTROL.md) | Traderie governance control sheet — production authority, lifecycle state, approved SHA, unresolved gates |
| [`repos/traderie/RELEASE_GATES.md`](../repos/traderie/RELEASE_GATES.md) | Traderie release gate evidence — deployment proof, runtime gate status, health check results |
| [`repos/traderie/PHASE_B_CODEX_PACKET.md`](../repos/traderie/PHASE_B_CODEX_PACKET.md) | Traderie Phase B Codex execution packet — superseded; retained as historical execution evidence |
| [`repos/traderie/STATUS.md`](../repos/traderie/STATUS.md) | Traderie VPS status — deprecated; replaced by CONTROL.md. Retained as historical reference only |

### Reddit Ops governance

| Document | Purpose |
|----------|---------|
| [`repos/reddit-ops/CONTROL.md`](../repos/reddit-ops/CONTROL.md) | Reddit Ops governance control sheet — production authority, lifecycle state, unresolved gates |
| [`repos/reddit-ops/RELEASE_GATES.md`](../repos/reddit-ops/RELEASE_GATES.md) | Reddit Ops release gate evidence — frontier, idempotence, locking, migration, OAuth gates |
| [`repos/reddit-ops/CUTOVER_HISTORY.md`](../repos/reddit-ops/CUTOVER_HISTORY.md) | Reddit Ops PostgreSQL cutover chronology — two failed attempts, root cause, final cutover |
| [`repos/reddit-ops/STABILIZATION.md`](../repos/reddit-ops/STABILIZATION.md) | Reddit Ops stabilization checklist — 13 gates remaining to production-complete |
| [`repos/reddit-ops/RUNBOOK.md`](../repos/reddit-ops/RUNBOOK.md) | Reddit Ops operational runbook — health checks, manual run, rollback, drift detection |

### Public workflows

| Document | Purpose |
|----------|---------|
| [`../workflows/README.md`](../workflows/README.md) | Public engineering-work lifecycle — task, result, log, journal, and intentional promotion |
| [`../workflows/session-close.md`](../workflows/session-close.md) | Supporting safe-close procedure |

### Historical public reference

| Document | Purpose |
|----------|---------|
| [`PORTFOLIO_BASELINE.md`](PORTFOLIO_BASELINE.md) | Dated portfolio assessment baseline — historical inventory, patterns, and gaps; current state remains in ROADMAP and CONTROL records |
| [`historical/FOUNDATION_SESSIONS_1_8.md`](historical/FOUNDATION_SESSIONS_1_8.md) | Completed foundation sessions and period priorities — preserved historical public evidence |

## Core reading path

Read these first to understand the control plane. Do not read every supporting document unless the task needs it.

1. [`README.md`](../README.md) — what this repository is and is not
2. [`PORTFOLIO.md`](PORTFOLIO.md) — Buddy's all-project view: priorities, direction, notes, decisions
3. [`ROADMAP.md`](../ROADMAP.md) — what requires attention now and why
4. [`OPERATING_MODEL.md`](OPERATING_MODEL.md) — why the control plane exists and how the portfolio is governed
5. [`PORTFOLIO_UNIVERSE.md`](PORTFOLIO_UNIVERSE.md) — what is known to exist; read this before inferring importance from admission
5. [`REPOSITORY_CONTROL_MODEL.md`](REPOSITORY_CONTROL_MODEL.md) — how portfolio standards apply to each managed repository
6. [`REPOSITORY_WORK_PROTOCOL.md`](REPOSITORY_WORK_PROTOCOL.md) — how substantial work becomes reviewed, durable evidence
7. [`GIT_WORKFLOW.md`](GIT_WORKFLOW.md) — how tracked changes are branched, packaged, and reviewed
8. [`HEALTH_CONTRACT.md`](HEALTH_CONTRACT.md) — how operational evidence is represented and evaluated
9. The relevant `repos/<repo>/CONTROL.md` — current repository-specific authority

## Task-specific reading

Read these only when applicable to the assigned work:

- Applicable portfolio standards:
   - `PORTFOLIO_CONVENTIONS.md` — shared technical conventions and VPS admission requirements
   - `HEALTH_CONTRACT.md` — health reporting contract and producer registry
   - `DATA_LIFECYCLE_STANDARD.md` — retention, pruning, storage thresholds
   - `LOGGING_STANDARD.md` — logging for machine, agent, and planning work
   - `GIT_WORKFLOW.md` — Git branch naming, commits, agent rules
   - `LLM_TENETS.md` — LLM system design principles
- Detailed gate evidence or phase packet only when the task requires gate-specific detail.
- For public work lifecycle, read [`../workflows/README.md`](../workflows/README.md) and `REPOSITORY_WORK_PROTOCOL.md`. A locally provisioned private supplement may add private mechanics but is not required for clone orientation.
- For VPS operational work, read `agents/VPS_ORCHESTRATION.md` first. A private local runbook may provide approved host-specific procedures when it is provisioned.
- For Hermes bridge interaction, read `HERMES_OPERATOR_GUIDE.md` — bridge protocol, orientation flow, independent verification.

## Actor-specific reading paths

### New human maintainer

```
README.md → PORTFOLIO.md → OPERATING_MODEL.md → REPOSITORY_CONTROL_MODEL.md
→ targeted repos/<repo>/CONTROL.md
```

Read the core reading path (above) in order. Skip task-specific, agent, and Hermes documents until they become relevant.

### OpenCode execution agent

```
AGENTS.md + agents/LOCAL_IMPLEMENTATION.md
→ docs/README.md core reading path
→ PORTFOLIO.md (Buddy priorities and direction)
→ REPOSITORY_WORK_PROTOCOL.md
→ GIT_WORKFLOW.md
→ target repos/<repo>/CONTROL.md
→ task-relevant standards
```

The agent reading order is defined in `agents/LOCAL_IMPLEMENTATION.md`. Follow it exactly.

### Strong Codex (architecture work)

```
Core reading path
→ PORTFOLIO_CONVENTIONS.md
→ HEALTH_CONTRACT.md
→ DATA_LIFECYCLE_STANDARD.md
→ agents/VPS_ORCHESTRATION.md
→ relevant repos/<repo>/CONTROL.md + RELEASE_GATES.md
```

Strong Codex needs the broadest path due to architecture, deployment, and database authority.

### Hermes (orchestration)

```
agents/HERMES_AGENT_CONTRACT.md
→ PORTFOLIO.md (Buddy's all-project view)
→ docs/PORTFOLIO_INTENT.md (formal intent layer)
→ docs/OPERATING_MODEL.md (resident agent model, authority model)
→ agents/VPS_ORCHESTRATION.md
→ docs/HERMES_OPERATOR_GUIDE.md
→ REPOSITORY_WORK_PROTOCOL.md (artifact-only orchestration §)
→ target repos/<repo>/CONTROL.md
→ orchestrator-task-packet-template.md
```

Hermes reads agent contracts before repository governance because its authority model is defined there.

## Fresh-agent repository intelligence route

After the core reading path, a new agent can orient using three read-only generated views:

```sh
./tools/show_portfolio_status.sh --no-color
python3 tools/ingestion_dashboard.py --no-live --summary --stdout-only
./tools/show_ready_work.sh
```

The first view is a **derived managed-record summary**: purpose, lifecycle, control-record state, blocker, and next task. The second is a **derived observation summary**: current evidence or an explicit `UNKNOWN`, never a status inferred from Git activity. The third is a filtered task convenience view, not a replacement for `ROADMAP.md` or a repository's authorized next work.

For the authoritative distinction and refresh rules, see [`REPOSITORY_CONTROL_MODEL.md`](REPOSITORY_CONTROL_MODEL.md#portfolio-intelligence-and-refresh). Generated output is for orientation and routing; confirm a decision in the relevant `CONTROL.md`, health evidence, and roadmap before acting. For public recent-work context, use `ROADMAP.md` completed milestones and Git history; private reports and journals are not assumed to be available in a clone.

## Authority model

### Hierarchy

The portfolio uses a layered authority model:

```
Buddy Intent Layer
docs/PORTFOLIO_INTENT.md
  ↓
Portfolio Roadmap
ROADMAP.md
  ↓
Repository Roadmaps (per managed repo)
repos/<repo>/ROADMAP.md
  ↓
Implementation Specs (per chunk)
(referenced from repo ROADMAP.md)
  ↓
Execution Queues
TODO.md
  ↓
Agent Task Results
_internal/outbox/
  ↓
Journals / History
_internal/logs/
```

Each layer answers a different question:

| Layer | Question | Authority |
|---|---|---|
| Intent | What matters? | `docs/PORTFOLIO_INTENT.md` |
| Portfolio roadmap | Where are we investing? | `ROADMAP.md` |
| Repository roadmap | How do we build it? | `repos/<repo>/ROADMAP.md` (where it exists) |
| Implementation spec | Exactly what should happen? | Referenced from repo roadmaps |
| Execution queue | What does the agent do next? | `TODO.md` |
| Result report | What happened? | `_internal/outbox/` artifacts |
| Journal | What did we learn? | `_internal/logs/sessions/SESSION_JOURNAL.md` |
| Why does Ivy Control exist? | `docs/OPERATING_MODEL.md` |
| What exists and how does it relate to the portfolio? | `docs/PORTFOLIO_UNIVERSE.md` |
| What is currently authorized or true for one managed repository? | `repos/<repo>/CONTROL.md` |
| What proves workload health and evidence confidence? | `docs/HEALTH_CONTRACT.md` plus dated producer/evidence artifacts |
| How do humans and agents perform and preserve work? | `docs/REPOSITORY_WORK_PROTOCOL.md` |
| How are tracked changes branched, reviewed, and integrated? | `docs/GIT_WORKFLOW.md` |
| How is the public work lifecycle organized? | `workflows/README.md` and `docs/REPOSITORY_WORK_PROTOCOL.md` |
| What is private? | Local-only supplements may exist, but they are not public-clone authority or dependencies. |

`ROADMAP.md` is the portfolio-wide strategic direction. Per-repo `CONTROL.md` files govern individual repository lifecycle, production authority, and gate status. `docs/PORTFOLIO_INTENT.md` captures what Buddy cares about — the layer Hermes watches for alignment checks. Per-repo `ROADMAP.md` files hold phased execution detail with dependency maps and implementation chunks.

Portfolio standards (`PORTFOLIO_CONVENTIONS.md`, `HEALTH_CONTRACT.md`, `DATA_LIFECYCLE_STANDARD.md`, etc.) define cross-repo conventions that CONTROL.md records must comply with or explicitly deviate from.

```
docs/PORTFOLIO.md (Buddy's all-project working view — notes, priorities, direction)
  └── docs/PORTFOLIO_INTENT.md (Buddy's formal intent layer — what Hermes watches)
        └── ROADMAP.md (portfolio-level strategic direction)
              └── repos/<repo>/CONTROL.md (managed lifecycle, support, gates, deviations)
                    └── repos/<repo>/ROADMAP.md (per-repo execution detail)
                          └── standards and dated evidence (how claims are evaluated)
```

A repo `CONTROL.md` may grant a standards exception; the standards may not override a CONTROL.md exception. `ROADMAP.md` may override a CONTROL.md gate only during an authorized campaign phase.

### Active vs historical materials

The core governance documents above are active authority. Technical standards and runbooks are supporting reference unless their own status line says otherwise; dated baselines, deprecated status files, and completed phase packets are historical evidence. Old-tree documents (from the predecessor `ivy-control/vps/` path) are not present in this repository. Any reference to an old-tree file is a historical marker, not an active-reading link.

### CONTROL.md role

Each managed repository has a control sheet at `repos/<repo>/CONTROL.md` that records:
- lifecycle state and production authority;
- approved SHA and deployment status;
- standards compliance state and accepted deviations;
- current blockers and next authorized work.

A repository without a CONTROL.md is not yet under active portfolio governance.

### Portfolio universe and managed registry

`PORTFOLIO_UNIVERSE.md` is the curated, human-readable known asset universe. It includes infrastructure, historical lineage, restricted assets, and acknowledged external/private assets as appropriate. It is explicitly incomplete until a separately approved discovery task reconciles it.

The **managed registry** is a derived/aggregated view of CONTROL.md records, generated by a tool such as `tools/portfolio_registry.py` or an extended health view. It does not replace CONTROL.md as the per-repo source of truth, and it is not the complete portfolio universe.

### Private session artifacts

`_internal/outbox/` contains ignored session artifacts — execution packets, evidence files, and intermediate reports produced during GPT-orchestrated work. These files are not durable Git authority. They are retained for provenance and traceability but must not be treated as active standards, policy, or configuration. The authority table above, including root `ROADMAP.md` and per-repository control records, identifies the current sources of truth.

## Repository Documentation Contract

Every Ivy-portfolio repository is expected to have a consistent set of
documents forming a governing contract. A repository that is missing any of
these has a documentation gap.

### Contract documents

| Document | Purpose | Authority |
|----------|---------|-----------|
| `README.md` | Human/project orientation. What is this repo? How does someone understand it quickly? | Root `/README.md` for ivy-control-vps; repo-local for managed repos. |
| `ROADMAP.md` | Owner-approved long-horizon direction. Strategic decisions, future milestones, sequencing principles. Must not become an implementation checklist. Changes require Buddy approval. | Root `/ROADMAP.md` (portfolio-wide). Managed repos may have their own for project-specific direction. |
| `TODO.md` | Short-term implementation queue. Near-term work derived from ROADMAP. Detailed enough for implementation agents. May be updated during execution workflows. | Root `/TODO.md` (session-scoped). Managed repos may have their own for local queue. |
| `AGENTS.md` | Agent operating instructions. Repo-specific constraints, workflows, validation commands, boundaries. Only information important enough for every agent working in this repo. | Per-repository where agent interaction is expected. |
| `CONTROL.md` | Ivy control-plane relationship. Lifecycle, gates, evidence expectations, ownership metadata. Not a project roadmap. Not a duplicate README. | `repos/<repo>/CONTROL.md` for managed repos only. |
| Evidence, logs, journals | Historical execution and operational proof. Result reports, gate packets, agent logs, session journals. Not replacement documentation. | `_internal/outbox/`, `_internal/logs/`, `repos/<repo>/RELEASE_GATES.md`, `repos/<repo>/RUNBOOK.md` etc. |

Unmanaged repositories are not expected to have `CONTROL.md` but benefit from
the other contract documents.

### `README_INTERNAL.md` is not a required standard

The old `README_INTERNAL.md` pattern (a private catch-all document under
`_internal/`) is no longer a required or expected convention. Existing files
should be audited:

- duplicate public content → migrate to the correct authority or remove
- agent instructions → `AGENTS.md`
- project direction → `ROADMAP.md`
- implementation queue → `TODO.md`
- historical execution → logs, journals, or archive
- genuinely private content that has no public authority home → retain as-is

### Documentation creation governance

Before adding or modifying any documentation, check whether an existing
authority document already owns the information. This is not a ban on
documentation — it is a rule against duplicate authority.

Every proposed new document must answer:

1. **What question does this document answer?**
2. **Which existing authority does not already answer it?**
3. **Who owns updates to it?**
4. **Why should this not live in an existing document?**

If the answers are unclear, do not create the document. Route the content to
the correct existing authority instead.

This rule is discoverable from `AGENTS.md` (Development behavior),
`docs/REPOSITORY_WORK_PROTOCOL.md` (§7 — making a tracked change), and
every agent entry path. If you encounter a request to create a new document
that does not satisfy these checks, stop and escalate.

## Predecessor tree

The `ivy-control/vps/` directory in the old `ivy-control` repository contains historical planning documents, completed execution evidence, and reference material that has not been promoted here.

The current authority set lives in this repository. Old-tree material is reference-only unless explicitly cited by a current CONTROL.md, RELEASE_GATES.md, or phase packet. No old-tree document overrides an active document in this repository.

Private VPS access details and local evidence may be provisioned separately for an authorized VPS task. They are not part of the public repository or normal clone reading path; `agents/VPS_ORCHESTRATION.md` defines the public interaction boundary first.

## New documents

A new document must serve a distinct durable authority role that no existing document can absorb. Before creating a file, identify its unique purpose, why an existing document cannot hold the material, and which current document it supersedes or complements. Index it here on creation.

The documentation creation governance rules above (under Repository Documentation Contract) are the authority for this gate. This section is preserved as the index location where new documents are recorded.


## Historical public material

The completed foundation narrative formerly held in this navigation page is preserved at [`historical/FOUNDATION_SESSIONS_1_8.md`](historical/FOUNDATION_SESSIONS_1_8.md). It is not current execution authority.
