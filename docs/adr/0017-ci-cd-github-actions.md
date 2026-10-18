---
title: "ADR-0017: CI/CD with GitHub Actions, GameCI and fastlane"
status: accepted
owner: architecture
last_reviewed: 2026-10-18
related: [ADR-0008, ADR-0014, docs/06-environments/ci-cd.md]
---

# ADR-0017: CI/CD with GitHub Actions, GameCI and fastlane

- **Date:** 2026-10-18
- **Deciders:** project owner

## Context

The pipeline must cover repo checks, .NET builds and tests, Unity builds for iOS and Android, container deploys to three environments, Terraform plans and applies, store uploads (TestFlight and Play internal testing), and backlog sync to GitHub Projects (ADR-0014).

## Decision

1. **GitHub Actions** is the CI/CD system. The repository is hosted on GitHub to enable Actions, Projects and OIDC to AWS.
2. **Unity builds** use **GameCI** (`game-ci/unity-builder`, `unity-test-runner`) on Linux runners for Android, and **macOS runners** for iOS (Xcode archive). Self-hosted macOS runners may replace GitHub-hosted ones if minutes cost becomes material.
3. **Store delivery** uses **fastlane**: `pilot` (TestFlight) and `supply` (Play internal track). Signing assets are stored encrypted (fastlane `match` in a private bucket, or GitHub secrets).
4. **Server deploys:** build container, push to ECR (shared account), then deploy to `dev` automatically on `main`. Staging deploys on release tags (`v*`); prod deploys on the same artifact promoted with manual approval (GitHub Environments with required reviewers).
5. Workflows are path-filtered: `docs/**` and `backlog/**` run only repo checks.
6. CI publishes machine-readable artifacts (test results as JUnit XML, coverage, `terraform plan -json`, build size reports) for agents to inspect.

## Alternatives considered

| Option | Why not |
| --- | --- |
| Unity Build Automation (Cloud Build) | Convenient, but splits CI; per-minute cost; less control |
| Codemagic / Bitrise | Good mobile CI, but another vendor; GameCI covers it |
| AWS CodePipeline | Weaker developer experience and ecosystem; no Projects integration |

## Consequences

Requires a Unity license activation secret in CI, an Apple Developer account and App Store Connect API key, and a Google Play service account. These are tracked in `EP-04`.

## Compliance

Branch protection: required checks `repo-checks`, `server`, `shared`, `client-editmode` (once they exist).
