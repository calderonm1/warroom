---
title: Server conventions (ASP.NET Core and Orleans)
status: accepted
owner: engineering
last_reviewed: 2026-10-18
related: [ADR-0004, docs/03-architecture/server-runtime.md]
---

# Server conventions

| ID | Rule | Enforced by |
| --- | --- | --- |
| CONV-SRV-001 | Projects follow the layout in [`server/README.md`](../../server/README.md). Grains contain no hosting, HTTP or ASP.NET references. | NetArchTest |
| CONV-SRV-002 | Grain interfaces live in `WarRoom.Server.Grains.Abstractions`. Methods return `Task`/`ValueTask`, accept and return serializable DTOs (`[GenerateSerializer]`), never domain entities. | review |
| CONV-SRV-003 | Grain methods are short. Long work is split into steps or delegated to workers. Grain call timeouts: 10 s default. | review |
| CONV-SRV-004 | `[Reentrant]` is forbidden on `MatchGrain` (single-threaded authority). Allowed on read-only query grains with justification. | review |
| CONV-SRV-005 | HTTP endpoints use minimal APIs grouped per resource (`MapGroup("/v1/matches")`), validated against OpenAPI (contract tests). | contract tests |
| CONV-SRV-006 | Errors in HTTP: RFC 9457 Problem Details with a stable `code` (`MATCH_FULL`, `NOT_ENTITLED`). Codes are listed in `shared/contracts/errors.yaml`. | contract tests |
| CONV-SRV-007 | Configuration through `IOptions<T>` with validation on start (`ValidateOnStart`). Missing config means fail fast. | startup |
| CONV-SRV-008 | All outbound calls have timeouts, retries with jitter (Polly / `Microsoft.Extensions.Http.Resilience`) and circuit breakers. | review |
| CONV-SRV-009 | DB access via repository interfaces in Persistence. No SQL in grains. Queries parameterized. | review |
| CONV-SRV-010 | Every request and grain call is traced (OTel). Logs include `match_id` / `player_id` scopes. | review |
| CONV-SRV-011 | The local DevHost runs every role in one process with in-memory or Testcontainers dependencies; `make server-dev` starts it. | docs |
