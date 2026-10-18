---
title: Data and persistence
status: accepted
owner: architecture
last_reviewed: 2026-10-18
related: [ADR-0016, EP-06, docs/05-conventions/naming.md]
---

# Data and persistence

## 1. Stores

| Store | Data | Durability |
| --- | --- | --- |
| Aurora PostgreSQL | players, identities, devices, entitlements, purchases, matches, match_nation, command log, snapshot index, ratings, chat archive, Orleans tables | Multi-AZ, PITR 14 days (prod), daily snapshots |
| S3 | match snapshots, replays, analytics Parquet, content bundles, DB exports | Versioned, lifecycle-managed |
| Valkey | presence, rate limits, token revocation, short caches | Ephemeral, rebuildable |

## 2. Core schema (initial)

| Table | Key columns | Notes |
| --- | --- | --- |
| `player` | `player_id uuid pk`, `display_name`, `created_at`, `status`, `country_code`, `deleted_at` | No email here |
| `player_identity` | `player_id`, `provider` (`guest`/`apple`/`google`/`email`), `subject`, `linked_at` | unique (provider, subject) |
| `device` | `device_id`, `player_id`, `platform`, `push_token`, `last_seen_at` | |
| `match` | `match_id`, `map_id`, `content_pack_version`, `config_version`, `queue_id`, `speed_tier`, `status`, `seed`, `created_at`, `started_at`, `ended_at` | |
| `match_nation` | `match_id`, `nation_id`, `player_id null`, `controller` (`player`/`ai`/`neutral`), `coalition_id`, `joined_at`, `left_at` | |
| `match_command_log` | `match_id`, `seq bigint`, `game_time bigint`, `nation_id`, `client_command_id uuid`, `payload bytea`, `received_at` | pk (match_id, seq); partitioned by month |
| `match_snapshot` | `match_id`, `seq`, `game_time`, `s3_key`, `state_hash`, `created_at` | |
| `entitlement` | `player_id`, `sku`, `source`, `granted_at`, `expires_at` | |
| `purchase` | `purchase_id`, `player_id`, `store`, `store_transaction_id`, `sku`, `status`, `raw_receipt_ref` | |
| `rating` | `season_id`, `player_id`, `mu`, `phi`, `sigma`, `matches` | Glicko-2 |
| `chat_message` | `channel_id`, `message_id`, `sender_player_id`, `body`, `created_at`, `moderation_state` | 90-day retention |

## 3. Event sourcing details

1. A command is accepted, then the log row is inserted (one round trip, batched up to 5 ms), then applied, then acknowledged.
2. Scheduled events are **not** logged. They are re-derived deterministically from the state plus the command log.
3. Snapshot cadence: every 6 game-hours, plus on deactivation. The snapshot key format is `snapshots/<match_id>/<seq>.wrsnap.zst`.
4. Recovery: load the latest snapshot whose `state_hash` verifies, then replay log rows with `seq > snapshot.seq`.
5. Match end: final snapshot plus full log, then a replay bundle in `replays/<yyyy>/<mm>/<match_id>.wrreplay`, with the log partition rows kept for 180 days.

## 4. Migrations

- Forward-only migrations. No destructive change without a two-phase (expand/contract) plan noted in the PR.
- Migrations run in CI against an ephemeral Postgres (Testcontainers) and in each environment via the Migrator task before services deploy.

## 5. Data classification

| Class | Examples | Rules |
| --- | --- | --- |
| C1 Secret | signing keys, store credentials | KMS / Secrets Manager only |
| C2 Personal | email (Cognito only), device IDs, IP, push tokens, chat | Encrypted at rest; agents read only via redacted views |
| C3 Gameplay | match state, command logs (pseudonymous player IDs) | Agents may read in all envs |
| C4 Public | leaderboards, display names | — |
