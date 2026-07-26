# Portfolio Intent

**Status:** Current authority for Buddy's priorities and current cares.
**Updated:** 2026-07-19
**Purpose:** What Buddy currently cares about. This is the layer Hermes watches.
It is distinct from engineering truth, roadmap phases, or implementation queues.

---

## What This Is

Portfolio Intent answers: **"What matters right now?"** It is Buddy's
highest-level priority signal — the reason certain repos receive attention,
certain features get built, and certain infrastructure gets investment.

It does not contain:
- implementation detail (that belongs in repo ROADMAP.md or TODO.md);
- task assignments (that belongs in TODO.md);
- gate evidence (that belongs in CONTROL.md and RELEASE_GATES.md);
- architecture decisions (that belongs in the relevant standard).

---

## What This Is Not

Portfolio Intent is not a roadmap. A roadmap explains *how* and *when*. Intent
explains *why* and *what matters*. Hermes should read this document to answer
"Is what we are doing still aligned with what Buddy cares about?"

---

## Current Priorities

### Palworld KB / STS

| Field | Value |
|-------|-------|
| **Status** | Active |
| **Intent** | Demonstrate a complete backend/frontend AI prototype. |
| **Why** | Proves the reusable application architecture across KB, backend, and frontend. |
| **Hermes observation** | Roadmap progress, test health, deployment state |

### Adult Research Ontology

| Field | Value |
|-------|-------|
| **Status** | High priority |
| **Intent** | Demonstrate ontology extraction and classification capability over a 17k+ story corpus. |
| **Why** | Proves the research pipeline methodology at scale. |
| **Hermes observation** | Extraction throughput, classification accuracy, pipeline health |

### Ivy VPS Infrastructure

| Field | Value |
|-------|-------|
| **Status** | Infrastructure priority |
| **Intent** | Move all active portfolio systems onto autonomous VPS operation with health monitoring, backup, and recovery. |
| **Why** | Reduces Mac dependency, enables Hermes resident operation, establishes production baseline. |
| **Hermes observation** | Host capacity, service health, backup freshness, drift detection |

### IdleHacking Market

| Field | Value |
|-------|-------|
| **Status** | Active |
| **Intent** | Develop autonomous market intelligence and trading capability. |
| **Why** | Strategic automation target with real-time data value. |
| **Hermes observation** | Collector health, data freshness, archive continuity |

### SJC Intel

| Field | Value |
|-------|-------|
| **Status** | Active |
| **Intent** | Move toward scheduled autonomous intelligence generation from the current manual research workflow. |
| **Why** | Demonstrates the research automation pipeline for public-information intelligence. |
| **Hermes observation** | Publication readiness, scheduler state, data growth |

### WGU Atlas / BSDA Courses

| Field | Value |
|-------|-------|
| **Status** | Deferred — blocked by upstream boundaries |
| **Intent** | Publish WGU Atlas with manual review gate. Create phone-friendly Reddit activity workflow for BSDA. |
| **Why** | Portfolio completeness. |
| **Hermes observation** | Boundary gate status, upstream dependency health |

---

## Priority Framework

Buddy's attention follows this order:

1. **Active prototype** — proving a new capability (Palworld KB)
2. **Research pipeline** — extraction/classification at scale (Adult Research)
3. **Infrastructure** — keeping the platform healthy (VPS)
4. **Automation** — reducing manual toil (IdleHacking, SJC)
5. **Completeness** — finishing what exists (WGU Atlas, BSDA)

---

## Hermes Consumption

Hermes reads `docs/PORTFOLIO_INTENT.md` to answer:

- "What does Buddy currently care about?"
- "Is the current work aligned with those cares?"
- "Which repos need attention?"
- "Where is investment misaligned with intent?"

Hermes must never modify this document. Intent changes come from Buddy.

---

## Change Process

This document is updated by Buddy only. Agents may reference it for context
and note misalignments in result reports, but may not edit it.

Intent changes are expected to be infrequent — they reflect genuine priority
shifts, not daily task reshuffling.
