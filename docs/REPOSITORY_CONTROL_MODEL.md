# Repository Control Model

**Status:** Current authority.
**Purpose:** Defines how ivy-control-vps governs managed repositories. Each managed repository receives a `CONTROL.md` that records admission, applicable standards, compliance, blockers, and next authorized work.

---

## ivy-control-vps role

ivy-control-vps is the portfolio control plane. It owns:

- cross-repository standards and conventions
- gate decisions (admission, publication, deployment, activation)
- approved SHA tracking
- repository status aggregation
- agent instruction model (`AGENTS.md`)
- portfolio Intent Layer (`docs/PORTFOLIO_INTENT.md`)
- portfolio-level roadmap (`ROADMAP.md`)
- per-repo roadmap conventions (when a `repos/<repo>/ROADMAP.md` exists)

Managed repositories remain separate codebases with their own code, data, tests, and local workflows. A managed control record describes an operational support relationship; it does not assign portfolio value or require VPS deployment.

---

## Control mechanism

Every managed repository receives a file at `repos/<repo>/CONTROL.md` containing:

- repository identity (purpose, remote, branch)
- current approved SHA (publication anchor)
- portfolio admission state
- applicable standards matrix
- accepted repository-specific deviations
- link to detailed release-gate evidence (`RELEASE_GATES.md`)
- current blocker
- next authorized phase

---

## Standards applicability

Each portfolio standard is assigned one of these applicability states for every repository:

| State | Meaning |
|-------|---------|
| **REQUIRED** | Standard applies and compliance must be demonstrated. |
| **NOT APPLICABLE** | Repository has no use for this standard. Must be documented why. |
| **REQUIRED WITH EXCEPTION** | Standard applies but an approved deviation exists. Exception must be documented in CONTROL.md. |
| **NOT YET ASSESSED** | Standard has not been evaluated. Does not imply exemption. |

---

## Compliance states

Within each applicable standard, compliance is recorded as:

| State | Meaning |
|-------|---------|
| **PASS** | Repository meets the standard. |
| **PASS WITH CONDITION** | Repository meets the standard with documented conditions. Conditions must be resolved by a named gate. |
| **BLOCKED** | Repository does not meet the standard and cannot proceed past the blocking gate. |
| **UNDEFINED** | Compliance has not been evaluated. |

---

## Gate separation

The following gates are defined sequentially:

| # | Gate | Controls |
|---|------|----------|
| 1 | Portfolio Admission | Repository is recognized as managed. |
| 2 | Public Repository Readiness | Repository is safe for GitHub publication. |
| 3 | GitHub Publication | Repository is published at an approved SHA. |
| 4 | Deployment Readiness | Repository can be deployed to infrastructure. |
| 5 | VPS Deployment | Bounded one-shot deployment proof. |
| 6 | Operational Activation | Continuous collection and production authority. |

A later gate cannot pass until the previous gate has passed. Each requires explicit Buddy dispatch to proceed.

Detailed gate evidence is recorded in `repos/<repo>/RELEASE_GATES.md`.

### Canonical ingestion-admission subgate

For repositories or workloads that own ingestion, Gate 4 includes the **Canonical Ingestion-Admission Gate**. It is narrower than full repository maturity and confirms the evidence required for a safe VPS authority-transfer review.

The gate requires evidence for:

- collector authority;
- scheduler or trigger authority;
- writer authority;
- canonical data authority;
- reviewed source and exact deployment SHA;
- secrets and runtime configuration;
- deterministic entry point;
- locking or concurrent-run protection;
- idempotency or duplicate prevention;
- bounded runtime and timeout behavior;
- retry and terminal failure behavior;
- schema and migration state where applicable;
- health output;
- freshness;
- counts, backlog, or output manifest where applicable;
- backup;
- checksum and manifest;
- isolated restore or equivalent recovery proof;
- rollback;
- Mac fallback, archive, or recovery role;
- legacy scheduler shutdown;
- successful manual run;
- successful natural scheduled or event-triggered run;
- exactly one active production writer.

Repository-specific gates may add requirements, but they must not silently omit the common gate unless a documented workload-specific exception is recorded in `repos/<repo>/CONTROL.md`.

Passing this subgate does not imply full public maturity, LLM maturity, dashboard polish, cleanup authority, or production activation. Scheduler activation still requires Gate 6.

### Gate 1 — Portfolio Admission requirements

A repository is admitted as managed when it satisfies:

- **Repository identity** — purpose, canonical remote, default branch, approved SHA
- **Repo and GitHub readiness** — secret/history risk assessed, gitignore coverage, dependency manifests, license or documented private status, known track/un track clutter
- **Minimal durable docs** — README.md, AGENTS.md (if agent interaction is expected), and comprehensive `.gitignore`; add a private local supplement only when durable context cannot safely be public
- **Report consolidation** — current reports indexed or consolidated, superseded reports marked, no uncontrolled reporting/archive/log growth
- **Logging and observability** — durable activity log, current session state, worker report contract
- **Collector efficiency** (if applicable) — inventory of scheduled collectors with cadence, concurrency lock, timeout, retry, quota posture
- **PostgreSQL lifecycle and storage budget** (if applicable) — migration/rollback/validation layout, backup/restore plan, retention policy, storage estimate, capacity dependency
- **LLM boundary** (if applicable) — provider config externalized, prompt versioning, structured contracts, audit metadata, cost limits

These requirements expand Gate 1 to a structured admission review. Each requirement maps to sub-checks in the evidence template at `repos/<repo>/RELEASE_GATES.md`. The gate produces `PASS`, `PASS WITH CONDITIONS`, or `FAIL`.

### Authority-transfer lifecycle

When a repository transitions authority between systems (e.g. file-based to PostgreSQL, Mac to VPS), the lifecycle is:

1. **Shadow mode** — Run new system and old system in parallel. Validate output automatically.
2. **Parity confirmation** — Automated comparison confirms row-count, field-value, and freshness parity between old and new authority.
3. **Cutover approval** — Buddy reviews the parity report and explicitly approves switching authority.
4. **Fallback activation** — Document the fallback procedure. Ensure the old system can resume on failure.
5. **Retirement of old path** — Remove or archive legacy scripts, paths, and data after a stabilization period and Destructive Operation Gate approval.

Each stage has its own evidence record and approval. No stage is skipped.

### Review checkpoints

Substantial multi-repo work follows these checkpoints:

| # | Trigger | Review | Outcome |
|---|---------|--------|---------|
| 1 | Standards consolidation complete | Codex verifies gaps against audits | Request specific Gates or hold |
| 2 | Backup/health/LLM/capacity evidence exists | Buddy + Codex review readiness | Authorize schema/adapter lanes or hold |
| 3 | Repo-local adapters, migrations, parity exist | Review tests, migrations, rollback | Authorize shadow VPS work or hold |
| 4 | Shadow reports complete | Review production impact, monitoring, backup | Authorize cutover or extend shadow |
| 5 | Cutover reports complete | Review legacy paths, retained data, publication | Authorize cleanup with Destructive Operation Gate |

### Worker-result contract

Every worker report delivered under this control model must include:

- assignment ID and title
- working directory and git status
- authority documents read
- commands or inspections run
- files changed, or explicit statement that no files changed
- verified facts and inferred conclusions
- unverified claims
- validation or tests run and results
- gates used or needed
- risks and stop/escalate conditions encountered
- deliverables produced
- completion status: `DONE`, `BLOCKED`, `NEEDS_BUDDY_DECISION`, `NEEDS_CODEX_REVIEW`, or `GATE_REQUIRED`
- next assignment IDs unlocked, if any

### Named gates from shared conventions

The old tree defines eleven named gates (Database Authority, Backup/Restore, GitHub Push, VPS Capacity, Scheduler, PostgreSQL Cutover, Merge, Publication, Destructive Operation, LLM Budget, LLM Stage Authority, Sensitive Review). Under this six-gate model they become sub-gates or evidence checks:

| Old gate | Corresponds to | Evidence location |
|----------|----------------|-------------------|
| GitHub Push | Gate 2 — Public Repository Readiness | `RELEASE_GATES.md` |
| Database Authority | Gate 4 — Deployment Readiness (PG sub-check) | `RELEASE_GATES.md` |
| Backup/Restore | Gate 4 — Deployment Readiness (backup sub-check) | `RELEASE_GATES.md` |
| VPS Capacity | Gate 4 — Deployment Readiness (capacity sub-check) | `RELEASE_GATES.md` |
| Scheduler | Gate 6 — Operational Activation | `RELEASE_GATES.md` |
| PostgreSQL Cutover | Authority-transfer lifecycle (cutover stage) | `RELEASE_GATES.md` |
| Merge, Publication, Destructive Operation | Standing safety gates — apply at any stage | Buddy approval |
| LLM Budget, LLM Stage Authority | Standing cost and safety gates | `RELEASE_GATES.md` |
| Sensitive Review | Standing privacy gate | `RELEASE_GATES.md` |

This mapping prevents ambiguity without creating a competing gate model.

---

## Approved SHA tracking

Every managed repository has a recorded approved SHA. This is the commit that was verified at publication time. Future deployment must use this SHA or a later reviewed and recorded replacement. The approved SHA is recorded in `CONTROL.md` and cross-referenced in `RELEASE_GATES.md`.

`CONTROL.md` may include a `git_custody` block. It is a fail-closed capability
record: `inspect`, `local_commit`, `push_branch`, `create_pr`, `merge`, and
`update_approved_sha` are explicit booleans. In H4.1 only `inspect` and a
separately dispatched `local_commit` may be true; remote/policy-changing fields
remain false. Conflicting approved-SHA values between machine-readable and
human-readable control content block custody until canonical evidence resolves
them.

---

## Control-sheet update triggers

CONTROL.md must be reviewed or updated when:

- a new gate passes or blocks
- the approved SHA changes
- a standard changes applicability
- a deviation is granted or revoked
- the blocker changes
- the next authorized phase changes

---

## Relationship between documents

A managed repository's documents form a governing contract defined by
`docs/README.md` §Repository Documentation Contract. CONTROL.md is one part of
that contract — it owns lifecycle, gates, and evidence expectations. It does
not replace the repo's README, ROADMAP, TODO, or AGENTS.md.

| Document | Role |
|----------|------|
| `repos/<repo>/CONTROL.md` | Active governance authority. One-stop for current state. |
| `repos/<repo>/README.md` | Human/project orientation. Required by the contract for every managed repo. |
| `repos/<repo>/AGENTS.md` | Agent operating instructions. Required when agent interaction is expected. |
| `repos/<repo>/ROADMAP.md` | Owner-approved direction when the repo has project-specific sequencing. |
| `repos/<repo>/TODO.md` | Short-term implementation queue when the repo has agent-visible work. |
| `repos/<repo>/RELEASE_GATES.md` | Detailed gate evidence. Referenced by CONTROL.md. |
| `repos/<repo>/STATUS.md` | **Deprecated** once CONTROL.md exists. Retained as historical reference, not updated. |
| `repos/<repo>/<phase-packet>.md` | Bounded execution instructions for the next authorized phase. Not a governance document. Public. |
| Locally provisioned private evidence packets | Private gate evidence and ad-hoc task artifacts. Not governance; evidence only. |
| `docs/PORTFOLIO.md` | Human portfolio working view. Buddy's all-project surface for priorities, notes, direction, and decisions. Does not override CONTROL.md. |
| `docs/PORTFOLIO_INTENT.md` | Formal Buddy intent layer. What Hermes watches for alignment. |
| `docs/PORTFOLIO_CONVENTIONS.md` | Durable cross-repo conventions. Referenced by CONTROL.md applicability matrix. |
| `docs/DATA_LIFECYCLE_STANDARD.md` | Portfolio data-lifecycle principles. Referenced by CONTROL.md. |
| `docs/PORTFOLIO_UNIVERSE.md` | Curated known asset universe and portfolio relationship. It may acknowledge assets that do not have and should not receive a CONTROL.md record. |

### Documentation creation governance

Before creating any new file in a managed repository, check whether an existing
authority document can own the content. See `docs/README.md` §Repository
Documentation Contract for the four-question gate. A new doc must answer a
distinct question that no existing document already answers. If the gate is
unclear, do not create the document.

---

## Per-repo roadmap

A managed repository may have its own `ROADMAP.md` when it has project-specific
sequencing that cannot be expressed at the portfolio level.

### When to create

A per-repo ROADMAP.md is appropriate when the repo has:
- multiple phases with dependency chains;
- a mix of agent-implementable work and high-reasoning gates;
- implementation chunks that require specs before coding;
- enough scope that a coding agent cannot execute without phased context.

A per-repo ROADMAP.md is NOT appropriate when:
- the repo is source-only with minimal scope (use CONTROL.md + TODO.md);
- the repo is deferred or blocked at Gate 1;
- the portfolio ROADMAP.md already covers the repo's direction adequately.

### Required structure

```
# <Repo Name> Roadmap

## North Star
- Final desired capability

## Current State
- Existing implementation, accepted decisions, known limitations

## Dependency Map
- Prerequisites, blockers, critical path, parallel work

## Workstreams
- Grouped related work with objectives, dependencies, owner type

## Execution Chunks
Per chunk:
- Goal, Worker Tasks, Inputs, Outputs, Validation, Dependencies, Exit Gate

## Implementation Specifications
- Interfaces, contracts, data structures, APIs, ownership boundaries

## High Reasoning Gates
Per gate:
- Decision, Evidence, Reviewer, Outcomes, Downstream Impact

## Agent Assignment Model
- Per phase: what agent type suits it and why

## Risks and Unknowns

## Completion Criteria
```

### Relationship to portfolio ROADMAP.md

The portfolio `ROADMAP.md` references active per-repo roadmaps in §2 (Active
Initiatives). A repo with its own ROADMAP.md should have a portfolio entry
point that links to it. The per-repo roadmap does not replace the portfolio
entry — an operator should discover the repo's existence from the portfolio
level first.

### Relationship to CONTROL.md

CONTROL.md records lifecycle state, gates, SHA, blockers. The per-repo
ROADMAP.md records phased execution direction. CONTROL.md `next_task` may
reference a phase in the repo ROADMAP.md. They complement each other and
should not conflict.

### Creation workflow

Per-repo roadmaps use a controlled Codex handoff. The workflow is:

1. Agent gathers context (README, CONTROL, existing docs, git log).
2. Agent compresses into a context packet (not a full repo dump).
3. User approves a Codex call.
4. Codex produces a roadmap proposal.
5. Agent reconciles (fixes paths, corrects assumptions).
6. Buddy approves the candidate.
7. git-steward commits ROADMAP.md.

**Model selection:**

- **Default: Strong Codex** for roadmap generation. Strong Codex identifies
  hidden constraints, architectural boundaries, false assumptions, and creates
  executable chunks that agents can follow without reinterpretation.
- **Optional: Fast Codex** for comparison, benchmarking, low-complexity
  repositories, or auditing Strong Codex output. Fast Codex provides first-pass
  structure; its formatting contribution can be recreated by OpenCode
  refinement or GPT editing.

**Context packet requirement:** The Codex prompt must be a compressed context
packet containing repository identity, current state, architecture, dependency
analysis, and agent execution model. Codex must not receive the full repository.

### Roadmap lifecycle states

Every per-repo roadmap artifact must carry an explicit status to distinguish
proposals from canonical authority.

| State | Meaning | When used |
|-------|---------|-----------|
| `PROPOSAL` | A draft roadmap created for discussion | Before any review |
| `TRIAL` | A proposed roadmap being tested on a non-critical repo | First implementation |
| `ACTIVE` | Current execution authority — agents use this for chunk execution | Normal operation |
| `MIGRATION_PENDING` | An old roadmap is being replaced; migration in progress | During format upgrades |
| `CANONICAL` | Same as ACTIVE — authoritative for the repo | Normal operation |
| `ARCHIVED` | Superseded, preserved for historical reference | After replacement |

The status should appear as a header line in the roadmap file:

```
# <Repo Name> Roadmap
**Status:** ACTIVE
```

### Required migration rule

No agent may replace an existing authoritative roadmap unless the task
explicitly states:
- this is a migration;
- the old authority is being replaced;
- review has occurred.

### Trial rule

New workflow designs or roadmap formats must first be tested on:
- a non-critical repository;
- a repository with no existing ROADMAP.md;
- a copied or proposed artifact (not canonical).

The trial result determines adoption. Trial artifacts must carry `PROPOSAL`
or `TRIAL` status.

---

## Portfolio intelligence and refresh

The control plane answers different questions through different sources. Do not create a second registry or promote generated output into authority.

| Need | Authority or generated view | Refresh meaning |
|---|---|---|---|
| What does Buddy want across the portfolio — priorities, notes, direction, decisions? | `docs/PORTFOLIO.md` and `docs/PORTFOLIO_INTENT.md` | Buddy writes freely in PORTFOLIO.md; PORTFOLIO_INTENT.md documents formal intent. Reconciliation propagates to CONTROL.md, ROADMAP.md when authorized. |
| What assets are known, including ungoverned, private, historical, and infrastructure assets? | `docs/PORTFOLIO_UNIVERSE.md` | Deliberately update when an asset relationship is learned or changed. `DISCOVERY_INCOMPLETE` remains explicit until separately authorized discovery occurs. |
| What is true and authorized for a managed repository? | `repos/<repo>/CONTROL.md` and its gate evidence | Update when a gate, approved SHA, support state, blocker, next authorized work, or evidence basis changes. |
| What managed records currently say in aggregate? | `tools/portfolio_registry.py` / `tools/show_portfolio_status.sh` | Re-run the generator. It reads CONTROL metadata; it does not write it or discover untracked repositories. |
| What does current operational evidence show? | `tools/ingestion_dashboard.py` summary/JSON and `docs/HEALTH_CONTRACT.md` | Run a permitted read-only collection. Freshness and `UNKNOWN` are evidence outcomes, not documentation failures. |
| What should happen next? | `ROADMAP.md`, then the target `CONTROL.md` | Refresh by review and authorized roadmap/control updates, never by a generated task list alone. |

### How a repository enters the control plane

1. Acknowledgement begins in `PORTFOLIO_UNIVERSE.md`; it does not grant inspection, publication, VPS, or runtime authority.
2. When an operational support relationship is deliberately accepted, create a managed `repos/<repo>/CONTROL.md` record and state applicable standards, support state, boundaries, and next authorized work.
3. The registry generator may then expose the CONTROL metadata as a derived summary. A source-only, restricted, or deferred asset receives only the controls proportional to its role.
4. Health producers or adapters are added only for a workload that actually needs operational evidence. Their output remains subject to the health contract and evidence freshness rules.

**Refresh is not discovery and is not Git activity.** A refresh either re-runs a generated view from existing records or collects permitted operational evidence. It never silently changes an authority document, upgrades an asset's importance, or makes an incomplete inventory complete.

---

## Machine-readable metadata block

Every CONTROL.md begins with a YAML front-matter block. This block is the machine-readable identity and state record consumed by portfolio tooling (registry scripts, Hermes inspectors, dashboard generators).

### Schema definition

```yaml
---
control_model_version: "<semver>"
repository:
  slug: "<repo-slug>"
  purpose: "<one-line description>"
  remote: "<canonical-remote-url>"
  default_branch: "<branch>"
  approved_sha: "<full-commit-sha-or-null>"
  local_path: "<mac-development-path>"
  vps_path: "<vps-checkout-path-or-null>"
lifecycle:
  admission_gate: <1-6-or-null>
  state: "<lifecycle-classification>"
github:
  visibility: "<public|private|null>"
  publication_gate: <1-6-or-null>
  clean_history: <true|false|null>
vps:
  clone_state: "<cloned|not-cloned|pending>"
  runtime_location: "<vps-path-or-null>"
scheduler:
  active: "<systemd-timer-or-other>"
  writer: "<writer-description>"
  legacy: "<description-of-disabled-predecessor>"
database:
  present: <true|false>
  name: "<db-name-or-null>"
  schemas: []
  migrations: "<range-or-null>"
data_locations:
  archive: "<mac-archive-path-or-null>"
  backup: "<vps-backup-path-or-null>"
  source_only: <true|false>
health:
  state: "<healthy|degraded|unknown>"
roadmap:
  gates: []
  blockers: []
  next_task: "<next-authorized-work-reference>"
continuity:
  current_focus: "<current bounded workstream>"
  recent_milestone: "<most recent durable outcome; not a health claim>"
  recent_reference: "<public commit, report, or canonical artifact reference>"
  long_horizon: "<durable product or operational direction>"
hermes:
  scope: "<read-only|read-only-with-pr|none>"
  artifact_paths: |-
    optional; list of publication-safe directory paths Hermes may write
    (e.g. "agent/reports/", "logs/"). Required when Hermes operates under
    Mode 0 on a VPS-resident checkout. Default: none (single-task dispatch).
codex_stops: []
buddy_decisions: []
last_verified: "<yyyy-mm-dd>"
evidence_basis: "<path-to-gate-evidence>"
---
```

### Field semantics

Every field is defined in the field reference table below. The front matter is **required** for every CONTROL.md. Fields marked `optional` may be omitted or set to `null`. Fields marked `private` must not appear in public GitHub copies of CONTROL.md (use a tracked-but-redacted or `.gitignore`-excluded copy if needed). Fields marked `live-verification-dependent` must be refreshed from live inspection, not copied from a prior snapshot.

### Continuity metadata

The optional `continuity` block is the lightweight orientation layer for a
managed repository. It belongs in `CONTROL.md`, not in a second README, TODO,
registry, or private-memory file. It lets a fresh engineer or Hermes answer
"what were we doing?" while retaining the existing authority split:

| Field | Meaning | Must not replace |
|---|---|---|
| `current_focus` | The bounded workstream currently being advanced | `roadmap.next_task` / current authorization |
| `recent_milestone` | Most recent durable, reviewable outcome | Git history, result reports, or dated evidence |
| `recent_reference` | Public pointer that lets an agent verify the milestone | The underlying commit or artifact |
| `long_horizon` | Stable product or operational direction | `ROADMAP.md` portfolio sequencing |

Continuity text is orientation metadata, not a health claim, task queue, or
permission grant. It must agree with `roadmap.blockers`, `roadmap.next_task`,
the current CONTROL body, and the portfolio roadmap. Update it only when the
focus or durable milestone changes; never update it merely because Git activity
occurred. A repository without this optional block remains governed normally.

#### Incremental migration

Do not mass-fill continuity metadata from memory. Migrate one repository after
checking its current `CONTROL.md`, public README/roadmap, relevant Git history,
and any permissible dated evidence. Start with an actively supported workstream
where the next bounded task is known. Use public commit or canonical-artifact
references only; private session paths, sensitive data, and raw logs do not
belong in the block. Revisit the block during the same review that changes a
blocker, next authorized work, or durable milestone.

---

## Hermes permissions field

The `hermes.scope` field in the metadata block records Hermes's authorized inspection and action scope for this repository.

| Value | Meaning |
|-------|---------|
| `none` | Hermes may not inspect this repository. |
| `read-only` | Hermes may run read-only commands, compare SHAs, check health, and produce structured reports. No branch creation, PR preparation, or file modification. |
| `orchestrate-artifact-only` | Hermes may coordinate explicitly dispatched work and write only declared task/report/log/journal-proposal artifacts. It may not write code, Git, data, configuration, services, or canonical documents. |
| `read-only-with-pr` | Hermes may inspect, create isolated branches, run tests, and prepare pull requests for review. Self-merge is prohibited. |

Scope changes require a Gate 3+ passage and Buddy approval documented in `RELEASE_GATES.md`. Hermes must never exceed the scope recorded here, even if the VPS environment permits broader access.

### Codex capabilities field

The `hermes.codex_capabilities` field in the metadata block controls which
Codex escalation capabilities Hermes may request for this repository. Each
capability has an enabled state and an approval requirement.

```yaml
hermes:
  scope: "orchestrate-artifact-only"
  codex_capabilities:
    roadmap_repair:
      enabled: false
      requires_buddy_approval: true
    architecture_review:
      enabled: false
      requires_buddy_approval: true
    implementation_blocker_review:
      enabled: false
      requires_buddy_approval: true
    production_change_review:
      enabled: false
      requires_buddy_approval: true
```

| State | Meaning |
|---|---|
| `enabled: true` | Capability is available. Hermes may use it when the trigger condition is met. |
| `enabled: false` | Capability is not available. Hermes must not request it. Falls back to `NEEDS_BUDDY_REVIEW`. |
| `requires_buddy_approval: true` | Each use requires per-call Buddy approval. Hermes produces escalation context; Buddy reviews before Codex is invoked. |
| `requires_buddy_approval: false` | Capability is pre-authorized. Hermes may proceed to escalation without per-use approval. |

Default state for all capabilities: `enabled: false`, `requires_buddy_approval: true`.
Capability definitions are documented in `agents/HERMES_AGENT_CONTRACT.md` §3.5d.

---

## Strong Codex stop conditions

The `codex_stops` list in the metadata block enumerates conditions under which Strong Codex must stop and escalate to Buddy.

Portfolio-wide defaults (defined in ROADMAP §1B):
- Conflicting canonical-data claims, unexplained missing intervals, duplicate writers, or source/DB/archive disagreement
- Any live database mutation, schema/retention architecture change, scheduler/writer transfer, failed restore, or destructive cleanup
- Browser-profile manipulation, browser recovery/corruption, or source-to-installed userscript verification requiring sensitive profile access
- Cross-repository ownership conflict, privacy/publication ambiguity, or capacity projection threatening the VPS
- Disagreement between live evidence and a control/authority document

Repository-specific additions may be recorded in `codex_stops` to capture workload-specific risk.

Strong Codex must also stop on any condition listed in the portfolio-wide defaults, even if not duplicated in the repository's local list. The local list is additive only.

---

## Decisions requiring Buddy

The `buddy_decisions` list in the metadata block records pending or accepted decisions that require Buddy authorization for this repository.

Each entry should reference the specific decision (e.g. "Approve WGU Reddit clean publication/history strategy") and may include a state annotation: `PENDING`, `APPROVED`, `REJECTED`, or `DEFERRED`.

The canonical list of portfolio-wide Buddy decisions is maintained in ROADMAP §10. Repository-specific decisions supplement, not replace, the portfolio list.

---

## Registry-facing fields

Managed-registry scripts consume the following fields from the metadata block for aggregation and health/dashboard views:

| Field | Purpose |
|-------|---------|
| `repository.slug` | Unique machine-readable repo identifier |
| `repository.remote` | Canonical GitHub remote |
| `lifecycle.state` | Current operational classification |
| `lifecycle.admission_gate` | Highest passed gate number |
| `github.visibility` | Public/private status |
| `github.publication_gate` | Publication gate status |
| `vps.clone_state` | Whether VPS checkout exists |
| `health.state` | Aggregated health status |
| `database.present` | Whether the repo uses PostgreSQL |
| `scheduler.active` | Description of active scheduler |
| `hermes.scope` | Hermes authorization level |
| `continuity.*` | Generated orientation context; advisory routing only |

These fields are consumed by `tools/portfolio_registry.py` (or equivalent). They must be updated whenever a gate passes, the SHA changes, or the health state changes. A managed-registry update does not replace reading CONTROL.md for detailed governance, and it does not replace `PORTFOLIO_UNIVERSE.md` as the broader asset inventory.

---

## Data/archive/backup location inventory

The `data_locations` block in the metadata block records where this repository's data lives across the three tiers:

| Tier | Path field | Description |
|------|------------|-------------|
| Production runtime | `vps.runtime_location` | VPS working tree or data directory |
| VPS backup | `data_locations.backup` | PostgreSQL dump root or file-export backup root |
| Mac archive | `data_locations.archive` | Long-term Mac archive path |
| Source-only | `data_locations.source_only` | `true` when the repo has no VPS runtime or persistent data |

A repository should document known paths even when they are not yet populated. Missing paths indicate gaps, not exemptions.

Detailed backup/restore evidence and manifest locations are documented in `RELEASE_GATES.md`, not in CONTROL.md. The metadata block records the *inventory*, not the *evidence*.
