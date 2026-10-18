---
title: "ADR-0005: Shared deterministic simulation library"
status: accepted
owner: architecture
last_reviewed: 2026-10-18
related: [ADR-0003, ADR-0004, R-ENG-03, docs/03-architecture/simulation.md]
---

# ADR-0005: Shared deterministic simulation library

- **Date:** 2026-10-18
- **Deciders:** project owner

## Context

Game rules (movement, combat, economy, research) must be identical on server (authority) and client (previews such as "arrives in 3h 12m" and "projected battle outcome"). They must also be reproducible: replaying a match's command log from a snapshot must give the exact same state. That gives us debugging, regression tests and AI-driven investigations. Unity players are limited to .NET Standard 2.1 and C# 9 until the CoreCLR/.NET 10 line ships (R-ENG-03).

## Decision

1. All game rules live in `shared/simulation/WarRoom.Simulation`, targeting **`netstandard2.1`** with **`<LangVersion>9</LangVersion>`**.
2. The simulation is a **pure, deterministic state machine**: `(State, Command | ScheduledEvent, RNG) → (State', Events[])`. It has no I/O, no clocks, no threads, and no static mutable state.
3. Determinism rules (enforced by analyzers and tests):
   - All state arithmetic uses fixed-point (`Fixed64`, Q32.32). `float` and `double` are forbidden in state and transition code (allowed only in client presentation code).
   - Randomness comes from an injected `IDeterministicRandom` (PCG32) seeded per match and advanced only by the simulation.
   - Iteration order must be deterministic: sorted collections or ID-ordered arrays. Never iterate `Dictionary`/`HashSet` where it affects state.
   - Time is `GameTime` (int64 milliseconds of game time), provided by the scheduler, never read from the system.
4. The library depends only on `shared/contracts` generated types (or its own domain types) and nothing else.
5. Golden replay tests: recorded snapshots plus command logs must reproduce a recorded state hash. A hash mismatch is a release-blocking bug.

## Alternatives considered

| Option | Why not |
| --- | --- |
| Separate client and server rule implementations | Drift, double work, cheating-detection blind spots |
| Server-only rules, client shows server results | No offline previews; worse UX; slower iteration |
| Floating-point with tolerance | Cross-platform float differences (ARM vs x64, IL2CPP vs CoreCLR) break replay equality |

## Consequences

- Fixed-point math is slightly less ergonomic; a `Fixed64` type with operators and a math library is an early story (`ST-05.1.2`).
- C# 9 limits apply in `shared/` (no file-scoped namespaces, no global usings, no `record struct`).
- Replays become a superpower: any production bug can be reproduced locally by an agent.

## Compliance

- A custom Roslyn analyzer or banned-API list (`BannedSymbols.txt` with `Microsoft.CodeAnalysis.BannedApiAnalyzers`) bans `System.Random`, `DateTime.Now`, `float` and `double` in `WarRoom.Simulation` (`ST-05.1.3`).
- CI builds `shared/` with `netstandard2.1` and runs golden replay tests on x64 and arm64.
