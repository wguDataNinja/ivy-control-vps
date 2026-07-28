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
| Result report | `_internal/outbox/session-<N>/<NN>-<descriptive-slug>.md` | Consolidated outcome, evidence, validation, next handoff |
| Execution log | `_internal/logs/agents/YYYY-MM-DD/<task-slug>.md` | Concise chronology of actions performed |

Writing these artifacts is explicitly authorized despite the general `_internal/` protection rule. Result reports must contain the minimum fields defined in `docs/REPOSITORY_WORK_PROTOCOL.md` §4. Execution logs must not duplicate the report — they record what was done, not what was found.

Tasks without a session number use `session-0`.

## Work lifecycle

Follow:

```text
task
 ↓
bounded implementation
 ↓
validation
 ↓
result report → _internal/outbox/session-<N>/
 ↓
review
 ↓
promotion into authority