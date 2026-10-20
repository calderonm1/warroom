---
title: CI/CD pipelines
status: review
owner: ops
last_reviewed: 2026-10-20
related:
  [
    ADR-0017,
    EP-04,
    .github/workflows/repo-checks.yml,
    .github/workflows/backlog-sync.yml,
    .github/actions/setup-uv/action.yml,
    .github/actions/setup-dotnet/action.yml,
    .github/actions/setup-buf/action.yml,
  ]
---

# CI/CD pipelines

| Workflow | Trigger | Jobs | Status |
| --- | --- | --- | --- |
| `repo-checks.yml` | every PR and push (`paths: "**"`) | backlog validate, index freshness, docs check, ops manifests, tools lint and tests, workflow conventions | **live** |
| `backlog-sync.yml` | push to `main` touching `backlog/**`; manual | sync backlog to GitHub Projects | **live** (needs secrets, see below) |
| `shared.yml` | changes in `shared/**` | build netstandard2.1, unit, property and golden tests (x64 + arm64), coverage gate | `ST-04.1.2` |
| `server.yml` | changes in `server/**`, `shared/**` | build, unit, integration (Testcontainers), contract tests, container build, push to ECR on `main` | `ST-04.1.3` |
| `client.yml` | changes in `client/**`, `shared/**` | GameCI EditMode tests; Android build (Linux); iOS build (macOS); size report | `ST-04.2.1`, `ST-04.2.2` |
| `contracts.yml` | changes in `shared/contracts/**` | buf lint/breaking, Spectral, codegen drift | `ST-04.1.4` |
| `infra.yml` | changes in `infra/**` | fmt, tflint, checkov, plan per env (PR comment); apply dev on merge | `ST-04.3.1` |
| `deploy.yml` | `main` (dev), `v*` tags (staging), manual promote (prod) | migrate DB, deploy ECS, smoke tests | `ST-04.3.2` |
| `mobile-release.yml` | `v*` tags | fastlane: TestFlight + Play internal; promote on approval | `ST-04.2.3` |
| `nightly.yml` | schedule | soak AI match, PlayMode perf, drift detection, E2E bots vs dev | `ST-04.4.1` |

## Required repository configuration (once the repo is on GitHub)

| Kind | Name | Used by |
| --- | --- | --- |
| Variable | `WR_PROJECT_OWNER` (user or org login) | backlog-sync |
| Variable | `WR_PROJECT_NUMBER` (Projects v2 number) | backlog-sync |
| Secret | `WR_PROJECTS_TOKEN` (fine-grained PAT or GitHub App token with Issues RW + Projects RW) | backlog-sync |
| Secret | `UNITY_LICENSE` / `UNITY_EMAIL` / `UNITY_PASSWORD` | client builds |
| Secret | `APP_STORE_CONNECT_API_KEY_*`, `MATCH_PASSWORD` | iOS release |
| Secret | `PLAY_SERVICE_ACCOUNT_JSON` | Android release |
| OIDC role | `arn:aws:iam::<acct>:role/wr-<env>-github-deploy` | infra, deploy |

Machine-readable artifacts from every run: JUnit XML, coverage (Cobertura), `terraform plan -json`, build size JSON, and the backlog sync plan JSON.

## Workflow conventions

`make ci-check` (`wr ci check`) enforces path filters, concurrency, pinned third-party actions, and that the three setup composites exist.

| Rule | Requirement |
| --- | --- |
| Path filters | Every `pull_request`, `pull_request_target` and `push` trigger sets `paths` or `paths-ignore`. `repo-checks` uses `**` so it stays the baseline check until area pipelines exist. Schedule-only and manual-only workflows are not required to declare paths. |
| Concurrency | Every workflow sets `concurrency.group` (use `${{ github.workflow }}-${{ github.ref }}`) and `cancel-in-progress`. Pull-request checks set `cancel-in-progress: true` so a newer push cancels the superseded run. Workflows that write outside the repo (backlog sync, deploy, Terraform apply) set `cancel-in-progress: false`. |
| Pinned actions | A third-party `uses:` is `owner/repo@` plus the full 40-character commit SHA, with the version in a trailing comment. Local steps use `./.github/actions/<name>`. |
| Setup actions | Install tools only through the composite actions below, after `actions/checkout`. Versions come from the repo pins, not from the workflow. |
| Caching | `setup-uv` enables the uv cache. `setup-dotnet` enables the NuGet cache when a `*.csproj` or `packages.lock.json` is present (otherwise the cache step would fail with no lockfile). |
| Permissions | Workflows set the minimum `permissions` they need. Repo checks and backlog sync are `contents: read`. |

| Action | Installs | Version pin |
| --- | --- | --- |
| [`.github/actions/setup-uv`](../../.github/actions/setup-uv/action.yml) | uv | `.tool-versions` |
| [`.github/actions/setup-dotnet`](../../.github/actions/setup-dotnet/action.yml) | .NET SDK | `global.json` |
| [`.github/actions/setup-buf`](../../.github/actions/setup-buf/action.yml) | buf CLI (`setup_only`; no lint or push) | `.tool-versions` |

Area pipelines (`shared`, `server`, `client`, `contracts`) call these actions. They do not pin their own copies of setup-uv, setup-dotnet or buf. Dependabot updates of the pinned SHAs are `ST-04.1.5`.
