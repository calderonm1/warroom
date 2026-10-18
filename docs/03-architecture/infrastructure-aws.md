---
title: Infrastructure (AWS)
status: accepted
owner: architecture
last_reviewed: 2026-10-18
related: [ADR-0007, ADR-0008, ADR-0018, EP-03, docs/06-environments/README.md]
---

# Infrastructure (AWS)

## 1. Accounts (AWS Organizations)

| Account | Purpose | Notes |
| --- | --- | --- |
| `warroom-management` | Organizations, billing, IAM Identity Center, SCPs | No workloads |
| `warroom-shared` | ECR, Route 53 public zones, CI artifact bucket, fastlane match bucket | Read access granted to env accounts |
| `warroom-dev` | Shared cloud dev environment | Scale-to-zero schedules; agents may deploy |
| `warroom-staging` | Production-like, for release candidates and load tests | Same topology as prod, smaller scale |
| `warroom-prod` | Production | Strictest SCPs, no agent writes |

## 2. Network (per env)

- VPC /16 across 3 AZs (2 in dev): public subnets (ALB, NAT), private subnets (ECS tasks), isolated subnets (Aurora, Valkey).
- VPC endpoints for S3, ECR, CloudWatch Logs, Secrets Manager, SQS (cuts NAT cost).
- Dev uses a single NAT gateway (or NAT instance); prod uses one per AZ.

## 3. Compute (ECS on Fargate, Graviton/arm64)

| Service | Dev | Staging | Prod (launch) |
| --- | --- | --- | --- |
| gateway | 1 × 0.5 vCPU | 2 × 1 vCPU | 3+ × 2 vCPU, autoscale on connections |
| silo | 1 × 1 vCPU | 2 × 2 vCPU | 3+ × 4 vCPU, autoscale on CPU and activations |
| workers | 1 × 0.25 vCPU | 1 × 0.5 vCPU | 2+ × 1 vCPU, autoscale on queue depth |
| admin | 1 × 0.25 vCPU (internal ALB) | same | same |

Orleans silo-to-silo traffic uses a private service-discovery namespace (Cloud Map) and the Postgres membership table.

## 4. Data

| Resource | Dev | Staging | Prod |
| --- | --- | --- | --- |
| Aurora PostgreSQL Serverless v2 | 0 to 2 ACU (auto-pause) | 0.5 to 8 ACU | 2 to 64 ACU, Multi-AZ reader |
| ElastiCache Valkey serverless | min | min | scaled |
| S3 buckets | `wr-<env>-snapshots`, `wr-<env>-replays`, `wr-<env>-analytics`, `wr-<env>-content` | | |

## 5. Edge

- Route 53: `api.<env>.<domain>` (ALB), `cdn.<env>.<domain>` (CloudFront), prod drops the env label.
- ACM certificates, WAF managed rule groups plus rate-based rules on ALB, Shield Standard.

## 6. Cost guardrails

| ID | Guardrail |
| --- | --- |
| COST-001 | AWS Budgets per account with alerts at 50/80/100% (dev $150/mo, staging $300/mo initial; prod set at beta) |
| COST-002 | Dev and staging ECS services scale to 0 outside 07:00 to 24:00 owner local time (EventBridge Scheduler) unless the `keep-alive` tag is set |
| COST-003 | Aurora auto-pause in dev |
| COST-004 | Cost allocation tags required (`project`, `env`, `component`) |
| COST-005 | Monthly cost report artifact (Cost Explorer API → JSON) for agent review |

## 7. Tagging (mandatory)

`project=warroom`, `env=<dev|staging|prod>`, `component=<gateway|silo|...>`, `managed_by=terraform`, `owner=<handle>`, `story=<ST-id that created it>`.
