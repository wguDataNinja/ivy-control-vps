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

Preferred format: `agent-<number>-<descriptive-slug>` or equivalent per-repository convention.

Identifiers must not be reused within the same session and actor sequence. A completed or superseded task retains its identifier.

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

### Repository-approved locations

| Repository | Prompt location | Result-report location | Log location |
|---|---|---|---|
| Ivy Control VPS | `_internal/inbox/session-<N>/` | `_internal/outbox/session-<N>/` | `_internal/logs/agents/YYYY-MM-DD/` |
| Palworld KB | `_inbox/` | `agent-reports/` (by type) | `logs/agent-log.md` |
| SJC Intel | (none defined) | `_outbox/` | `logs/agents/` |
| Other repos | `_inbox/`, `inbox/`, or documented equivalent | `_outbox/`, `outbox/`, or documented equivalent | `logs/` or documented equivalent |

A repository using an alternative path must document it in AGENTS.md, README_INTERNAL.md, or CONTROL.md.

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
| Journal | Navigation across reviewed substantial results | A task transcript |
| Canonical documentation | Settled operating, product, or policy truth | A replacement for task evidence |

An inbox artifact is preferred for multi-step or cross-session work, but a direct handoff remains valid when recorded in the result report. Read-only exploration, brief questions, and trivial safe changes may use a reduced workflow; substantial implementation, audit, architecture, durable-artifact, or operational work must use the full evidence path.

---

## 7. Minimum Start-of-Work Checks

### How to make a tracked change

For a normal, non-production change, use this path:

1. Identify the relevant authority document and task scope. Do not use a result report or chat history as substitute authority.
2. Inspect the current working tree and preserve unrelated or protected work.
3. Use a bounded task branch unless an explicitly authorized exception applies; select the branch prefix from `docs/GIT_WORKFLOW.md`.
4. Implement only the approved scope and run task-appropriate validation.
5. Create a result report and an execution log when the work is substantial or creates a durable artifact.
6. Have the authorized Git writer package the exact public files after reviewing the diff. Agents do not self-merge or push private history.
7. After review, record the journal entry and promote only settled truth into the appropriate roadmap, control record, or canonical standard.

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
9. Report final branch, status, and anything requiring Buddy.

---

## 9. Minimum Session-Close Checks

Before closing a session:

1. Inspect all task result reports for completion state.
2. Verify Git state and distinguish pre-existing dirt from session changes.
3. Confirm `_internal/` or equivalent private-data directory is not staged.
4. Verify all required session logs exist.
5. Update or verify TODO.md contains the next-session plan.
6. Commit and push authorized durable changes.
7. Do not discard, restore, or truncate TODO.md.

---

## 10. Git and Private-Data Boundaries

- `_internal/` (or per-repository equivalent) must never be tracked or staged.
- Private manifests, execution packets, backup logs, and scope-decision artifacts stay outside Git.
- Commits must not contain passwords, secrets, private absolute paths, or sensitive content.
- Use `git-steward` or equivalent for Git write operations unless explicitly authorized otherwise.

---

## 11. Session Journals

Each managed repository must declare its journal location in AGENTS.md, README_INTERNAL.md, or CONTROL.md.

- The portfolio journal (`_internal/logs/sessions/SESSION_JOURNAL.md` in ivy-control-vps) records one row per substantial reviewed agent result across all managed repositories.
- Repository journals record repository-local history of reviewed results with the same semantic fields.
- Every substantial reviewed task must receive a journal entry.
- Journal entries link to result reports.
- Local path variation is allowed.
- Alignment requires actual evidence of use (see §21A of the private workflow for the four evidence levels).
- Reports and journals remain evidence, not canonical architecture.
- Private GPT orchestration mechanics remain under `_internal/`.
