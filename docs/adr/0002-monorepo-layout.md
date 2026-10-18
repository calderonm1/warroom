---
title: "ADR-0002: Single monorepo for game, backend, infra, content and docs"
status: accepted
owner: architecture
last_reviewed: 2026-10-18
related: [AGENTS.md, docs/05-conventions/naming.md]
---

# ADR-0002: Single monorepo

- **Date:** 2026-10-18
- **Deciders:** project owner

## Context

Client and server share simulation code and protocol contracts. Content changes affect both. A solo developer working with AI agents benefits from having every piece of context in one place, with atomic cross-cutting changes.

## Decision

1. One repository, `warroom`, with top-level directories `client/`, `server/`, `shared/`, `content/`, `infra/`, `ops/`, `tools/`, `docs/`, `backlog/` (see [AGENTS.md](../../AGENTS.md#3-repository-map)).
2. Large binary assets use Git LFS ([`.gitattributes`](../../.gitattributes)). Unity assets are force-text serialized.
3. CI runs path-filtered jobs so a docs change does not trigger a Unity build.
4. A change that touches a contract updates both producers and consumers in the same PR.

## Alternatives considered

| Option | Pros | Cons |
| --- | --- | --- |
| Polyrepo (client, server, infra) | Smaller clones, independent permissions | Contract drift, cross-repo PRs, agents lose context |
| Unity Version Control (Plastic) for client | Better large-binary handling | Splits the source of truth; weaker AI and CI tooling integration |

## Consequences

The repo grows large with art. Mitigated by LFS and, if needed later, partial clone or sparse checkout. Revisit if binary assets exceed about 20 GB (story `ST-02.5.4` tracks LFS budget monitoring).

## Compliance

Directory layout is checked by reviewers. CI path filters are defined in `.github/workflows/`.
