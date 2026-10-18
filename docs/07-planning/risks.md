---
title: Risk register
status: review
owner: product
last_reviewed: 2026-10-18
related: [docs/07-planning/effort.md, docs/07-planning/open-questions.md]
---

# Risk register

Risks carry permanent IDs (`RISK-NNN`). Likelihood (L) and impact (I) use a 1 to 5 scale; score = L × I. Review this register at every milestone exit.

| ID | Risk | L | I | Score | Mitigation | Owner epic |
| --- | --- | --- | --- | --- | --- | --- |
| RISK-001 | Solo scope overrun: the project is team-sized | 4 | 5 | 20 | Narrow launch pack; milestones are capability gates; cut scope before quality; AI agents implement well-specified stories | all |
| RISK-002 | Simulation desyncs between client prediction and server | 3 | 4 | 12 | Fixed-point maths only, no floats in `WarRoom.Simulation`; state hash per tick; golden replays in CI on both runtimes (ADR-0005) | EP-05 |
| RISK-003 | Unity runtime changes (CoreCLR migration) break shared code assumptions | 2 | 3 | 6 | Shared code pinned to netstandard2.1 / C# 9; CI builds the shared assembly with both toolchains | EP-05 |
| RISK-004 | Globe rendering misses 60 fps on mid-range Android | 3 | 4 | 12 | Performance budget per frame; low-end AVD and a real mid-range phone in the test matrix; quality tiers | EP-09 |
| RISK-005 | Low player population makes 32/64-player queues slow to fill | 4 | 4 | 16 | AI nations fill empty slots; start with 16-player matches; scheduled match starts; cross-platform pool | EP-17, EP-18 |
| RISK-006 | Name conflict: existing "War Room" game on Steam | 3 | 3 | 9 | Store title "War Room: Global Theater"; attorney trademark search; fallbacks listed in naming doc | EP-01 |
| RISK-007 | No Mac makes iOS builds and signing harder | 4 | 3 | 12 | macOS CI runners with fastlane match; cloud Mac rental as a fallback; see open question OQ-001 | EP-04 |
| RISK-008 | AWS costs grow before revenue | 3 | 3 | 9 | Budgets and anomaly alerts per account; Fargate Spot and Aurora min capacity in dev; dev scales to zero at night | EP-03 |
| RISK-009 | Store rejection: monetization or privacy policy issues | 2 | 4 | 8 | Fair-monetization rules (ADR-0010); privacy labels and account deletion built in M4; follow both store guidelines | EP-21, EP-23 |
| RISK-010 | Cheating via modified clients | 3 | 4 | 12 | Server authoritative; server filters hidden state before sending (fog of war); rate limits; anomaly telemetry | EP-16, EP-23 |
| RISK-011 | Geodata licensing restricts commercial use | 2 | 4 | 8 | Use public-domain or permissive sources (Natural Earth); licence register in the geodata pipeline | EP-10 |
| RISK-012 | AI agents introduce subtle bugs or drift from conventions | 3 | 3 | 9 | Binding AGENTS.md, Cursor rules, schema-first contracts, required checks, human review of every PR | EP-01 |
| RISK-013 | Agent or CI credentials misused against prod | 1 | 5 | 5 | Agents are read-only outside dev; SCPs deny writes in prod; OIDC with short-lived sessions; no long-lived keys | EP-03 |
| RISK-014 | Weeks-long matches lose players mid-match (abandonment) | 4 | 3 | 12 | AI takes over inactive nations; speed tiers 2x/4x; check-in friendly design; inactivity rules | EP-17, EP-19 |
| RISK-015 | Art quality falls short of genre expectations | 3 | 4 | 12 | Art direction set early in the design system; budget for contract artists; stylised readable look over realism | EP-11 |

## Top risks to retire in M1

RISK-002, RISK-004 and RISK-007 must be retired or downgraded before M1 exits, because they invalidate architecture choices if they materialise late.
