---
title: Technical design (TDD) overview
status: accepted
owner: architecture
last_reviewed: 2026-10-18
related: [ADR-0003, ADR-0004, ADR-0005, ADR-0006, ADR-0007]
---

# Technical design overview

## System context

```mermaid
flowchart LR
  subgraph Devices
    iOS[iOS client<br/>Unity]
    Android[Android client<br/>Unity]
    Web[Web client<br/>Unity WebGPU - later]
  end

  subgraph AWS["AWS (per environment account)"]
    CF[CloudFront<br/>content bundles]
    WAF[WAF] --> ALB[ALB<br/>TLS, WebSocket]
    ALB --> GW[Gateway<br/>ASP.NET Core<br/>WS + meta HTTP]
    GW <--> SILO[Orleans Silos<br/>MatchGrain, PlayerGrain...]
    GW --> ID[Identity svc]
    ID --> COG[Cognito]
    SILO --> PG[(Aurora PostgreSQL)]
    SILO --> S3[(S3 snapshots / replays)]
    GW --> VK[(Valkey)]
    SILO --> SQS[SQS]
    SQS --> WK[Workers<br/>notifications, receipts,<br/>analytics]
    GW --> FH[Firehose] --> S3A[(S3 analytics)] --> ATH[Athena]
    APPC[AppConfig] -.-> GW & SILO
  end

  iOS & Android & Web -- WSS protobuf / HTTPS JSON --> WAF
  iOS & Android & Web -- bundles --> CF
  WK --> FCM[FCM → APNs]
  WK --> STORES[App Store / Play APIs]
  iOS & Android -. crashes .-> SENTRY[Sentry]
  GW & SILO -. errors .-> SENTRY
```

## Components

| Component | Responsibility | Doc |
| --- | --- | --- |
| Shared simulation | Deterministic game rules, used by server (authority) and client (preview) | [simulation](simulation.md) |
| Gateway | Terminates WebSockets, authenticates, routes commands to grains, fans out updates, meta HTTP API | [server runtime](server-runtime.md) |
| Silo | Hosts grains: matches, players, lobbies, queues, chat | [server runtime](server-runtime.md) |
| Workers | Async jobs: push notifications, receipt validation, analytics export, cleanup | [server runtime](server-runtime.md) |
| Identity | Guest credentials, Cognito token exchange, War Room session tokens | [identity](identity-and-accounts.md) |
| Protocol | Protobuf envelopes, sequencing, resync | [networking](networking-and-protocol.md) |
| Persistence | Postgres, command log, snapshots, Valkey | [data](data-and-persistence.md) |
| Client | Unity app: globe, HUD, state sync, platform services | [client architecture](client-architecture.md) |
| Globe renderer | Province-ID cubemap globe | [globe rendering](globe-rendering.md) |
| Geodata pipeline | Natural Earth → provinces, adjacency, map assets | [geodata pipeline](geodata-pipeline.md) |
| Infrastructure | AWS accounts, network, services, IaC | [infrastructure](infrastructure-aws.md) |
| Observability | Logs, metrics, traces, crashes, analytics | [observability](observability-and-analytics.md) |
| Security | Threat model, anti-cheat, data protection | [security](security-and-anti-cheat.md) |
| Scale | Capacity model, load tests, limits | [scalability](scalability-and-capacity.md) |

## Key flows

### Command flow (for example, "move army")

```mermaid
sequenceDiagram
  participant C as Client
  participant G as Gateway
  participant M as MatchGrain
  participant DB as Postgres
  C->>G: ClientEnvelope{CommandSubmit{id, MoveArmy}}
  G->>G: auth, rate limit, schema check
  G->>M: SubmitCommand(nationId, cmd)
  M->>M: Simulation.Validate(state, cmd)
  alt valid
    M->>DB: append match_command_log(seq)
    M->>M: Simulation.Apply → events, schedule ArrivalEvent
    M-->>G: Ack{id, seq} + per-nation visible deltas
    G-->>C: ServerEnvelope{CommandAck}, ServerEnvelope{StateDelta}
  else invalid
    M-->>G: Reject{id, reason}
    G-->>C: ServerEnvelope{CommandRejected}
  end
```

### Time progression

The `MatchGrain` keeps a priority queue of scheduled events keyed by `GameTime`. An Orleans timer (while active) or reminder (while idle) wakes the grain at the next event's real-time equivalent. The grain processes all due events in deterministic order, persists, and pushes deltas. Idle matches cost almost nothing (see [simulation](simulation.md#time-model)).

## Cross-cutting non-functional requirements

| ID | Requirement | Where addressed |
| --- | --- | --- |
| NFR-PERF-001 | 60/30 fps globe | [globe rendering](globe-rendering.md#performance-budgets) |
| NFR-PERF-002 | Command ack p95 ≤ 250 ms | [server runtime](server-runtime.md), [scalability](scalability-and-capacity.md) |
| NFR-SCALE-001 | 5k matches, 100k CCU | [scalability](scalability-and-capacity.md) |
| NFR-AVAIL-001 | 99.9%, RPO ≤ 1 min | [data](data-and-persistence.md) |
| NFR-SEC-001 | Server authority, no hidden-state leaks | [security](security-and-anti-cheat.md) |
| NFR-PRIV-001 | GDPR/CCPA, account deletion | [identity](identity-and-accounts.md), [security](security-and-anti-cheat.md) |
| NFR-OPS-001 | Machine-readable environments | [AI environment access](../06-environments/ai-environment-access.md) |
