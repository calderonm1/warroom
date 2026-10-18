---
title: "ADR-0007: AWS as the cloud provider"
status: accepted
owner: architecture
last_reviewed: 2026-10-18
related: [BR-012, R-CLD-01, R-CLD-02, R-CLD-03, docs/03-architecture/infrastructure-aws.md]
---

# ADR-0007: AWS as the cloud provider

- **Date:** 2026-10-18
- **Deciders:** project owner

## Context

The owner prefers AWS (Associate certification in progress) unless it is clearly outclassed (BR-012). AWS is used by 57% of game studios on cloud (R-CLD-01) and offers every primitive needed. Azure PlayFab's default model is client-driven and its parent division is in flux (R-CLD-03). Google Cloud is strong in analytics and AI but offers no decisive advantage for this workload.

## Decision

1. Primary cloud: **AWS**. Initial region **us-east-1**. Additional regions (eu-central-1, ap-northeast-1) are added when latency data justifies them (EP-25).
2. Multi-account via **AWS Organizations**: `warroom-management`, `warroom-shared` (ECR, CI artifacts, DNS), `warroom-dev`, `warroom-staging`, `warroom-prod`. Humans sign in through **IAM Identity Center**. CI uses **GitHub OIDC** roles. No IAM users with long-lived keys.
3. Core services:

   | Need | Service |
   | --- | --- |
   | Containers | ECS on Fargate (Gateway, Silo, Workers) |
   | Load balancing | ALB (WebSocket support, TLS via ACM) |
   | Relational DB | Aurora PostgreSQL Serverless v2 |
   | Cache / rate limits | ElastiCache for Valkey (serverless) |
   | Object storage | S3 (snapshots, replays, telemetry, assets) |
   | CDN | CloudFront (Addressables bundles, web client) |
   | Async jobs | SQS + EventBridge Scheduler |
   | Identity | Cognito (ADR-0009) |
   | Secrets / config | Secrets Manager, SSM Parameter Store, AppConfig (ADR-0020) |
   | Observability | CloudWatch, X-Ray via ADOT (ADR-0013) |
   | Analytics | Firehose → S3 (Parquet) → Athena (ADR-0013) |
   | Edge protection | AWS WAF, Shield Standard |
   | Device testing | AWS Device Farm (supplements local devices) |

4. Use AWS-specific services behind interfaces in code (`IBlobStore`, `ISecretProvider`, `IFeatureFlags`) so local dev and tests run without AWS.
5. Third-party services where clearly better: Sentry (crashes), Firebase Cloud Messaging (push delivery, ADR-0019).

## Alternatives considered

| Option | Why not |
| --- | --- |
| Google Cloud (GKE + Agones, Firebase, BigQuery) | Agones targets session servers; no decisive advantage; owner's skills are AWS |
| Azure + PlayFab | Client-driven default; organizational uncertainty |
| Bare metal / Hetzner | Cheaper compute, but more ops burden for a solo developer; revisit for cost at scale |

## Consequences

Strong alignment with the owner's skills. Some vendor lock-in, contained by interfaces and Terraform. Cost guardrails (AWS Budgets per account, dev scale-to-zero schedules) are mandatory (`ST-03.1.4`).

## Compliance

All resources are created by Terraform (ADR-0008). Service Control Policies block unapproved regions and services. Tags are enforced with AWS Config rules in staging and prod.
