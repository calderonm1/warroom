# ops/: environments and agent access

| Path | Purpose |
| --- | --- |
| [`environments/`](environments/) | One YAML manifest per environment: what it is, where it runs, how to observe it, what agents may do there. Validated by `make ops-validate` against [`environments/schema.json`](environments/schema.json). |
| [`mcp/`](mcp/README.md) | MCP server configuration for AI agents (AWS, CloudWatch, Sentry, GitHub, Unity CLI) |

Values marked `TBD` are filled in by the infrastructure stories that create them (see `EP-03`). The manifests are the contract between infrastructure and agents. If you change infrastructure, update the manifest in the same commit.
