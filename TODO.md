# Session 12 — Establish the VPS Portfolio Engineering Workspace

## Intent

Establish the VPS as the trusted, always-available portfolio engineering
workspace now. Ivy Control VPS becomes VPS-resident first; Hermes becomes
available there as a bounded orchestrator; Palworld becomes the first
meaningful active managed repository; other repositories join as their actual
needs and evidence allow.

VPS residency is not a reward for portfolio perfection. It is the environment
that helps unfinished repositories become healthier.

The standard for a VPS-resident repository is not "finished." It is:

> clean, understandable, reproducible, and safe for another engineer or agent
> to continue.

Known incomplete work is allowed when it is documented. Private, unexplained,
or dirty local state is not copied into the workspace.

```text
Ivy Control VPS on VPS
  → governed portfolio engineering workspace
  → clean Palworld working baseline on VPS
  → Hermes coordinates approved bounded work
  → more repositories align as they become ready
```

## Current verified state

- VPS root disk is 76% used with 8.7 GB free; current capacity is `GREEN`, but
  clone footprint and resident-agent resource bounds must be checked.
- The largest observed home-directory consumers are apps (4.4 GB), `.hermes`
  (2.8 GB), and `.cache` (2.0 GB), not portfolio data (821 MB).
- Session 11 added VPS inventory/dashboard topology sourcing. One stale
  inventory statement and one missing Task 3 log link need repair.
- Ivy Control has two local commits ahead of `origin/main`; the refactored
  source revision must be approved and published before the VPS clone.
- Palworld is an active unfinished project. Its current working tree has
  experiment output, but that does not prevent a clean branch/clone from being
  an active managed repository.

## Non-negotiable boundaries

- A VPS repository checkout is a clean approved public Git clone. It may contain
  source, tests, public documentation, declared control records, deployment
  instructions, known incomplete work, and deliberately sanitized agent
  workflow artifacts.
- Never copy, mount, transfer, or synchronize `_internal/`, raw agent
  reasoning, private prompts, private logs/evidence, credentials,
  Mac-specific paths, temporary experiments, or unreviewed generated data.
- `TODO.md` is currently tracked and therefore appears in a normal clone. It
  must either be a concise publication-safe queue or be explicitly excluded
  from Hermes' VPS task-input model; it cannot become a private task channel by
  accident. Resolve this in Task 1 before relying on it from the VPS.
- VPS-private task packets, raw evidence, and runtime logs require a separately
  approved location outside each Git checkout. They are never a substitute for
  canonical repository documentation.
- Do not delete, `git clean`, reset, restore, move, or stage Palworld experiment
  artifacts without an exact-path disposition and Buddy approval.
- Hermes never merges, pushes to `main`, deploys, changes systemd, writes
  production data, accesses protected raw data, or changes its own permissions.
- Hermes cannot create GPT/Buddy acceptance, decisions, or canonical promotion.
  It may create only factual workflow artifacts marked `PENDING_GPT_REVIEW`.
- No cleanup is authorized by this TODO. Retention/accounting precedes any
  separately approved destructive operation.

## P0 — Task 1: Finalize governed VPS-workspace residency rules

Reconcile the existing public authorities before any clone is treated as a
resident engineering workspace. This is a focused alignment, not a new
governance system.

1. Distinguish a **VPS engineering checkout** from a production workload:
   repositories may be active and incomplete while their production data,
   services, schedulers, credentials, and runtime state remain absent.
2. State the two-tier artifact model: publication-safe repository artifacts in
   Git; private operational/task material only in a deliberately provisioned
   external location.
3. Resolve the tracked `TODO.md` policy for a clean clone and define the
   declared public artifact paths Hermes may read or write for a pilot.
4. Add a small residency preflight to existing VPS/Git/work-protocol authority:
   approved SHA, clean clone, `_internal/` absence, no-secret/public-path
   review, validation, capacity/footprint, and no direct checkout editing.
5. Reconcile any documentation that still calls every VPS checkout a production
   deployment target or implies Hermes is already installed/authorized beyond
   verified reality.

### Acceptance evidence

- An engineer can distinguish a professional active VPS working copy from a
  production activation.
- The allowed public and prohibited private artifact classes are unambiguous.
- The artifact path and write boundary for the first Hermes pilot are explicit.

## P0 — Task 2: Ivy Control VPS residency

Move the newly refactored Ivy Control VPS repository to the VPS as the
source/control-plane home.

### Required preconditions

1. Review and publish the approved refactored SHA currently ahead of
   `origin/main`; preserve and exclude protected local changes.
2. Create an exact deployment packet: remote, SHA, clean-tree evidence, VPS
   path/owner, clone footprint, reserve-capacity check, no-secret scan, and
   rollback/removal plan.
3. Verify `_internal/` is ignored and absent from the clone. Do not mount,
   transfer, or synchronize it.
4. State initial scope honestly: this is an engineering workspace, not a
   production service activation; no production data, private evidence
   ingestion, or Hermes credential authority is introduced.

### Acceptance evidence

- VPS clone is a clean approved SHA from the public remote.
- `git status`, origin, branch/SHA, and read-only control-plane commands work
  in the VPS checkout.
- Clone footprint and remaining capacity are recorded.
- `_internal/` and secret-bearing local material are absent.

## P0 — Task 3: Palworld active managed baseline and VPS residency

Do not make Palworld “portfolio perfect” first. Make it honest, cleanly
represented, and ready for managed work.

1. Identify the last good approved commit and current experiment boundary.
2. Inventory experiment output as tracked/untracked/ignored/modified.
3. Propose exact disposition: preserve, package for review, archive, branch,
   or delete. Stop for approval before destructive cleanup.
4. Establish a clean working branch or clean clone for the active roadmap.
5. Record current state, known gaps, next work, and the Hermes/OpenCode role.
6. After footprint review, place the clean source-only Palworld clone on VPS.

Unfinished is acceptable. Dirty, unexplained, or copied-private state is not.

### Acceptance evidence

An explicit branch/baseline record; reviewed experiment disposition; clean or
classified working state; source-only VPS clone with no runtime, database,
timer, or private-data role.

## P0 — Task 4: Minimum VPS Hermes orchestration and first roadmap pilot

Implement only the minimum needed for Hermes to coordinate from the VPS
workspace, then use it to do real bounded work on the clean Palworld baseline.
Update only the existing applicable authorities:

- `agents/HERMES_AGENT_CONTRACT.md`
- `agents/VPS_ORCHESTRATION.md`
- `docs/OPERATING_MODEL.md`
- `docs/REPOSITORY_WORK_PROTOCOL.md`
- `agents/orchestrator-task-packet-template.md` — reusable packet template,
  not a competing authority; include **Read first**, delegation target, allowed
  paths, checkpoint rule, and the post-completion instruction to write the
  next packet only when the delegation envelope permits it.

### Mode 0 — orchestrator coordination

Mode 0 is local/VPS repository coordination. It grants **no** SSH escalation,
service control, credential, production-data, Git-write, or deployment power.

Hermes receives an explicit **delegation envelope**:

- target repository and approved roadmap section(s);
- maximum tasks/chunks, one task in flight, and checkpoint cadence;
- target repository's declared public/private artifact paths;
- executor class, allowed implementation scope, and validation;
- stop conditions and GPT/Buddy escalation owner.

Hermes may write only task packets, factual review reports, concise
orchestration logs, and `PENDING_GPT_REVIEW` journal proposals in the target
repository's declared permitted artifact paths. It delegates code, scripts,
schemas, tests, fixtures, canonical data, configuration, migrations, services,
and all Git writes.

### Minimum write barrier

A real multi-task pilot requires an enforceable artifact-only write boundary.
If that is not enforceable, Hermes is limited to one human-dispatched delegated
task at a time and is not yet autonomous across roadmap chunks.

```text
read approved roadmap
  → create Task 1 packet
  → delegate to OpenCode
  → review result and validation
  → create next bounded packet only if inside the envelope
  → GPT/Buddy accepts journal semantics
```

The first chunk should be read-only or documentation-safe. It must not alter
canonical KB data, promote records, deploy services, or create Git writes.

### Acceptance evidence

A complete evidence cycle exists: task packet → delegated result → factual
Hermes review → GPT/Buddy-reviewed journal entry. Only then decide whether
Hermes can continue through multiple chunks and later propose scoped PRs.

## Parallel P0 hygiene — do not block residency unnecessarily

1. Correct the stale Reddit backup-unit statement in `docs/VPS_INVENTORY.md`.
2. Repair the missing Session 11 Task 3 log link or recreate its concise log
   from retained evidence.
3. Produce a bounded disk-accounting/retention proposal for `.hermes`,
   `.cache`, and `apps`; no cleanup until separately approved.
4. Keep operational uncertainty visible: Passport recovery confidence; Reddit
   canonicality/publication; Idle Hacking durability; Traderie natural-run and
   exporter evidence; SJC Intel readiness.

## P1 — After the first pilot passes

- Give Hermes per-repository branch/PR credentials with no `main` merge right.
- Let Hermes prepare, test, and propose PRs for explicitly approved repos.
- Add clean source-only clones for other active repositories as their footprint
  and privacy boundaries are reviewed.
- Evaluate persistent Hermes service installation only after the orchestration
  loop is proven.

## Deferred

- Automatic cleanup or retention enforcement.
- General production deployment authority.
- Database, systemd, timer, or credential mutation.
- Broad multi-repository parallel orchestration.
- Palworld runtime/database/data deployment.
