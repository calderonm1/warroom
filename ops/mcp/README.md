# MCP servers for AI agents

[`mcp.example.json`](mcp.example.json) is a Cursor-compatible MCP configuration (`.cursor/mcp.json` format). Copy it to `.cursor/mcp.json` (gitignored) or into your user-level Cursor config and fill in the profiles and tokens. **Never commit real tokens.**

| Server | Purpose | Credentials | Safe default |
| --- | --- | --- | --- |
| `aws` (official AWS MCP server) | Read AWS resources, docs, CLI-equivalent calls | `AWS_PROFILE=wr-dev-agent` (switch per env) | agent roles are read-only outside dev (ADR-0018) |
| `cloudwatch` (awslabs CloudWatch MCP) | Logs Insights, alarms, metrics analysis | same profile | `CloudWatchReadOnlyAccess` |
| `sentry` | Crash and error triage | Sentry auth token (read scopes) | read-only token |
| `github` | Issues, PRs, Projects | fine-grained PAT | repo-scoped |
| `unity` (Unity CLI MCP) | Drive the Unity Editor: console, scenes, tests, builds | local only | approve connection in the Editor |

Setup notes:

- AWS: configure SSO profiles per [AWS accounts and access](../../docs/06-environments/aws-accounts-and-access.md). Agent profiles assume `wr-agent-readonly` (staging, prod) or `wr-agent-deployer` (dev).
- Unity: install the Unity CLI, run `unity pipeline install` in `client/`, then `unity mcp configure cursor` and `unity skill install cursor`. Agents that can run shell commands should prefer `unity command` / `unity eval` (faster, fewer tokens).
- The example's `aws` entry uses `awslabs.aws-api-mcp-server` with `READ_OPERATIONS_ONLY=true`. AWS Labs marks it as superseded by the official AWS MCP server, so migrate the entry when setting up (story `ST-01.3.3`).
- MCP package names and versions change often. Verify them against the official docs when setting up.
