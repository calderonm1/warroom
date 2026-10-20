# Geodata pipeline

Python 3.12 project for map generation, managed by [uv](https://docs.astral.sh/uv/) in this directory ([ADR-0021](../../docs/adr/0021-geodata-uv-project.md)). It is separate from the root repo-tooling venv so GIS dependencies never land in `warroom-tools`.

Stage 1 (ST-10.1.1) fetches pinned sources and checks SHA-256 before use ([GEO-006](../../docs/03-architecture/geodata-pipeline.md#4-rules)). Later stages (province generation, adjacency, bake) are separate stories.

```bash
make setup            # uv sync for repo tooling and this project
make geodata-fetch    # download sources.lock.yaml into artifacts/geodata/raw/
make geodata-test     # pytest
```

`make geodata-fetch ARGS="--json"` prints `{"ok": true, "results": [...]}`.

## Manifest

`sources.lock.yaml` is the only download list. It starts empty; ST-10.1.2 pins real sources and licences.

| Field | Required | Rule |
| --- | --- | --- |
| `id` | yes | Lowercase letters, digits, hyphens |
| `version` | yes | Source version label |
| `url` | yes | `https` URL. Redirects off HTTPS fail |
| `sha256` | yes | Lowercase hex digest of the file bytes |
| `filename` | yes | Basename only. This is the cache filename, not the URL path |
| `max_bytes` | no | Positive integer. Default 512 MiB (`DEFAULT_MAX_BYTES`) |

Verified files are stored at `artifacts/geodata/raw/<sha256>/<filename>` (gitignored). A cache hit is hashed again and reused. A mismatch or a hash that does not match the manifest deletes the bad file and downloads again. Nothing is written to the cache path until the digest matches.

## Layout

| Path | Role |
| --- | --- |
| `src/warroom_geodata/` | Package (`geodata` console script) |
| `tests/` | Pytest. Tests use an in-memory downloader and do not touch the network |
| `sources.lock.yaml` | Pinned URLs and checksums |
| `uv.lock` | Pinned Python dependencies |
