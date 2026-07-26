# Git Workflow

**Status:** Current Git engineering standard for the Mac-based portfolio control plane. Existing repositories and history are preserved unless a separate migration is authorized; these conventions do not authorize renames, rewrites, publication, or deployment.

## Naming and identity

- Prefer lowercase kebab-case for new repository names and canonical Ivy portfolio slugs: `reddit-ops`, `sjc-intel`, `ivy-control-vps`.
- Preserve established repository names, URLs, default branches, and language-specific package names. A legacy underscore name is not a reason to rename a repository.
- Python packages/modules use lowercase snake_case when the language requires it. Repository and package names need not match.
- Canonical durable filenames are `README.md`, `AGENTS.md`, `CONTROL.md`, and `RELEASE_GATES.md` when those roles apply.
- New task/session identifiers use `session-<N>` and `agent-<N>-<descriptive-slug>`; see `docs/REPOSITORY_WORK_PROTOCOL.md`.

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

For the full task-to-promotion sequence, including result reports, logs, journal entries, and canonical-document promotion, follow `docs/REPOSITORY_WORK_PROTOCOL.md`. This document owns Git boundaries; it does not replace the work-continuity protocol.

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

## Git Steward MVP

The Git Steward MVP lives at `tools/git_steward/` in the control repository. It
is a publication-candidate validator with three independent operational modes.
It does not execute push, pull-request creation, or any remote mutation during
this task.

### Operational modes

The MVP exposes three explicit modes via `--mode`:

| Mode | CLI flag | Purpose |
|---|---|---|
| Validate | `--mode validate` (default) | Read-only safety-gate check; no approval required |
| Publish branch | `--mode publish-branch` | Requires Gate 1; validates + generates push command |
| Create draft PR | `--mode create-draft-pr` | Requires Gate 2; validates + generates draft PR command |

Each mode is independent. There is no combined push-and-PR mode, no merge mode,
and no generic ambiguous execution mode.

### Scope

The MVP validates 21 safety checks per invocation:

1. exact repository path
2. exact repository identity
3. exact remote identity
4. exact candidate branch
5. candidate branch is not the default branch
6. exact expected base SHA
7. base is an ancestor of candidate HEAD
8. exact expected candidate HEAD
9. clean tracked state
10. no untracked files
11. approved tracked-file manifest
12. protected paths absent
13. secret scan passes
14. large-file scan passes
15. absolute developer paths absent
16. operational mode matches granted authority
17. explicit branch push refspec uses `refs/heads/`
18. explicit PR base and head
19. merge remains unsupported
20. deterministic SHA-256 evidence generated
21. upstream-to-main warning recorded (non-blocking)

It does **not** support:

- merging, rebasing, or force-pushing;
- default-branch push;
- branch deletion;
- tag or release publication;
- multi-repository batches;
- automatic credential changes;
- unattended destructive cleanup.

### Usage

```bash
# Validate mode (no approval required)
python3 -m tools.git_steward.steward <manifest-path>

# Publish-branch mode (requires Gate 1 approval)
python3 -m tools.git_steward.steward <manifest-path> --mode publish-branch

# Create-draft-PR mode (requires Gate 2 approval)
python3 -m tools.git_steward.steward <manifest-path> --mode create-draft-pr

# JSON output for programmatic consumption
python3 -m tools.git_steward.steward <manifest-path> --json
```

A publication manifest is a YAML or JSON document specifying the repository
path, candidate branch, expected SHAs, protected-path policy, and approval
state. See `_internal/manifests/session-13/palworld-baseline-v1.yaml` for an
example.

### Independent authority gates

Publication to a remote repository requires three explicit, independent gates:

| Gate | Mode | Action | Authority in manifest |
|---|---|---|---|
| Gate 1 | `publish-branch` | Branch push | `approvals.branch_publication.approved` |
| Gate 2 | `create-draft-pr` | Draft PR creation | `approvals.draft_pr_creation.approved` |
| Gate 3 | N/A (outside MVP) | Merge | Buddy + GitHub review |

Rules:

- Gate 1 and Gate 2 are structurally independent. Approving Gate 1 does not
  imply Gate 2, and vice versa.
- Gate 3 is outside Git Steward's scope entirely — it requires GitHub review
  and Buddy decision.
- An approval set to `true` requires both `approved_by` (non-empty string) and
  `approval_ref` (non-empty string).
- An execution agent cannot approve its own work.
- GPT review does not constitute Buddy approval.
- `false` approval fields are valid in `validate` mode.
- No single agent invocation may pass more than one gate without explicit
  task authority.
- There is no merge approval field in the executable MVP contract.

### SHA-256 evidence

All digests use full 64-character SHA-256 with UTF-8 encoding.

**Canonical manifest digest:** computed from deterministic JSON serialization
with sorted keys. Covers: `task_id`, `session_id`, `repository_path`,
`repository_remote`, `expected_base_branch`, `expected_base_sha`,
`candidate_branch`, `expected_candidate_head`, `target_pr_base`, and all
`manifest` fields. Excludes: timestamps, run IDs, evidence output paths,
and approval values.

**Tracked-file digest:** computed from sorted `git ls-files` output joined
with newline separators, then SHA-256 hashed.

Approval changes alter execution evidence (different gate outcomes).
Tracked-file changes alter the tracked-file digest.
Prior evidence is invalidated when manifest fields or tracked files change.

### Upstream policy

If a candidate branch has an upstream configured to `origin/main`, Git Steward:

- records the upstream state in evidence;
- emits a non-blocking warning;
- always uses an explicit full refspec for publication
  (`refs/heads/<branch>:refs/heads/<branch>`);
- never allows a bare `git push` that would follow the upstream.

Do not alter a candidate branch's upstream during Git Steward validation.

### Evidence sanitization

Evidence files are checked for unsanitized content including:

- token patterns (`ghp_`, `gho_`, `github_pat_`, `sk-`);
- private key markers (`-----BEGIN`);
- non-GitHub HTTP URLs.

Each check produces a warning printed to stderr. Evidence is written before
sanitization checking so the check result does not block evidence generation.

### Safety guarantees

- All validation functions are read-only — no git mutation occurs during
  validation.
- Push commands are generated as strings only; the MVP never executes them.
- The generated push command uses an explicit full refspec
  (`refs/heads/<branch>:refs/heads/<branch>`) — never a bare `git push`.
- Publication destination is never determined by upstream configuration.
- The generated PR command includes `--draft` — never a non-draft PR.
- No `--force` flag appears in any generated command.
- No merge command is generated.
- Every failure produces a stable error identifier (`ERR_*`), a nonzero exit,
  and a human-readable explanation.
- Stale or removed files: the MVP does not delete, add, or modify files.
- All validation occurs before any mutation path is executed.

### First pilot environment

The first publication pilot is intentionally Mac-based. It tests publication
logic, credential readiness, and exact remote SHA verification — not VPS
execution. VPS deployment of Git Steward is a separate follow-up task.

### Implementation agents

Implementation agents edit and validate files. They must not stage, commit,
push, merge, integrate, restore, clean, or alter Git state directly.

For Git writes, the executing agent follows the task authorization model in
`docs/REPOSITORY_WORK_PROTOCOL.md`. The Git Steward MVP validates candidate
state and generates commands; it does not perform writes on its own.

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
- `architecture/`

The private `_internal/` repository may normally remain on `main` because it has no remote and no collaboration workflow.

## Commit messages

Use one coherent change per commit. For new portfolio-managed work, prefer scoped Conventional Commit syntax:

Examples:

- `docs(control-plane): define portfolio universe`
- `feat(health): add evidence card schema`
- `fix(reddit-ops): correct collector validation`
- `ops(backup): record restore verification procedure`

The scope is optional when it adds no clarity. Existing concise imperative history remains valid and must not be rewritten for style. Keep migrations with their necessary validation and rollback material when they are one coherent change.

Public and private changes must be committed in their respective repositories.

## Merge and integration authority

- Agents do not approve their own work.
- Agents do not merge public work unless the task explicitly authorizes a bounded integration after validation.
- The private repository is never merged into the public repository.
- Buddy remains the default authority for policy and public-history decisions.

## Branch and review model

- `main` is the intended default integration branch for new or actively published repositories. Legacy default branches remain in place until a separately approved migration.
- Use a short-lived task branch by default for tracked work. Typical prefixes are `docs/`, `feat/`, `fix/`, `ops/`, `chore/`, `recovery/`, and `architecture/`.
- Direct public commits to `main` are exceptional: Buddy must explicitly authorize the exact bounded change, and normal validation/review still applies.
- Pull requests are preferred when the repository has a suitable review surface. A reviewable branch plus exact diff and validation evidence remains the minimum until then.
- Agents may inspect, edit within their task scope, create proposals, and run validation. Implementation agents do not directly stage, commit, push, merge, delete, restore, clean, or rewrite history. `git-steward` performs only explicitly authorized exact-path Git writes.

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
- a clearly identified private local supplement exists if durable memory content is needed
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

## VPS engineering-workspace readiness

A VPS engineering workspace is a clean public checkout for controlled ongoing
work. It is not automatically a production deployment. Before residency,
verify the exact published SHA, remote identity, clean working tree, clone
footprint and capacity reserve, and a rollback SHA. Confirm `_internal/` is
ignored and absent, and that no secrets, private host paths, temporary
experiments, or unreviewed generated output enter the checkout.

The checkout may contain intentional publication-safe workflow artifacts, but
private task packets, raw execution evidence, runtime logs, credentials, and
private prompts belong in an explicitly provisioned location outside Git. A
tracked root `TODO.md` that is not current or publication-safe may be omitted
from a declared sparse workspace profile; never replace it with private task
content. Do not edit the workspace ad hoc: tracked changes remain branch-based
and review bound. A deployed runtime, service, timer, database, or data
authority still requires its separate gate.
