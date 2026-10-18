---
title: Git, review and release conventions
status: accepted
owner: engineering
last_reviewed: 2026-10-18
related: [ADR-0017, .github/pull_request_template.md]
---

# Git, review and release conventions

| ID | Rule | Enforced by |
| --- | --- | --- |
| CONV-GIT-001 | Trunk-based: short-lived branches off `main`; merge via PR with squash. `main` is always deployable to dev. | branch protection |
| CONV-GIT-002 | Branch names `<type>/<story-id>-<slug>` with type in `feat, fix, chore, docs, refactor, test, perf, infra, spike`. | CI |
| CONV-GIT-003 | **Conventional Commits**: `<type>(<scope>): <summary> [<story-id>]`. Scopes: `sim, server, client, globe, net, infra, ci, content, docs, backlog, tools`. | commitlint (CI) |
| CONV-GIT-004 | PR description uses the [template](../../.github/pull_request_template.md): story link, what changed, how verified, docs updated, risk. | template |
| CONV-GIT-005 | PRs are small: target ≤ 400 changed lines excluding generated code and content data. | review |
| CONV-GIT-006 | Required checks must pass. No force-push to `main`. | branch protection |
| CONV-GIT-007 | Agent-authored PRs are labelled `agent` and get a human approval before merge to `main` while the project is solo (the owner reviews). | review |
| CONV-GIT-008 | Versioning: SemVer for the app (`MAJOR.MINOR.PATCH`) plus a monotonically increasing build number. Server images are tagged `<semver>-<shortsha>`. Contracts versioned independently by package. | CI |
| CONV-GIT-009 | Releases: tag `vX.Y.Z` on `main` to build a release candidate, deploy to staging, run the smoke and E2E suite, then promote the same artifacts to prod (manual approval). | CI |
| CONV-GIT-010 | Changelog generated from Conventional Commits (`CHANGELOG.md`, per release). | CI |
| CONV-GIT-011 | Large binaries only via LFS ([`.gitattributes`](../../.gitattributes)). A pre-commit check rejects files > 5 MB that are not LFS-tracked. | pre-commit hook |
