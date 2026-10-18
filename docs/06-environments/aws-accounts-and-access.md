---
title: AWS accounts and access
status: review
owner: ops
last_reviewed: 2026-10-18
related: [ADR-0007, ADR-0018, docs/03-architecture/infrastructure-aws.md, EP-03]
---

# AWS accounts and access

## 1. Bootstrap order (EP-03, feature FE-03.1)

1. Create (or reuse) a management account; enable **AWS Organizations** and **IAM Identity Center**. Enable MFA on root; store root credentials offline.
2. Create the accounts `warroom-shared`, `warroom-dev`, `warroom-staging`, `warroom-prod` via Terraform in `infra/org/` (or the console once, then import).
3. In each account, run `infra/bootstrap/` with admin SSO: S3 state bucket, GitHub OIDC provider, `wr-<env>-github-plan` (read-only plan) and `wr-<env>-github-deploy` roles, agent roles.
4. Apply SCPs: region allow-list (us-east-1 plus future regions), deny leaving the org, deny disabling CloudTrail, and deny agent roles write access in prod.
5. Budgets and cost anomaly detection per account.

## 2. Human access

| Permission set | Accounts | Notes |
| --- | --- | --- |
| `WarRoomAdmin` | all | Owner only; MFA; session 4 h |
| `WarRoomDeveloper` | dev (admin-ish), staging (read + ECS exec), prod (read) | future collaborators |
| `WarRoomReadOnly` | all | auditors, support |

CLI profiles (`~/.aws/config`): `wr-dev`, `wr-staging`, `wr-prod` (SSO), plus `wr-dev-agent`, `wr-staging-agent`, `wr-prod-agent` assuming the agent roles.

## 3. Agent access

See [AI environment access](ai-environment-access.md).
