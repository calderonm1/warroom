---
title: Simulation design
status: accepted
owner: architecture
last_reviewed: 2026-10-18
related: [ADR-0005, ADR-0011, EP-05, docs/02-game-design/core-loop.md]
---

# Simulation design

The simulation is the heart of War Room: a pure, deterministic C# library (`WarRoom.Simulation`) shared by the server (authority) and client (preview). Rules are numbered `SIM-NNN`.

## 1. Model

```
Step(state: MatchState, input: Command | ScheduledEvent, rng: IDeterministicRandom)
  -> (state': MatchState, events: SimEvent[], scheduled: ScheduledEvent[])
```

| ID | Rule |
| --- | --- |
| SIM-001 | `MatchState` is the complete authoritative state. Anything not in it does not exist for the rules. |
| SIM-002 | `Step` is pure: same inputs give the same outputs, bit for bit, on every platform. |
| SIM-003 | Commands are validated by `Validate(state, nationId, command) -> Result` before `Apply`. Validation has no side effects. |
| SIM-004 | Every state change emits a `SimEvent` (for example `ArmyDeparted`, `ProvinceCaptured`). Clients and analytics consume events, never diffs computed elsewhere. |
| SIM-005 | Scheduled events are ordered by `(GameTime, Priority, Sequence)`. Ties are broken by a monotonic sequence number assigned at scheduling. |
| SIM-006 | State hash: `MatchState.ComputeHash()` (xxHash64 over canonical serialization) is computed after every step in debug and test builds, and every N steps in production, and stored with snapshots. |

## 2. Time model

| ID | Rule |
| --- | --- |
| SIM-010 | `GameTime` is int64 milliseconds since match start in game time. Real time = game time ÷ speed multiplier. |
| SIM-011 | **Movement and combat are event-driven.** A move schedules `ArmyArrives(provinceId)` at the computed arrival time. No per-frame ticking. |
| SIM-012 | **Economy ticks** every game hour (`EconomyTick`): resource production, upkeep, morale drift, construction progress. |
| SIM-013 | **Combat rounds** run every 15 game minutes per active engagement until it resolves. |
| SIM-014 | **Daily tick** at game midnight: research day-gating, VP accounting, AI strategic re-planning, inactivity checks. |
| SIM-015 | The server converts the next scheduled `GameTime` into a wall-clock wake-up. Idle matches sleep until the next event. |

A 64-player match at 1x produces on the order of 10³ to 10⁴ steps per real hour. One silo core can therefore host hundreds of active matches (see [scalability](scalability-and-capacity.md)).

## 3. Determinism rules

| ID | Rule |
| --- | --- |
| SIM-020 | Numbers in state use `Fixed64` (Q32.32) or integers. No `float`/`double`. |
| SIM-021 | Randomness comes only from `IDeterministicRandom` (PCG32, seeded by match seed and step index). Never `System.Random` or `Guid.NewGuid`. |
| SIM-022 | Collections that affect outcomes are ordered (sorted by ID). No `Dictionary`/`HashSet` enumeration in rule code. |
| SIM-023 | No static mutable state, no threads, no I/O, no reflection-based ordering. |
| SIM-024 | Trig and sqrt on the sphere use fixed-point lookup tables or CORDIC from `WarRoom.Simulation.Math`. Distances between provinces are **precomputed** in map content where possible. |
| SIM-025 | Content (unit stats and so on) is loaded into immutable, ID-sorted arrays at match creation and pinned for the match's lifetime. |

## 4. Module layout

```
WarRoom.Simulation/
  Core/         MatchState, Step, Scheduler, Ids, GameTime, StateHash
  Math/         Fixed64, FixedVector3, lookup tables, geodesic helpers
  Random/       IDeterministicRandom, Pcg32
  Content/      ContentDatabase (immutable), definitions (UnitDef, BuildingDef...)
  Map/          Province graph, adjacency, pathfinding (A* on province graph)
  Economy/      resources, production, upkeep, morale
  Military/     units, armies, movement, combat resolution
  Research/     research queue, day-gating
  Diplomacy/    relations, treaties, coalitions
  Visibility/   fog of war, intel (server uses it to filter deltas)
  Ai/           AI nation controllers (deterministic, same rules as players)
  Commands/     command definitions + validators + appliers
  Events/       SimEvent definitions
  Serialization/ canonical binary snapshot format
```

## 5. Commands (initial set)

| Command | Validates | Effect |
| --- | --- | --- |
| `MoveArmy(armyId, path[] or targetProvinceId, mode)` | ownership, reachable path, not in combat lock | schedules departure and arrival events |
| `SplitArmy` / `MergeArmies` | co-located, ownership | army composition changes |
| `QueueProduction(provinceId, unitDefId, count)` | building requirements, resources, research | reserves resources; schedules completion |
| `QueueConstruction(provinceId, buildingDefId)` | slots, resources | schedules completion |
| `StartResearch(researchId)` | prerequisites, day-gate, slot | schedules completion |
| `SetStandingOrder(armyId, rule)` | rule schema, slot limits | stored; evaluated on relevant events |
| `ProposeTreaty` / `RespondTreaty` | relation state | diplomacy state changes |
| `Attack(armyId, targetArmyId or provinceId)` | range, line of movement | engagement or movement |
| `LaunchMissile(siteId, target)` | range, stock | schedules impact |

All commands carry `clientCommandId` (UUIDv7 from the client) for idempotency. A duplicate ID returns the original result.

## 6. Testing strategy

| Layer | What | Tooling |
| --- | --- | --- |
| Unit | each rule and validator | xUnit |
| Property | invariants (resources never negative, provinces have exactly one owner, armies are never in two places) | FsCheck |
| Golden replay | recorded scenarios reproduce known state hashes | xUnit + fixtures in `shared/simulation/WarRoom.Simulation.Tests/Golden/` |
| Cross-platform | the same golden replays on x64 (CI) and arm64 (CI + device) | GitHub Actions matrix, Unity PlayMode test |
| Soak | 64-nation AI-only match simulated at max speed to completion | nightly job |
| Performance | steps/sec benchmark per scenario | BenchmarkDotNet |

## 7. Client usage

The client keeps a **local mirror** of the visible state (from server deltas) and uses the simulation for:

- previews (travel time, production ETA, combat odds), using the same functions as the server;
- optimistic UI for low-risk commands (queue order shown immediately, reconciled on ack).

It never runs authoritative steps. Hidden information is absent from the mirror by construction.
