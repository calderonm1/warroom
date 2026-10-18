---
title: Observability and analytics
status: accepted
owner: architecture
last_reviewed: 2026-10-18
related: [ADR-0013, ADR-0018, EP-20, docs/05-conventions/logging-and-errors.md]
---

# Observability and analytics

## 1. Signals

| Signal | Source | Sink | Retention |
| --- | --- | --- | --- |
| Logs (JSON) | all server processes | CloudWatch Logs `/wr/<env>/<service>` | dev 7 d, staging 14 d, prod 30 d (then S3) |
| Metrics | OTel + EMF | CloudWatch Metrics namespace `WarRoom/<env>` | 15 months |
| Traces | OTel | X-Ray | 30 d |
| Errors/crashes | Sentry SDKs | Sentry project `warroom-client`, `warroom-server` | plan default |
| Product events | client + server `wr.*` | Firehose → S3 Parquet → Athena (`wr_<env>_analytics`) | 25 months, pseudonymous |

## 2. Golden metrics (alarms)

| Metric | Alarm (prod) |
| --- | --- |
| `gateway.connections.active` | anomaly band |
| `command.ack.latency` p95 | > 250 ms for 5 min |
| `command.rejected.rate` | > 5% for 10 min |
| `match.step.duration` p99 | > 50 ms |
| `match.activation.failures` | > 0 in 5 min |
| `match.state_hash.mismatch` | > 0 (page) |
| `db.commandlog.append.latency` p95 | > 50 ms |
| `notifications.send.failure.rate` | > 2% |
| client crash-free sessions (Sentry) | < 99.5% |

## 3. Product analytics events (initial)

| Event | Key properties |
| --- | --- |
| `wr.app.opened` | platform, version, cold/warm, device tier |
| `wr.session.started` / `wr.session.ended` | duration_ms, matches_viewed |
| `wr.tutorial.step_completed` | step_id |
| `wr.match.joined` | match_id, map_id, queue_id, speed_tier, slot_type |
| `wr.match.checkin` | match_id, game_day, minutes_since_last |
| `wr.command.submitted` | command_type (no payload) |
| `wr.match.left` / `wr.match.ended` | reason, rank, vp, days_played |
| `wr.store.viewed` / `wr.purchase.completed` | sku, price_tier, store |
| `wr.notification.opened` | category |

All events share the envelope `{event, event_id, occurred_at, player_id (pseudonymous), session_id, env, app_version, platform}`. Schemas live in `shared/contracts/telemetry/events.yaml`.

## 4. Dashboards (as code)

Dashboards are defined in Terraform (CloudWatch) or as JSON in `ops/dashboards/`, never only in a console, so agents can read them.
