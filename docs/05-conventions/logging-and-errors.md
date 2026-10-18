---
title: Logging, errors and tracing
status: accepted
owner: engineering
last_reviewed: 2026-10-18
related: [ADR-0013, docs/03-architecture/observability-and-analytics.md]
---

# Logging, errors and tracing

## 1. Log format (server)

JSON, one object per line. Mandatory fields:

| Field | Example |
| --- | --- |
| `ts` | `2026-10-18T17:42:01.123Z` |
| `level` | `Information` |
| `msg` | `Command rejected` (template, constant) |
| `env` | `dev` |
| `service` | `silo` |
| `version` | `0.4.2-abc1234` |
| `trace_id` / `span_id` | OTel IDs |
| `event_id` | stable numeric ID per log site (LoggerMessage) |

Contextual fields when available: `match_id`, `nation_id`, `player_id` (pseudonymous UUID), `command_type`, `error_code`, `duration_ms`.

## 2. Rules

| ID | Rule | Enforced by |
| --- | --- | --- |
| CONV-LOG-001 | Message templates are constant; data goes in properties (`"Command {CommandType} rejected: {ErrorCode}"`). | analyzer CA2254 |
| CONV-LOG-002 | Levels: `Debug` (dev only), `Information` (lifecycle), `Warning` (handled anomaly), `Error` (failed operation needing attention), `Critical` (service degraded). | review |
| CONV-LOG-003 | Never log secrets, tokens, emails, IPs, chat bodies or full command payloads in staging/prod. | log redaction tests |
| CONV-LOG-004 | Every error has a stable `error_code` (UPPER_SNAKE) listed in `shared/contracts/errors.yaml`, shared by logs, HTTP Problem Details and protocol `Error` messages. | CI check |
| CONV-LOG-005 | Exceptions are logged once, at the boundary that handles them, with the exception object. | review |
| CONV-LOG-006 | Client logs: Unity `Debug.Log*` only through `WarRoom.Client.Core.Log` wrapper (levels, Sentry breadcrumbs, stripped in release except warnings and errors). | banned API test |
| CONV-LOG-007 | Trace context propagates client→gateway (`traceparent` in `Hello` and HTTP) and gateway→grains (Orleans OTel). | integration test |
