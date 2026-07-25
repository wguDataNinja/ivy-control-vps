---
vps_inventory_version: "1.0"
last_updated: "2026-07-20"
source: "docs/VPS_INVENTORY.md"
authority: "VPS deployment topology — not governance, not health signals"

vps_host:
  hostname: ubuntu-4gb-nbg1-1
  provider: Hetzner Cloud
  plan: CX23
  os: Ubuntu 24.04 LTS
  ssh_alias: ih-market-vps
  runtime_user: scraper

workloads:
  - id: reddit-ops
    display_name: WGU Reddit
    purpose: "Daily WGU subreddit collection and PostgreSQL ingestion"

    lifecycle: production-runtime
    admission_gate: 5

    runtime_path: "/home/scraper/apps/wgu-reddit"
    deployment_method: scp
    approved_sha: "7047400"

    systemd:
      active_timer: wgu-reddit-postgres-run.timer
      active_service: wgu-reddit-postgres-run.service
      backup_timer: wgu-reddit-backup.timer
      backup_service: wgu-reddit-backup.service
    legacy_units:
      - timer: wgu-reddit-shadow-run.timer
        service: wgu-reddit-shadow-run.service
        type: systemd
        state: disabled
      - timer: com.buddy.wgu-reddit.dailyupdate
        type: launchd
        state: disabled

    data_paths:
      - "/home/scraper/data/wgu-reddit"
      - "/home/scraper/backups/postgres/reddit_ops"
    config_paths:
      - "/home/scraper/config/wgu-reddit.env"
      - "/home/scraper/config/wgu-reddit-pg.env"

    database:
      name: reddit_ops
      schemas: [reddit_core, wgu_reddit, bsda_courses]
      migrations: "0001-0006"
      health_table: null

    expected_cadence: daily at 07:00 UTC
    expected_cadence_seconds: 86400
    freshness_threshold_hours: 30

    declared_health_state: degraded
    health_producer: null
    health_script: null
    health_conformance: adapter-compatible

    owning_repo: reddit-ops
    control_record: repos/reddit-ops/CONTROL.md
    runbook: repos/reddit-ops/RUNBOOK.md
    release_gates: repos/reddit-ops/RELEASE_GATES.md

    verification_date: "2026-07-19"
    verification_sources:
      - repos/reddit-ops/CONTROL.md
      - repos/reddit-ops/RUNBOOK.md
      - repos/reddit-ops/STABILIZATION.md
      - repos/reddit-ops/RELEASE_GATES.md
      - repos/reddit-ops/CUTOVER_HISTORY.md
      - tools/ingestion_dashboard.py
    verification_basis: "YAML fields from CONTROL.md front matter; systemd names cross-referenced against dashboard probes, RUNBOOK.md, and dashboard output; backup drift noted from CONTROL.md inline prose"

  - id: traderie
    display_name: Traderie
    purpose: "Diablo II market-data pipeline for completed-trade analysis"

    lifecycle: production-runtime
    admission_gate: 5

    runtime_path: "/home/scraper/apps/traderie"
    deployment_method: git-clone
    approved_sha: "e5ebd0f"

    systemd:
      active_timer: traderie-ingest-snapshot.timer
      active_service: null
      backup_timer: null
      backup_service: null
    legacy_units:
      - timer: com.buddy.traderie.dailysnapshot
        type: launchd
        state: disabled

    data_paths:
      - "/home/scraper/data/traderie"
      - "/home/scraper/backups/postgres/traderie"
    config_paths:
      - "/home/scraper/config/traderie-pg.env"

    database:
      name: traderie
      schemas: [app, archive, health]
      migrations: "001-017"
      health_table: health.health_runs

    expected_cadence: daily
    expected_cadence_seconds: 86400
    freshness_threshold_hours: 30

    declared_health_state: degraded
    health_producer: traderie/snapshot, traderie/health_export
    health_script: scripts/traderie_health_export.py
    health_conformance: canonical

    owning_repo: traderie
    control_record: repos/traderie/CONTROL.md
    runbook: null
    release_gates: repos/traderie/RELEASE_GATES.md

    verification_date: "2026-07-19"
    verification_sources:
      - repos/traderie/CONTROL.md
      - repos/traderie/RELEASE_GATES.md
      - repos/traderie/STATUS.md
      - repos/traderie/PHASE_B_CODEX_PACKET.md
      - tools/ingestion_dashboard.py
      - docs/health/producer-registry.md
    verification_basis: "YAML fields from CONTROL.md front matter; timer name confirmed in dashboard and tests; producer registration from docs/health/producer-registry.md; health conformance from docs/health/portfolio-conformance-matrix.md; root systemd timer (not user) documented per Session 9 live discovery"

  - id: ih-market-companion
    display_name: IH Market Companion
    purpose: "Public market snapshot collection via Chrome + Tampermonkey"

    lifecycle: browser-dependent
    admission_gate: null

    runtime_path: "/home/scraper/vps_helper/collector_helper.py"
    deployment_method: scp
    approved_sha: "ae50fd4"

    systemd:
      active_timer: null
      active_service: ih-collector-helper.service
      backup_timer: null
      backup_service: null
    legacy_units: []
    shared_service_with: idlehacking-kb

    data_paths:
      - "/home/scraper/data/market"
    config_paths:
      - "/home/scraper/config/ih-market.env"

    database: null

    expected_cadence: continuous (Chrome-driven)
    expected_cadence_seconds: 3600
    freshness_threshold_hours: 6

    declared_health_state: unknown
    health_producer: null
    health_script: null
    health_conformance: adapter-required

    owning_repo: ih-market-companion
    control_record: repos/ih-market-companion/CONTROL.md
    runbook: null
    release_gates: null

    verification_date: "2026-07-19"
    verification_sources:
      - repos/ih-market-companion/CONTROL.md
      - tools/ingestion_dashboard.py
      - docs/health/portfolio-conformance-matrix.md
    verification_basis: "YAML fields from CONTROL.md front matter; service name confirmed in dashboard probes; health conformance from portfolio-conformance-matrix.md; shared helper relationship inferred from matching service names across two CONTROL.md files"

  - id: idlehacking-kb
    display_name: Idle Hacking KB
    purpose: "Private chat archiving and knowledge base"

    lifecycle: browser-dependent
    admission_gate: null

    runtime_path: "/home/scraper/apps/idlehacking-kb-metadata"
    deployment_method: git-clone
    approved_sha: "61379d3"

    systemd:
      active_timer: null
      active_service: ih-collector-helper.service
      backup_timer: null
      backup_service: null
    legacy_units: []
    shared_service_with: ih-market-companion

    data_paths:
      - "/home/scraper/data/private/chat"
    config_paths:
      - "/home/scraper/config/idlehacking-pg.env"

    database:
      name: idlehacking_kb
      schemas: [chat, archive, provenance, claims, qa, llm, health]
      migrations: "001-010"

    expected_cadence: continuous (Chrome-driven)
    expected_cadence_seconds: 3600
    freshness_threshold_hours: 6

    declared_health_state: degraded
    health_producer: null
    health_script: null
    health_conformance: divergent

    owning_repo: idlehacking-kb
    control_record: repos/idlehacking-kb/CONTROL.md
    runbook: null
    release_gates: null

    verification_date: "2026-07-19"
    verification_sources:
      - repos/idlehacking-kb/CONTROL.md
      - tools/ingestion_dashboard.py
      - docs/health/portfolio-conformance-matrix.md
    verification_basis: "YAML fields from CONTROL.md front matter; service name matches ih-market-companion (shared); database schemas from CONTROL.md; health conformance from portfolio-conformance-matrix.md (divergent — live but semantically incorrect cumulative failure counting)"

  - id: ivy-control-vps
    display_name: VPS / Control Plane
    purpose: "Host monitoring, capacity tracking, control-plane revision tracking"

    lifecycle: monitoring
    admission_gate: null

    runtime_path: "/home/scraper/apps/ivy-control-vps"
    deployment_method: git-clone
    approved_sha: "1cd48d756ede1018b7f74f0ecc30c3f8fc68e044"

    systemd:
      active_timer: null
      active_service: null
      backup_timer: null
      backup_service: null
    legacy_units: []

    data_paths: []
    config_paths: []

    database: null

    expected_cadence: on-demand
    expected_cadence_seconds: null
    freshness_threshold_hours: null

    declared_health_state: null
    health_producer: vps/capacity_snapshot, control-plane/revision
    health_script: tools/producers/vps_capacity_snapshot.py
    health_conformance: null

    owning_repo: ivy-control-vps
    control_record: repos/ivy-control-vps/CONTROL.md
    runbook: null
    release_gates: null

    verification_date: "2026-07-20"
    verification_sources:
      - tools/ingestion_dashboard.py
      - tools/producers/vps_capacity_snapshot.py
      - tools/producers/control_plane_revision.py
      - docs/health/producer-registry.md
      - repos/ivy-control-vps/CONTROL.md
    verification_basis: "Clean public engineering workspace verified at the approved exact SHA; no service, scheduler, production data, private context, or _internal tree. The obsolete tracked root TODO is deliberately absent through the declared sparse workspace profile. Producer references remain from tools/producers/ directory and dashboard capacity collection."
---

# VPS Inventory v1

**Purpose:** VPS deployment topology layer for the Ivy portfolio control plane. Documents what runs on the VPS, how it runs, and what is expected of each workload.

**Authority model:** This file is a derived view — it aggregates information from per-repo `CONTROL.md` files, operational runbooks, and verified live state. It does not replace any of its sources. See §Authority Separation below.

**Maintained by:** OpenCode agents when workload topology changes (new deployment, lifecycle change, timer rename). Verify against CONTROL.md on each update.

---

## Authority Separation

| Artifact | Owns | Examples |
|---|---|---|
| `repos/*/CONTROL.md` | Repository governance | Lifecycle, gates, blockers, Buddy decisions, Hermes scope, backup policy |
| `docs/VPS_INVENTORY.md` | VPS topology | Runtime path, systemd units, data/config paths, cadence, health sources |
| `docs/HEALTH_CONTRACT.md` | Health architecture | 46-field schema, producer pipeline, freshness semantics, adapter interface |
| Dashboard / producers | Current evidence | Service state, backup age, capacity, last run timestamps, health payloads |

### Rules

1. **VPS_INVENTORY.md is policy, not evidence.** It declares what SHOULD be true about VPS topology. Current runtime state belongs in the dashboard output (`_internal/generated/ingestion-dashboard/status.json`).
2. **When VPS_INVENTORY.md disagrees with live evidence, it is drift.** Drift is detected by comparing this file against live probes — not by silently updating this file to match live state.
3. **When VPS_INVENTORY.md disagrees with CONTROL.md, CONTROL.md wins.** CONTROL.md is the per-repo governance authority. This file is a derived aggregation.
4. **This file must not contain secrets.** No IP addresses, passwords, tokens, or private paths outside `/home/scraper/`.

---

## Workload Details

### reddit-ops (WGU Reddit)

Daily WGU subreddit collection running as a systemd user service on the VPS. PostgreSQL 16 backend with approved-partial exit semantics. Deployed via SCP (Git publication blocked by credential-bearing commit history).

**Key characteristics:**
- Sole VPS timer/service for production collection
- Legacy shadow timer preserved as SQLite rollback
- Backup unit ExecStart has drifted on VPS — references `backup_reddit_ops.sh` instead of `backup_reddit_ops_pg.sh` (documented in `repos/reddit-ops/CONTROL.md:197`)
- No dedicated health script exists on disk despite documentation references (see `repos/reddit-ops/CONTROL.md:130,164`)
- Health conformance: adapter-compatible — health state is derivable from `reddit_core.ingestion_runs` + systemd probes

### traderie

Diablo II market-data pipeline with segmented generation. Root systemd timer (not user-scoped). Only workload with a working canonical v2 health producer.

**Key characteristics:**
- Root systemd timer `traderie-ingest-snapshot.timer` — not user-scoped like other workloads
- No user-scoped service unit; timer triggers a script directly
- Health producer registered in `docs/health/producer-registry.md` as `traderie/snapshot` and `traderie/health_export`
- Active blocker: `pc_hc_nl` segment timeout on 2026-07-16 natural run
- No dedicated runbook in repos/traderie/ — operational knowledge in CONTROL.md and RELEASE_GATES.md

### ih-market-companion

Browser-dependent market snapshot collection. Uses Chrome + Tampermonkey userscript, with `collector_helper.py` as a systemd service providing a health endpoint on `127.0.0.1:8765`.

**Key characteristics:**
- Shares `ih-collector-helper.service` with idlehacking-kb (see `shared_service_with`)
- No volume database — data is file-based in `/home/scraper/data/market`
- Health conformance: adapter-required — existing `health.private_status` table has divergent schema
- Userscript source authority unresolved (pending Buddy decision)

### idlehacking-kb

Private chat archiving and knowledge base. Metadata in PostgreSQL, raw chat data in `/home/scraper/data/private/chat/`.

**Key characteristics:**
- Shares `ih-collector-helper.service` with ih-market-companion
- Chat data is protected — metadata (file count, sizes) is acceptable for inspection; bodies are not
- Health conformance: divergent — health endpoint returns cumulative failure counts as current state, which is semantically incorrect per HEALTH_CONTRACT.md §4.8
- PostgreSQL metadata DB with 7 schemas

### VPS / Control Plane

The monitoring and control surface of the Ivy control plane. Runs read-only capacity probes, deployed-revision tracking, and dashboard generation. Not a deployed workload in the traditional sense — included for complete VPS topology visibility.

**Key characteristics:**
- No systemd units — probes run on-demand or via Hermes
- Producer contracts exist in `tools/producers/`: `vps_capacity_snapshot.py`, `control_plane_revision.py`
- Dashboard output at `_internal/generated/ingestion-dashboard/`

---

## Maintenance Rules

1. **Update when:** a workload is deployed, retired, renamed, or changes timer/service/data paths. Also update when a lifecycle state changes or a new workload is admitted to the VPS.
2. **Verify against:** the workload's `CONTROL.md`, its runbook (if any), and the dashboard's live probe output.
3. **Do not add:** runtime evidence fields (current service state, backup age, last run timestamp). These belong in the dashboard.
4. **Do not add:** non-VPS repos. They are documented in `tools/portfolio_registry.py` and their own `CONTROL.md` files.
5. **Source precedence:** CONTROL.md YAML front matter is authoritative for lifecycle, scheduler, database, and health state. Systemd names are verified against dashboard probes. Paths are verified against the private inventory and CONTROL.md.

---

## Non-VPS Repositories

The following managed repositories have no VPS deployment and are not included in this inventory. See `repos/*/CONTROL.md` for their lifecycle state and `tools/portfolio_registry.py` for the aggregate repository list.

| Repository | Lifecycle | Reason excluded |
|---|---|---|
| sjc-intel | source-only | Not yet deployed to VPS; no active scheduler |
| wgu-catalog | batch | No VPS runtime discovered |
| palworld-kb | source-only | Capability prototype; no VPS requirement |
| bsda-courses | downstream | LLM consumer; no VPS presence |
| wgu-atlas | downstream | LLM consumer; no VPS presence |
| reckless-ben | restricted | NO_LAUNCH policy |

---

## Change Log

| Date | Change | Author |
|---|---|---|
| 2026-07-19 | v1 created from CONTROL.md sources + live verification across 5 VPS workloads | OpenCode (Session 11, Task 5) |
