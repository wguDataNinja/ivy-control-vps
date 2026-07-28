# AGENTS.md


Before acting:

1. Confirm the repository path.
2. Read the current local `TODO.md`.
3. Inspect `git status --short --branch`. For the full checkout-verification
   procedure (remotes, origin/main, divergence), see `agents/HERMES_AGENT_CONTRACT.md`
   §2 Step 0.
4. Identify the task scope, authority source, affected files, validation requirements, and any managed repository impact.
5. Read the applicable standards:
   - `docs/OPERATING_MODEL.md`
   - `docs/REPOSITORY_WORK_PROTOCOL.md`
   - `docs/GIT_WORKFLOW.md`
   - `docs/LOGGING_STANDARD.md`
   - relevant `repos/<repo>/CONTROL.md` when working on a managed repository.

If the task, authority, or allowed changes are unclear, stop and ask.

Reading a file does not authorize mutation.

## Hermes Orchestrator Mode

If you are Hermes operating as the orchestrator, follow this workflow before proposing or delegating work:

1. Confirm repository identity and read required authority documents.
2. Read the applicable roadmap and repository control documents.
3. Identify and execute required gates before planning work.
4. Report gate results before proposing implementation paths.
5. If a gate fails, stop execution planning and escalate according to the Hermes contract.
6. Only after approval and successful gates, create task packets and delegate work.

Before relying on the control-plane checkout for any of the above, execute the
checkout-verification procedure in `agents/HERMES_AGENT_CONTRACT.md` §2 Step 0.
Do not silently treat a dirty, detached, stale, or divergent checkout as
authoritative.

Hermes does not choose implementation work around failed gates.

## Repository authority

Use the correct authority for each question:

| Question | Authority |
|---|---|
| What is Ivy Control VPS? | `README.md`, `docs/OPERATING_MODEL.md` |
| What are Buddy's current priorities and direction? | `docs/PORTFOLIO.md`, `docs/PORTFOLIO_INTENT.md` |
| What direction are we taking? | `ROADMAP.md` |
| What is current session work? | `TODO.md` |
| How should agents operate? | This file + applicable standards |
| What is a managed repository's state? | `repos/<repo>/CONTROL.md` |
| What proves operational state? | Evidence artifacts + health contract |
| How does work become durable? | `docs/REPOSITORY_WORK_PROTOCOL.md` |

Generated views are routing aids, not authority.

## Documentation governance

Before creating any durable documentation:

1. Check whether an existing authority document already owns the information.
2. Update the existing authority instead of creating a duplicate.
3. If a new document appears necessary, explain:
   - what question it answers;
   - why existing documents cannot own it;
   - who owns future updates.

Do not create new standards, guides, plans, summaries, or reference documents without this review.

Prefer:

existing authority → update

over:

new document → new authority

## TODO.md

`TODO.md` is task input from Buddy or GPT.

Agents must:

- read the local working-tree version;
- preserve it;
- never edit, restore, stage, commit, stash, or replace it;
- report recommended future work instead.

## Development behavior

Agents may:

- inspect repository files;
- edit approved files;
- create approved files;
- run tests and validation;
- perform task-authorized implementation work.

Agents must:

- stay within task scope;
- preserve unrelated work;
- verify claims with evidence;
- distinguish completed work from planned work;
- report uncertainty instead of guessing.

## Git

Git history is part of the engineering record.

Agents must:

- inspect status before Git operations;
- preserve unrelated changes;
- keep commits focused and meaningful;
- validate before committing;
- follow `docs/GIT_WORKFLOW.md`.

Agents must not:

- force-push;
- rewrite history;
- delete branches;
- merge protected branches without authorization;
- stage protected or unrelated files.

Normal agents perform Git inspection only unless the task explicitly authorizes Git writes through the repository workflow.

## Protected data

Do not modify, stage, commit, expose, or delete:

- `_internal/`
- `TODO.md`
- ignored files
- untracked files
- unrelated local changes

Protected-data changes require explicit approval.

## Session and task artifacts

Every substantial task must produce two artifacts in `_internal/`:

| Artifact | Path | Purpose |
|---|---|---|
| Result report | `_internal/outbox/runs/<run-id>/<task-id>-<descriptive-slug>.md` | Consolidated outcome, evidence, validation, next handoff awaiting review |
| Execution log | `_internal/logs/agents/YYYY-MM-DD/<task-slug>.md` | Concise chronology of actions performed |

Inbox and outbox paths are active workflow queues, not durable history.

Use inbox for:

- pending task packets;
- bounded instructions awaiting execution;
- active run inputs.

Use outbox for:

- fresh execution results awaiting review;
- validation output awaiting acceptance;
- temporary delivery artifacts.

New Ivy Control VPS inbox/outbox paths must use one canonical queue location:

```text
_internal/inbox/runs/<run-id>/
_internal/outbox/runs/<run-id>/
```

Accepted run ID formats:

- `YYYY-MM-DD-<descriptive-slug>`
- `session-<N>-<descriptive-slug>`

Examples:

- `2026-07-28-portfolio-readiness`
- `2026-07-28-idlehacking-context`
- `session-14-palworld-kb`

Agents must not invent a bare `session-<N>` inbox or outbox directory. Existing
historical `_internal/inbox/session-<N>/` and `_internal/outbox/session-<N>/`
directories are legacy evidence only; do not use them for new artifacts.

If repository-oriented active queue views are needed, use:

```text
_internal/inbox/repos/<repo>/<task-id>/
_internal/outbox/repos/<repo>/<task-id>/
```

Do not duplicate the same artifact into both run and repository queue views.
Choose one canonical active queue location and link from any secondary index.

After Hermes validates a completed task, copy the task packet, execution report,
validation report, and execution log into the durable repository-organized
archive:

```text
_internal/orchestration/repos/<repo>/tasks/<task-id>/
_internal/orchestration/cross-repo/tasks/<task-id>/
```

Use the cross-repo namespace for tasks spanning multiple managed repositories.
Use `_internal/orchestration/cross-repo/tasks/<task-id>/` for portfolio-wide
reviews, multi-repository context packets, authority-resolution work,
control-plane migration work, and cross-repository dependency analysis. Do not
move or delete active inbox/outbox artifacts during archive promotion. Stable
task IDs must link packet, report, validation, log, and archive manifest.

Before writing a new artifact path, validate ambiguous destinations with:

```bash
python3 -m tools.hermes_orchestrator validate-artifact-destination --path <path>
```

Writing these artifacts is explicitly authorized despite the general `_internal/` protection rule. Result reports must contain the minimum fields defined in `docs/REPOSITORY_WORK_PROTOCOL.md` §4, supplemented by the fields below. Execution logs must not duplicate the report — they record what was done, not what was found.

Tasks without a session number must still use a globally distinguishable
`<run-id>` rather than falling back to `session-0`.

### Applicability

These reporting rules apply uniformly to all execution agents — Hermes, OpenCode, Codex, and any future approved executor. Every agent performing substantial work must follow the same artifact conventions regardless of its role, invocation method, or whether it operates as orchestrator, implementer, reviewer, or validator.

### Pre-work requirements

Before beginning any substantial task, every agent must:

1. Determine the current session number from `TODO.md`, the task inbox, or the most recent session journal.
2. Determine the current task number or stable identifier.
3. Locate the matching inbox task packet at `_internal/inbox/runs/<run-id>/`, `_internal/inbox/repos/<repo>/<task-id>/`, or the target repository's documented equivalent inbox path.
4. If the task was received only through a direct chat handoff (no inbox packet exists), create a task packet and place it in the correct inbox location before starting execution. The packet must record the original prompt source, scope, authority boundaries, and validation expectations.

### Post-work requirements

After every substantial task — whether it completes, partially completes, fails, or is blocked — the agent must produce exactly one result report and one execution log at the paths specified above. The result report and log are required even when the task terminates early due to a blocker, gate, error, or ambiguous authority. A task that produces neither a report nor a log is not considered complete.

### Minimum report fields

Result reports must include the following fields. These are consistent with `docs/REPOSITORY_WORK_PROTOCOL.md` §4 and extend them with fields specific to execution agent reporting:

| Field | Description |
|---|---|
| Session | Session number |
| Task number | Task identifier |
| Executor | Agent that performed the work |
| Source task packet | Path to the inbox packet, or "direct handoff" |
| Scope received | Scope as defined in the task or packet |
| Actions performed | What the agent actually did |
| Evidence/validation | Tests, checks, and verification performed |
| Files changed | Paths created, modified, or deleted |
| Blockers/deviations | What stopped progress or differed from the approved scope |
| Final disposition | Completed, partial, failed, blocked, or human decision required |
| Recommended next action | What the next actor or session should do |

## Work lifecycle

Follow:

```text
task
 ↓
bounded implementation
 ↓
validation
 ↓
result report → _internal/outbox/runs/<run-id>/
 ↓
Hermes validation
 ↓
durable artifact archive → _internal/orchestration/repos/<repo>/tasks/<task-id>/ or cross-repo equivalent
 ↓
review
 ↓
promotion into authority
```
