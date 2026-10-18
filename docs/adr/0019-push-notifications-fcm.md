---
title: "ADR-0019: Push notifications via Firebase Cloud Messaging (HTTP v1) for iOS and Android"
status: accepted
owner: architecture
last_reviewed: 2026-10-18
related: [PR-003, docs/02-game-design/core-loop.md, docs/03-architecture/server-runtime.md]
---

# ADR-0019: Push notifications via FCM

- **Date:** 2026-10-18
- **Deciders:** project owner

## Context

Push notifications are core to check-in play (PR-003): "Your army arrived", "Under attack", "Research complete". Both platforms must be supported, with per-category opt-in and quiet hours.

## Decision

1. The backend sends pushes through **Firebase Cloud Messaging HTTP v1** for both Android and iOS (FCM relays to APNs using an APNs auth key).
2. Only the Firebase Messaging SDK is used in the client. No Firebase Analytics, to keep telemetry in one place (ADR-0013).
3. A `NotificationWorker` consumes `notification.requested` messages from SQS, applies per-player preferences, quiet hours, dedup and rate limits, then sends.
4. Web push (for the future web client) goes through the same FCM integration.

## Alternatives considered

| Option | Why not |
| --- | --- |
| Amazon SNS mobile push | Works, but less ergonomic token management and fewer client SDK features |
| Direct APNs + FCM | Two integrations for no gain |
| OneSignal | Another vendor holding player data |

## Consequences

One small Google dependency. Push tokens are stored in Postgres keyed by player and device.

## Compliance

Integration test with the FCM dry-run (`validate_only`) mode in CI (`ST-19.2.2`).
