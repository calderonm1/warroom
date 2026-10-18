---
title: "ADR-0016: Data storage: PostgreSQL (Aurora), Valkey, S3; event-sourced match persistence"
status: accepted
owner: architecture
last_reviewed: 2026-10-18
related: [ADR-0004, ADR-0005, NFR-AVAIL-001, docs/03-architecture/data-and-persistence.md]
---

# ADR-0016: Data storage

- **Date:** 2026-10-18
- **Deciders:** project owner

## Context

Matches must not lose state on node failure (NFR-AVAIL-001) and must be replayable (ADR-0005). Meta data (players, entitlements, ratings, lobbies) is relational. Hot ephemeral data (presence, rate limits, recent chat) needs a fast cache.

## Decision

1. **PostgreSQL** (Aurora PostgreSQL Serverless v2 in AWS; PostgreSQL 17 locally) is the system of record for meta data, Orleans clustering, grain state and **match command logs**.
2. **Match persistence is event-sourced:** every accepted command is appended to `match_command_log` (match_id, seq, game_time, nation_id, payload, server_received_at) **before** it is acknowledged. Full **snapshots** are written to S3 every N game-hours and on deactivation, and indexed in `match_snapshot`.
3. **Valkey** (ElastiCache serverless) holds presence, rate-limit counters, session revocation lists and short-lived caches. It is never the only copy of important data.
4. **S3** stores snapshots, replays, analytics (Parquet), content bundles and backups. Lifecycle rules: replays to Glacier after 90 days; analytics retention per the privacy policy.
5. Schema migrations: EF Core migrations (or plain SQL via a migration tool chosen in `ST-06.4.1`), applied by a one-shot ECS task in CI before deploy.
6. Naming: `snake_case` tables and columns, singular table names (see [naming](../05-conventions/naming.md)).

## Alternatives considered

| Option | Why not |
| --- | --- |
| DynamoDB | Great scale, but relational meta queries and Orleans providers favour Postgres; less portable locally |
| Redis (OSS) | Licensing changes; Valkey is the open fork supported by ElastiCache |
| State-only persistence (no command log) | Loses replays and debugging; weaker durability story |

## Consequences

Event sourcing adds storage volume: roughly 1 to 5 MB per match for commands, plus snapshots. That is cheap at S3 and Aurora prices.

## Compliance

Integration tests kill a silo mid-match and assert state is restored with no lost acknowledged commands (`ST-06.3.4`).
