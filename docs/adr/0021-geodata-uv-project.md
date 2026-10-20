---
title: "ADR-0021: Separate uv project for the geodata pipeline"
status: accepted
owner: architecture
last_reviewed: 2026-10-20
related: [ADR-0015, ST-10.1.1, docs/03-architecture/geodata-pipeline.md, tools/geodata/README.md]
---

# ADR-0021: Separate uv project for the geodata pipeline

- **Date:** 2026-10-20
- **Deciders:** project owner (via ST-10.1.1)
- **Supersedes:** [ADR-0015](0015-repo-tooling-python-uv.md)

## Context

ADR-0015 put repo tooling and the geodata pipeline in one uv project with `pyproject.toml` and `uv.lock` at the repo root. ST-10.1.1 requires `tools/geodata` to be its own uv project with its own lockfile. GIS libraries (shapely, pyproj, geopandas) are large and must not enter the lightweight repo-tooling environment that `make check` uses on every change.

## Decision

1. Repo tooling stays the uv project at the repository root (`pyproject.toml`, `uv.lock`, package `warroom_tools`).
2. The geodata pipeline is a separate uv project at `tools/geodata` (`pyproject.toml`, `uv.lock`, package `warroom_geodata`). GIS dependencies are added there, and only there, when a pipeline stage needs them.
3. Both projects use Python 3.12+, ruff, and pytest. `make check` runs both.
4. Game runtime code is never Python. Python is tooling only.
5. Commands that agents consume accept `--json`.
6. Geodata downloads are listed only in `tools/geodata/sources.lock.yaml`. Bytes are stored under `artifacts/geodata/raw/<sha256>/<filename>` only after SHA-256 matches. Cache hits are hashed again before use. URLs and redirects must stay on HTTPS.

Rules 4 and 5 restate ADR-0015. Rule 1 narrows ADR-0015's single-project rule to repo tooling. Rules 2 and 6 are the geodata split.

## Alternatives considered

| Option | Why not |
| --- | --- |
| One root uv project, as ADR-0015 first stated | Conflicts with ST-10.1.1 and pulls GIS packages into every tooling install |
| uv workspace with one lockfile | A workspace has a single lockfile, so `tools/geodata` would not have its own lockfile |

## Consequences

Two Python environments to sync (`make setup` does both). Geodata can gain heavy native dependencies without slowing backlog and docs checks.

## Compliance

`make check` runs ruff and pytest in the root project and in `tools/geodata`. `tests/test_sources.py` covers cache hits, hash mismatches, and manifest rejection.
