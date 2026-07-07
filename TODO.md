# OpenCode Task: Repository Coherence Review and Git Completion

Work in:

`/Users/buddy/projects/ivy-control-vps`

Start at `AGENTS.md` and follow the local implementation contract.

You are currently expected to be on:

`docs/local-implementation-contract`

This task has two goals:

1. review the entire repository for coherence, consistency, completeness, and contradictions;
2. handle the remaining Git work for the current branch, including committing, pushing, and opening a pull request when possible.

Do not merge the pull request.

## Required reading

Read all tracked files in the repository, including:

- `README.md`
- `AGENTS.md`
- `TODO.md`
- all files under `agents/`
- all files under `docs/`
- all files under `workflows/`
- `.gitignore`

Also read relevant private files under `internal/`, including:

- `internal/README_INTERNAL.md`
- the current GPT bootstrap/session log
- current agent logs relevant to repository setup, logging, Git workflow, `AGENTS.md`, and the local implementation contract

Do not expose private content in tracked files or in the public final report.

## Review scope

Review the repository as a complete operating system for local implementation work.

Check for:

- contradictory rules;
- duplicated rules that should be routed instead;
- broken or misleading links;
- stale statements;
- missing references between router, contracts, standards, and documentation index;
- inconsistent terminology;
- inconsistent path references;
- unclear authority boundaries;
- places where provisional work is presented as final;
- places where completed work is still listed as pending;
- Git instructions that conflict with the actual branch workflow;
- logging requirements that are not discoverable;
- public/private boundary mistakes;
- unnecessary documentation sprawl;
- instructions that are too vague for an agent to follow;
- instructions that are too detailed for the file where they live;
- any issue that would cause OpenCode, Codex, or a future maintainer to behave incorrectly.

## Review method

First produce a concise internal findings list before editing.

Classify findings as:

- **Must fix now** — contradiction, broken link, unsafe instruction, stale authority, or workflow failure.
- **Should fix now** — clarity or consistency issue within current scope.
- **Defer** — unresolved VPS/Hermes, deployment, credentials, repo admission, LLM strategy, automation, or other future policy.

Do not change deferred policy.

## Allowed tracked changes

Modify only files that need correction based on the review.

Expected candidates include:

- `README.md`
- `AGENTS.md`
- `agents/LOCAL_IMPLEMENTATION.md`
- `docs/README.md`
- `docs/OPERATING_MODEL.md`
- `docs/LOGGING_STANDARD.md`
- `docs/GIT_WORKFLOW.md`
- `workflows/session-close.md`
- `TODO.md`

Do not create new tracked files unless a clear gap cannot be solved by improving an existing file.

Prefer routing and concise references over duplicating full policy.

## Required outcomes

At minimum, confirm that:

- `AGENTS.md` is a short router;
- `agents/LOCAL_IMPLEMENTATION.md` is the detailed local contract;
- `docs/GIT_WORKFLOW.md` is the Git authority;
- `docs/LOGGING_STANDARD.md` is the logging authority;
- `docs/README.md` accurately indexes current tracked documentation;
- `docs/OPERATING_MODEL.md` distinguishes implemented, provisional, and pending areas;
- private `internal/` material remains ignored and separate;
- the VPS/Hermes path and authority remain explicitly unresolved;
- no agent is authorized to self-merge;
- no tracked file claims a capability or process that does not exist.

## Findings report

In the final response, report all material findings concisely under:

- Must fix now
- Should fix now
- Deferred

Do not dump every sentence reviewed. Report only findings that affect behavior, authority, clarity, safety, or maintainability.

If no issue is found in a category, say `None`.

## Private logging

Create or update:

`internal/logs/agents/2026-07-07/repository-coherence-review.md`

Use:

```markdown
# Repository coherence review

- Did:
- Result:
- Checked:
- Next:
```

Update the current private GPT session log only if this review resolves or materially changes an existing item.

## TODO handling

After the review is complete, replace `TODO.md` with the next actionable queue.

The next queue should begin with:

1. provisional VPS/Hermes orchestration contract;
2. actual VPS path and private-context model when known;
3. logging retention and periodic review automation;
4. repository-admission process;
5. portfolio-level LLM strategy;
6. daily documentation loop;
7. repo-specific templates.

Do not mark unresolved items as complete.

## Validation

Before Git actions:

- verify every Markdown link;
- run `git diff --check`;
- confirm `internal/` remains ignored;
- confirm no private content or secrets appear in tracked files;
- confirm no unrelated tracked changes are included;
- review all changed files;
- review staged changes with `GIT_PAGER=cat`;
- create or update the private agent log;
- report process friction, unclear instructions, missing prerequisites, and possible improvements.

## Git handling

Handle the Git work without asking Buddy to run terminal commands unless authentication or a missing capability blocks progress.

Use the current task branch:

`docs/local-implementation-contract`

If the branch is not current, stop and report the actual branch rather than switching over unexplained work.

After validation:

1. stage only intended tracked files;
2. commit any additional coherence fixes;
3. push the branch;
4. open a pull request against `main` using `gh` if available and authenticated;
5. if a pull request already exists, update it rather than creating a duplicate;
6. do not merge the pull request;
7. do not approve your own pull request;
8. do not force-push;
9. do not add or force-add anything under `internal/`.

Use this commit message when fixes are made:

`Review repository coherence`

If no tracked fixes are needed, do not create an empty commit. Push only if the branch is not already current on the remote.

The pull request should summarize:

- local implementation contract;
- coherence review performed;
- tracked files changed;
- validation completed;
- unresolved VPS/Hermes boundaries;
- confirmation that private files remain ignored.

## Final report

Return:

- branch name;
- commits on the branch not yet in `main`;
- pull-request URL and status;
- files reviewed;
- files changed;
- Must fix now findings;
- Should fix now findings;
- Deferred findings;
- validation results;
- private log path;
- final working-tree status;
- concise process feedback;
- the single remaining action Buddy must take, if any.
```
