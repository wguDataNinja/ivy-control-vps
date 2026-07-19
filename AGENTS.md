# AGENTS.md

This repository is developed locally with OpenCode, Codex, or similar coding agents.

This is the single agent instruction file for this repository. Do not create nested `AGENTS.md` files unless explicitly required by a repository-specific workflow.

## Scope

Work only in:

`/Users/buddy/projects/ivy-control-vps`

Before acting:

1. Confirm the repository path.
2. Read the current local `TODO.md`.
3. Inspect `git status --short --branch`.
4. Identify the task scope, authority source, affected files, validation requirements, and any managed repository impact.
5. Read the applicable standards:
   - `docs/OPERATING_MODEL.md`
   - `docs/REPOSITORY_WORK_PROTOCOL.md`
   - `docs/GIT_WORKFLOW.md`
   - `docs/LOGGING_STANDARD.md`
   - relevant `repos/<repo>/CONTROL.md` when working on a managed repository.

If the task, authority, or allowed changes are unclear, stop and ask.

Reading a file does not authorize mutation.

## Repository authority

Use the correct authority for each question:

| Question | Authority |
|---|---|
| What is Ivy Control VPS? | `README.md`, `docs/OPERATING_MODEL.md` |
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

## Work lifecycle

Follow:

```text
task
 ↓
bounded implementation
 ↓
validation
 ↓
result report
 ↓
review
 ↓
promotion into authority