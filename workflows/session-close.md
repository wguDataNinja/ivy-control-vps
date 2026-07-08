# Session Close Workflow

Close a session without losing important decisions.

## Two-part closeout

Session close follows two sequential parts:

1. **Repository-side closeout** — An agent inspects Git state, checks agent logs, verifies gate packets, confirms `_internal/` remains excluded, identifies unresolved ad-hoc tasks, and creates or populates the GPT session-log file with metadata and links.

2. **Discussion-side capture** — GPT fills or appends decisions, rationale, deferred ideas, open questions, gate outcomes, roadmap impact, and the next handoff.

## Private workflow

The detailed closeout procedure, including the exact steps for each part, is defined in the private workflow:

`_internal/GPT_ORCHESTRATED_WORKFLOW.md` §13

That document governs the private orchestration mechanics and is the authoritative procedure for session close.
