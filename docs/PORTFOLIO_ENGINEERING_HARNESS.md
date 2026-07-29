# Portfolio Engineering Harness

**Status:** Current standard for new admissions and active harness migrations.

## Purpose

The portfolio harness makes a repository reconstructable without chat history.
It is deliberately a small contract: source and product authority remain local;
Ivy governs admission, cross-repository authority, and supervised evidence.

## One model, three locations

| Location | Owns | Does not own |
|---|---|---|
| Repository root | Product purpose, architecture, roadmap, local rules, deterministic health commands | Portfolio policy or private raw evidence |
| Repository-declared task area | Bounded local task packet, result, and journal navigation | Product authority or a second roadmap |
| Ivy Control VPS | Admission CONTROL, portfolio priority, task orchestration, sealed cross-repository archive, Git-custody policy | Repository implementation or domain truth |

Each active repository has one authoritative product/architecture reading order,
one declared task/report location, and one journal location. Existing
repositories retain their declared paths until an explicit migration: `agent/`,
`_internal/`, and legacy `agent-reports/` are not interchangeable aliases.
Ivy `_internal/inbox` and `_internal/outbox` are the active **portfolio** queue;
`_internal/orchestration` is the durable **portfolio** task archive. They are
not copied into application repositories.

## Required local entrypoints

An active harness-profile repository contains:

1. `README.md` — purpose and practical entrypoint.
2. `AGENTS.md` — short startup route, boundaries, declared artifact paths, and
   stop conditions.
3. `HARNESS.json` — machine-readable orientation: authority files, active
   task, health commands, evidence/journal locations, and Git policy.
4. `ROADMAP.md` — current sequencing and dependency state.

`PRODUCT.md` and `ARCHITECTURE.md` are required when product or architecture
facts are not already owned by an equivalent existing document. Do not create
duplicates merely to satisfy a checklist.

## Fresh-agent route

1. Read `README.md`, `AGENTS.md`, and `HARNESS.json`.
2. Read the authority files named by `HARNESS.json` and the active task.
3. Inspect Git state; preserve dirt and stop if task scope is ambiguous.
4. Run the declared deterministic checks before claiming completion.
5. Write only to the task/report/log paths declared by the repository or the
   bounded Hermes packet. Seal portfolio evidence before cleanup.

Maker and checker are separate roles for supervised work. A maker cannot
accept its own result. Git Steward may make only explicitly allowed custody
writes after checker acceptance and sealed evidence; it has no standing write
authority.

## Admission and migration

New or materially restructured repositories use `templates/HARNESS.json` and
pass `tools/validate_repository_harness.py`. Add a central CONTROL record only
after the repository identity, local path, scope, and next authorized work are
known. Do not bulk-migrate mature repositories solely for uniform filenames;
declare their existing local convention in CONTROL/AGENTS and migrate only
when a concrete task can verify the change.

## Deliberate non-features

This standard does not create an autonomous scheduler, mandate a database,
replace product tests, authorize remote Git, or turn reports into authority.
It is a navigation and verification floor, not a framework.
