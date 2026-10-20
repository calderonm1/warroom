---
title: Security and privacy conventions
status: accepted
owner: engineering
last_reviewed: 2026-10-20
related: [docs/03-architecture/security-and-anti-cheat.md, ADR-0018]
---

# Security and privacy conventions

| ID | Rule | Enforced by |
| --- | --- | --- |
| CONV-SEC-001 | No secrets in the repo. Secret scanning (gitleaks) runs in pre-commit and CI. | pre-commit: [`.pre-commit-config.yaml`](../../.pre-commit-config.yaml) (ST-02.1.2). CI: ST-04.1.5. |
| CONV-SEC-002 | Dependencies are pinned (lockfiles: `uv.lock`, `packages.lock.json`, Unity `packages-lock.json`). Dependabot/Renovate updates weekly. | CI |
| CONV-SEC-003 | New third-party dependency requires a line in the PR: purpose, license, maintenance status. Licenses allowed: MIT, Apache-2.0, BSD, ISC, MPL-2.0, OFL (fonts), Unity Asset Store EULA. GPL/AGPL forbidden in shipped code. | review + license check (`ST-04.1.5`) |
| CONV-SEC-004 | Validate all client input on the server: schema, ranges, ownership, rate. | tests |
| CONV-SEC-005 | Least privilege IAM: one task role per service; no wildcards on actions in prod policies (checkov). | checkov |
| CONV-SEC-006 | PII only in designated tables (C2); access from code goes through `IPersonalDataStore` with audit logging. | review |
| CONV-SEC-007 | Agents use `wr-agent-readonly` for any non-dev environment (ADR-0018). Never paste production data into prompts beyond what redacted views provide. | IAM + review |
| CONV-SEC-008 | Security-relevant changes (auth, payments, IAM, admin API) need the `security` label and an explicit threat check in the PR. | PR template |
| CONV-SEC-009 | Container images: distroless or chiselled .NET base images, non-root user, scanned by ECR enhanced scanning (Inspector). | CI |
