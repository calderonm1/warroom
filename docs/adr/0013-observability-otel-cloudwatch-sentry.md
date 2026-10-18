---
title: "ADR-0013: Observability and analytics: OpenTelemetry, CloudWatch, Sentry, Firehose to Athena"
status: accepted
owner: architecture
last_reviewed: 2026-10-18
related: [ADR-0018, docs/03-architecture/observability-and-analytics.md, docs/05-conventions/logging-and-errors.md]
---

# ADR-0013: Observability and analytics

- **Date:** 2026-10-18
- **Deciders:** project owner

## Context

A solo developer needs to detect and diagnose issues fast, and AI agents need machine-readable, queryable telemetry (via MCP) to investigate. Product decisions need gameplay analytics without the cost of a commercial analytics suite.

## Decision

1. **Server telemetry:** OpenTelemetry SDK for .NET (traces, metrics, logs). Exported through the AWS Distro for OpenTelemetry (ADOT) collector sidecar to **CloudWatch Logs**, **CloudWatch Metrics** (EMF) and **X-Ray**.
2. **Structured JSON logs only**, with mandatory fields (see [logging and errors](../05-conventions/logging-and-errors.md)).
3. **Errors and crashes:** **Sentry** for client (Unity SDK: native crashes, ANRs, exceptions) and server exceptions, with release health. The Sentry MCP is available to agents.
4. **Product analytics:** the client and server emit `wr.*` events (schema-registered) to the Gateway's `/v1/telemetry` endpoint, then **Kinesis Data Firehose**, then S3 (Parquet, partitioned by date and event), queried by **Athena**. Dashboards in **Amazon Managed Grafana** or QuickSight (decided in `ST-20.4.1`).
5. Event schemas are registered in `shared/contracts/telemetry/events.yaml` and validated in CI.

## Alternatives considered

| Option | Why not |
| --- | --- |
| Datadog / New Relic | Excellent, but expensive at scale for a solo budget |
| Firebase Crashlytics + Analytics | Free, but splits telemetry across clouds; weak server story |
| GameAnalytics / Unity Analytics | Vendor-owned data; limited raw access for agents |

## Consequences

Low cost, raw data ownership, and agent-queryable telemetry (CloudWatch MCP, Athena SQL). Some dashboard building effort.

## Compliance

Logging lint (`ST-20.1.2`) rejects unstructured logs on the server. Telemetry event schema validation runs in CI.
