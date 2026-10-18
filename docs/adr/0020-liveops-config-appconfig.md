---
title: "ADR-0020: Remote config and feature flags via AWS AppConfig"
status: accepted
owner: architecture
last_reviewed: 2026-10-18
related: [ADR-0010, docs/03-architecture/server-runtime.md, docs/02-game-design/progression-and-seasons.md]
---

# ADR-0020: Remote config and feature flags via AWS AppConfig

- **Date:** 2026-10-18
- **Deciders:** project owner

## Context

Live ops needs to tune balance, toggle features, run events, and configure queues (for example, enabling or disabling casual Logistics Boost) without client releases, with safe rollout and instant rollback.

## Decision

1. **AWS AppConfig** (feature flags and freeform JSON configurations, validated by JSON Schema) is the remote config system. Deployment strategies: linear rollout with CloudWatch alarm-based rollback.
2. The server reads AppConfig through the AppConfig Agent sidecar. **The client never talks to AppConfig directly**: the server delivers the relevant client config in the session bootstrap message, signed and versioned.
3. **Balance changes to running matches are forbidden.** A match pins its content pack version and balance config at creation. New config applies to new matches only.
4. Local dev uses a file-backed implementation of `IFeatureFlags` / `IRemoteConfig`.

## Alternatives considered

| Option | Why not |
| --- | --- |
| LaunchDarkly / Statsig | Excellent, but cost at scale; another vendor |
| Unity Remote Config | Client-centric; engine-vendor lock-in |
| Config in the database with a custom admin UI | Reinventing safe rollout and rollback |

## Consequences

Running matches are stable and reproducible. Live ops tooling builds on AppConfig plus an admin UI later (`EP-22`).

## Compliance

Unit tests assert that `MatchGrain` loads config only at creation. Schema validation of config documents runs in CI.
