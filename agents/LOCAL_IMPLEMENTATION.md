# Local Implementation Agent Contract

## 1. Applicability

This contract applies when the current repository path is:

`/Users/buddy/projects/ivy-control-vps`

It applies to local implementation agents such as OpenCode, Codex, and similar coding or documentation agents acting under Buddy's direction.

If the path or assigned role does not match, stop before write actions and report the ambiguity.

## 2. Required reading order

1. `AGENTS.md`
2. `agents/LOCAL_IMPLEMENTATION.md` — this file
3. `docs/README.md` — documentation index
4. Task-relevant standards: `docs/GIT_WORKFLOW.md`, `docs/LOGGING_STANDARD.md`
5. `_internal/README_INTERNAL.md` (or legacy `internal/README_INTERNAL.md`) when available locally
6. Task-specific private logs under `_internal/logs/` (or legacy `internal/logs/`) only when relevant

Do not load every file for every task. Read enough context to understand authority, scope, validation, and logging obligations.

## 3. Task boundaries

- Identify the assigned scope before editing.
- Avoid unrelated cleanup.
- Avoid creating policy where the repository marks a decision as pending.
- Preserve existing authority documents unless the task explicitly changes them.
- Report missing prerequisites or conflicting instructions.
- Stop rather than guess when a change could affect production, credentials, destructive operations, or unresolved governance.

## 4. Planning before changes

For substantive work, produce a brief plan before editing that includes:

- files expected to change;
- validation to run;
- whether Git write authority is granted;
- whether a private agent log is required;
- any unresolved ambiguity.

A separate planning artifact is not required for trivial edits unless the task asks for one.

## 4A. Change lifecycle

For a tracked change, follow `docs/REPOSITORY_WORK_PROTOCOL.md` as the canonical task-to-promotion path. In practical terms: identify authority and scope, protect unrelated work, use an authorized branch, implement and validate, write the required result/report evidence, then hand exact public paths to `git-steward` when Git packaging is authorized.

Do not promote a result report, execution log, private session note, or chat conclusion into a standard, roadmap, or CONTROL record without explicit task scope and review.

## 5. Editing rules

- Make the smallest coherent change that satisfies the task.
- Use existing repository structure and conventions.
- Avoid unnecessary file creation.
- Keep public tracked content publication-safe.
- Keep private notes under excluded `_internal/` paths (legacy `internal/` is also gitignored).
- Never force-add ignored private files.
- Never store secrets in tracked or private documentation.
- Leave concise stubs where decisions are unresolved rather than inventing details.

## 6. Validation

Run validation appropriate to the task, including as applicable:

- syntax or formatting checks;
- tests;
- Markdown link checks;
- `git diff --check`;
- staged diff review without opening a pager (`GIT_PAGER=cat git diff --staged`);
- confirmation that private files remain ignored;
- confirmation that no unrelated tracked changes are included.

Distinguish between validation completed, validation unavailable, and validation not applicable.

## 7. Logging

Follow `docs/LOGGING_STANDARD.md`.

Create a concise private agent log for meaningful work that changes repository state or creates durable artifacts. Use the existing structure:

```markdown
# <agent or task>

- Did:
- Result:
- Checked:
- Next:
```

Read-only exploration and simple factual answers are normally exempt.

When requested, include concise process feedback covering friction, unclear instructions, missing prerequisites, or possible improvements.

## 8. Git behavior

Follow `docs/GIT_WORKFLOW.md`.

- Work on a task branch by default.
- Commit and push only when explicitly authorized.
- Never merge your own work.
- Never force-push.
- Never discard unexplained local changes.
- Review staged changes before commit.
- Report branch, commit SHA, push result, and working-tree status when Git actions occur.

A bounded direct commit to `main` is allowed only when Buddy explicitly grants that authority for the specific task and the Git standard permits it.

## 9. Tool and environment behavior

- Use the actual current repository path as a routing signal.
- Prefer non-interactive commands for agent workflows.
- Use `GIT_PAGER=cat` for Git output that might invoke a pager.
- Provide one pasteable command block when Buddy asks for terminal commands.
- Do not assume an agent can open a pull request automatically.
- When a capability is unavailable, report the exact next command or comparison URL instead of pretending the action occurred.

## 10. Completion criteria

Before declaring meaningful work complete:

- assigned scope satisfied;
- validation reported;
- private agent log created or updated when required;
- unresolved issues clearly listed;
- tracked and private boundaries preserved;
- Git state reported if files changed;
- concise process feedback included when requested.

## 11. Prohibited behavior

Local implementation agents must not:

- treat this local contract as VPS or Hermes authority;
- perform production or VPS changes without explicit assignment and approved authority;
- modify credentials or secrets;
- self-merge;
- force-push;
- discard unknown work;
- invent missing standards;
- commit `_internal/` or `internal/` content;
- claim validation, commit, push, PR creation, or deployment that did not occur.
- run `rm -rf`, `git clean`, or `git reset --hard` without explicit authorization from a separately approved recovery procedure;
- interpret ambiguous phrases as authorization to delete files.

## 12. Destructive-action safety

The following are prohibited unless a separately approved recovery procedure explicitly authorizes the exact command:

- `rm -rf` or any broad deletion command;
- `git clean`;
- `git reset --hard`;
- force-push;
- history rewriting;
- deleting or overwriting untracked files without knowing what they contain.

Before any deletion or cleanup:

1. Clarify ambiguous instructions.
2. Inspect `git status` and confirm tracked, untracked, and ignored boundaries.
3. Confirm task authority explicitly covers the exact action.
4. List exact files before acting.

Ignored and untracked files may be irreplaceable and must be treated as user data.

`TODO.md` must never be restored, edited, staged, or committed by implementation agents. When asked only to read `TODO.md`, no Git or file mutation is authorized.
