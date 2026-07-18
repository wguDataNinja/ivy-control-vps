# Portfolio Universe

**Status:** Current authority for the curated, known Ivy portfolio universe. **DISCOVERY_INCOMPLETE** — this is not a complete filesystem, GitHub, or historical-repository inventory.

## Purpose

This document answers: **what is known to exist and why does it matter to the portfolio?** It is a human-readable orientation layer for Buddy, engineers, and agents.

It does not own live health, priorities, deployment state, schedules, approved revisions, blockers, or backup evidence. Those belong respectively to the health contract and dated evidence, `ROADMAP.md`, and managed repository `CONTROL.md` records.

## Principles

- **Not admitted does not mean unimportant.** Admission authorizes a specific operational support model; it is not a quality or portfolio-value score.
- **Discovery incomplete does not mean low value.** An unreviewed or undiscovered asset is an inventory gap, not a judgment.
- **Classification and priority are separate.** This document classifies relationships; `ROADMAP.md` sets current execution priority.
- **Infrastructure belongs in the universe.** A dependency that protects portfolio data can be critical without being an application project.
- **Acknowledgement is not governance.** External or private assets can be named here without granting Ivy Control inspection, publication, deployment, or operational authority.

## Taxonomy

| Classification | Meaning |
|---|---|
| Managed operational | Ivy Control has a current record for a workload with an operational or runtime support lane. |
| Managed development | Ivy Control has a current record, but support is source-only, research, deferred, or otherwise non-runtime. |
| Infrastructure / support | A dependency or supporting system that protects or enables portfolio work. |
| Portfolio candidate | Known asset whose relationship or support model is not yet established. |
| External / private | Acknowledged asset outside current public governance or requiring private handling. |
| Historical / predecessor | Preserved lineage or superseded control-plane material; not current authority. |
| Discovery required | Known by reference but not sufficiently identified for a support decision. |
| Outside scope | Explicitly not governed by Ivy Control unless a later decision changes that boundary. |

## Known initial assets

| Asset | Classification | Portfolio relationship | Discovery confidence |
|---|---|---|---|
| ivy-control-vps | Managed operational | Portfolio control plane and reference implementation for governance, evidence, continuity, and bounded operations support. | Confirmed |
| ivy-control | Historical / predecessor | Earlier control-plane lineage; retained as historical context only. | Confirmed by current documentation |
| Reddit Ops | Managed operational | WGU Reddit collection and canonical-data continuity workload. | Confirmed by current control record |
| Traderie | Managed operational | Deterministic production data pipeline with bounded recovery work. | Confirmed by current control record |
| Idle Hacking KB | Managed operational | Knowledge/data system with protected corpus, metadata, and LLM/agent boundaries. | Confirmed by current control record |
| IH Market Companion | Managed operational | Idle Hacking market collection companion with browser-dependent boundaries. | Confirmed by current control record |
| Palworld KB | Managed development | Public source-only knowledge project; runtime support is not required. | Confirmed by current control record |
| WGU Catalog | Managed development | Low-frequency catalog/source workflow with proportional batch support. | Confirmed by current control record |
| WGU Atlas | Managed development | Downstream LLM application; valuable without a current runtime support lane. | Confirmed by current control record |
| BSDA Courses | Managed development | Staged LLM and course-data portfolio asset; deferred support does not reduce value. | Partial — current path/remote remains unresolved |
| SJC Intel | Managed development | Research/intelligence system; may remain operator-driven rather than a VPS service. | Confirmed by current control record |
| Reckless Ben | Managed development | Restricted `NO_LAUNCH` asset with approval-governance value. | Partial — preserved control record, source identity unresolved |
| Passport | Infrastructure / support | Portfolio backup and recovery dependency. | Confirmed by current backup documentation |
| chive_gate | External / private | Referenced lineage and dependency context; no current Ivy Control support model. | Discovery required |
| idle-hacker | External / private | Related ecosystem context; ownership and governance remain unresolved. | Discovery required |
| Hermes | Infrastructure / support | Read-only resident observation assistant; not a scheduler or production authority. | Confirmed by current operator documentation |
| adult-media-research | External / private | Separate private research asset acknowledged without current Ivy Control governance. | Discovery required |
| adultgraph | External / private | Separate private asset acknowledged without current Ivy Control governance. | Discovery required |

## Relationship to managed controls

`repos/<slug>/CONTROL.md` is the active authority for a managed repository's lifecycle, operational support, exceptions, and next authorized work. The machine-derived managed registry aggregates those records. This universe remains the broader human-readable inventory: it can include infrastructure, historical lineage, restricted assets, and acknowledged external/private assets that do not have or should not receive a managed control record.

## Discovery boundary

The complete repository-universe inventory is future work. It requires an explicitly scoped discovery task with approved locations, privacy handling, and a reconciliation process. Do not infer a new asset's value, exposure, owner, or support model from its absence here.
