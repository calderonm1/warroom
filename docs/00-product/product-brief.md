---
title: Product brief (confirmed requirements)
status: accepted
owner: product
last_reviewed: 2026-10-18
related: [docs/00-product/vision.md, docs/07-planning/roadmap.md]
---

# Product brief

This is the confirmed project brief. It is the contract for scope at the highest level. Requirement IDs (`BR-NNN`) are permanent.

## Business requirements

| ID | Requirement |
| --- | --- |
| BR-001 | Product name **War Room**. The store listing may add a subtitle (see [naming](naming-and-brand.md)). |
| BR-002 | Real-time grand strategy, genre peers: Conflict of Nations / Supremacy, Hearts of Iron IV. |
| BR-003 | 3D globe as the primary map, not a flat projection. |
| BR-004 | iOS and Android at launch from one codebase; architecture must allow a web client later without rewriting game logic or backend. |
| BR-005 | Built to commercial quality and to run at scale: many concurrent matches, many thousands of concurrent players. |
| BR-006 | Solo developer for now; process and code must be team-ready (onboarding a collaborator must not require rewrites). |
| BR-007 | Modern-day setting at launch; content model must allow other settings as expansions. |
| BR-008 | AI-first development: docs, backlog, environments and tooling are designed for AI agents to interpret and act on. |
| BR-009 | Backlog is AI-first (YAML in repo) and synced to GitHub Projects for human readability. |
| BR-010 | Conventions (naming, code, UI design, git) are defined before feature code and enforced by tooling where possible. |
| BR-011 | Separate dev, staging and prod environments. |
| BR-012 | AWS is the preferred cloud unless clearly outclassed (it is not; see [ADR-0007](../adr/0007-cloud-aws.md)). |
| BR-013 | Monetization follows current industry best practice and avoids pay-to-win (see [ADR-0010](../adr/0010-monetization-fair-by-design.md)). |

## Product requirements (summary; detail lives in the GDD)

| ID | Requirement | GDD |
| --- | --- | --- |
| PR-001 | Matches of 16, 32 and 64 players at launch; 100-player event maps later | [match lifecycle](../02-game-design/match-lifecycle.md) |
| PR-002 | Persistent real-time matches lasting days to weeks, at speed tiers 1x, 2x and 4x | [match lifecycle](../02-game-design/match-lifecycle.md) |
| PR-003 | Playable in 5 to 10 minute check-ins: standing orders, queues, briefings, push notifications | [core loop](../02-game-design/core-loop.md) |
| PR-004 | Economy, production, research, land/air/naval/missile/drone warfare, diplomacy, fog of war | GDD sections |
| PR-005 | AI-controlled nations fill empty slots and take over inactive players | [AI nations](../02-game-design/ai-nations.md) |
| PR-006 | Coalitions with shared victory; ranked and casual queues | [diplomacy](../02-game-design/diplomacy-and-coalitions.md) |
| PR-007 | Fair monetization: cosmetics, seasonal pass, convenience subscription | [monetization](../02-game-design/monetization.md) |
| PR-008 | Short skirmish mode (1 to 2 hours) after launch | [match lifecycle](../02-game-design/match-lifecycle.md) |

## Non-functional requirements (summary; detail lives in the TDD)

| ID | Requirement |
| --- | --- |
| NFR-PERF-001 | 60 fps on reference devices and ≥ 30 fps on minimum-spec devices on the globe view |
| NFR-PERF-002 | Command round-trip (client send → server ack) p95 ≤ 250 ms within region |
| NFR-SCALE-001 | Architecture supports ≥ 5,000 concurrent matches and ≥ 100,000 CCU by horizontal scaling only |
| NFR-AVAIL-001 | Match runtime availability ≥ 99.9% monthly; no match state lost on node failure (RPO ≤ 1 min of commands) |
| NFR-SEC-001 | Server-authoritative; no hidden state ever sent to clients |
| NFR-PRIV-001 | GDPR/CCPA compliant; in-app account deletion (Apple requirement) |
| NFR-COST-001 | Infrastructure cost per DAU tracked from beta, target ≤ $0.01/DAU/day at scale |
| NFR-OPS-001 | Every environment is described by a machine-readable manifest, readable by agents |
