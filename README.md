# War Room

**War Room** is a real-time grand strategy game for iOS and Android, with a planned web client. Matches are played on a fully 3D globe. Players lead modern nations through economy, research, diplomacy and military campaigns in persistent matches that last days to weeks.

> Store name: **War Room: Global Theater**, subtitle **"Real-Time Global Strategy"** (see [naming and brand](docs/00-product/naming-and-brand.md)).
> Everywhere else (repos, cloud resources, code, docs) the product is simply **War Room**, with the short code `wr` and the identifier `warroom`.

This repository is the single source of truth for the game. It holds the design documents, the architecture decision records, the development conventions, the machine-readable backlog, the environment manifests, and (as the backlog is delivered) the client, server and infrastructure code.

The project is **AI-first**: every document, backlog item and environment is structured so an AI coding agent can find it, interpret it and act on it safely. Start with [`AGENTS.md`](AGENTS.md).

## Repository map

| Path | What lives there |
| --- | --- |
| [`AGENTS.md`](AGENTS.md) | Operating manual for AI agents (and humans). Read this first. |
| [`docs/`](docs/README.md) | Product, research, game design (GDD), architecture (TDD), UX, conventions, environments and planning docs |
| [`docs/adr/`](docs/adr/README.md) | Architecture Decision Records: every significant decision, with its rationale |
| [`backlog/`](backlog/README.md) | Epics, features and stories as validated YAML. The source of truth for work. |
| [`ops/`](ops/README.md) | Machine-readable environment manifests (local, dev, staging, prod) and MCP configuration for agents |
| [`tools/`](tools/README.md) | Repo tooling: backlog validator, index generator, GitHub Projects sync, docs checker |
| [`design/`](design/tokens.json) | Design tokens (colours, type, spacing, motion) generated into Unity USS; see the [design system](docs/04-ux/design-system.md) |
| [`.github/`](.github/workflows/repo-checks.yml) | CI workflows (repo checks, backlog sync) and the PR template |
| [`.cursor/rules/`](.cursor/rules/00-project-core.mdc) | Always-on and scoped rules for AI agents in Cursor |
| [`client/`](client/README.md) | Unity 6 mobile client (scaffolded by backlog story `ST-02.3.1`) |
| [`server/`](server/README.md) | .NET 10 backend: gateway, match runtime (Orleans), meta APIs |
| [`shared/`](shared/README.md) | Code shared by client and server: deterministic simulation (`netstandard2.1`, C# 9) and protocol contracts |
| [`content/`](content/README.md) | Data-driven game content: nations, units, research, maps |
| [`infra/`](infra/README.md) | Terraform for AWS accounts and environments |

## Tech stack at a glance

| Layer | Choice | Decision |
| --- | --- | --- |
| Client | Unity 6.3 LTS, URP, UI Toolkit, C# | [ADR-0003](docs/adr/0003-client-engine-unity.md) |
| Shared simulation | Pure C# library, `netstandard2.1`, C# 9, deterministic | [ADR-0005](docs/adr/0005-shared-deterministic-simulation.md) |
| Backend | .NET 10, ASP.NET Core, Microsoft Orleans | [ADR-0004](docs/adr/0004-backend-dotnet-orleans.md) |
| Protocol | Protobuf over WebSocket (real-time); HTTP+JSON with OpenAPI (meta) | [ADR-0006](docs/adr/0006-protocol-protobuf-websocket.md) |
| Cloud | AWS: ECS Fargate, Aurora PostgreSQL, ElastiCache Valkey, S3, CloudFront | [ADR-0007](docs/adr/0007-cloud-aws.md) |
| Infrastructure as code | Terraform (OpenTofu-compatible) | [ADR-0008](docs/adr/0008-iac-terraform.md) |
| Identity | Amazon Cognito (Apple, Google, email) plus first-party guest accounts and War Room session tokens | [ADR-0009](docs/adr/0009-identity-cognito-plus-guest.md) |
| Globe | Custom stylized globe, province ID map rendering, no photoreal tiles | [ADR-0012](docs/adr/0012-globe-rendering-custom.md) |
| Observability | OpenTelemetry, CloudWatch, Sentry | [ADR-0013](docs/adr/0013-observability-otel-cloudwatch-sentry.md) |
| CI/CD | GitHub Actions, GameCI, fastlane | [ADR-0017](docs/adr/0017-ci-cd-github-actions.md) |

The full index is at [docs/adr/README.md](docs/adr/README.md).

## Getting started

Prerequisites: `git`, `make`, and [uv](https://docs.astral.sh/uv/) for repo tooling. Client and server prerequisites are listed in [local development](docs/06-environments/local-development.md).

```bash
make setup     # install repo tooling (Python, via uv)
make check     # validate backlog, docs, and the generated index (same as CI)
make help      # list every task
```

Backlog workflow:

```bash
make backlog-index        # regenerate backlog/INDEX.md after editing backlog YAML
make backlog-next         # list stories that are ready and have no open dependencies
make backlog-sync-plan    # dry run: show what would change in GitHub Projects
```

## Status

The project is in **Milestone M0: Foundation**. Design docs, conventions, ADRs and the backlog are in place. Code scaffolding is the next set of stories. See the [roadmap](docs/07-planning/roadmap.md) and [backlog index](backlog/INDEX.md).
