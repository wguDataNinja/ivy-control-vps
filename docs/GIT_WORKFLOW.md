# Git Workflow

**Status:** Initial / provisional. This standard will be evaluated through actual use and revised when friction or gaps are discovered. Repository protection settings, VPS deployment details, and Hermes permissions remain explicitly unresolved.

## Principles

- GitHub is the source of truth for tracked public material.
- The MacBook and VPS should use approved commits.
- Agents must not self-merge.
- Direct production edits are not the intended workflow.
- Private `internal/` content must never be committed or force-added.
- Local implementation and VPS orchestration are distinct contexts.
- Ambiguity should be reported rather than resolved by inventing policy.

## Buddy working locally

The normal path for substantive work:

1. Start from an updated `main`.
2. Create a short-lived branch for substantive work.
3. Make and review changes.
4. Validate affected files.
5. Commit with a clear message.
6. Push the branch.
7. Merge through GitHub review when practical.
8. Update local `main` after merge.

A narrowly defined low-friction exception exists for trivial documentation fixes authored by Buddy directly on `main`. This exception is for Buddy only and should not become the agent default.

## Local implementation agents

OpenCode, Codex, and similar agents should:

- Inspect `AGENTS.md` and applicable standards first.
- Work on a task branch unless Buddy explicitly authorizes a bounded direct commit.
- Keep changes within assigned scope.
- Validate before completion.
- Create the required private agent log.
- Commit and push only when the task explicitly grants authority.
- Open or prepare a pull request when required.
- Never merge their own pull request.
- Never add ignored `internal/` files.

If the agent environment cannot open a pull request automatically, report the exact branch and comparison URL or the next command to run.

## VPS and Hermes (provisional)

This section is provisional. Future VPS and Hermes work should:

- Operate from an approved clean commit.
- Avoid ad hoc production edits.
- Use bounded branches or delegated implementation agents for tracked changes.
- Require Buddy approval for merges and policy-changing work.
- Record deployed commit SHAs.
- Verify working-tree cleanliness before updates.
- Stop on unexpected local changes.
- Define rollback around known approved SHAs.

The actual VPS path, deployment mechanism, credentials model, and Hermes permission boundary are not yet defined.

## Branch naming

Use a simple provisional convention:

```
<type>/<short-description>
```

Suggested types:

- `docs/` — documentation changes
- `feat/` — new features
- `fix/` — bug fixes
- `ops/` — operational changes
- `chore/` — maintenance, tooling, cleanup

Keep names lowercase, short, and hyphenated.

## Commit messages

Use concise imperative messages that describe one coherent change.

Examples:

- `Add initial Git workflow standard`
- `Clarify agent logging requirements`
- `Fix documentation links`

A complex commit-message framework is not required.

## Pull requests and merge authority

- Agents do not approve or merge their own work.
- Buddy is the default merge authority until another policy is approved.
- Pull requests should summarize scope, validation, unresolved issues, and operational impact.
- Squash merge may be used for small coherent branches.
- Merge commits or rebases may be used later if a repository has a justified need.

Exact repository protection settings remain pending.

## Dirty trees and rollback

- Do not pull, deploy, or switch branches over unexplained local changes.
- Inspect and classify changes first.
- Do not discard work automatically.
- Use known commit SHAs for deployment and rollback references.
- Record exceptions and unresolved state in the appropriate log.

## Secrets and ignored material

- Never commit secrets.
- Never force-add `internal/`.
- Inspect staged changes before committing.
- Use `.env.example` only for safe placeholders.
- Private local or VPS context must be provisioned separately from Git.

## Practical commands

```bash
# Create a branch
git checkout -b docs/git-workflow-standard

# Review status (no pager)
GIT_PAGER=cat git status
GIT_PAGER=cat git diff --staged

# Commit and push
git add <files>
git commit -m "Add initial Git workflow standard"
git push -u origin <branch-name>

# Update local main after merge
git checkout main
git pull

# Check for a clean working tree
GIT_PAGER=cat git status

# Display current commit SHA
git rev-parse HEAD
```

Destructive reset, force-push, and automatic cleanup commands are not part of the standard workflow.
