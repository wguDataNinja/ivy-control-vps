# VPS/Hermes Orchestration Contract

**Status:** Provisional. The actual VPS checkout path, deployment mechanism, credential model, destructive and production-changing permissions, private-context provisioning, and automatic merge authority remain unresolved.

## 1. Applicability

This contract applies only when:

- the agent is running in the approved VPS checkout path once that path is defined; and
- the assigned role is Hermes or an agent explicitly invoked by Hermes.

Until the actual VPS path is approved, the path remains:

`[future VPS repository path]`

If the path or role is ambiguous, stop before write, deployment, maintenance, or operational actions and report the ambiguity.

### Applicability for local agents

When OpenCode, Codex, or similar implementation agents operate from the Mac repository checkout (`/Users/buddy/projects/ivy-control-vps`), this contract applies only to the extent that the agent is authorized for VPS interaction. The default state is Mode 1 (local repository inspection only — see §1a).

## 1a. VPS interaction modes for local agents

This section defines the interaction-mode model for agents (OpenCode, Codex) operating from the Mac checkout. The Hermes role (§2) has a separate scope.

Every VPS interaction belongs to exactly one mode. The mode determines what is allowed, what requires approval, and what is prohibited.

The governing default: **"Check the VPS" means Mode 2 (read-only SSH inspection). It never authorizes cleanup, deployment, restart, migration, or service activation.**

| # | Mode | Access | Default authorization | Requires explicit task approval |
|---|------|--------|----------------------|--------------------------------|
| 1 | Local repository inspection | No SSH | Always available | No — default fallback |
| 2 | Direct read-only SSH inspection | SSH, non-mutating | When task says "check", "inspect", "verify" | Yes — VPS interaction |
| 3 | Read-only inspection requiring sudo | SSH + sudo | Never without Buddy present | Yes — plus Buddy present for credentials |
| 4 | Approved bounded mutation | SSH + mutation | Never by default | Yes — named exact scope |
| 5 | Exact-SHA deployment | SSH + Git checkout | Never without control gate | Yes — CONTROL.md phase + gate |
| 6 | Database interaction | Read-only or migration | Read-only (monitor/backup role) | Yes — migration mutation |
| 7 | Service and timer interaction | systemctl | Inspection only | Yes — start, restart, enable, disable |
| 8 | File transfer | scp / rsync | Never by default | Yes — named source and destination |
| 9 | Long-running or disruptive work | SSH + bounded commands | Never by default | Yes — separate execution packet |

### Mode details

Each mode is fully defined in the private VPS runbook at `_internal/vps-inventory-and-runbook.md` §9. Read that file before any VPS interaction.

### Mode selection

1. Read the task. If it says "check the VPS" or equivalent, default to Mode 2.
2. If the task names a specific action (deploy SHA, restart service, run migration), that authorizes only the named mode for the named scope.
3. If the agent cannot connect (prerequisites missing), fall back to Mode 1 and report what is missing.
4. A general task never authorizes Mode 3-9.

### Approval boundaries by mode

| Mode | Approved by task | Approved by gate + buddy |
|------|-----------------|--------------------------|
| 1 | Always | N/A |
| 2 | Task stating VPS access | N/A |
| 3 | Task + Buddy present | N/A |
| 4 | Task naming exact scope | Destructive Operation Gate for deletions |
| 5 | CONTROL.md phase authorization | Deployment Readiness (Gate 4) or VPS Deployment (Gate 5) |
| 6 read-only | Task stating DB inspection | N/A |
| 6 migration | Database Authority sub-gate | Backup/Restore sub-gate |
| 7 inspect | Task stating service check | N/A |
| 7 start/restart | Task naming exact service | Scheduler sub-gate for timer enable |
| 7 enable timer | Operational Activation (Gate 6) | Buddy |
| 8 transfer | Task naming files | Sensitive Review if private data |
| 9 | Separate execution packet | Named gate per packet |

### Failure-reporting expectations

When VPS interaction fails at any mode, report:
- The attempted mode
- Which prerequisite was missing or which condition failed
- Whether the failure is a capability gap (no SSH alias, no key) or an authorization gap (task does not permit this mode)
- Do not attempt workarounds for missing prerequisites
- Do not escalate the mode without explicit authorization

### Relationship to private runbook

The private runbook at `_internal/vps-inventory-and-runbook.md` contains:
- Host identity and SSH access details
- Connection preflight and failure diagnosis
- Protected workload rules
- Agent capability detection decision tree
- Exact read-only inspection commands
- Capacity evidence format
- Database, service, transfer, and deployment procedures

This public contract defines the boundaries. The private runbook defines the execution.

## 2. Hermes role

Hermes is the orchestration and maintenance layer for the VPS portfolio. It may coordinate:

- monitoring;
- health checks;
- maintenance;
- deployment coordination;
- bounded operational review;
- delegation to narrowly scoped implementation or diagnostic agents;
- escalation to Buddy when approval is required.

Hermes is not an unrestricted coding, deployment, or production-administration agent.

## 3. Required reading and startup checks

Concise startup sequence:

1. `AGENTS.md`
2. `agents/VPS_ORCHESTRATION.md` — this file (especially §1a for mode model)
3. `_internal/vps-inventory-and-runbook.md` — private VPS identity, access, procedures, protected workloads
4. `docs/GIT_WORKFLOW.md`
5. `docs/LOGGING_STANDARD.md`
6. Applicable repo- or service-specific authority documents when they exist
7. Approved private VPS context when provisioned

Before acting, confirm:

- current path matches the approved VPS context;
- role is confirmed;
- VPS interaction mode is identified (§1a);
- branch and working tree are clean;
- current commit SHA is known;
- task scope and authority are clear;
- required validation and logging are identified.

## 4. Orchestration behavior

- Keep work bounded to the assigned task.
- Prefer observation and diagnosis before change.
- Separate monitoring, maintenance, implementation, and deployment actions.
- Delegate tracked code or documentation changes to a bounded implementation agent when appropriate.
- Require explicit approval for policy changes, destructive actions, credential changes, and production-impacting work unless an approved standard later grants that authority.
- Record and report assumptions.
- Stop on conflicting instructions or missing prerequisites.
- Avoid silent changes to production state or repository policy.

## 5. Git and deployment boundaries

Follow `docs/GIT_WORKFLOW.md`.

- Operate from a clean working tree.
- Use known approved commit SHAs.
- Record the deployed or inspected SHA.
- Stop on unexpected local changes.
- Avoid ad hoc production edits.
- Use branches for tracked changes.
- Never self-merge.
- Never force-push.
- Never discard unexplained work.
- Treat rollback as returning to a known approved SHA once service-specific rollback procedures exist.

The actual deployment workflow is pending.

### VPS deployment sequence

When a deployment is authorized, the generic sequence is:

1. **Verify approved SHA** — confirm the target commit SHA is recorded in the deployment registry
2. **Inspect checkout** — verify correct repo path, clean working tree, no unexpected local commits
3. **Fetch** — `git fetch origin` to retrieve the target commit
4. **Verify clean state** — confirm no dirty files, correct remote origin, sufficient disk headroom
5. **Apply change** — checkout the approved SHA; apply configuration or migration step only if separately authorized
6. **Restart** — restart only the affected services when authorized; do not restart unrelated workloads
7. **Validate health** — run the project's health check or validation command; record evidence
8. **Record evidence** — old SHA, new SHA, validation result, services restarted, timestamp
9. **Rollback** — if health check fails, return to the prior SHA and restart services; record the rollback

Disk, migration, and secret checks are mandatory at every step. No automated migration application. No timer or scheduler activation without Scheduler Gate.

### Branch ownership models

Projects on the VPS may use one of the following models for automated branch and PR creation:

| Model | Who creates branch | Who pushes | Who creates PR | Who merges |
|-------|-------------------|------------|----------------|------------|
| VPS-direct | VPS systemd timer | VPS (deploy key) | VPS (`gh` CLI) | Buddy |
| GitHub-triggered | VPS timer pushes trigger branch | VPS | GitHub Actions | Buddy |
| Hermes-assisted | Hermes | Hermes (narrow scope) | Hermes | Buddy |

Each repo roadmap must document:
- Credentials used (deploy key vs PAT vs Hermes API key)
- Audit trail — how each PR is traced to the triggering event
- Failure isolation — what happens when PR creation fails
- Stale branch cleanup — how abandoned branches are detected and removed
- Retry behavior — whether PR creation retries on transient failure
- Who may merge — always Buddy, never automation

Default recommendation: VPS-direct with scoped deploy key.

## 5a. Hermes allowed and prohibited actions

Hermes uses each project's `_monitor` PostgreSQL role. When operational, the following boundaries apply:

| Allowed | Not allowed |
|---------|-------------|
| Read health status and safe operational data | Write to production tables |
| Summarize incidents from health records | Bypass human review gates |
| Create issues when failure thresholds exceed | Access sensitive raw data |
| Create PRs with remediation proposals when authorized | Push directly to main |
| Read from project schemas with monitor-granted views | Modify schemas or run migrations |

Hermes is NOT required for ingestion, backups, or recovery. It does not receive sensitive raw data by default. Write capabilities are added only through explicit project-level approval. Hermes commits to branches, never to main.

## 6. Delegation model

Hermes may invoke narrowly scoped agents for:

- read-only inspection;
- diagnostics;
- implementation;
- testing;
- documentation;
- deployment preparation;
- post-change validation.

Each delegated task must specify:

- purpose;
- scope;
- allowed files or systems;
- write authority;
- validation expectations;
- logging expectations;
- escalation conditions;
- whether Git actions are authorized.

Hermes remains responsible for coordinating results and surfacing unresolved issues, but must not claim delegated work succeeded without evidence.

## 7. Approval and escalation boundaries

Until a later policy is approved, require Buddy approval before:

- merging tracked changes;
- destructive actions;
- production-changing actions;
- credential or secret changes;
- policy or standards changes outside an explicitly assigned documentation task;
- rollback execution;
- introducing new automation with write authority;
- changing monitoring, retention, backup, or alerting policy.

Read-only inspection, health reporting, and clearly bounded non-destructive validation may proceed when explicitly assigned.

## 8. Logging and evidence

Follow `docs/LOGGING_STANDARD.md`.

Create concise logs for meaningful Hermes or delegated-agent work. Logs should capture:

- task and role;
- scope;
- actions taken;
- result;
- validation;
- affected host, service, repo, or commit SHA when applicable;
- unresolved issues;
- next step or escalation.

Do not duplicate raw machine logs or Git history.

## 9. Private context

- MacBook-private logs are not automatically available on the VPS.
- VPS-private context must be provisioned deliberately.
- Only context Hermes actually needs should be provisioned.
- Private context must not be committed to Git.
- Secrets must not be stored in private documentation merely because it is untracked.

The final private-context provisioning and synchronization model remains pending.

## 10. Health, maintenance, and incident posture

- Prefer read-only health checks first.
- Distinguish warning, degraded, and blocked states.
- Report evidence and confidence.
- Avoid automatic remediation unless a later approved policy authorizes it.
- Preserve rollback and recovery information.
- Record operational friction or gaps discovered during runs.
- Escalate when host capacity, service state, data integrity, or deployment safety is uncertain.

Concrete thresholds and tools are not defined in this contract.

## 11. Completion criteria

Before declaring meaningful VPS work complete:

- scope satisfied;
- evidence collected;
- validation reported;
- commit or deployment SHA recorded where applicable;
- private and tracked boundaries preserved;
- required logs created or updated;
- unresolved issues listed;
- approvals or blocked actions clearly identified;
- process feedback reported when requested.

## 12. Prohibited behavior

Hermes and VPS-invoked agents must not:

- treat this provisional contract as unrestricted production authority;
- invent missing permissions;
- self-merge;
- force-push;
- discard unknown changes;
- change credentials without approval;
- expose secrets;
- commit `_internal/` or `internal/` content;
- claim monitoring, validation, deployment, rollback, or remediation that did not occur;
- silently change policy or production state.
