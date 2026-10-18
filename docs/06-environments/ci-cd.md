---
title: CI/CD pipelines
status: review
owner: ops
last_reviewed: 2026-10-18
related: [ADR-0017, EP-04, .github/workflows/repo-checks.yml]
---

# CI/CD pipelines

| Workflow | Trigger | Jobs | Status |
| --- | --- | --- | --- |
| `repo-checks.yml` | every PR and push | backlog validate, index freshness, docs check, ops manifests, tools lint and tests | **live** |
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
