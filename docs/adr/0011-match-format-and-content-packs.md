---
title: "ADR-0011: Match format (16 to 64 players, days to weeks, speed tiers) and data-driven content packs"
status: accepted
owner: product
last_reviewed: 2026-10-18
related: [BR-007, R-SIZE-01, R-SIZE-02, R-SIZE-04, R-TIME-01, R-TIME-04, docs/02-game-design/match-lifecycle.md, docs/02-game-design/content-model.md]
---

# ADR-0011: Match format and content packs

- **Date:** 2026-10-18
- **Deciders:** project owner

## Context

The market leader's newest title chose 32 to 64 players (R-SIZE-02). Smaller maps feel more decisive (R-SIZE-03) and fill faster, which is crucial for a new game's liquidity. Multi-day real-time is the genre standard (R-TIME-01), but fast speeds exhaust players (R-TIME-04). The setting is modern at launch, with expansion to other settings (BR-007).

## Decision

1. Launch map lineup: **regional maps of 16 and 32 players** and **one 64-player world map**. 100-player event maps come post-launch once concurrent users support them.
2. Speed tiers: **1x** (about 3 to 4 weeks), **2x** (about 1.5 to 2 weeks), **4x** (about 1 week). Match length is bounded by a victory-point threshold and a maximum match day.
3. Player count, coalition size, speed tier and victory rules are **map/queue configuration**. No code path assumes a specific player count. The engine must support at least 128 nations per match.
4. **Skirmish mode** (8 players, 1 to 2 hours, compressed time) is post-launch, built on the same engine with a different time scale and ruleset.
5. All setting-specific content is a **content pack** (`content/packs/<id>`): nations, units, research, buildings, resources, maps, localization. The engine knows only generic concepts (unit classes, damage types, resource types by ID). The launch pack is `modern`.

## Alternatives considered

| Option | Why not |
| --- | --- |
| 100-player maps only (CoN classic) | Slow fill for a new game; many abandoned slots |
| Short session matches only | Breaks the genre's core fantasy and social loop |
| Hard-coded modern units | Blocks expansions; mixes balance and code |

## Consequences

The simulation must scale from 8 to 128 nations. Content schemas and validators are first-class deliverables (`EP-05`, `EP-10`).

## Compliance

Content schema validation in CI. Simulation tests run on 8, 32 and 128 nation fixtures.
