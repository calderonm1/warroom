---
title: "ADR-0014: Backlog as code (YAML) with one-way sync to GitHub Projects"
status: accepted
owner: product
last_reviewed: 2026-10-18
related: [BR-009, backlog/README.md, ADR-0015]
---

# ADR-0014: Backlog as code with GitHub Projects sync

- **Date:** 2026-10-18
- **Deciders:** project owner

## Context

Agents need the backlog in the repo, versioned with code, with structured acceptance criteria and links to docs. Humans want a board view (BR-009).

## Decision

1. The backlog lives in `backlog/epics/EP-NN-<slug>.yaml`, one file per epic containing its features and stories, validated against `backlog/schema/backlog.schema.json`.
2. IDs: `EP-NN`, `FE-NN.N`, `ST-NN.N.N`. They are permanent and never reused.
3. `backlog/INDEX.md` is **generated** (`make backlog-index`) and CI checks it is fresh.
4. **One-way sync** (repo → GitHub): `tools/backlog sync-github` creates or updates one GitHub Issue per story (and per epic), adds them to a Projects (v2) board, and sets fields `Status`, `Priority`, `Size`, `Milestone`, `Epic`, `Type`. Issues carry a hidden marker `<!-- warroom-backlog-id: ST-… -->`.
5. Changes made on the board are **not** synced back. The board shows a banner field "Edit in repo". Status changes come from commits and PRs that update the YAML.
6. The sync runs in CI on pushes to `main` that touch `backlog/`, and manually via `make backlog-sync`.

## Alternatives considered

| Option | Why not |
| --- | --- |
| GitHub Issues as the source of truth | Agents need API calls to read; weak structure; not versioned with code |
| Two-way sync | Conflict resolution complexity; split brain |
| Linear / Jira | Extra tool; same split-source problem |

## Consequences

Humans edit in the repo, which is simple when solo. If a team grows, revisit two-way sync for status only.

## Compliance

`make backlog-validate` (schema, unique IDs, dependency integrity, no cycles, doc links exist) and an index freshness check run in CI.
