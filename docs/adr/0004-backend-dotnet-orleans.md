---
title: "ADR-0004: .NET 10 backend with Microsoft Orleans match actors"
status: accepted
owner: architecture
last_reviewed: 2026-10-18
related: [ADR-0005, ADR-0007, R-CLD-02, docs/03-architecture/server-runtime.md]
---

# ADR-0004: .NET 10 backend with Microsoft Orleans

- **Date:** 2026-10-18
- **Deciders:** project owner

## Context

Matches run continuously for days to weeks. Each match is a self-contained, stateful simulation with 16 to 100 players, most of whom are offline at any moment. The workload is many long-lived, mostly idle, stateful entities with bursts of commands. This is a poor fit for session-based dedicated game servers such as GameLift, which are designed for 20-minute FPS sessions (R-CLD-02), and an excellent fit for the **virtual actor** model. The server should run the same C# simulation as the client (ADR-0005).

## Decision

1. Backend language and runtime: **C# on .NET 10 (LTS)**, ASP.NET Core for HTTP and WebSockets.
2. Stateful game logic runs in **Microsoft Orleans** grains:
   - `MatchGrain` (one per match) owns authoritative match state and the event scheduler.
   - `PlayerGrain`, `LobbyGrain`, `QueueGrain`, `CoalitionChatGrain` and similar own their entities.
3. Process roles: **Gateway** (WebSocket and meta HTTP; Orleans client), **Silo** (grain host), **Workers** (background jobs). They are deployable separately and can be co-hosted in dev.
4. Orleans clustering, persistence and reminders use **PostgreSQL** (ADO.NET providers). Snapshots go to S3 (ADR-0016).
5. Grains must be non-blocking, single-threaded per activation (the Orleans default), and must not call external HTTP in the simulation path.

## Alternatives considered

| Option | Pros | Cons | Why not |
| --- | --- | --- | --- |
| AWS GameLift fleets, one process per match | Managed fleets, matchmaking (FlexMatch) | Designed for short sessions; a weeks-long idle match per process is wasteful; harder persistence | Wrong workload shape |
| Nakama (Go/TS) | Batteries included (auth, chat, matchmaking) | Different language from the Unity client, so no shared simulation; authoritative matches need custom handlers anyway | Loses the shared-code benefit |
| Akka.NET | Mature actor model | More boilerplate; manual cluster sharding | Orleans virtual actors are simpler for a solo dev |
| Stateless services + DB per command | Simple scaling | Load and reload of state per command; hard to run timers and events | Latency and cost |
| Metaplay | Shared C# logic, server-authoritative | Commercial SDK, opinionated toward base-builder games | Lock-in and cost |

## Consequences

- One language end to end (C#), so agents and the developer context-switch less.
- Orleans adds clustering concepts to learn; documented in [server runtime](../03-architecture/server-runtime.md).
- Matches survive silo failure: grains reactivate elsewhere from the latest snapshot and command log.

## Compliance

Architecture tests (NetArchTest) enforce that `WarRoom.Server.Grains` does not reference ASP.NET or HTTP clients (`ST-02.2.3`).
