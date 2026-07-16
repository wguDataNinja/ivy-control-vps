# Ivy Control VPS Roadmap

**Status:** Active ingestion-first operating plan. Reconciled from current control sheets, database/health standards, the private Session 8 evidence review, and the generated local dashboard on 2026-07-15.

**Purpose:** This is the broad current home for agents: it states what is true, what is next, who can act, what is blocked, and which gate/evidence closes a task. Repository control sheets and release gates remain the authority for repository-specific decisions; `docs/DATABASE.md`, `docs/HEALTH_CONTRACT.md`, and `docs/PORTFOLIO_CONVENTIONS.md` remain the technical standards.

## §0 Operator Summary

### Current dashboard

```sh
./tools/open_ingestion_dashboard.sh
```

The dashboard is the current simple operator surface. It refreshes safe read-only evidence and writes a private local HTML/JSON view. Evidence precedence is: live measurement, validated producer payload, read-only database/service inspection, control document, roadmap, placeholder, then unknown. A control- or roadmap-only claim can never be green; missing evidence is **UNKNOWN**, not healthy. Idle Hacking chat and market are separate lanes.

### Current workload truth

| Workload | Current classification | Immediate issue | Evidence |
|---|---|---|---|
| WGU Reddit / Reddit Ops | `CANDIDATE_CANONICAL` | Scheduled backup is broken; recent completeness and archive continuity are unproven | Live dashboard + `repos/reddit-ops/CONTROL.md` |
| Idle Hacking chat | `CAPTURING_BUT_NOT_DURABLE` | Acknowledgement, replay, archive continuity, and truthful current-failure health are open | Live dashboard + Session 8 evidence |
| Idle Hacking market | `CAPTURING_BUT_NOT_DURABLE` | Same durability gap; PostgreSQL reconciliation is also pending | Live dashboard + Session 8 evidence |
| Traderie | `DEGRADED_BUT_BOUNDED` | Focused `pc_hc_nl` natural-run recovery only | `repos/traderie/CONTROL.md` |
| VPS capacity | `CURRENTLY_ACCEPTABLE` | Continue disk, inode, memory, backup-staging, and restore-headroom monitoring | Live dashboard |

### Immediate P0 priorities

1. Repair and re-prove WGU Reddit backup/restore; do not retire fallback paths.
2. Prove WGU recent completeness, archive-to-VPS continuity, and single-writer canonicality.
3. Make Idle Hacking chat and market health truthful, separate, acknowledged, and replayable.
4. Add the missing dashboard adapters before claiming portfolio ingestion is trustworthy.
5. Keep Traderie in its focused recovery lane; do not reopen its architecture.

### Execution-state vocabulary

- **READY — PARALLEL:** bounded preparation may run independently.
- **READY — SEQUENTIAL:** may begin only after stated dependency completes.
- **BLOCKED BY GATE:** needs evidence or an approval gate.
- **REQUIRES STRONG CODEX:** live, privileged, irreversible, or broad-context execution.
- **REQUIRES BUDDY:** risk, privacy, publication, destructive, or acceptance decision.
- **DEFERRED:** intentionally parked; do not infer authority to resume.

## §1 Authority and Execution Rules

### §1A Operating boundaries

- `docs/OPERATING_MODEL.md` defines roles and implementation-mode authority.
- `docs/REPOSITORY_CONTROL_MODEL.md` defines Gates 1–6 and the Canonical Ingestion-Admission subgate.
- `docs/HEALTH_CONTRACT.md` defines canonical health semantics; dashboard scaffolding does not supersede it.
- Managed repositories own source, schemas, tests, and repository-local behavior. ivy-control-vps owns portfolio status, gates, shared standards, and admission evidence.
- No mutable production data, dumps, browser profiles, raw archives, secrets, or large generated data belongs in Git.

### §1B High-reasoning stops

Stop and escalate to **Strong Codex** for technical ambiguity; escalate to **Buddy** for risk, privacy, publication, destructive action, and operational acceptance. Stop on:

- conflicting canonical-data claims, unexplained missing intervals, duplicate writers, or source/DB/archive disagreement;
- any live database mutation, schema/retention architecture change, scheduler/writer transfer, failed restore, or destructive cleanup;
- browser-profile manipulation, browser recovery/corruption, or source-to-installed userscript verification requiring sensitive profile access;
- cross-repository ownership conflict, privacy/publication ambiguity, or capacity projection threatening the VPS;
- disagreement between live evidence and a control/authority document.

### §1C Role boundary

| Owner | Current authority |
|---|---|
| OpenCode | Source audits, fixtures/tests, adapters, docs, size audits, readiness packets, and non-production preparation. |
| Strong Codex | Approved live PostgreSQL/restore/deployment work, scheduler or writer transfer, technical canonicality conflicts, browser recovery, and high-risk architecture. |
| git-steward | Authorized exact-file Git staging, commits, publication, and SHA recording only. |
| Hermes | Read-only inspection, comparison, reporting, and later gated PR preparation. |
| Buddy | Publication, source ownership, privacy, destructive action, operational acceptance, and activation decisions. |

## §2 Active P0 — Ingestion Trust

### §2A WGU Reddit canonicality and recovery — `§7B-G1`

**State:** `CANDIDATE_CANONICAL` / **BLOCKED BY GATE** for legacy retirement.

The active authority is `wgu-reddit-postgres-run.timer` and its PostgreSQL writer. The SQLite shadow timer is disabled and Mac launchd is documented disabled. The latest observed scheduled collection succeeded, but the installed backup unit references the wrong script and currently fails. `reddit_ops` is therefore candidate canonical for recent operations, not verified canonical for the complete dataset.

| Task | State | Owner | Depends on | Completion unlocks |
|---|---|---|---|---|
| Source-safe corrected backup unit, tests, publication packet | READY — PARALLEL | OpenCode | Secret/history review | Strong Codex repair packet |
| Monitor-role canonicality report: source/DB frontier, recent completeness, duplicates/gaps, lock/writer state | READY — PARALLEL | OpenCode | Sanitized monitor query design | Verified-canonical review |
| Archive inventory and VPS/archive continuity report | READY — PARALLEL | OpenCode | Approved archive metadata access | Historical continuity review |
| Corrected unit install, fresh dump/checksum/manifest, isolated restore | REQUIRES STRONG CODEX | Strong Codex | Buddy-approved packet; reviewed source | Backup/restore acceptance |
| Legacy fallback retirement decision | REQUIRES BUDDY | Buddy | All acceptance criteria below | Controlled inactive-fallback observation |

**Can run in parallel with:** Idle Hacking health adapters, database-product preparation, SJC readiness, Palworld source admission.

**Hard dependencies:** No legacy fetcher retirement before a current backup/restore, recent source completeness, archive-to-VPS continuity, one-writer proof, dashboard freshness, and documented fallback pass.

**High-reasoning stop:** Any unexplained source/DB/archive gap, duplicate anomaly, lock conflict, failed restore, or uncertainty about credential-bearing history.

**Completion unlocks:** `VERIFIED_CANONICAL` review and later, separately approved legacy retirement.

**Acceptance criteria for `VERIFIED_CANONICAL`:**

- active VPS scheduler, exact writer, advisory lock, and inactive legacy schedulers are evidenced;
- source frontier equals or is explained by database frontier over an agreed recent window;
- recent posts are complete; duplicate and gap checks pass;
- earliest/latest archive and VPS ranges overlap or have an explained handoff with no missing interval;
- current backup, checksum, manifest, `pg_restore --list`, and isolated restore pass;
- dashboard reports source freshness, DB freshness, backup age, restore-proof age, writer state, and canonicality classification;
- Buddy accepts the evidence and natural-run observation window.

### §2B Idle Hacking Collector — explicit browser dependency

**Component:** **Idle Hacking Collector** · namespace `ih-market-companion` · observed version `2026-05-03.3`.

It collects read-only Idle Hacking chat and public stackables market data through Chrome/Tampermonkey, then posts to `ih-collector-helper.service` on loopback. Browser/profile lifecycle remains Buddy-managed and sensitive. Browser or helper process health does **not** prove that chat or market data is being captured, offloaded, and archived.

Current source/deployment truth:

- an exact userscript copy is tracked in `idlehacking_kb`; an identical IH Market Companion copy is ignored;
- the installed Tampermonkey copy is not hash-verified because extension/profile storage is sensitive;
- the active helper matches the current tracked KB helper source, while the IH Market helper source differs;
- source authority, reproducible installation receipt, drift detection, and rollback receipt remain open.

**Can run in parallel with:** WGU preparation and shared dashboard work.

**Hard dependencies:** No browser restart automation, source consolidation, profile recovery, or retention cleanup before source ownership, safe installation evidence, and recovery authority are resolved.

**High-reasoning stop:** Browser/profile manipulation, a source/install hash mismatch, selector/auth/navigation failure, retention-loss risk, or cross-repo source ownership conflict.

**Completion unlocks:** bounded browser-hardening drills and trustworthy producer registration.

### §2C Idle Hacking chat durability — `§4I-G1`

**State:** `CAPTURING_BUT_NOT_DURABLE` / **READY — PARALLEL** for source/tests; live changes require Strong Codex packet.

| Required evidence | Current state |
|---|---|
| collector heartbeat and latest chat source activity | Live helper evidence exists |
| current durable local write | Live helper retention evidence reports success |
| current vs lifetime failure semantics | Open; cumulative historical failures must not permanently make current success red |
| acknowledgement destination/receipt | Open; current acknowledgement is pending |
| oldest backlog age/count and retention deadline | Partially available; adapter required |
| archive freshness and replay proof | Open |
| PostgreSQL metadata freshness | Partially applicable; metadata does not prove raw-body capture |

**Tasks:** create a separate sanitized `idlehacking_kb/chat_capture` producer; add fixtures for current-success-after-historical-failure, current failure, stale heartbeat, acknowledgement cap, and sanitization; define archive acknowledgement and replay contract; surface all fields in dashboard.

### §2D Idle Hacking market durability — `§4D-G1`

**State:** `CAPTURING_BUT_NOT_DURABLE` / **READY — PARALLEL** for source/tests; PostgreSQL/live admission is sequential.

| Required evidence | Current state |
|---|---|
| current market capture and local durable write | Live helper evidence exists |
| acknowledgement destination/receipt and backlog age | Open; acknowledgement pending |
| missing-interval detection and idempotent backfill | Required after prior loss window; not yet proven |
| PostgreSQL import/reconciliation/restore | Planned, not production authority |
| Mac archive freshness/replay | Archive role exists; current continuity proof open |

**Tasks:** create separate sanitized `ih_market_companion/market_capture` producer; acknowledgement/backlog/retention adapter; source-to-archive interval report; idempotent PostgreSQL import/reconciliation packet; restore proof before any authority transfer.

### §2E Traderie bounded recovery — `§7A-G1`

**State:** `DEGRADED_BUT_BOUNDED` / **READY — SEQUENTIAL**.

Retain only the focused path: investigate `pc_hc_nl` natural-run timeout with runtime/progress evidence; reconcile DB/file health output; apply tested source correction if warranted; prove bounded then genuine natural run; perform reboot proof only after natural success. The VPS remains the documented sole scheduler/writer. Do not redesign schemas, migrations, or ownership absent a current integrity finding.

### §2F P0 dashboard and alert adapters — `§3E-G1`

**State:** simple operator page implemented; live trust adapters **READY — PARALLEL**.

The current command is `./tools/open_ingestion_dashboard.sh`. It is deliberately a transitional local dashboard, not a public dashboard or a health-architecture replacement.

| Missing adapter | Owner | State |
|---|---|---|
| Reddit source frontier, DB frontier, recent completeness, duplicate/gap, archive continuity, backup age, restore-proof age, sole writer | OpenCode prepares / Strong Codex validates live query | READY — PARALLEL |
| Traderie live exporter | Traderie source owner | READY — PARALLEL |
| IH installed-userscript verification | Buddy + Strong Codex | REQUIRES BUDDY / REQUIRES STRONG CODEX |
| IH acknowledgement, oldest backlog age, retention deadline, archive freshness, replay state | IH Market + KB source owners | READY — PARALLEL |
| Host recurring capacity and backup-staging/restore headroom | OpenCode prepares / Hermes later observes | READY — PARALLEL |

Use GREEN only for current live/producer evidence across required path; YELLOW for delayed/incomplete/pending evidence; RED for current failure/stale critical state; UNKNOWN for absent or unverified evidence. Fastest alert thresholds apply to chat heartbeat/durable write. A polished dashboard, API, and alert delivery remain later products.

## §3 Shared Platform Products

### §3A Canonical Ingestion-Admission Gate — `§3A-G1`

Every ingestion workload must evidence collector, scheduler, writer, canonical data authority, reviewed SHA, deterministic entrypoint, lock/idempotency, bounded failure behavior, health/freshness/counts, backup/checksum/manifest/restore, rollback, Mac/archive role, inactive legacy scheduler, successful manual and natural run, and exactly one production writer. This remains Gate 4 evidence; it does not itself authorize activation.

### §3B PostgreSQL onboarding productization — `§3B-G1`

**State:** shared preparation **READY — PARALLEL**; live admission **REQUIRES STRONG CODEX**, one repository at a time.

Products to create or promote from Traderie, Reddit Ops, IH KB, and IH Market evidence:

1. onboarding guide and per-repository checklist;
2. source-authority and recent-versus-archive decision inventory;
3. schema/migration/rollback/validation template and role/grant matrix;
4. idempotent importer and reconciliation-report standard;
5. health producer/adapter template and fixture set;
6. backup, SHA-256, manifest, and `pg_restore --list` process;
7. isolated restore, rollback, bounded-pilot, and natural-run acceptance packets;
8. cleanup-eligibility criteria that never imply cleanup authority.

The portfolio may prepare one onboarding wave, but production cutovers remain independent. Not every repository needs PostgreSQL: file/export-only and source-only repositories document `not applicable` rather than inventing a database.

### §3C Deployment, exact SHA, and drift — `§3C-G1`

**State:** **READY — PARALLEL** for templates/source readiness; deployment **REQUIRES STRONG CODEX**.

Promote exact-SHA deployment, checkout cleanliness, service/unit source hash, deployed revision health field, drift check, rollback SHA, and helper installation/update verification. WGU Reddit is blocked by its credential-bearing publication history; no normal push or Git checkout claim is permitted until a clean strategy is approved.

### §3D Scheduler and natural-run products — `§3D-G1`

**State:** **READY — PARALLEL** for templates; activation **BLOCKED BY GATE**.

Promote systemd unit validation, one-scheduler/one-writer evidence, locking, timeout/progress evidence, natural-run acceptance, rollback, and reboot-recovery packet. Timer enablement remains Gate 6 plus Buddy approval.

### §3E Health, backup, capacity, and browser hardening — `§3E-G1`

**State:** **READY — PARALLEL**.

Health producers must provide sanitized v2 evidence and distinguish producer silence, exporter failure, collector failure, stale observations, and aggregate failure. Backup state is not archive acknowledgement. Capacity monitoring includes disk, inodes, memory, PostgreSQL/WAL growth, logs, backup staging, and restore headroom. Browser hardening is a named product: source/install integrity, profile ownership, safe manual recovery, heartbeat, current durable write, acknowledgement, replay, and bounded recovery drills.

## §4 Repository Advancement — Publish, Clone, and Data Placement

### §4A Independent advancement wave

Repositories may advance independently:

1. local cleanup/completion;
2. tests and durable documentation;
3. GitHub readiness and approved push;
4. VPS footprint review;
5. source-only VPS clone for approved SHA;
6. Hermes-readable setup and read-only inspection;
7. optional database onboarding;
8. optional production activation under Gates 4–6.

Publishing or cloning does not authorize service activation, data transfer, database creation, or production authority.

### §4B Footprint and placement review

Before a VPS clone or admission, inspect checkout size, largest tracked files, untracked/ignored data, Git object history, `.db` files, dumps, archives, generated data, browser profiles, model artifacts, dependency footprint, mutable runtime growth, log retention, backup staging, PostgreSQL growth, and archive destination.

Default placement:

- Git: code, schemas, migrations, tests, documentation, small sanitized fixtures.
- VPS: approved code clone, recent operational PostgreSQL data, bounded runtime state, logs outside checkout.
- Mac/backup storage: large historical/private corpus, raw archives, long retention, protected browser-profile backups.
- Never Git: live DBs/dumps, profiles, raw archives, large generated data, secrets, or mutable runtime state.

### §4C Priority code/runtime/data matrix

| Repository/workload | Code and normal development | GitHub / VPS clone | Runtime and recent data | Historical/private/archive | Hermes-safe work | Mac-only / blocker |
|---|---|---|---|---|---|---|
| WGU Reddit / Reddit Ops | Producer repo; Mac development | Publication blocked by history; VPS runtime is not clean Git clone | VPS PostgreSQL `reddit_ops` and current collector | SQLite fallback, exports, Mac archive role | Read-only status/drift once clone exists | Publication decision, canonicality, backup repair |
| Traderie | Mac repo | Published/deployed exact SHA | VPS PostgreSQL and systemd | Mac archive/backup | Read-only checks | Focused timeout recovery |
| IH Market Companion | Mac repo | Published; source-only clone possible after footprint review | Browser helper, bounded market snapshots; PG planned | Mac archive | Tests/docs/health adapter | Source ownership, acknowledgement, import/reconciliation |
| Idle Hacking KB | Mac repo | Publication privacy review open; clone after safe SHA | VPS metadata DB and bounded chat state | Full private corpus/Mac archive | Fixtures, metadata, tests, docs, later PR prep | Raw corpus, privacy, source authority |
| SJC Intel | Mac repo | Prepare for publication/clone | No production runtime | Mac development data | Tests/docs/packet | Gate 4 readiness |
| Palworld KB | Mac repo | Published; source-only clone suitable | No service/DB required | No VPS archive scope | Tests/docs/PR prep | Content work, later admission |

## §5 Executable Work Queue

### §5A Ready — parallel OpenCode queue

| Task | Depends on | Completion unlocks |
|---|---|---|
| Reddit corrected-backup source, tests, publication/repair packet | Source review | Strong Codex repair |
| Reddit monitor-role canonicality and archive-continuity query/report design | Safe schema knowledge | Canonicality review |
| IH chat/market separate health adapters, fixtures, acknowledgement/retention fields | Source ownership decision may be deferred but must be recorded | Dashboard trust fields |
| Database onboarding guide/checklist/templates | Existing evidence | Faster repo-local preparation |
| SJC Intel readiness packet and source audit | Repo-local access | Gate 4 review |
| Palworld KB source-only admission/footprint packet | Repo-local access | Optional VPS clone |
| IH KB and IH Market publication/footprint/source-boundary preparation | Privacy/ownership review | Independent clone/admission decisions |

### §5B Ready — sequential / Strong Codex queue

| Task | State | Requires | Completion unlocks |
|---|---|---|---|
| Reddit backup unit repair, fresh backup, isolated restore | REQUIRES STRONG CODEX | Buddy-approved exact packet and reviewed source | Current recovery evidence |
| Reddit verified-canonical review | REQUIRES STRONG CODEX | Monitor report + archive continuity + repaired restore | Buddy retirement decision |
| IH source-to-installed userscript verification | REQUIRES STRONG CODEX / REQUIRES BUDDY | Safe browser UI/export procedure | Deployment drift evidence |
| IH PostgreSQL import/reconciliation pilot | REQUIRES STRONG CODEX | Repo-local source/tests, manifest, capacity, backup/restore packet | Market authority-transfer review |
| Traderie deploy/natural-run/reboot proof | REQUIRES STRONG CODEX | Focused source correction and natural-run preconditions | Production-complete review |

### §5C Blocked and Buddy decisions

| Decision / gate | State | Needed before unlock |
|---|---|---|
| WGU Reddit clean publication/history strategy | REQUIRES BUDDY | Safe reviewed history and publication scope |
| WGU fallback retirement | REQUIRES BUDDY | Verified canonicality, backup/restore, observation window |
| Canonical Idle Hacking userscript source and duplicate disposition | REQUIRES BUDDY | Cross-repo ownership decision |
| Chat/market acknowledgement destination and archive authority | REQUIRES BUDDY | Durable offload/replay contract |
| Browser recovery/install verification | REQUIRES BUDDY | Sensitive-profile procedure and timing |
| Controlled reboot timing | REQUIRES BUDDY | Workload-specific success gates |

## §6 Repository Workstreams

### §6A SJC Intel — `§4C-G1`

**State:** `READY — PARALLEL`. Prepare source authority, scheduler/writer boundary, migrations/roles if needed, health adapter, backup/restore and rollback packet, exact-SHA/footprint review, and tests. No production cutover without Gate 4/5 packet.

### §6B IH Market Companion — `§4D-G1`

**State:** source/health preparation `READY — PARALLEL`; production import `REQUIRES STRONG CODEX`. Resolve collector source ownership, acknowledgement/replay, market adapter, idempotent import, interval reconciliation, Mac archive continuity, backup/restore, then use a bounded pilot. Public browser/runtime collection and private personal-trade data remain distinct.

### §6C WGU Catalog — `§4E-G1`

**State:** `READY — PARALLEL` for batch-source authority. It is a low-frequency file/export workflow unless evidence later justifies PostgreSQL; do not invent daemon or database requirements.

### §6D WGU-derived boundary — `§4F-G1`

**State:** `BLOCKED BY GATE`. Resolve Reddit/catalog/analysis/LLM ownership and safe publication representation before new derived workload activation. This does not block deterministic WGU Reddit stabilization or unrelated repositories.

### §6E Idle Hacking KB — `§4I-G1`

**State:** metadata continuity and health work `READY — PARALLEL`; publication/source privacy decision `REQUIRES BUDDY`. Keep raw bodies outside PostgreSQL; retain Mac corpus authority; correct top-level health semantics; add private-safe adapter; preserve 44-natural-export/metadata restore evidence as completed history rather than reopening it.

### §6F Palworld KB — `§4K-G1`

**State:** `READY — PARALLEL`. Published source-only admission under a small VPS checkout is suitable after footprint review. No service, timer, PostgreSQL, archive transfer, or runtime dependency is implied. Main work is content quality.

### §6G Restricted and downstream repositories

- Reckless Ben remains `NO_LAUNCH` / **DEFERRED** unless explicitly reclassified.
- BSDA Courses and WGU Atlas remain downstream consumers; advance their LLM/product work only after upstream data contracts and WGU boundary decisions are adequate.

## §7 Gates and Acceptance Criteria

### §7A Traderie Recovery Gate — `§7A-G1`

Pass when focused timeout diagnosis/source correction is evidenced, DB/file health behavior is reconciled, backup freshness is demonstrated, a genuine natural generation succeeds, and later reboot proof succeeds. See `repos/traderie/CONTROL.md` and release gates.

### §7B Reddit Recovery and Canonicality Gate — `§7B-G1`

Pass the recovery subgate when corrected backup unit, fresh checksum/manifest, isolated restore, and scheduled backup proof pass. Pass canonicality only when §2A acceptance criteria pass. Legacy retirement is a later Buddy decision, not a side effect.

### §7C Idle Hacking Durability Gate — `§7C-G1`

Pass chat and market independently only when source/install authority is known, capture and current durable write are fresh, acknowledgement/oldest backlog/retention deadline are visible, archive freshness and replay are proven, and applicable DB reconciliation/restore passes. Browser process liveness alone fails this gate.

### §7D Platform Confidence Gate — `§7D-G1`

Before a new production wave: dashboard exposes current evidence, capacity is within threshold, backup/restore products work, one-writer rules are demonstrable, and the bounded privileged execution path is sufficient for the packet. It does not require polished public UI or full portfolio maturity.

## §8 Hermes Evolution

**Current:** read-only inspection, health comparison, status reports, drift/defect identification, and bounded evidence requests. Hermes is not a production controller.

**Next gated stage:** after clean clone, scoped credential/audit design, test/secret-scan checks, and repository-specific Buddy approval, Hermes may inspect VPS clones, identify bounded work, create isolated branches, run tests, and prepare pull requests for review.

**Still prohibited:** self-merge, autonomous production deployment, database mutation, broad secrets access, destructive operations, unrestricted service control, and treating its conclusions as unverified authority.

## §9 Completed Milestones and Evidence References

Completed work remains evidence, not active execution flow:

- Traderie PostgreSQL schema/roles/migrations, backup/isolated restore, segmented runtime, and sole VPS authority are documented in its control/release evidence; natural-run recovery remains open.
- Reddit Ops migration, roles, locking, frontier/idempotence, approved-partial semantics, and earlier restore proof are documented in `repos/reddit-ops/` and `docs/DATABASE.md`; current backup/continuity closure remains open.
- Idle Hacking KB metadata onboarding, idempotent reconciliation, isolated restore, archive verification, and bounded cleanup/natural-export evidence remain recorded in private Session 7 material; health semantics and archive acknowledgement remain open.
- IH Market bounded retention/helper deployment and publication evidence remain references; durable archive and PostgreSQL reconciliation remain open.
- The simple dashboard command is implemented; it is a transitional view with named missing adapters, not a claim of complete health architecture.

## §10 Decisions Requiring Buddy

1. Approve WGU Reddit clean publication/history strategy and later backup-repair execution packet.
2. Accept or hold WGU Reddit canonicality and the legacy-retirement observation window after evidence passes.
3. Select the one tracked canonical Idle Hacking userscript source and disposition of duplicate copies.
4. Select chat and market archive-acknowledgement destination/receipt authority and archive role.
5. Approve any browser-profile inspection/recovery/install-verification procedure.
6. Approve controlled reboot timing only after workload-specific prerequisites pass.
7. Approve Hermes PR credentials and scope per repository after the staged gate is designed.

## Reference continuity

The active stable references retained here are `§3A-G1` (Canonical Ingestion-Admission), `§3B-G1` (PostgreSQL Productization), `§3C-G1` (Exact-SHA Deployment), `§3D-G1` (Scheduler), `§3E-G1` (Health), `§4C-G1` through `§4K-G1` (repository workstreams), and `§7A-G1`/`§7B-G1` (Traderie/Reddit). New `§7C-G1` and `§7D-G1` make Idle Hacking durability and platform confidence explicit without replacing the six-gate control model.
