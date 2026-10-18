---
title: "ADR-0001: Record architecture decisions"
status: accepted
owner: architecture
last_reviewed: 2026-10-18
related: [docs/05-conventions/documentation.md]
---

# ADR-0001: Record architecture decisions

- **Date:** 2026-10-18
- **Deciders:** project owner

## Context

War Room is built solo with heavy AI assistance over a long horizon. AI agents lack memory between sessions. Without durable, discoverable records of *why* things are the way they are, agents (and future collaborators) will re-litigate or silently contradict past decisions. That is the fastest route to tech debt.

## Decision

1. Significant decisions are recorded as ADRs in `docs/adr/NNNN-kebab-title.md` using [the template](0000-template.md).
2. A decision is "significant" if it affects more than one component, is costly to reverse, introduces a dependency or vendor, or constrains how code must be written.
3. ADR statuses: `draft`, `review`, `accepted`, `superseded`, `deprecated`. Accepted ADRs are immutable except for status, `last_reviewed`, and links. To change a decision, write a new ADR that supersedes it.
4. Each ADR states its **Compliance** mechanism so agents know how it is enforced.
5. [`docs/adr/README.md`](README.md) lists every ADR with its status.

## Alternatives considered

| Option | Why not |
| --- | --- |
| Decisions in a wiki or Notion | Not versioned with code; invisible to agents working in the repo |
| Decisions only in PR descriptions | Not discoverable; no supersession model |

## Consequences

A small writing overhead per decision. In return, agents get a reliable "why" layer, and `AGENTS.md` can rank ADRs as the top source of truth.

## Compliance

`make docs-check` validates ADR front matter and the index. Review checklist item: "Does this change require an ADR?"
