# Repo tooling

Python 3.12 tooling managed by [uv](https://docs.astral.sh/uv/) ([ADR-0015](../docs/adr/0015-repo-tooling-python-uv.md)). The package is `tools/warroom_tools` and installs a `wr` command. Use the `make` targets; they are what CI runs.

```bash
make setup        # uv sync for this project and for tools/geodata
make check        # lint, tool tests, geodata lint and tests, docs-check, backlog-validate, index freshness, ops-validate
```

The geodata pipeline is a second uv project at [`tools/geodata`](geodata/README.md) ([ADR-0021](../docs/adr/0021-geodata-uv-project.md)). `make geodata-fetch` downloads `sources.lock.yaml` and verifies SHA-256.

## Commands

| Make target | `wr` command | What it does |
| --- | --- | --- |
| `make backlog-validate` | `wr backlog validate` | Schema per epic file; unique IDs; feature and story ID prefixes match parents; `depends_on` targets exist; no cycles; done stories have finished dependencies; ready stories are sized XS to M and link docs; `docs` paths exist; `refs` are defined in `docs/`; every backlog ID mentioned in docs, ops, rules and READMEs exists |
| `make backlog-index` | `wr backlog index` | Regenerates `backlog/INDEX.md` deterministically |
| `make backlog-index-check` | `wr backlog index --check` | Fails if `INDEX.md` is stale (CI) |
| `make backlog-next` | `wr backlog next [--json] [--milestone M1] [--limit N]` | Ready stories whose dependencies are all done, by milestone, priority, ID |
| `make backlog-sync-plan` | `wr backlog sync-github -v` | Dry run of the GitHub sync. Without credentials it prints an offline plan |
| `make backlog-sync` | `wr backlog sync-github --apply` | Creates and updates issues and project fields |
| `make docs-check` | `wr docs check` | Front matter (CONV-DOC-001), index coverage (CONV-DOC-002), relative links and `related` paths (CONV-DOC-003) |
| `make docs-stale` | `wr docs stale [--days 180] [--json]` | Docs whose `last_reviewed` is older than the threshold (CONV-DOC-009) |
| `make ops-validate` | `wr ops validate` | Environment manifests against `ops/environments/schema.json`; prod and staging agent policy guardrails; active environments have no `TBD` values |
| `make doctor` | `wr doctor [--json]` | Toolchain versions from `global.json`, `.tool-versions`, `.terraform-version` and `.unity-version`. A missing or wrong tool exits non-zero and names `docs/06-environments/local-development.md#1-workstation-prerequisites`. Not part of `make check` |
| `make geodata-lint` | `ruff` in `tools/geodata` | Lint and format-check the geodata project |
| `make geodata-test` | `pytest` in `tools/geodata` | Cache and SHA-256 tests (no network) |
| `make geodata-fetch` | `geodata fetch [--json]` | Download `tools/geodata/sources.lock.yaml` into `artifacts/geodata/raw/<sha256>/` after the digest matches |

Output lines start with `ERROR` or `WARN`, followed by the file and the reason. Commands exit non-zero on failure.

## GitHub Projects sync

The sync is one way: repo to GitHub ([ADR-0014](../docs/adr/0014-backlog-as-code-github-projects.md)). Each epic and story becomes one issue labelled `backlog` with a hidden marker `<!-- warroom-backlog-id: ST-… -->`. Reruns find issues by marker and update them. Done and cancelled stories close their issues.

Adding an issue to the project is idempotent. If a Projects auto-add workflow (or a previous partial run) already placed the issue on the board, `addProjectV2ItemById` returns "Content already exists in this project"; the sync looks up the existing item id and continues setting fields instead of aborting.

### Configuration

| Name | Kind | Purpose |
| --- | --- | --- |
| `GITHUB_TOKEN` or `WR_PROJECTS_TOKEN` | secret | Token with `repo` and `project` scopes (a fine-grained token needs Issues read/write and Projects read/write) |
| `GITHUB_REPOSITORY` | env | `owner/name` of the repo that holds the issues |
| `WR_PROJECT_OWNER` | variable | User or organization login that owns the project |
| `WR_PROJECT_NUMBER` | variable | Project number from the project URL |

### Required project fields

Create these in the project before the first sync (ST-01.2.4). The sync checks them and lists anything missing.

GitHub Projects already has system fields named **Type** (Issue / Pull request / Draft) and **Milestone** (repo milestones). Do not try to create custom fields with those names. Leave the system fields in place (hide them from views if you want) and create **Kind** and **Roadmap** instead.

| Field | Field type | Options |
| --- | --- | --- |
| Status | single select (reuse the built-in field) | Draft, Ready, In Progress, Blocked, Done, Cancelled |
| Priority | single select | P0, P1, P2, P3 |
| Size | single select | XS, S, M, L, XL |
| Roadmap | single select | M0, M1, M2, M3, M4, M5, M6, M7 |
| Kind | single select | Epic, Feature, Chore, Spike, Docs, Infra, Test, Bug |
| Epic | text | (epic ID, for example EP-05) |

The built-in project Status field can be reused by renaming its options to match.

## Development

- Code lives in `tools/warroom_tools/`, tests in `tools/tests/`. Tests build small fixture repos in temporary directories; they never touch the network.
- `make format` fixes lint and formatting. Ruff config is in the root `pyproject.toml`.
- Add dependencies with `uv add <pkg>` (or `uv add --dev <pkg>`). Never edit `uv.lock` by hand.
