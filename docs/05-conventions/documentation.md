---
title: Documentation conventions
status: accepted
owner: engineering
last_reviewed: 2026-10-18
related: [ADR-0001, AGENTS.md, tools/README.md]
---

# Documentation conventions

## 1. Front matter (required on every `docs/**/*.md`)

```yaml
---
title: Human-readable title
status: draft | review | accepted | superseded | deprecated
owner: product | design | ux | architecture | engineering | ops
last_reviewed: 2026-10-18
related: [ADR-0005, EP-05, docs/03-architecture/simulation.md]
---
```

## 2. Rules

| ID | Rule | Enforced by |
| --- | --- | --- |
| CONV-DOC-001 | Front matter is present and valid. | `make docs-check` |
| CONV-DOC-002 | Every doc is linked from [`docs/README.md`](../README.md). | `make docs-check` |
| CONV-DOC-003 | Relative links resolve. Paths in `related` that look like file paths must exist. | `make docs-check` |
| CONV-DOC-004 | Requirements and rules carry permanent IDs (`GDD-*`, `NFR-*`, `CONV-*`, `SIM-*`, ...). Deprecated rules are struck through and kept, never renumbered. | review |
| CONV-DOC-005 | Prefer tables and numbered rules. One topic per doc; split docs over about 400 lines. | review |
| CONV-DOC-006 | Diagrams in Mermaid (text, diffable, agent-readable). No binary diagrams as the only source. | review |
| CONV-DOC-007 | Docs describe the **current or decided** state. Speculation goes in `open-questions.md` or a `draft` doc. | review |
| CONV-DOC-008 | When code changes behaviour described in a doc, the doc changes in the same PR. | PR template |
| CONV-DOC-009 | `last_reviewed` is updated when a doc is materially reviewed or changed. Docs not reviewed in 180 days are listed by `make docs-stale`. | tooling |
