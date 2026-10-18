---
title: Effort characterization
status: review
owner: product
last_reviewed: 2026-10-18
related: [docs/07-planning/roadmap.md, docs/07-planning/risks.md, backlog/README.md]
---

# Effort characterization

This doc sizes the work **by technical scope**, not by calendar time. The sizes are relative and get recalibrated as stories close. The backlog's story `size` field uses the same scale.

## Scale

| Size | Meaning for a story | Typical shape |
| --- | --- | --- |
| XS | One file or one config change, no new tests | rename, doc fix, flag |
| S | One component, a handful of tests | a grain method, a UI panel |
| M | Several files in one subsystem, new test fixtures | a new order type end to end |
| L | Crosses two subsystems or adds a new contract | a new protocol message and handler and UI |
| XL | Must be split before work starts | — |

Epics are sized by **share of total effort** and **complexity drivers**.

## Overall picture

War Room is a large project for a solo developer. Comparable shipped titles were built by teams of 20 to 60 people. The plan stays feasible because of four deliberate choices:

1. **Narrow first content pack.** One modern-era pack, one map size per queue at launch, a curated unit roster.
2. **Shared deterministic simulation.** Gameplay rules are written once and run on both client (prediction) and server (authority).
3. **Managed cloud services.** No self-run databases, brokers or Kubernetes.
4. **AI-first workflow.** Every story is written so an agent can implement it with tests; the human acts as reviewer, designer and integrator.

The work that **cannot** be delegated to code agents dominates the risk: game feel and balance, art direction, store and legal processes, and playtesting.

## Per-epic sizing

| Epic | Share | Complexity drivers | Specialist help worth buying |
| --- | --- | --- | --- |
| EP-01 AI-first foundation | 1% | docs volume, tooling | trademark attorney |
| EP-02 Dev environment and scaffolding | 3% | Unity plus .NET plus Docker toolchain, LFS | — |
| EP-03 Cloud environments and IaC | 5% | multi-account AWS, least-privilege IAM, cost control | AWS review (optional) |
| EP-04 CI/CD | 4% | Unity licensing in CI, iOS signing without a Mac | — |
| EP-05 Shared simulation | 8% | determinism, fixed-point math, replay tooling | — |
| EP-06 Match runtime | 8% | Orleans placement, persistence, crash recovery | — |
| EP-07 Protocol | 3% | versioning, delta compression, visibility filtering | — |
| EP-08 Identity | 3% | Apple/Google sign-in, guest upgrade, deletion | — |
| EP-09 Globe rendering | 8% | custom shaders, mobile GPU budgets, picking | technical artist (contract) |
| EP-10 Geodata pipeline | 4% | GIS data licensing, province generation, baking | — |
| EP-11 Client shell and design system | 6% | UI Toolkit at scale, safe areas, theming | UI/UX designer (contract) |
| EP-12 Economy | 5% | balance, hourly ticks, fairness constraints | — |
| EP-13 Military and combat | 7% | pathing on province graph, combat resolution, balance | — |
| EP-14 Research | 2% | tree data, UI | — |
| EP-15 Diplomacy and chat | 4% | coalition rules, chat moderation | — |
| EP-16 Intel and fog of war | 4% | server visibility filtering, leak tests | — |
| EP-17 AI nations | 6% | utility AI that plays credibly and cheaply | — |
| EP-18 Lobbies, matchmaking, rating | 3% | queue fill at low population, rating maths | — |
| EP-19 Notifications and check-in play | 2% | FCM/APNs, quiet hours, batching | — |
| EP-20 Observability and analytics | 3% | event schema, Athena, dashboards | — |
| EP-21 Monetization and store | 4% | receipt validation, store policies, refunds | — |
| EP-22 LiveOps | 3% | seasons, events, remote config | — |
| EP-23 Safety, moderation, compliance | 3% | GDPR/CCPA, age ratings, reporting | privacy counsel |
| EP-24 Onboarding | 2% | tutorial match, FTUE tuning | — |
| EP-25 Launch readiness | 2% | store assets, runbooks, load tests | — |
| EP-26 Web client | 6% | WebGL/WebGPU budgets, input parity | — |

The shares add up to about 100%. **Art and audio production** are not counted above. If assets are bought or contracted, that adds coordination work. If they are made in-house, they are a second project of similar size to the code.

## Where effort concentrates

- **M1 is the most uncertain milestone.** It proves the simulation, the runtime, the renderer and the deploy pipeline at once. Expect rework here, and treat it as the place to change ADRs if a bet fails.
- **M2 is the largest code milestone.** It contains most gameplay systems. The work parallelizes well across agent sessions because the systems are isolated behind the simulation's system interfaces.
- **M4 is the largest non-code milestone.** Store review, compliance, beta operations and load testing all land here.

## Recalibration

After each milestone, compare completed story sizes with actual change size (files touched, tests added), then update this doc and the scale table. Sizes are never converted into dates in this repo.
