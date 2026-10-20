# AGENTS.md: operating manual for War Room

This file is the entry point for every AI agent (Cursor, Claude Code, Codex, Copilot and others) and every human contributor. Read it fully before changing anything. Rules here are binding. When a rule conflicts with a request, stop and surface the conflict instead of silently picking one.

## 1. What this project is

War Room is a commercial, server-authoritative, real-time grand strategy game for iOS and Android, with a planned web client. Matches run for days to weeks on a 3D globe with 16 to 64 players (100 later). Built solo with AI assistance, to production standards. Avoiding tech debt is a primary goal.

## 2. Source-of-truth hierarchy

When documents disagree, the higher one wins. Fix the lower one in the same change.

1. **Accepted ADRs** in [`docs/adr/`](docs/adr/README.md). Decisions and their constraints.
2. **Conventions** in [`docs/05-conventions/`](docs/05-conventions/README.md). How code, docs and commits are written.
3. **Architecture (TDD)** in [`docs/03-architecture/`](docs/03-architecture/README.md) and **Game design (GDD)** in [`docs/02-game-design/`](docs/02-game-design/README.md). What is built and how it works.
4. **Backlog** in [`backlog/`](backlog/README.md). What to build next, with acceptance criteria.
5. Code comments and everything else.

Never make a decision that contradicts an accepted ADR. If one needs to change, write a new ADR that supersedes it (see [ADR-0001](docs/adr/0001-record-architecture-decisions.md)).

## 3. Repository map

```
AGENTS.md            you are here
docs/                all design docs (index: docs/README.md)
  adr/               architecture decision records
backlog/             epics/features/stories (YAML, schema-validated); INDEX.md is generated
ops/environments/    machine-readable environment manifests (local/dev/staging/prod)
ops/mcp/             MCP server configuration for agents
tools/               Python repo tooling (backlog, docs checks, GitHub Projects sync)
client/              Unity 6 client
server/              .NET 10 backend
shared/              shared simulation (netstandard2.1, C# 9) and protocol contracts (.proto)
content/             data-driven game content (YAML), validated against schemas
infra/               Terraform
```

## 4. How to pick up and complete work

1. **Find work.** Run `make backlog-next` or read [`backlog/INDEX.md`](backlog/INDEX.md). Only take stories with `status: ready` whose `depends_on` are all `done`. If asked to do something with no story, create or extend a story first (an S-size story is fine) so the work stays traceable. Factory roles: [supervisor](.cursor/skills/supervisor/SKILL.md), [implement-story](.cursor/skills/implement-story/SKILL.md), [review-pr](.cursor/skills/review-pr/SKILL.md). Shell hooks in [`.cursor/hooks.json`](.cursor/hooks.json) deny merge, push to `main`, and `terraform apply`.
2. **Load context.** Read the story, its feature and epic, every path in its `docs:` lists, and the ADRs they reference. Read the relevant conventions doc for the language you will touch.
3. **Plan.** For M-size or larger stories, write a short plan as a comment in the PR description, or as `agent_notes` on the story, before coding.
4. **Branch.** Use `<type>/<story-id>-<short-slug>`, for example `feat/ST-05.1.2-command-validation`.
5. **Implement** following the conventions. Keep changes scoped to the story.
6. **Verify.** Run `make check` plus the tests for the area touched. Every acceptance criterion must be demonstrably met, by a test where possible.
7. **Update docs and backlog in the same change.** Set the story `status` (`in-progress`, then `done`), update any doc whose truth changed, and run `make backlog-index`.
8. **Commit** using Conventional Commits with the story ID: `feat(sim): validate move commands [ST-05.1.2]`. See [git and review](docs/05-conventions/git-and-review.md).

### Definition of Done (all stories)

- All acceptance criteria are met and covered by automated tests where technically possible.
- `make check` passes, along with the language-specific lint and test suites for the touched area.
- Docs that describe the changed behaviour are updated. New decisions are recorded as ADRs.
- Story status is updated and `backlog/INDEX.md` is regenerated.
- No secrets, credentials or personal data are committed. No new warnings are introduced.
- Observability: new server code paths emit structured logs and traces per [logging and errors](docs/05-conventions/logging-and-errors.md).

## 5. Hard rules (never violate)

1. **The server is authoritative.** The client never decides outcomes, and the server never sends information a player is not entitled to see (fog of war is enforced server-side). See [security and anti-cheat](docs/03-architecture/security-and-anti-cheat.md).
2. **The shared simulation must be deterministic.** In `shared/simulation`: no `DateTime.Now`, no `System.Random`, no floating-point math in state transitions (use fixed-point), no unordered-collection iteration that affects state, no I/O. See [simulation](docs/03-architecture/simulation.md).
3. **Shared code targets `netstandard2.1` and C# 9.** Unity's limits apply. Do not use C# 10+ features in `shared/`.
4. **Contracts are schema-first.** Change `.proto` and OpenAPI files first. Never hand-edit generated code. Breaking protocol changes need a new package version (`warroom.match.v2`).
5. **Content is data, not code.** Nations, units, research and maps live in `content/` as YAML and are validated against schemas. No hard-coded balance numbers in C#.
6. **Agents never mutate production.** Agents may read dev, staging and prod through the read-only roles in [AI environment access](docs/06-environments/ai-environment-access.md). Agents may deploy to `dev` only. Staging and prod changes go through CI with human approval.
7. **No secrets in the repo.** Use AWS Secrets Manager or SSM, GitHub Actions secrets, or local `.env` files (gitignored). Use `.env.example` for documentation.
8. **Do not invent product decisions.** If the GDD is silent, propose an addition to the GDD and mark it `status: draft` rather than implementing an assumption silently.
9. **Monetization must stay fair** ([ADR-0010](docs/adr/0010-monetization-fair-by-design.md)): nothing purchasable may grant combat power in ranked queues.
10. **Never renumber backlog IDs.** IDs are permanent, even when items move or are cancelled.

## 6. Commands

| Command | Purpose |
| --- | --- |
| `make help` | List all tasks |
| `make setup` | Install repo tooling |
| `make check` | Everything CI checks for docs and backlog (run before every commit) |
| `make backlog-validate` | Schema plus referential checks on `backlog/` |
| `make backlog-index` | Regenerate `backlog/INDEX.md` |
| `make backlog-next` | Stories ready to start |
| `make backlog-sync-plan` / `make backlog-sync` | Dry run or apply sync to GitHub Projects |
| `make docs-check` | Front matter, internal links, and doc index coverage |
| `make test-tools` | Unit tests for repo tooling |
| `make doctor` | Report missing or wrong toolchain versions (JSON with `ARGS="--json"`) |

Client, server and infra commands are added to the `Makefile` by their scaffolding stories and documented in [local development](docs/06-environments/local-development.md).

## 7. Writing docs (agents included)

- Every Markdown file under `docs/` starts with the YAML front matter defined in [documentation conventions](docs/05-conventions/documentation.md): `title`, `status`, `owner`, `last_reviewed`, `related`.
- Every new doc must be linked from [`docs/README.md`](docs/README.md). `make docs-check` enforces this.
- Prefer tables, numbered rules and explicit IDs over prose. Write so the doc can be retrieved and understood out of context.
- Use stable IDs for referenceable rules and requirements, for example `GDD-ECON-004` or `NFR-PERF-002`, so code, tests and stories can cite them.

## 8. Environments for agents

Machine-readable environment descriptions live in [`ops/environments/`](ops/environments/). Each manifest lists endpoints, AWS account and region, log groups, dashboards, the IAM role an agent should assume, and what the agent is allowed to do there. Read the manifest before touching any environment. MCP servers (AWS, CloudWatch, Sentry, GitHub, Unity CLI) are configured per [ops/mcp/README.md](ops/mcp/README.md).

## 9. When unsure

Stop and ask, or leave a clearly marked `TODO(ST-xx.y.z): question` in a draft PR. Do not guess on security, money, player data, or anything that touches production.
