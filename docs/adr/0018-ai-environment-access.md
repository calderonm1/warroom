---
title: "ADR-0018: AI-first environment access (manifests, read-only agent roles, MCP, replays)"
status: accepted
owner: architecture
last_reviewed: 2026-10-18
related: [BR-008, NFR-OPS-001, R-CLD-05, R-ENG-04, docs/06-environments/ai-environment-access.md]
---

# ADR-0018: AI-first environment access

- **Date:** 2026-10-18
- **Deciders:** project owner

## Context

The project must be designed so AI agents can access and interpret environments easily (BR-008), without putting production at risk.

## Decision

1. **Environment manifests:** each environment has `ops/environments/<env>.yaml` (schema-validated) describing its purpose, AWS account and region, endpoints, log groups, dashboards, alarms, data classification, and the agent policy.
2. **Agent IAM roles** per account, assumable through IAM Identity Center or CI OIDC:
   - `wr-agent-readonly`: read-only (`ReadOnlyAccess` minus data-plane reads of PII tables and secrets), plus CloudWatch Logs Insights and Athena query on anonymized views.
   - `wr-agent-deployer` (**dev only**): may deploy ECS services and apply Terraform in dev.
   - Prod has no agent write role. Service Control Policies deny agent roles any `Put/Delete/Update` in prod.
3. **MCP servers** configured in `ops/mcp/`: the official AWS MCP server and the CloudWatch MCP server (with the read-only profile), Sentry MCP, GitHub MCP, Unity CLI MCP.
4. **Debug surfaces built into the product:**
   - Admin/debug API (`/admin/v1/...`, OpenAPI documented). Full in dev and staging; read-only and audited in prod.
   - Match **replay export**: any match can be exported (snapshot plus command log) and replayed locally with `make replay MATCH=<id> ENV=<env>`.
   - `make env-status ENV=<env>` prints JSON health, version and recent error summaries.
5. **Telemetry conventions** (ADR-0013) ensure every log and trace carries `env`, `service`, `version`, `match_id`, `trace_id`, so agents can correlate.

## Alternatives considered

| Option | Why not |
| --- | --- |
| Agents use the owner's admin credentials | Unsafe; no audit separation |
| No agent access to cloud | Wastes the main productivity lever for debugging and ops |

## Consequences

Some upfront IAM and tooling work (`EP-03`, feature `FE-03.5`). In return, agents can safely investigate production issues end to end.

## Compliance

IAM Access Analyzer and an SCP test (`ST-03.5.3`) verify that the agent roles cannot write in prod. Manifests are validated by `make ops-validate`.
