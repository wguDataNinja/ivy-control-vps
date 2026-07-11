# Session Close Workflow

Close a session without losing important decisions.

## Two-part closeout

Session close follows two sequential parts:

1. **Repository-side closeout** — An agent inspects Git state, checks agent logs, verifies gate packets, confirms `_internal/` remains excluded, identifies unresolved ad-hoc tasks, and creates or populates the GPT session-log file with metadata and links.

2. **Discussion-side capture** — GPT fills or appends decisions, rationale, deferred ideas, open questions, gate outcomes, roadmap impact, and the next handoff.

## Protected root TODO

The root `TODO.md` is the authoritative next-session plan.

During repository cleanup, it must not be discarded, restored to `HEAD`, replaced by an older short version, or treated as disposable local state. A dirty `TODO.md` may be intentional and required at session close.

Before invoking git-steward or attempting to make the repository clean:

- verify that root `TODO.md` contains the complete approved next-session plan;
- preserve that content exactly;
- exclude it from cleanup actions that would erase or shorten it;
- do not assume that a protected file should be reverted merely because it is not intended for the same commit as other documentation;
- if repository policy requires special handling, resolve that handling without losing the root TODO.

The session is not considered safely closed if the next-session TODO has been lost, truncated, or reverted.

## Private workflow

The detailed closeout procedure, including the exact steps for each part, is defined in the private workflow:

`_internal/GPT_ORCHESTRATED_WORKFLOW.md` §13

That document governs the private orchestration mechanics and is the authoritative procedure for session close.
