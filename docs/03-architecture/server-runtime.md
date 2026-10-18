---
title: Server runtime
status: accepted
owner: architecture
last_reviewed: 2026-10-18
related: [ADR-0004, ADR-0016, ADR-0019, ADR-0020, EP-06, docs/05-conventions/server.md]
---

# Server runtime

## 1. Processes

| Process | Project | Scales on | Notes |
| --- | --- | --- | --- |
| Gateway | `WarRoom.Server.Gateway` | concurrent connections (target ≤ 20k WS per task) | Stateless except for connection state; Orleans client |
| Silo | `WarRoom.Server.Silo` | active grains, CPU | Hosts grains; Orleans cluster membership in Postgres |
| Workers | `WarRoom.Server.Workers` | queue depth | SQS consumers |
| Admin | `WarRoom.Server.Admin` | n/a (internal) | Internal ALB, IAM-authenticated. Debug API. |
| Migrator | one-shot task | n/a | Applies DB migrations before deploy |

In local dev, all of them run in **one process** (`WarRoom.Server.DevHost`) for fast iteration.

## 2. Grains

| Grain | Key | State | Responsibility |
| --- | --- | --- | --- |
| `MatchGrain` | matchId | MatchState (in memory), command log, scheduler | Authority for one match; validates and applies commands; advances time; emits per-nation deltas |
| `MatchDirectoryGrain` | singleton per shard | open matches index | Lists joinable matches for lobbies |
| `QueueGrain` | queueId (`ranked:world64:1x`) | waiting players | Matchmaking: fills matches, triggers creation |
| `PlayerGrain` | playerId | profile, active matches, settings, entitlements cache | Per-player meta state; notification preferences |
| `PresenceGrain` | playerId | online sessions | Routes pushes vs in-app notifications |
| `ChatChannelGrain` | channelId | recent messages (bounded) | Match, coalition and private chat; persists to Postgres |
| `RatingGrain` | seasonId:playerId | Glicko-2 rating | Updated on match end |

Rules:

| ID | Rule |
| --- | --- |
| SRV-001 | Grains never block. All I/O is async with timeouts. |
| SRV-002 | `MatchGrain` persists the command to the log **before** acknowledging (write-ahead). |
| SRV-003 | `MatchGrain` writes a snapshot every 6 game-hours, on deactivation, and on graceful shutdown. On activation it loads the latest snapshot and replays the log tail. |
| SRV-004 | While a match has connected players, the grain stays active (timer-driven). When nobody is connected, it may deactivate. An Orleans **reminder** wakes it for the next scheduled event. |
| SRV-005 | Per-nation deltas are filtered by `Visibility` **inside** the grain. The gateway never sees unfiltered state. |
| SRV-006 | Grain calls between matches are forbidden (matches are isolated). Cross-match effects go through `PlayerGrain` or events. |

## 3. Gateway

- WebSocket endpoint `/v1/ws`, authenticated with a War Room access token in the first message (not the URL).
- Per-connection **outbound queue** with backpressure. Slow clients get coalesced deltas, and are disconnected if they fall more than 30 s behind.
- **Rate limits** (Valkey token bucket): 20 commands/s burst, 5/s sustained per player; chat 1 msg/s.
- Meta HTTP API (`/v1/...`) per OpenAPI: profile, matches list, lobby, store catalog, receipts, settings, telemetry ingest.
- Health: `/healthz` (liveness), `/readyz` (Orleans client connected, DB reachable).

## 4. Workers and async messaging

| Queue | Producer | Consumer | Purpose |
| --- | --- | --- | --- |
| `wr-<env>-notifications` | grains | NotificationWorker | Push via FCM, with preferences and quiet hours |
| `wr-<env>-receipts` | Gateway | ReceiptWorker | App Store / Play validation, entitlement grant |
| `wr-<env>-match-ended` | MatchGrain | RatingWorker, AnalyticsWorker | Ratings, season progress, archive replay |
| `wr-<env>-account-deletion` | Gateway | DeletionWorker | GDPR erasure workflow |

All messages are JSON with a `type`, `version`, `id` and `occurred_at` envelope (schemas in `shared/contracts/messages/`). Consumers are idempotent.

## 5. Configuration

- Static config: environment variables (12-factor), documented in `server/README.md` and each environment manifest.
- Remote config and flags: AppConfig (ADR-0020). Matches pin config at creation.
- Secrets: Secrets Manager, injected as ECS secrets.

## 6. Admin and debug API (AI-first)

| Endpoint | dev/staging | prod |
| --- | --- | --- |
| `GET /admin/v1/matches?status=active` | yes | yes (read-only) |
| `GET /admin/v1/matches/{id}/state?nation=` | full state JSON | redacted, audited |
| `GET /admin/v1/matches/{id}/replay` | snapshot + log bundle | audited, PII-stripped |
| `POST /admin/v1/matches/{id}/commands` | inject commands for testing | **disabled** |
| `POST /admin/v1/time/advance` | fast-forward a match | **disabled** |
| `GET /admin/v1/players/{id}` | yes | PII-redacted |

The OpenAPI spec lives at `shared/contracts/openapi/admin-api.v1.yaml` so agents can discover it.
