# Repository Work Protocol

**Status:** Current authority for portfolio-wide work-tracking conventions.
**Purpose:** Define repository-neutral rules for planning, executing, tracking, and closing work across all managed repositories.
**Scope:** Ivy Control VPS and all repositories governed by `repos/*/CONTROL.md`.

---

## 1. Session Boundaries

A session is a bounded continuity container with flexible boundaries.

A session may end when:
- a coherent body of work completed;
- the workday ended;
- context limits are reached;
- an approval or privileged boundary was reached;
- work needs to pause safely;
- attention moves to another repository;
- Buddy chooses to close it.

A session does not need to align exactly with one task, roadmap phase, commit, release, milestone, or calendar day. A session may contain several tasks, and a task may continue across practical work periods.

---

## 2. Task Identity

Every substantial unit of agent work receives a stable identifier.

Preferred format: `YYYY-MM-DD-<descriptive-slug>` for run-level tasks or
`agent-<number>-<descriptive-slug>` / equivalent per-repository convention for
repository-local task IDs.

Identifiers must not be reused within the same session and actor sequence. A completed or superseded task retains its identifier.

For Ivy Control VPS active queues, agents must not create a bare `session-<N>`
directory. A run/task ID must be globally distinguishable inside the control
plane, for example `2026-07-28-portfolio-readiness`,
`2026-07-28-idlehacking-context`, or `session-14-palworld-kb`.

---

## 3. Task Prompts

A task may begin through:
- an inbox artifact (`_internal/inbox/` or per-repo equivalent);
- a direct pasted prompt;
- an approved repository-local task file;
- another clearly recorded handoff channel.

An inbox artifact is preferred but not required. When a prompt is delivered directly, the result report must record the source as "direct handoff."

---

## 4. Result Reports

**Substantial agent work must produce one consolidated result report.**

The report is the primary handoff artifact between the executing agent, GPT, Buddy, later agents, and later sessions. It must be understandable without access to the original prompt.

### Minimum fields

| Field | Description |
|---|---|
| Session | Session number |
| Task identifier | Stable slug |
| Repository | Repositories affected |
| Prompt source | Inbox file, direct handoff, or other |
| Status | Completed, partial, blocked |
| Objective | Task objective as understood |
| Sources inspected | Files and systems examined |
| Changes made | Files changed, evidence created |
| Validation | Tests, checks, verification performed |
| Findings | Decisions, results, conclusions |
| Assumptions | Uncertainties, unverified claims |
| Blockers | What stopped progress |
| Git state | Current branch, status |
| Next handoff | What the next actor should do |

### Active workflow locations

Inbox and outbox paths are active workflow queues. They hold work currently
being dispatched, reviewed, or handed off. They are not the long-term index for
all Hermes task history.

| Repository | Prompt location | Active result-report location | Log location |
|---|---|---|---|
| Ivy Control VPS | `_internal/inbox/runs/<run-id>/` | `_internal/outbox/runs/<run-id>/` | `_internal/logs/agents/YYYY-MM-DD/` |
| Palworld KB | `_inbox/` | `agent-reports/` (by type) | `logs/agent-log.md` |
| SJC Intel | (none defined) | `_outbox/` | `logs/agents/` |
| Other repos | `_inbox/`, `inbox/`, or documented equivalent | `_outbox/`, `outbox/`, or documented equivalent | `logs/` or documented equivalent |

A repository using an alternative path must document it in AGENTS.md, CONTROL.md, or a clearly identified private local supplement.

The optional repository-oriented active queue view is:

```text
_internal/inbox/repos/<repo>/<task-id>/
_internal/outbox/repos/<repo>/<task-id>/
```

Use this only when it is the canonical queue location for that artifact. Do not
copy the same active artifact into both `runs/` and `repos/` queues. The
durable repository-organized archive remains the permanent task-history index.

Legacy `_internal/inbox/session-<N>/` and `_internal/outbox/session-<N>/`
directories remain historical evidence and may be linked from old reports,
control records, and docs. New work must not target those bare session paths.
Validate proposed new destinations with:

```bash
python3 -m tools.hermes_orchestrator validate-artifact-destination --path <path>
```

### Durable Hermes artifact history

After Hermes validates a completed task, active artifacts are promoted into a
repository-organized durable history under the control plane's private
orchestration tree:

```text
_internal/orchestration/repos/<repo>/tasks/<task-id>/
_internal/orchestration/cross-repo/tasks/<task-id>/
```

Use `repos/<repo>/tasks/<task-id>/` when one managed repository owns the task.
Use `cross-repo/tasks/<task-id>/` when the task spans multiple repositories or
portfolio-level coordination and should not be attributed to one repository.

Each archived task directory contains a `manifest.json` that records the stable
task ID, repositories, source queue paths, copied archive paths, artifact
hashes, validation disposition, and the fact that active queue artifacts were
copied rather than moved.

The archive step is allowed only after Hermes validation returns `COMPLETED` or
`COMPLETED_WITH_WARNINGS`. Other dispositions remain in the active queue until
rework, escalation, or Buddy review resolves them.

Historical migration rule: do not bulk-move legacy session trees merely to
normalize paths. Preserve auditability by leaving cited evidence in place unless
a specific artifact has a known incorrect location and can be moved with a
manifest recording original path, filename, checksum, migration date, inferred
repository/workstream, confidence, source session name, and destination.

### VPS workspace artifact boundary

A clean VPS checkout must not rely on Ivy Control VPS's Mac-local `_internal/`
tree. For a VPS-resident repository, its AGENTS.md or CONTROL.md must declare
the publication-safe artifact paths Hermes may use, or Hermes must remain
limited to a single human-dispatched task. Private task packets, raw evidence,
and runtime logs require a separately provisioned location outside the Git
checkout. Result reports, logs, and journal proposals created by Hermes remain
evidence only and cannot promote canonical truth.

### Multi-artifact review rule

When a task produces multiple artifacts that require a review decision (such as
model outputs, comparison reports, or generated proposals):

- The reviewer must inspect primary artifacts directly.
- Agent-produced comparisons or summaries are secondary evidence only.
- A single review bundle containing all primary artifacts must be assembled
  before the reviewer is asked for a decision.

This prevents summary substitution — the decision-maker must see the actual
outputs, not another agent's interpretation of them.

---

## 5. Execution Logs

A separate agent execution log is required when the repository or portfolio logging standard calls for it. Where both a report and log exist:

- The **report** serves handoff (primary deliverable).
- The **log** serves durable execution chronology.
- Reports and logs must not duplicate entire command transcripts or canonical documentation.
- Reports and logs should reference each other by path.

---

## 6. Artifact Distinctions

| Artifact | Role | Durable? |
|---|---|---|
| **ROADMAP.md** | Direction, priorities, gates, sequencing | Yes — canonical |
| **CONTROL.md** | Per-repository policy, lifecycle, blockers, SHA | Yes — canonical |
| **Canonical docs** (`docs/`) | Technical standards, architecture, conventions | Yes — canonical |
| **Result reports** | Task output, findings, handoff | Evidence only |
| **Execution logs** | Chronological execution record | Evidence only |
| **Session logs** | Discussion memory, decisions, rationale | Evidence only |
| **TODO.md** | Current-session task plan | Session-scoped |
| **Gate packets** | High-reasoning decision evidence | Evidence only |

Evidence is not canonical authority. Durable decisions should be promoted to the appropriate canonical document.

### Work-continuity lifecycle

For substantial work, the normal lifecycle is:

```text
task intent (inbox artifact or direct handoff)
  → bounded execution
  → outbox result report
  → agent execution log when meaningful work occurred
  → Hermes validation
  → archive/promotion into repository-organized artifact history
  → review and acceptance meaning
  → journal navigation entry
  → intentional promotion into canonical documentation when durable truth changed
```

Each artifact has one role:

| Artifact | Role | Does not become |
|---|---|---|
| Inbox | Task intent, scope, constraints, and validation expectations | Decision or architecture authority |
| Result report | Consolidated outcome, evidence, validation, risks, and next handoff | Permanent documentation automatically |
| Agent log | Concise execution chronology | A second result report or architecture explanation |
| Artifact manifest | Stable task-to-artifact index after validation | Canonical policy or roadmap truth |
| Journal | Navigation across reviewed substantial results | A task transcript |
| Canonical documentation | Settled operating, product, or policy truth | A replacement for task evidence |

An inbox artifact is preferred for multi-step or cross-session work, but a direct handoff remains valid when recorded in the result report. Read-only exploration, brief questions, and trivial safe changes may use a reduced workflow; substantial implementation, audit, architecture, durable-artifact, or operational work must use the full evidence path.

### Artifact-only orchestration

An explicitly dispatched Hermes orchestration run follows the artifact-driven
lifecycle:

```
Task packet → execution agent → execution report
  → Hermes validation → validation outcomes:
    → [ACCEPT] → journal update → next packet or stop
    → [REJECT] → rework or escalate
    → [NEEDS_BUDDY_REVIEW] → stop, report to Buddy
    → [NEEDS_CODEX] → check capability registry → escalate if authorized
```

Hermes may create task packets, factual review reports, concise orchestration
logs, and journal proposals only inside the target repository's declared
permitted artifact paths. It must use
`agents/orchestrator-task-packet-template.md`, operate inside a delegation
envelope, and stop after every delegated task unless the next packet remains
within that envelope. Before creating any packet, Hermes must evaluate the
roadmap section against `agents/HERMES_ROADMAP_SUFFICIENCY_GATE.md`.

Between receiving an execution report and authorizing the next task, Hermes
must produce a validation report. See `agents/HERMES_AGENT_CONTRACT.md` §3.5b
for the validation criteria and `agents/HERMES_AGENT_CONTRACT.md` §3.5c for
the validation outcomes.

Hermes never supplies GPT/Buddy acceptance, decisions, lessons, or canonical
promotion. Hermes coordinates; execution agents implement; Buddy approves.
Codex escalation requires Buddy approval in all cases where
`requires_buddy_approval` is true.

---

## 7. Minimum Start-of-Work Checks

### How to make a tracked change

For a normal, non-production change, use this path:

1. Identify the relevant authority document and task scope. Do not use a result report or chat history as substitute authority.
2. Inspect the current working tree and preserve unrelated or protected work.
3. **Before creating any new file**, confirm that no existing authority document can absorb the material. Apply the documentation creation governance gate (see `docs/README.md` §Repository Documentation Contract — four-question check). If the gate is unclear, do not create the document.
4. Use a bounded task branch unless an explicitly authorized exception applies; select the branch prefix from `docs/GIT_WORKFLOW.md`.
5. Implement only the approved scope and run task-appropriate validation.
6. Create a result report and an execution log when the work is substantial or creates a durable artifact.
7. Have the authorized Git writer package the exact public files after reviewing the diff. Agents do not self-merge or push private history.
8. After review, record the journal entry and promote only settled truth into the appropriate roadmap, control record, or canonical standard.

For a production, VPS, database, destructive, privacy-sensitive, or authority-changing action, stop at step 1 until the applicable control record, gate, and task authorization permit the action. `agents/VPS_ORCHESTRATION.md` defines the VPS interaction modes.

Before beginning substantial work:

1. Confirm the repository path.
2. Read TODO.md (local disk version).
3. Read AGENTS.md if present.
4. Apply applicable standards.
5. Inspect `git status --short --branch`.
6. Identify exact task, allowed files, and required validation.
7. If the task involves a managed repository, read its CONTROL.md.
8. Stop if any instruction is ambiguous or destructive.

---

## 8. Minimum Task-Close Checks

Before declaring task completion:

1. Review every changed file.
2. Run relevant tests and validation.
3. Run `git diff --check` for tracked changes.
4. Verify `git status` is as expected.
5. Confirm no secrets or private content are staged.
6. Confirm TODO.md was not changed by the agent.
7. Confirm required result report exists.
8. Confirm required execution log exists (if applicable).
9. Produce an integration packet if the work should be promoted to the
   authoritative branch. See `docs/GIT_WORKFLOW.md` §Branch Integration Workflow
   for the packet format and lifecycle.
10. Report final branch, status, and anything requiring Buddy.

---

## 9. Minimum Session-Close Checks

Before closing a session:

1. Inspect all task result reports for completion state.
2. Discover task boundaries from outbox artifacts, agent logs, and session context. Create a per-session task journal at `_internal/logs/sessions/session-<N>/TASK_JOURNAL.md` with one template section per task.
3. GPT fills the semantic fields (objective, assessment, decisions, lessons, follow-up). The agent does not infer semantic content.
4. Verify Git state and distinguish pre-existing dirt from session changes.
5. Confirm `_internal/` or equivalent private-data directory is not staged.
6. Verify all required session logs exist.
7. Update or verify TODO.md contains the next-session plan.
8. Commit and push authorized durable changes.
9. Do not discard, restore, or truncate TODO.md.

---

## 10. Git and Private-Data Boundaries

- `_internal/` (or per-repository equivalent) must never be tracked or staged.
- Private manifests, execution packets, backup logs, and scope-decision artifacts stay outside Git.
- Commits must not contain passwords, secrets, private absolute paths, or sensitive content.
- Use `git-steward` or equivalent for Git write operations unless explicitly authorized otherwise.
- **Temporary provision:** Until Git Steward is operational in `ivy-control-vps`,
  the GPT orchestrator may authorize a specific bounded commit for a reviewed
  manifest. See `docs/GIT_WORKFLOW.md` §Temporary Git-authority model for the
  full rules and restrictions. This provision expires when Git Steward is
  available.

---

## 11. Canonical human task directory

The durable archive is the one canonical human-facing directory for each
completed task: `_internal/orchestration/repos/<repo>/tasks/<task-id>/` or
`_internal/orchestration/cross-repo/tasks/<task-id>/`. It contains exactly one
`README.md` task index and one `final-report.md` marked `# Canonical Final
Report`, plus `task.md`, `manifest.json`, and detailed evidence or links.
Buddy opens the README or final report; role-specific maker, checker, custody,
decision, and log records remain detailed evidence, not competing outcomes.

Final reports give identity/objective, repository-qualified absolute paths,
starting/ending SHAs, disposition, change and validation summary, limitations,
decisions, next action, and links. Worktree cleanup is prohibited until packet,
maker result, checker result, and execution log are copied or linked and sealed
from this directory. Existing historical inbox/outbox files are retained and
linked, never silently moved. Cross-repository reports must name the owning
repository with absolute paths.

`tests/test_task_directory.py` enforces a final report, index links, evidence
section, and cross-repository path qualification.

## 12. Session Journals

Each managed repository must declare its journal location in AGENTS.md, CONTROL.md, or a clearly identified private local supplement.

- The portfolio journal (`_internal/logs/sessions/SESSION_JOURNAL.md` in ivy-control-vps) records one row per substantial reviewed agent result across all managed repositories.
- Repository journals record repository-local history of reviewed results with the same semantic fields.
- Every substantial reviewed task must receive a journal entry.
- Journal entries link to result reports.
- Local path variation is allowed.
- Alignment requires actual evidence of use (see §21A of the private workflow for the four evidence levels).
- Reports and journals remain evidence, not canonical architecture.
- Private GPT orchestration mechanics remain under `_internal/`.
