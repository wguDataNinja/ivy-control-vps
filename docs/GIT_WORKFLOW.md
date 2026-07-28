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
| Gate 3 | N/A (outside MVP) | Merge | [Gate 3 — Merge Review Procedure](#gate-3--merge-review-procedure) |

Rules:

- Gate 1 and Gate 2 are structurally independent. Approving Gate 1 does not
  imply Gate 2, and vice versa.
- Gate 3 is outside Git Steward's scope entirely — it follows the
  [Gate 3 — Merge Review Procedure](#gate-3--merge-review-procedure) defined
  below, which requires GitHub review, Buddy decision, and post-merge verification.
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

## Gate 3 — Merge Review Procedure

Gate 3 is the merge gate. It is outside Git Steward's scope (the MVP stops at
Gate 2). A Gate 3 merge requires explicit task authorization from Buddy with
an approved PR head SHA, base SHA, and merge strategy.

### Identity and topology

Record these before review:

- **Repository:** canonical remote and local path
- **PR number and URL**
- **Exact head SHA** (the approved feature commit)
- **Exact base SHA** (the target branch commit at review time)
- **Merge base** (the common ancestor)
- **Ahead/behind:** commits ahead of base, commits behind head
- **Draft state:** whether the PR is a draft
- **Mergeability:** whether GitHub reports the PR as mergeable

### Review scope

The reviewer must confirm:

1. **Full commit review** — every commit message, author, and diff in the PR.
2. **Full diff review** — every added, modified, and deleted file.
3. **Subsystem classification** — classify each changed file:
   - documentation or governance
   - source code or tooling
   - tests or fixtures
   - configuration or workflow
   - authority documents (CONTROL.md, AGENTS.md, RELEASE_GATES.md)
   - session or evidence artifacts
   - unrelated or private content
4. **Authority-document changes** — verify that any change to `AGENTS.md`,
   `CONTROL.md`, `ROADMAP.md`, `docs/`, or similar authority files is
   independently reviewable and does not silently change governance.
5. **Executable or operational changes** — verify that code changes are
   tested and do not alter production behavior without explicit scope.
6. **Unrelated or private content** — verify that no `_internal/`, credential,
   private path, or unreviewed session artifact appears in the diff.

### Validation

Before approving, the reviewer must run or confirm these pass:

| Check | Command |
|---|---|
| Whitespace / formatting | `git diff --check <base>..<head>` |
| Whitespace / formatting | `git diff --check <base>..<head>` — no output |
| Repository tests | repository-defined test suite |
| Portfolio / control validation | `python3 tools/portfolio_registry.py --validate` |
| Git Steward tests | `python3 -m pytest tests/test_git_steward.py -q` |
| Portfolio status | `tools/show_portfolio_status.sh --no-color` |
| Tool smoke test | verify executable entrypoints load |
| Remote SHA match | confirm remote head equals the approved head SHA |
| Remote base match | confirm remote base equals the reviewed base SHA |
| Mergeable | confirm GitHub reports MERGEABLE |

### Publication safety

Before merging, confirm:

- No secrets, tokens, or credentials in the diff.
- No private paths (`/Users/buddy/`, `_internal/`, etc.) in committed files.
- No large or generated files without a documented exception.
- No protected paths (_.env, *.key, *.pem, tunnel.json, config/ with secrets)
  are added or modified.
- No internal-only artifacts (raw evidence, execution packets, private prompts)
  appear in the diff.
- Test fixtures are clearly identifiable and contain no sensitive data.

### Consequences of merging

Merging:

- updates `main` to include the approved changes at the merge commit SHA;
- makes the approved feature history reachable from `main`;
- does **not** deploy application code, restart services, or activate
  production behavior;
- does **not** change credentials, rotate keys, or modify infrastructure;
- does **not** delete the feature branch;
- does **not** change repository visibility or branch protection;
- does **not** authorize publication in managed repositories;
- does **not** authorize autonomous Hermes operation beyond the bounded
  readiness checks in the authorizing task.

If the merge includes an approved SHA update for a managed repository, update
`repos/<repo>/CONTROL.md` approved_sha in a separate reviewed change.

### Rollback

A merge commit can be reverted with `git revert -m 1 <merge-sha>`. This is a
new commit and requires its own review and approval. Reverting does not
restore the pre-merge branch state — the feature branch remains on the remote
and can be used for a corrected merge after the revert is reviewed.

### Decision outcomes

| Outcome | Meaning | Action |
|---|---|---|
| `APPROVE_MERGE` | All checks pass, authorization matches. | Merge using the authorized strategy. |
| `APPROVE_AFTER_BOUNDED_CORRECTIONS` | Minor non-structural issues found. List exact corrections; re-review only the changed scope. | Apply corrections, re-validate, then merge. |
| `DO_NOT_MERGE` | Structural issues, authority violation, or safety failure. | Stop. Report to Buddy with evidence. |
| `HUMAN_DECISION_REQUIRED` | Precondition changed, ambiguity, or external dependency. | Stop. Report to Buddy without merging. |

### Approval template

A Gate 3 authorization must bind the following:

```text
Repository: <owner>/<repo>
PR: #<number> — <title>
Approved head SHA: <full-sha>
Approved base SHA: <full-sha before merge>
Merge strategy: merge commit | squash | rebase
Permitted actions:
  - merge (merge commit)
  - [list any other explicitly permitted actions]
Explicit non-authorizations:
  - deployment of application workloads
  - production activation
  - database changes
  - systemd changes
  - branch deletion (unless separately authorized)
  - repository visibility changes
  - credential changes
  - managed-repository publication
  - autonomous Hermes operation beyond bounded checks
Authorization valid only if:
  - PR head is still exactly the approved SHA
  - PR base remains the authorized target
  - PR remains mergeable
  - no unreviewed commits have been added
  - no material new findings
```

### Post-merge verification

After merging, verify:

| Check | Command |
|---|---|
| Resulting main SHA | `git rev-parse origin/main` |
| Merge parents | `git show --no-patch --pretty=raw <merge-sha>` — confirm first parent is previous main, second is approved head |
| Head reachability | `git merge-base --is-ancestor <approved-head> origin/main` |
| Branch state | `git branch -r --list origin/<feature-branch>` — branch should still exist unless separately authorized for deletion |
| Stash unchanged | `git stash list` — no new stashes introduced |
| Working tree | `git status --short` — clean unless pre-existing state is documented |
| Validation re-runs | Re-run applicable validation from the merged main |
| Validation re-runs | `git diff --check <pre-merge-base>..origin/main` |
| Validation re-runs | repository test suite |
| Validation re-runs | portfolio validation tools |
| Validation re-runs | tool smoke tests |
| Rollback evidence | Record the pre-merge main SHA for revert reference |

### Reusable merge-review checklist

Use this template in future task packets. Fill each field before deciding.

```text
## Pre-merge verification

- [ ] PR head matches approved SHA: ______
- [ ] PR base matches reviewed base: ______
- [ ] PR is mergeable (MERGEABLE): ______
- [ ] PR is not a draft (or draft merge is separately authorized): ______
- [ ] No unreviewed commits exist: ______
- [ ] Status checks pass (or none configured): ______

## Review scope

- [ ] All commits reviewed
- [ ] All diffs reviewed by file type
- [ ] Authority-document changes independently verified
- [ ] No secrets, private paths, or credentials in diff
- [ ] No protected or internal-only artifacts in diff

## Validation

- [ ] `git diff --check <base>..<head>` — clean
- [ ] Repository tests pass
- [ ] Portfolio validation passes
- [ ] Tool smoke tests pass
- [ ] Remote head matches approved SHA

## Authorization

- [ ] Merge strategy is authorized: ______
- [ ] Non-authorizations are respected
- [ ] Rollback SHA recorded: ______

## Post-merge

- [ ] Merge commit SHA: ______
- [ ] First parent: ______ (previous main)
- [ ] Second parent: ______ (approved head)
- [ ] Approved head reachable from main: ______
- [ ] Feature branch still exists (unless deletion authorized): ______
- [ ] Validation re-runs pass: ______
```

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

## Branch Integration Workflow

The Branch Integration Workflow governs promotion of reviewed work from a
working branch into the repository's authoritative branch (`main`).

It applies after:
- Hermes completes the delegation workflow (`agents/HERMES_AGENT_CONTRACT.md` §3.5f)
- The implementation agent commits completed work to a working branch
- Human review has accepted the result

Task packets that delegate integration work must include the instruction:
"Follow the Branch Integration Workflow in docs/GIT_WORKFLOW.md. Perform
its repository preflight and stop at every required approval gate."

### Prerequisites

#### Normal starting condition

Branch integration must begin from an environment that is:

- a clean working tree — no staged, unstaged, or untracked changes in
  tracked files;
- a known branch — not detached HEAD;
- an understood relationship to the authoritative remote branch —
  divergence classified and documented;
- no in-progress Git operation — no active merge, rebase, cherry-pick,
  revert, bisect, or index lock.

Known and intentionally isolated work may exist in a separate worktree,
separate clone, or documented preservation location, but the environment
where integration executes must satisfy every condition above.

#### Unexpected-dirty-state gate

Before any integration step, the agent must inspect the repository:

- `git status --short --branch`
- `git diff --cached --name-status`
- `git diff --name-status`
- `git stash list`
- `git worktree list --porcelain`
- presence of `MERGE_HEAD`, `REBASE_HEAD`, `CHERRY_PICK_HEAD`,
  `REVERT_HEAD`, `BISECT_LOG`, or `.git/index.lock`

If preflight finds unexpected state, the agent must stop before
integration. Unexpected state includes:

- staged changes;
- unstaged tracked changes;
- untracked files whose disposition is unknown;
- unresolved conflicts;
- active or interrupted Git operation;
- local branch divergence not yet classified;
- stashes whose relevance to the integration is unclear.

The agent that encounters unexpected state must:

- classify the state using `agents/HERMES_AGENT_CONTRACT.md` §3.11a
  terminology;
- preserve all work — do not reset, clean, stash, commit unrelated
  changes, or discard work;
- explain how the state affects the proposed integration;
- propose a reconciliation or isolation method;
- obtain approval before continuing.

The agent must not automatically:

- `git reset` of any form;
- `git clean`;
- `git stash` (unless the stash contents are documented and the action
  is approved);
- commit unrelated work;
- `git checkout` or `git switch` merely to continue without a
  preservation plan;
- overwrite or amend existing commits.

#### Committed history versus working-tree state

Correct integration reasoning requires these distinctions:

| Term | Meaning |
|------|---------|
| **Committed branch history** | Commits reachable from a branch ref. The only material Git operations (merge, cherry-pick, rebase, fast-forward) transfer between branches. |
| **Staged changes** | Files in the index. Not part of any branch. |
| **Unstaged tracked changes** | Working-tree edits to files Git tracks. Not part of any branch. |
| **Untracked files** | Files Git does not track. Not part of any branch. |
| **Stashes** | Working-tree snapshots outside branch history. |
| **Worktree-local state** | Changes specific to one `git worktree` link. Invisible to other worktrees. |

A merge, cherry-pick, fast-forward, or rebase operates only on committed
branch history. These operations do **not** carry uncommitted working-tree
changes, staged content, untracked files, stashes, or worktree-local
state. Uncommitted changes in the worktree may cause Git to refuse the
operation (Git will not overwrite dirty tracked files), but they are
never introduced by the operation. An agent that claims otherwise is
making a terminology error.

#### Environment selection

For a clean repository that satisfies the starting condition, normal
integration may proceed in the existing worktree.

When the current worktree contains unrelated or unresolved state,
acceptable isolation options include:

- a separate Git worktree created with `git worktree add`;
- a separate clone of the repository;
- an approved preservation-and-cleanup procedure that documents the
  current state, preserves it, and restores it afterward.

A separate worktree is not required for every integration. The default
principle is:

> Use the simplest environment that is demonstrably clean, understood,
> and safe.

Cherry-pick selects specific commits from a branch, but it does **not**
by itself provide a clean execution environment. The workspace where
cherry-pick runs must still satisfy the starting condition. Merge,
fast-forward, cherry-pick, and rebase must each be evaluated for
workspace cleanliness independently of commit selection.

### Step 1 — Working branch completion

Before requesting integration, the implementation agent must:

- Commit all intended changes to the working branch.
- Run task validation and confirm passing results.
- Run `git diff --check` — no whitespace or formatting errors.
- Run `git status --short` — confirm no staged or unstaged changes remain.
- Record the branch name, HEAD SHA, and validation results in the integration packet.

### Step 2 — Integration packet

The implementation agent produces an integration packet containing:

| Field | Content |
|-------|---------|
| Branch | Working branch name |
| Commit SHA(s) | Exact commits proposed for integration |
| Summary | One-paragraph description of changes |
| Validations performed | Commands run, exit codes, pass/fail summary |
| Pre-integration Git state | Branch, HEAD, status, stash, divergence |
| Risks | Anything that could break during integration |
| Recommended strategy | Merge commit, cherry-pick, fast-forward, or rebase |
| Post-integration SHA | Expected resulting HEAD on the authoritative branch |
| Rollback | How to revert if integration fails (exact `git revert` command) |
| Required approvals | Who must approve before integration |

The packet is a markdown document. It may be embedded in a result report or
standalone. The agent writes the packet; GPT and Buddy review it.

### Step 3 — GPT review

GPT reviews the packet against:

- Architecture consistency — does the change align with repository direction?
- Governance compliance — are all required authorities followed?
- Documentation impact — are documentation changes consistent and complete?
- Repository consistency — does the change work with the rest of the repo?
- Integration suitability — does the change belong on the authoritative branch?

GPT produces one of:

| Outcome | Meaning |
|---------|---------|
| `APPROVE` | Ready for integration |
| `REQUEST_CHANGES` | Specific defects identified; list exactly what must change |
| `DO_NOT_INTEGRATE` | Structural issue, authority violation, or safety failure |

### Step 4 — Human approval

Buddy reviews the packet and GPT's recommendation, then decides:

- Whether to integrate.
- Whether additional work is required.
- Whether the proposed integration strategy is acceptable.
- Whether any post-integration validation is required beyond the standard checks.

Buddy approval is required for all integrations into the authoritative branch.
No agent may self-approve integration.

### Step 5 — Integration execution

Only after Buddy approval may the authorized agent execute the integration.

Integration strategies and when each is appropriate:

| Strategy | When appropriate | Governance implications |
|----------|-----------------|------------------------|
| **Merge commit** | Default for multi-commit branches, PR merges, or when preserving feature-branch history matters. Creates an explicit merge commit with both parents. | Preserves full history. The merge commit documents the integration event. Post-integration `git log --first-parent` shows only merge commits. |
| **Fast-forward** | When the working branch is a linear extension of the authoritative branch with no divergence. No merge commit is created. | Produces a linear history. Suitable for short-lived single-commit tasks where the authoritative branch has not advanced. |
| **Cherry-pick** | When only specific commits from a branch should be promoted, or when the working branch cannot be merged as a unit. Each commit is applied individually. | Creates new commits with different SHAs. The original branch remains intact. Use when the branch contains commits that should not all be promoted, or when the working branch has diverged and a merge is undesirable. |
| **Rebase** | Requires explicit Buddy approval. Only when linear history is required and the author understands the rewrite implications. | Rewrites commit history. Creates new SHAs. Breaks existing references to old SHAs. Prohibited without explicit task authorization per the Destructive commands section. |

The integration agent must:

- Confirm the execution environment satisfies the starting condition
  defined in this workflow.
- Distinguish **commit selection** (which commits will be promoted) from
  **workspace isolation** (where the promotion executes). Cherry-pick
  isolates selected commits; it does not by itself provide a clean
  execution environment.
- Verify the authoritative branch is checked out in the correct
  environment and is up to date.
- Apply the approved strategy.
- Confirm the resulting HEAD SHA matches the expected post-integration SHA.
- Record the integration environment (worktree path or clone path) and
  final state in a result report.

### Command-plan self-review

Before recommending approval, the agent must review every proposed command
against the reported Git state. The review must answer:

- Can this command fail because of current working-tree state?
- Can it alter unrelated work?
- Does it depend on the current branch?
- Does it modify the authoritative branch?
- Does it require a clean worktree?
- Is rollback valid for the exact proposed strategy?
- Is the written explanation technically accurate?

An integration packet must not recommend `APPROVE` if its own command
sequence conflicts with the reported repository state.

### Step 6 — Post-integration validation

After integration, validate:

| Check | Command |
|-------|---------|
| Authoritative branch HEAD | `git rev-parse <branch>` — matches expected SHA |
| Working tree | `git status --short` — clean |
| Tests | Repository test suite — passing |
| Whitespace | `git diff --check <pre-sha>..HEAD` — clean |
| Expected commits | `git log --oneline <pre-sha>..HEAD` — matches packet |

The working branch may be deleted only if separately authorized. By default,
it is preserved for reference.

### Integration packet example

```markdown
## Integration Packet — Task 30

- **Branch:** `docs/branch-integration-workflow`
- **Commits:** `a1b2c3d` — `docs: add branch integration workflow`
- **Summary:** Formalizes the six-step promotion lifecycle from working branch
  to authoritative branch, including integration packet, review, approval,
  execution, and post-integration validation.
- **Validations:** `git diff --check` (clean), `pytest tests/` (53 passed),
  `portfolio_registry --validate` (0 issues)
- **Pre-integration state:** `docs/branch-integration-workflow` at `a1b2c3d`,
  clean working tree, no stash, no divergence.
- **Risks:** Documentation-only change; no behavioral impact.
- **Strategy:** Merge commit (multiple commits in branch).
- **Expected post-integration SHA:** `f8e9d0c` (merge commit).
- **Rollback:** `git revert -m 1 <merge-sha>`.
- **Required approvals:** Buddy.
- **GPT outcome:** `APPROVE`.
- **Buddy decision:** [pending]
```

## Merge and integration authority

- Agents do not approve their own work.
- Agents do not merge public work unless the task explicitly authorizes a bounded integration after validation.
- The private repository is never merged into the public repository.
- Buddy remains the default authority for policy and public-history decisions.
- All integrations follow the [Branch Integration Workflow](#branch-integration-workflow).
- **Gate 3 merges** (merging a feature branch into `main` via pull request) follow the
  explicit procedure defined in the [Gate 3 — Merge Review Procedure](#gate-3--merge-review-procedure)
  section above. That section defines the review scope, validation, publication safety,
  decision outcomes, approval template, and post-merge verification for every merge.
- No integration may proceed without a completed integration packet, GPT review, and Buddy approval.
- Agent authority for integration operates within these boundaries:
  - OpenCode may inspect, validate, classify, and propose integration plans.
  - OpenCode may execute an approved integration plan in an environment that
    satisfies the starting condition defined in this workflow.
  - GPT reviews the proposal for technical and governance correctness.
  - Buddy approves promotion to the authoritative branch.
  - Unexpected repository state returns the process to a stop-and-report gate
    before any integration work proceeds.

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
