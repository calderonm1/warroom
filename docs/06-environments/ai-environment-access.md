---
title: AI environment access
status: accepted
owner: ops
last_reviewed: 2026-10-18
related: [ADR-0018, ops/environments/dev.yaml, ops/mcp/README.md, EP-03]
---

# AI environment access

How AI agents discover, observe and (in dev) change environments, safely.

## 1. Discovery: environment manifests

Each environment has [`ops/environments/<env>.yaml`](../../ops/environments/), validated against [`schema.json`](../../ops/environments/schema.json). An agent should read the manifest **first**. Key sections:

| Section | Contents |
| --- | --- |
| `aws` | account alias and ID, region, CLI profile for agents |
| `endpoints` | gateway WS, meta API, admin API, CDN |
| `observability` | log groups, dashboards, alarms, Sentry project, Athena database |
| `data` | data classification present, redacted views for agents |
| `agent_policy` | `can_read`, `can_deploy`, `can_apply_infra`, `can_run_admin_writes`, notes |
| `runbooks` | links to runbooks for common operations |

## 2. Permissions matrix

| Capability | local | dev | staging | prod |
| --- | --- | --- | --- | --- |
| Read logs, metrics, traces | ✅ | ✅ | ✅ | ✅ (PII-redacted log groups) |
| Query Athena analytics | ✅ | ✅ | ✅ | ✅ (anonymized views) |
| Admin API reads | ✅ | ✅ | ✅ | ✅ redacted, audited |
| Admin API writes (inject commands, advance time) | ✅ | ✅ | ❌ | ❌ |
| Deploy services | ✅ | ✅ | ❌ (CI + approval) | ❌ |
| Terraform plan | ✅ | ✅ | ✅ | ✅ |
| Terraform apply | ✅ | ✅ | ❌ | ❌ |
| Read secret values | n/a | ❌ | ❌ | ❌ |

## 3. Tools available to agents

| Tool | How | Notes |
| --- | --- | --- |
| AWS MCP server / AWS CLI | profile `wr-<env>-agent` | read-only except dev |
| CloudWatch MCP server | same profile | logs insights, alarms, metrics |
| Sentry MCP | Sentry org token (read) | crash triage |
| GitHub MCP | repo token | issues, PRs, Projects |
| Unity CLI / `unity mcp` | local Editor | scene, console, tests, builds |
| `make env-status ENV=<env>` | repo tooling (`ST-03.5.4`) | JSON health summary |
| `make replay MATCH=<id> ENV=<env>` | repo tooling (`ST-06.5.2`) | downloads replay bundle; runs it locally with hash checks |
| `make logs ENV=<env> SERVICE=<svc> SINCE=1h` | repo tooling (`ST-03.5.4`) | wraps Logs Insights with JSON output |

## 4. Investigation playbook (for agents)

1. Read `ops/environments/<env>.yaml` and the runbook for the symptom.
2. `make env-status ENV=<env>`: versions, health, active alarms.
3. Query logs by `trace_id`, `match_id` or `error_code`. Check Sentry for client crashes in the same release.
4. If sim-related: export the replay, reproduce locally, and write a failing golden test.
5. Fix in a branch. Deploy to dev. Verify. Open a PR with evidence (queries, outputs).
