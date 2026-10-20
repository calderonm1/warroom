# War Room task runner. `make help` lists targets.
# Client, server and infra targets are added by their scaffolding stories (see AGENTS.md).

SHELL := /bin/bash
.DEFAULT_GOAL := help
WR := uv run --frozen wr

.PHONY: help setup check lint format test-tools doctor \
	backlog-validate backlog-index backlog-index-check backlog-next backlog-sync-plan backlog-sync \
	docs-check docs-stale ops-validate contracts-lint

help: ## List all tasks
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z0-9_-]+:.*##/ {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Install repo tooling (Python via uv)
	@command -v uv >/dev/null || { echo "uv is required: https://docs.astral.sh/uv/getting-started/installation/"; exit 1; }
	uv sync --frozen

check: lint test-tools docs-check backlog-validate backlog-index-check ops-validate contracts-lint ## Everything CI checks (run before every commit)
	@echo "All checks passed."

lint: ## Lint and format-check repo tooling
	uv run --frozen ruff check tools
	uv run --frozen ruff format --check tools

format: ## Auto-format repo tooling
	uv run --frozen ruff check --fix tools
	uv run --frozen ruff format tools

test-tools: ## Unit tests for repo tooling
	uv run --frozen pytest

doctor: ## Report toolchain versions (table; JSON with ARGS="--json")
	$(WR) doctor $(ARGS)

backlog-validate: ## Schema plus referential checks on backlog/
	$(WR) backlog validate

backlog-index: ## Regenerate backlog/INDEX.md
	$(WR) backlog index

backlog-index-check: ## Fail if backlog/INDEX.md is stale
	$(WR) backlog index --check

backlog-next: ## Stories ready to start (add ARGS="--json" for machine output)
	$(WR) backlog next $(ARGS)

backlog-sync-plan: ## Dry run of the GitHub Projects sync
	$(WR) backlog sync-github --verbose

backlog-sync: ## Apply the GitHub Projects sync (needs GITHUB_TOKEN, GITHUB_REPOSITORY, WR_PROJECT_OWNER, WR_PROJECT_NUMBER)
	$(WR) backlog sync-github --apply

docs-check: ## Front matter, internal links and doc index coverage
	$(WR) docs check

docs-stale: ## Docs not reviewed in 180 days
	$(WR) docs stale

ops-validate: ## Validate environment manifests in ops/environments
	$(WR) ops validate

contracts-lint: ## buf format, lint and breaking rules for shared/contracts (ST-07.1.1)
	@command -v buf >/dev/null || { echo "buf is required: docs/06-environments/local-development.md#1-workstation-prerequisites"; exit 1; }
	buf format -d --exit-code shared/contracts
	buf lint shared/contracts
	@if git cat-file -e main:shared/contracts/buf.yaml >/dev/null 2>&1; then \
		buf breaking shared/contracts --against '.git#branch=main,subdir=shared/contracts'; \
	elif git cat-file -e origin/main:shared/contracts/buf.yaml >/dev/null 2>&1; then \
		buf breaking shared/contracts --against '.git#branch=origin/main,subdir=shared/contracts'; \
	else \
		echo "buf breaking: no shared/contracts baseline on main yet; rules in shared/contracts/buf.yaml apply once it exists."; \
	fi
