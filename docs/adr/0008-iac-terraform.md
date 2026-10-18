---
title: "ADR-0008: Terraform (OpenTofu-compatible) for infrastructure as code"
status: accepted
owner: architecture
last_reviewed: 2026-10-18
related: [ADR-0007, docs/03-architecture/infrastructure-aws.md, docs/06-environments/README.md]
---

# ADR-0008: Terraform for infrastructure as code

- **Date:** 2026-10-18
- **Deciders:** project owner

## Context

Three cloud environments must be identical in shape, reproducible, reviewable by humans and agents, and cheap to tear down (dev). Agents need to read and propose infra changes reliably.

## Decision

1. All cloud resources are defined in **Terraform** (HCL), kept compatible with **OpenTofu** (no Terraform-Cloud-only features).
2. Layout: `infra/modules/*` (reusable) and `infra/envs/<env>/<stack>` (root modules). Stacks are split by blast radius: `network`, `data`, `compute`, `edge`, `identity`, `observability`, `agent-access`.
3. State: one S3 bucket per account with S3-native lockfiles (`use_lockfile = true`) and versioning enabled.
4. Every PR touching `infra/` gets a `terraform plan` (JSON and text) posted by CI. `apply` to dev runs on merge; staging and prod need manual approval in GitHub Environments.
5. Lint and security: `terraform fmt`, `tflint`, and `checkov` in CI.

## Alternatives considered

| Option | Why not |
| --- | --- |
| AWS CDK (C# or TypeScript) | Same language as the backend is attractive, but synthesized CloudFormation diffs are harder to review; slower deploys; AWS-only |
| CloudFormation directly | Verbose; weaker module ecosystem |
| Pulumi | Smaller ecosystem; state service considerations |

## Consequences

HCL is very well represented in AI training data and `plan -json` output is machine-readable, which makes it ideal for agents. Learning Terraform also complements the AWS certification.

## Compliance

CI blocks merges if `fmt`, `tflint` or `checkov` (high severity) fail. Drift detection runs nightly against staging and prod (`ST-03.4.3`).
