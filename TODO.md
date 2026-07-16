# Session 9 TODO — Portfolio Control Plane and VPS Readiness
Session 9 will organize `ivy-control-vps` as a VPS-ready control plane for the portfolio. The focus is to consolidate documentation, make repository status easy for agents to read, classify each repo for GitHub/VPS/database readiness, and prepare Hermes to assist safely with bounded repository work.
## P0 — Consolidate current authority
- Audit documentation and repo-specific packets for current, historical, duplicate, stale, or conflicting material.
- Keep `ROADMAP.md` as the broad execution home.
- Define the minimum live document set and archive completed one-time packets without losing references.
- Consolidate repo status around one authoritative `repos/<repo>/CONTROL.md`.
- Preserve detailed history, cutover evidence, and old execution packets outside the active reading path.
## P0 — Define the repository control contract
Each active repo control record should clearly state:
- purpose and code authority;
- GitHub and branch status;
- current lifecycle and health state;
- normal development host;
- VPS clone and runtime status;
- scheduler and production writer;
- database, recent data, archive, and backup locations;
- current blockers and next allowed work;
- Hermes permissions;
- Strong Codex stop conditions;
- decisions requiring Buddy;
- links to runbooks and evidence.
Add a small stable machine-readable metadata block so scripts and Hermes do not need to infer status from long prose.
## P0 — Create a portfolio registry
Create or formalize one registry containing:
| Repo | Status | GitHub | VPS clone | Runtime | Database | Health | Hermes scope | Next task |
|---|---|---|---|---|---|---|---|---|
Validate the registry against each repo’s `CONTROL.md` and flag missing or stale records.
## P0 — Prepare `ivy-control-vps` for VPS operation
- Define the authoritative VPS checkout path and update process.
- Keep mutable state, secrets, generated evidence, and private data outside the public checkout.
- Document exact-SHA deployment, validation, rollback, and drift checks.
- Make the ingestion dashboard runnable directly on the VPS.
- Ensure Hermes has access to the roadmap, registry, control records, dashboard JSON, and approved runbooks.
- Separate Mac development responsibilities from VPS operational responsibilities.
## P0 — Preserve ingestion trust work
Continue tracking:
- WGU Reddit canonicality, backup repair, archive continuity, and retirement of legacy fetchers.
- Idle Hacking Collector source ownership and browser hardening.
- Separate chat and market durability, acknowledgement, replay, and archive freshness.
- Traderie bounded recovery without broad redesign.
- Live dashboard adapters, alerts, duplicate-writer checks, and VPS capacity.
Do not let documentation consolidation hide or demote these active P0 items.
## P1 — Portfolio-wide readiness pass
For every managed repo, determine:
- canonical local and GitHub locations;
- clean/dirty and publication status;
- test and documentation readiness;
- repository and Git-history size;
- largest tracked, ignored, and untracked files;
- suitability for a source-only VPS clone;
- runtime and dependency footprint;
- PostgreSQL need;
- recent-versus-archive data placement;
- Hermes-safe task scope;
- next bounded task;
- blockers requiring Strong Codex or Buddy.
Classify each repo for:
- GitHub readiness;
- VPS clone suitability;
- database need;
- Mac/VPS data placement;
- Hermes usefulness.
## P1 — Publish-and-clone wave
Allow repos to advance independently through:
```text
clean
→ document and test
→ size review
→ GitHub-ready
→ approved push
→ VPS clone
→ Hermes-ready
→ optional database onboarding
→ optional production activation

Initial priority repos:

* SJC Intel;
* Palworld KB;
* Idle Hacking KB;
* IH Market Companion;
* Traderie bounded closure;
* WGU repos after trust and boundary review.

P1 — File-size and VPS-footprint controls

Before push or VPS cloning, inspect:

* checkout and Git-history size;
* largest files;
* live .db files and dumps;
* archives and raw datasets;
* browser profiles;
* generated assets;
* logs and temporary output;
* model artifacts;
* dependencies;
* expected mutable-data growth;
* backup staging and PostgreSQL growth.

Default policy:

* code, schemas, migrations, tests, and small fixtures may enter Git;
* recent operational data may live in VPS PostgreSQL;
* large historical and private datasets remain on the Mac or backup storage;
* live databases, dumps, profiles, raw archives, and large generated data do not enter Git.

P1 — Productize database onboarding

Turn prior Strong Codex work into a reusable process covering:

* source authority and data classification;
* recent-versus-archive decisions;
* schema and migrations;
* roles and grants;
* idempotent importers;
* reconciliation;
* health producers;
* backup, checksum, and manifest;
* isolated restore;
* rollback;
* bounded pilot;
* natural scheduled-run proof;
* cleanup eligibility.

Repo-local preparation may run in parallel. Live PostgreSQL admission remains sequential and handled through Strong Codex.

P1 — Begin using Hermes

Give Hermes a deterministic reading order:

1. ROADMAP.md
2. portfolio registry
3. relevant repo CONTROL.md
4. current dashboard JSON
5. applicable runbook
6. latest relevant evidence

Prepare a gated workflow for Hermes to:

* detect stale status and documentation;
* identify small useful tasks;
* inspect repository size and drift;
* validate setup and tests;
* create isolated branches;
* prepare pull requests for review.

Hermes must not self-merge, deploy, mutate databases, control production services broadly, access unrestricted secrets, or perform destructive work.

Start with one low-risk source-only repo.

P1 — Operator commands and drift checks

Work toward simple commands such as:

./tools/open_ingestion_dashboard.sh
./tools/show_portfolio_status.sh
./tools/show_ready_work.sh

Detect:

* roadmap workloads missing from the registry;
* registry repos missing CONTROL.md;
* stale control records;
* dashboard/control conflicts;
* deployed SHA drift;
* missing health producers;
* undocumented archive or backup ownership;
* repos marked Hermes-ready without a valid VPS checkout.

Execution model

Strong Codex

Use for:

* initial Session 9 architecture and consolidation decisions;
* conflicting authority or ownership;
* live database or VPS changes;
* restore failures;
* scheduler/writer transfer;
* browser-profile recovery;
* sensitive cross-repository decisions.

OpenCode

Use parallel agents for:

* documentation inventory;
* repo control-record audits;
* readiness and size classification;
* tests and fixtures;
* metadata and registry implementation;
* scripts and validations;
* repo-local publication preparation.

Git steward

Use for coherent commits, publication preparation, approved pushes, and exact-SHA records.

Buddy

Retains authority over publication, privacy, destructive cleanup, licenses, production acceptance, and expansion of Hermes permissions.

Session 9 completion criteria

Session 9 is complete when:

* the live documentation surface is small, indexed, and non-conflicting;
* every active repo has one authoritative control record;
* the portfolio registry is complete and validated;
* code, runtime, recent data, and archive locations are explicit;
* publish-and-clone and database-onboarding queues are populated;
* file-size and VPS-footprint controls exist;
* ivy-control-vps is ready for an exact-SHA VPS checkout;
* the dashboard and status evidence can run from the VPS;
* Hermes has a deterministic reading order and safe task contract;
* one low-risk Hermes pull-request pilot is ready for Buddy’s approval;
* ROADMAP.md remains the broad execution home.

