

# Agent Entry Point

This repository supports two distinct agent execution contexts. The repository path is the primary routing signal.

Before performing any write, deployment, maintenance, or operational action:

1. Run `pwd`.
2. Match the current repository path to one of the approved contexts below.
3. Read the required context-specific instructions before continuing.
4. Follow the repository logging standard in `docs/LOGGING_STANDARD.md`.
5. If the path or assigned role is ambiguous, stop and report the ambiguity.

## Local implementation context

Use this context when running in:

`/Users/buddy/projects/ivy-control-vps`

This context is for local implementation agents such as OpenCode or Codex performing:

- documentation work;
- code implementation;
- tests and validation;
- repository maintenance;
- standards development;
- branch and pull-request preparation.

Local implementation agents must:

- read `README.md`, `docs/README.md`, and applicable standards before making changes;
- inspect `internal/README_INTERNAL.md` when it is available locally;
- keep public tracked files publication-safe;
- keep private notes and session material under ignored `internal/` paths;
- create or update a concise agent log for meaningful work as required by `docs/LOGGING_STANDARD.md`;
- avoid VPS operational changes unless the task explicitly grants that authority;
- report unresolved ambiguity, failed validation, and process friction rather than inventing policy.

## VPS orchestration context

Use this context when running in:

`[future VPS repository path]`

This context is intended for Hermes and agents invoked by Hermes for:

- orchestration;
- monitoring;
- maintenance;
- health checks;
- deployment coordination;
- bounded operational actions.

The detailed Hermes contract, permissions, routing rules, approval boundaries, deployment authority, and VPS-private context model are not yet finalized.

Until those standards are approved, an agent running in the VPS context must not assume unrestricted authority. It must stop before destructive, production-changing, policy-changing, credential-related, or self-merging actions unless the task and an approved standard explicitly authorize them.

## Shared rules

All agents must:

- treat GitHub as the source of truth for tracked public material;
- avoid committing anything under `internal/`;
- avoid storing secrets in tracked or untracked documentation;
- validate affected files before declaring work complete;
- keep logs concise and avoid duplicating Git history;
- distinguish implemented behavior from planned or provisional behavior;
- avoid creating new standards or policy where the repository still marks a decision as pending.

## Unrecognized path or role

If the current repository path does not match an approved context, or the assigned role is unclear, do not perform write, deployment, or operational actions. Report the ambiguity and wait for direction.