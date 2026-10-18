---
title: Development conventions overview
status: accepted
owner: engineering
last_reviewed: 2026-10-18
related: [AGENTS.md, BR-010]
---

# Development conventions

Conventions are binding (rank 2 in the [source-of-truth hierarchy](../../AGENTS.md#2-source-of-truth-hierarchy)). Each rule has an ID `CONV-<AREA>-NNN`. Where possible, a rule is enforced by tooling. The **Enforced by** column says how, and "review" means a human or agent reviewer checks it.

| Doc | Area code | Covers |
| --- | --- | --- |
| [naming.md](naming.md) | NAME | Files, code, contracts, DB, cloud, content IDs, telemetry, branches |
| [csharp-style.md](csharp-style.md) | CS | C# style, analyzers, nullability, async, errors |
| [unity.md](unity.md) | UNITY | Project structure, assemblies, assets, UI Toolkit, performance |
| [server.md](server.md) | SRV | ASP.NET Core and Orleans patterns |
| [api-and-contracts.md](api-and-contracts.md) | API | Protobuf, OpenAPI, versioning, errors |
| [testing.md](testing.md) | TEST | Test pyramid, naming, coverage, determinism tests |
| [git-and-review.md](git-and-review.md) | GIT | Branches, commits, PRs, reviews, releases |
| [documentation.md](documentation.md) | DOC | Front matter, IDs, structure, ADRs |
| [logging-and-errors.md](logging-and-errors.md) | LOG | Structured logs, error codes, tracing |
| [security-and-privacy.md](security-and-privacy.md) | SEC | Secrets, PII, dependencies |
| [ai-agent-workflow.md](ai-agent-workflow.md) | AI | How agents plan, execute, verify and hand off |
