---
title: "ADR-0015: Python (managed by uv) for repo tooling and the geodata pipeline"
status: accepted
owner: architecture
last_reviewed: 2026-10-18
related: [ADR-0014, docs/03-architecture/geodata-pipeline.md, tools/README.md]
---

# ADR-0015: Python with uv for repo tooling

- **Date:** 2026-10-18
- **Deciders:** project owner

## Context

The repo needs scripts for backlog validation, GitHub sync, docs checks, content validation and a geodata pipeline (GIS processing). The GIS ecosystem (shapely, pyproj, geopandas) is Python-first.

## Decision

1. Repo tooling and the geodata pipeline are written in **Python 3.12+**, managed by **uv** (`pyproject.toml` and `uv.lock` at the repo root).
2. Lint and format with **ruff**; test with **pytest**.
3. Game runtime code is never Python. Python is tooling only.
4. All tools expose a CLI with `--json` output where useful, so agents can consume results.

## Alternatives considered

| Option | Why not |
| --- | --- |
| C# (dotnet tools/scripts) | Same language as the game, but weak GIS ecosystem and slower scripting iteration |
| Node/TypeScript | Weak GIS ecosystem |
| Bash | Not maintainable or testable at this complexity |

## Consequences

A third language in the repo (C#, HCL, Python), deliberately limited to tooling.

## Compliance

`make check` runs ruff and pytest for `tools/`.
