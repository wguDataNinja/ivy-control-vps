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
- public roadmap conventions (when a `ROADMAP.md` exists for a workstream)

Managed repositories remain separate codebases with their own code, data, tests, and local workflows.

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
- **Minimal durable docs** — README.md, AGENTS.md (if agent interaction is expected), README_INTERNAL.md with START HERE section, comprehensive .gitignore
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

| Document | Role |
|----------|------|
| `repos/<repo>/CONTROL.md` | Active governance authority. One-stop for current state. |
| `repos/<repo>/RELEASE_GATES.md` | Detailed gate evidence. Referenced by CONTROL.md. |
| `repos/<repo>/STATUS.md` | **Deprecated** once CONTROL.md exists. Retained as historical reference, not updated. |
| `repos/<repo>/<phase-packet>.md` | Bounded execution instructions for the next authorized phase. Not a governance document. Public. |
| `_internal/outbox/` and `_internal/tasks/` | Private gate-evidence packets and ad-hoc task artifacts. Not governance; evidence only. See `_internal/GPT_ORCHESTRATED_WORKFLOW.md`. |
| `docs/PORTFOLIO_CONVENTIONS.md` | Durable cross-repo conventions. Referenced by CONTROL.md applicability matrix. |
| `docs/DATA_LIFECYCLE_STANDARD.md` | Portfolio data-lifecycle principles. Referenced by CONTROL.md. |
