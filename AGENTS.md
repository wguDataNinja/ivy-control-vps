# AGENTS.md

This repository is developed locally with OpenCode, Codex, or similar coding agents.

This file is the single agent instruction file for this repository. Do not look for or create nested `AGENTS.md` files. Do not rely on separate agent contracts unless the task explicitly names one.

## Scope

Work only in:

`/Users/buddy/projects/ivy-control-vps`

Before acting:

1. Run `pwd` and confirm the path.
2. Read the current local `TODO.md` from disk.
3. Read the repository standards that apply to the task, including `docs/OPERATING_MODEL.md`, `docs/LOGGING_STANDARD.md`, and any repository-control or portfolio-convention document referenced by the task.
4. Inspect `git status --short --branch`.
5. Identify the exact task, allowed files, applicable standards, control-sheet or gate implications, and validation required.
6. If the task involves a managed repository, read its `repos/<repo>/CONTROL.md` before acting.
7. Stop and ask if the task or any destructive instruction is ambiguous.
6. Stop and ask if the task or any destructive instruction is ambiguous.

A request to read a file authorizes no Git or filesystem mutation.

## TODO.md

`TODO.md` is task input written by Buddy or GPT.

Agents must:

- read the local working-tree version;
- never replace it with a Git version;
- never edit, restore, stage, commit, stash, clear, or advance it;
- report recommended next work in the final response instead of changing it.

## Development behavior

Agents may perform ordinary development work explicitly required by the task, including:

- reading repository files;
- editing approved files;
- creating approved files;
- running tests and validation;
- using Git for task branches, commits, pushes, and task-specific integration when explicitly authorized.

Agents must:

- keep changes within scope;
- preserve unrelated work;
- inspect existing instructions and current state before editing;
- distinguish implemented behavior from planned or provisional behavior;
- avoid inventing policy, permissions, paths, credentials, or production details;
- report failed validation, ambiguity, missing prerequisites, and process friction;
- verify claims with evidence before reporting completion.

## Protected data

Treat these as protected user data:

- `_internal/`;
- `internal/` if present;
- untracked files;
- ignored files;
- uncommitted changes;
- `TODO.md`;
- local-only notes and task history.

Do not delete, overwrite, restore, move, clean, stage, commit, or expose protected data unless the task names the exact path and Buddy explicitly approves the exact action.

Git does not protect ignored, untracked, or uncommitted content.

## Destructive commands

Do not run destructive commands without Buddy's explicit approval for the exact command and exact targets.

Prohibited unless specifically approved:

- `rm -rf`;
- broad `rm` commands;
- `find ... -delete`;
- `find ... | xargs rm`;
- `git clean`;
- `git reset --hard`;
- `git checkout ... -- .`;
- `git restore .`;
- force-push;
- history rewriting;
- deleting branches;
- deleting or overwriting untracked or ignored files;
- mass replacement of the working tree.

Before any approved deletion or cleanup:

1. Show the exact target list.
2. Confirm tracked, untracked, ignored, and modified status.
3. Explain what is recoverable and what is not.
4. Obtain explicit approval.
5. Use exact-file operations only.

Ambiguous language is never authorization for deletion.

## Git rules

Git is for version control, not as a substitute for backups.

Agents must:

- inspect status before Git operations;
- avoid touching unrelated changes;
- use exact-file staging;
- use task branches unless the task explicitly authorizes direct work on `main`;
- never force-push;
- never rewrite shared history;
- never assume ignored or untracked files are recoverable;
- never merge or delete branches unless the task explicitly authorizes it;
- use `GIT_PAGER=cat` for review commands that might open a pager.

When task-specific integration is authorized, validate first, then commit, push, integrate, and verify local and remote SHAs.

## Git write delegation

To perform Git write operations, invoke the global `git-steward` subagent. Do not run those operations yourself.

- Normal implementation agents may run read-only Git inspection commands (`git status`, `git diff`, `git log`, `git show`, `git rev-parse`, `git branch`, `git remote -v`, `git ls-files`, `git check-ignore`, `git submodule status`).
- Normal agents must not stage, commit, push, merge, integrate, restore, clean, or alter Git state directly.
- `git-steward` owns routine staging, commit, push, and bounded integration within the current task authority.
- `git-steward` proceeds autonomously only after its mandatory internal certainty check passes.
- `git-steward` is still bound by `AGENTS.md`, `docs/GIT_WORKFLOW.md`, protected paths, and current task authority.
- Invoking `git-steward` does not create commit, push, merge, deletion, cleanup, or restore authority beyond what the current task already provides.
- No agent, including `git-steward`, may delete files.
- No agent may use Git to overwrite or discard `TODO.md`, `_internal/`, ignored, untracked, private, or unrelated work.
- Buddy should only be involved for genuine ambiguity, policy, permission, or protected-data decisions.

## Public and private boundaries

- Public tracked documentation may be pushed to GitHub.
- Private material must not be included in public commits.
- Do not store secrets in tracked or untracked documentation.
- Do not assume all local Git history is safe to push.
- Verify the exact diff before every commit and push.

## Logging

Follow `docs/LOGGING_STANDARD.md`.

Before meaningful work, read the applicable portfolio standards (`docs/OPERATING_MODEL.md`, `docs/REPOSITORY_CONTROL_MODEL.md`, `docs/LOGGING_STANDARD.md`) and any repository control sheet (`repos/<repo>/CONTROL.md`) that the task affects.

A concise private agent log is required whenever an agent performs meaningful work that:

- changes repository state;
- creates or changes a durable artifact;
- changes configuration or policy;
- performs deployment or operational work;
- changes a repository control sheet, release gate, or portfolio status;
- completes another substantive task with a durable result or decision.

Read-only exploration, simple factual answers, and inspections that produce no durable result or decision normally do not require a log.

Create or update the required log before declaring meaningful work complete. Use the organized private logging path defined by `docs/LOGGING_STANDARD.md`; do not use legacy `SESSION.md` or `LOG.md` as the primary record for new work.

Use the concise format defined by the logging standard. Record the result, validation, unresolved issues, and next work. Reference commits where relevant, but do not duplicate Git history or long command transcripts.

## Validation

Before declaring completion:

- review every changed file;
- run relevant tests or checks;
- run `git diff --check` for tracked changes;
- verify links when editing Markdown;
- confirm no secrets or private content are staged;
- confirm `TODO.md` was not changed by the agent;
- confirm any required private agent log was created or updated before completion;
- report the final branch and working-tree status;
- report anything that still truly requires Buddy.

## Final report

Return only the information needed to understand the result:

- work completed;
- files changed;
- validation performed;
- Git result, if authorized;
- required private log path, when meaningful work required one;
- unresolved issues;
- process friction;
- recommended next task;
- any action that truly requires Buddy.

## VPS work

This file is for local development only.

Do not perform VPS, Hermes, deployment, production, credential, or host-maintenance work from this repository unless Buddy gives a separate explicit task with the exact environment, permissions, and limits.

A separate VPS `AGENTS.md` will be created later in the actual VPS checkout.

### Authorized VPS interaction

Before any VPS work, read these files in order:

1. `agents/VPS_ORCHESTRATION.md` — interaction-mode model, approval boundaries, what each mode allows
2. `_internal/vps-inventory-and-runbook.md` — private host identity, SSH access, workload map, capacity evidence, exact read-only commands, protected workload rules

"Check the VPS" always means Mode 2 (read-only SSH inspection). It never authorizes cleanup, deployment, restart, migration, or service activation. See `agents/VPS_ORCHESTRATION.md` §1a for the complete mode model.