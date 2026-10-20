---
title: Documentation index
status: accepted
owner: architecture
last_reviewed: 2026-10-20
related: [AGENTS.md, docs/05-conventions/documentation.md]
---

# War Room documentation

This is the entry point for humans and AI agents. **Every doc in `docs/` must be linked from this page** (CONV-DOC-002; enforced by `make docs-check`).

Precedence when docs disagree: ADRs > conventions > technical design (TDD) and game design (GDD) > backlog > code. See [AGENTS.md](../AGENTS.md).

## Reading paths

| If you are... | Read in this order |
| --- | --- |
| An agent starting a story | [AGENTS.md](../AGENTS.md) → the story's `docs` links → [conventions](05-conventions/README.md) → [AI agent workflow](05-conventions/ai-agent-workflow.md) |
| Working on gameplay rules | [GDD overview](02-game-design/README.md) → [simulation design](03-architecture/simulation.md) |
| Working on infrastructure | [ADR-0007](adr/0007-cloud-aws.md) → [infrastructure](03-architecture/infrastructure-aws.md) → [environments](06-environments/README.md) |
| Working on client UI | [design system](04-ux/design-system.md) → [HUD and screens](04-ux/hud-and-screens.md) → [Unity conventions](05-conventions/unity.md) |
| New to the project | [vision](00-product/vision.md) → [product brief](00-product/product-brief.md) → [roadmap](07-planning/roadmap.md) |

## 00 — Product

- [Product vision](00-product/vision.md)
- [Product brief (confirmed requirements)](00-product/product-brief.md)
- [Glossary](00-product/glossary.md)
- [Naming, brand and identifiers](00-product/naming-and-brand.md)

## 01 — Research

- [Market and technology research (October 2026)](01-research/2026-10-market-research.md)

## 02 — Game design (GDD)

- [GDD overview](02-game-design/README.md)
- [Core loop and check-in play](02-game-design/core-loop.md)
- [Match lifecycle, modes, queues and victory](02-game-design/match-lifecycle.md)
- [Map, provinces and territory](02-game-design/map-and-territory.md)
- [Economy, resources, buildings and production](02-game-design/economy.md)
- [Military, movement and combat](02-game-design/military-and-combat.md)
- [Research and doctrines](02-game-design/research.md)
- [Diplomacy, coalitions and chat](02-game-design/diplomacy-and-coalitions.md)
- [Intel and fog of war](02-game-design/intel-and-fog-of-war.md)
- [AI nations and inactivity](02-game-design/ai-nations.md)
- [Progression, ranked, seasons and live ops](02-game-design/progression-and-seasons.md)
- [Monetization design](02-game-design/monetization.md)
- [Onboarding and tutorial](02-game-design/onboarding.md)
- [Content model, packs and sensitivity policy](02-game-design/content-model.md)

## 03 — Technical design (TDD)

- [TDD overview](03-architecture/README.md)
- [Simulation design](03-architecture/simulation.md)
- [Server runtime](03-architecture/server-runtime.md)
- [Networking and protocol](03-architecture/networking-and-protocol.md)
- [Data and persistence](03-architecture/data-and-persistence.md)
- [Globe rendering](03-architecture/globe-rendering.md)
- [Geodata and map content pipeline](03-architecture/geodata-pipeline.md)
- [Client architecture](03-architecture/client-architecture.md)
- [Identity and accounts](03-architecture/identity-and-accounts.md)
- [Infrastructure (AWS)](03-architecture/infrastructure-aws.md)
- [Observability and analytics](03-architecture/observability-and-analytics.md)
- [Security, privacy and anti-cheat](03-architecture/security-and-anti-cheat.md)
- [Scalability and capacity model](03-architecture/scalability-and-capacity.md)

## 04 — UX and design system

- [Design system](04-ux/design-system.md) (tokens in [`design/tokens.json`](../design/tokens.json))
- [HUD and screen inventory](04-ux/hud-and-screens.md)
- [Globe interaction model](04-ux/globe-interaction.md)
- [Accessibility and localization](04-ux/accessibility-and-localization.md)
- [Voice and copy guidelines](04-ux/voice-and-copy.md)

## 05 — Conventions (binding)

- [Conventions overview](05-conventions/README.md)
- [Naming](05-conventions/naming.md)
- [C# style and code rules](05-conventions/csharp-style.md)
- [Unity](05-conventions/unity.md)
- [Server (ASP.NET Core and Orleans)](05-conventions/server.md)
- [API and contracts](05-conventions/api-and-contracts.md)
- [Testing](05-conventions/testing.md)
- [Git, review and release](05-conventions/git-and-review.md)
- [Documentation](05-conventions/documentation.md)
- [Logging, errors and tracing](05-conventions/logging-and-errors.md)
- [Security and privacy](05-conventions/security-and-privacy.md)
- [AI agent workflow](05-conventions/ai-agent-workflow.md)

## 06 — Environments

- [Environments overview](06-environments/README.md) (machine-readable manifests in [`ops/environments/`](../ops/environments/))
- [Local development](06-environments/local-development.md)
- [Device testing (iOS, Android, emulators, device farms)](06-environments/device-testing.md)
- [CI/CD pipelines](06-environments/ci-cd.md)
- [AWS accounts and access](06-environments/aws-accounts-and-access.md)
- [Secrets management](06-environments/secrets.md)
- [AI environment access](06-environments/ai-environment-access.md)

## 07 — Planning

- [Roadmap and milestones](07-planning/roadmap.md)
- [Effort characterization](07-planning/effort.md)
- [Risk register](07-planning/risks.md)
- [Open questions](07-planning/open-questions.md)
- Backlog: [`backlog/README.md`](../backlog/README.md) and the generated [`backlog/INDEX.md`](../backlog/INDEX.md)

## Architecture Decision Records

- [ADR index](adr/README.md) and [template](adr/0000-template.md)
- [ADR-0001: Record architecture decisions](adr/0001-record-architecture-decisions.md)
- [ADR-0002: Single monorepo](adr/0002-monorepo-layout.md)
- [ADR-0003: Unity 6 LTS client](adr/0003-client-engine-unity.md)
- [ADR-0004: .NET 10 backend with Orleans](adr/0004-backend-dotnet-orleans.md)
- [ADR-0005: Shared deterministic simulation](adr/0005-shared-deterministic-simulation.md)
- [ADR-0006: Protobuf over WebSocket; HTTP+JSON for meta](adr/0006-protocol-protobuf-websocket.md)
- [ADR-0007: AWS](adr/0007-cloud-aws.md)
- [ADR-0008: Terraform](adr/0008-iac-terraform.md)
- [ADR-0009: Cognito plus guest accounts](adr/0009-identity-cognito-plus-guest.md)
- [ADR-0010: Fair-by-design monetization](adr/0010-monetization-fair-by-design.md)
- [ADR-0011: Match format and content packs](adr/0011-match-format-and-content-packs.md)
- [ADR-0012: Custom globe renderer](adr/0012-globe-rendering-custom.md)
- [ADR-0013: Observability](adr/0013-observability-otel-cloudwatch-sentry.md)
- [ADR-0014: Backlog as code with GitHub Projects sync](adr/0014-backlog-as-code-github-projects.md)
- [ADR-0015: Python and uv tooling (superseded by ADR-0021)](adr/0015-repo-tooling-python-uv.md)
- [ADR-0016: PostgreSQL, Valkey and S3](adr/0016-data-postgres-valkey-s3.md)
- [ADR-0017: GitHub Actions, GameCI and fastlane](adr/0017-ci-cd-github-actions.md)
- [ADR-0018: AI-first environment access](adr/0018-ai-environment-access.md)
- [ADR-0019: Push notifications via FCM](adr/0019-push-notifications-fcm.md)
- [ADR-0020: Remote config via AppConfig](adr/0020-liveops-config-appconfig.md)
- [ADR-0021: Separate uv project for the geodata pipeline](adr/0021-geodata-uv-project.md)
