# Git Workflow

**Status:** Local-development standard for the Mac-based repository. Portfolio-wide Git conventions remain pending — see the conventions list below.

### Pending portfolio-wide Git conventions

The following are explicitly not defined here and must be drafted as a separate portfolio-wide standard before they become requirements:

- Repository naming convention
- Default branch policy
- Commit-message house style
- Pull-request policy and review requirements
- Public-by-default engineering history expectations
- Private runtime-data exclusion from public repositories
- Initial publication review process
- Git history sanitization procedure
- Agent Git write authority model (beyond the existing local-agent rules)
- Exact-SHA deployment tagging
- Tag and release versioning

This document preserves the operator/implementation model for the local checkout. The portfolio-wide standard will supersede or extend these rules for the full portfolio.

## Principles

- The public repository at `/Users/buddy/projects/ivy-control-vps` contains only material that may be pushed to GitHub.
- Private notes live at `/Users/buddy/projects/ivy-control-vps/_internal/`.
- `_internal/` is excluded via `.gitignore` plus pre-commit and pre-push hooks, and must not be tracked by the public repository. It remains visible on disk and in the editor — ignored does not mean hidden.
- `_internal/` must be its own local Git repository with no remote configured.
- Public and private history must remain physically and logically separate.
- Agents must not self-merge unless a task explicitly authorizes a bounded integration.
- Ambiguity must be reported rather than resolved by inventing policy.

## Repository layout

```text
/Users/buddy/projects/ivy-control-vps/           public Git repository
/Users/buddy/projects/ivy-control-vps/_internal/ private local-only Git repository
```

The nested `_internal/` repository exists so private notes are versioned locally without entering public Git history.

The public repository must never stage, commit, merge, or push `_internal/`.

The private `_internal/` repository must have no GitHub remote and must never be pushed.

## Why separate repositories are required

Git pushes commits, not selected files.

If public and private files share one commit history, pushing that history can expose private files even if later commits delete them.

A separate nested local-only repository prevents ordinary public commits from containing private note contents.

Branch separation inside one repository is not sufficient because:

- private commits can be pushed accidentally;
- private commits can be merged or cherry-picked accidentally;
- switching branches can remove private files from the working tree;
- pushed Git history can retain private files even after deletion.

## Public repository rules

Public work may include:

- `README.md`;
- `AGENTS.md`;
- `docs/`;
- `workflows/`;
- approved source code and tests.

Before every public commit or push:

```bash
GIT_PAGER=cat git status --short --branch
GIT_PAGER=cat git diff --cached --name-only
GIT_PAGER=cat git log --oneline --decorate --graph origin/main..HEAD
GIT_PAGER=cat git diff --name-only origin/main...HEAD
```

If `_internal/` appears in a staged file list, commit diff, outgoing commit, or public history, stop. Do not commit or push.

Never run:

```bash
git add .
git add -A
git push --all
git push --mirror
```

Use exact-file staging only.

## Private `_internal/` repository rules

The private repository is rooted at:

`/Users/buddy/projects/ivy-control-vps/_internal/`

It must:

- have its own `.git/` directory;
- have no remote configured;
- track private notes and logs locally;
- remain physically present regardless of public branch switches;
- never be added as a submodule or gitlink in the public repository;
- never be pushed to GitHub;
- never contain secrets merely because it is private.

Before committing private notes:

```bash
cd /Users/buddy/projects/ivy-control-vps/_internal
GIT_PAGER=cat git status --short --branch
GIT_PAGER=cat git diff --cached --name-only
```

Use exact-file staging and local commits only.

Confirm no remote exists:

```bash
git remote -v
```

Expected result: no configured remotes.

## Buddy working locally

For public work:

1. Work in `/Users/buddy/projects/ivy-control-vps`.
2. Start from updated public `main`.
3. Create a short-lived public task branch.
4. Make and review only public changes.
5. Stage exact public files only.
6. Confirm `_internal/` is absent from staged and outgoing diffs.
7. Commit and push the public task branch.
8. Merge after review or under explicit bounded authorization.

For private notes:

1. Work in `/Users/buddy/projects/ivy-control-vps/_internal`.
2. Confirm the private repository has no remote.
3. Stage exact private files only.
4. Commit locally.
5. Do not push.

## Local implementation agents

OpenCode, Codex, and similar agents must:

- read `AGENTS.md` first;
- read the local working-tree `TODO.md` without modifying it;
- confirm which repository they are operating in before Git actions;
- never treat the public and private repositories as one Git history;
- use exact-file staging;
- never stage `_internal/` from the public repository;
- never add `_internal/` as a submodule or gitlink;
- never configure a remote in the private repository;
- never push private history;
- never delete private history without explicit approval;
- never assume GitHub is a backup for the private repository.

Implementation agents edit and validate files. They must not stage, commit, push, merge, integrate, restore, clean, or alter Git state directly.

For Git writes, invoke `git-steward`.

## Git Steward handoff

`git-steward` handles authorized Git packaging and closeout. It must not edit or delete files.

- Implementation agents edit and validate files.
- When Git write operations are needed, invoke the global `git-steward` subagent.
- `git-steward` inspects the working tree, classifies changed paths, stages exact paths, commits, pushes, and performs bounded integration — all within the current task authority.
- `git-steward` runs a mandatory internal certainty check before every write operation. It proceeds autonomously after the check passes.
- `git-steward` does not require user confirmation for routine authorized Git work. It stops only for real ambiguity or missing authority.
- No `LOG.md` requirement is introduced by this workflow.

Existing safeguards remain unchanged:
- Exact-path staging remains mandatory.
- Public/private separation remains unchanged.
- Local hooks (`pre-commit`, `pre-push`) remain active.
- `TODO.md` remains read-only — never staged, committed, or modified.
- No file deletion is permitted by any agent, including `git-steward`.

## Branch naming

Public branches:

```text
<type>/<short-description>
```

Suggested types:

- `docs/`
- `feat/`
- `fix/`
- `ops/`
- `chore/`
- `recovery/`

The private `_internal/` repository may normally remain on `main` because it has no remote and no collaboration workflow.

## Commit messages

Use concise imperative messages describing one coherent change.

Examples:

- `Clarify private repository boundary`
- `Record agent workflow decision`
- `Fix documentation links`

Public and private changes must be committed in their respective repositories.

## Merge and integration authority

- Agents do not approve their own work.
- Agents do not merge public work unless the task explicitly authorizes a bounded integration after validation.
- The private repository is never merged into the public repository.
- Buddy remains the default authority for policy and public-history decisions.

## Dirty trees and recovery

- Do not pull, merge, rebase, switch branches, restore, or clean over unexplained changes.
- Inspect tracked, untracked, staged, modified, and nested-repository state first.
- Do not discard work automatically.
- Do not use broad restore commands such as `git checkout ... -- .` or `git restore .`.
- Use exact-file operations only.
- Treat `_internal/`, `TODO.md`, uncommitted changes, and local-only commits as protected user data.
- Git is version control, not a complete backup system.

## Destructive commands

The following are prohibited without Buddy's explicit approval for the exact command and exact targets:

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
- deleting repositories or branches;
- deleting or overwriting untracked, private, ignored, or uncommitted data.

## Secrets

- Never commit secrets.
- Do not store secrets in `_internal/` merely because it is private.
- Use safe placeholders in public examples.
- Credential storage requires a separate approved design.

## Safeguards (implemented)

The following local protections are in place:

- `.gitignore` (root-anchored `/_internal/`) — excludes `_internal/` from the public repository working tree. Ignored does not mean hidden; `_internal/` remains visible on disk and in the editor.
- `.git/hooks/pre-commit` — blocks any public commit that stages `_internal/` paths.
- `.git/hooks/pre-push` — blocks any public push whose outgoing history contains `_internal/` paths.
- `_internal/.git/hooks/pre-push` — blocks all pushes from the private repository.

Back up the private repository separately. A local Git repository without a remote protects history from ordinary edits, but not from disk loss or destructive shell commands.

## Private repository visibility and recovery

`_internal/` is ignored by public Git but intentionally visible on disk and in the editor:

- It is an independent no-remote private Git repository. Commands that affect it must be run from inside `_internal/`.
- If a tracked private file is deleted from the working tree, it can be recovered from the private repository: `cd _internal && git restore <file>`.
- Public Git commands (`git add`, `git commit`, `git push` from the parent `ivy-control-vps` directory) must never be used as a substitute for managing private history.
- The private repository has no remote and its pre-push hook blocks all pushes. It is not backed up by GitHub.

## Legacy `internal/` path

The old `internal/` directory (gitignored) still exists and is preserved temporarily. New private content should be created under `_internal/`. A later task should migrate any remaining useful content and remove the legacy path.

## Public Repository Readiness

Before a repository is published on GitHub, the following must be verified:

### Secrets and credentials
- `.env`, `.env.*`, `tunnel.json`, `*.key`, `*.pem` in `.gitignore`
- No API keys, tokens, or passwords in committed files (`grep -r` zero hits)
- No PII in datasets, examples, or test fixtures
- No internal paths like `/Users/buddy/` in committed files

### Generated and runtime files
- Large binary files (>1 MB) excluded — no datasets, model weights, databases
- `node_modules/`, `__pycache__/`, `.venv/`, `.idea/` neither committed nor untracked
- Logs, caches, generated outputs gitignored or in designated directories

### Documentation and README
- `README.md` describes purpose, status, and basic usage — no placeholder content
- `AGENTS.md` exists if agent interaction is expected
- `README_INTERNAL.md` exists if durable memory content is needed
- No TODO, FIXME, or placeholder stubs in public-facing text
- LICENSE present or documented lack of license

### Fresh-clone validation
- Repository is self-contained — clone builds and tests pass
- Dependencies documented (`requirements.txt`, `package.json`, `pyproject.toml`)
- CI workflow configured (GitHub Actions or equivalent)

### Remote and identity
- Canonical remote URL matches the intended GitHub repository
- Push identity (GitHub user or deploy key) matches the repository owner
- Branch and upstream state confirm clean history with no unexpected divergence

Detailed gate evidence is recorded in `repos/<repo>/RELEASE_GATES.md`. This section defines the standards; the gate file records the specific pass/fail evidence.
