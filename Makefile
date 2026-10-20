# War Room task runner. `make help` lists targets.
# Client, server and infra targets are added by their scaffolding stories (see AGENTS.md).

SHELL := /bin/bash
.DEFAULT_GOAL := help
WR := uv run --frozen wr

.PHONY: help setup check lint format test-tools geodata-lint geodata-test geodata-fetch doctor \
	backlog-validate backlog-index backlog-index-check backlog-next backlog-sync-plan backlog-sync \
	docs-check docs-stale ops-validate

help: ## List all tasks
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z0-9_-]+:.*##/ {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Install repo tooling and the geodata project (Python via uv)
	@command -v uv >/dev/null || { echo "uv is required: https://docs.astral.sh/uv/getting-started/installation/"; exit 1; }
	uv sync --frozen
	uv sync --frozen --directory tools/geodata

check: lint geodata-lint test-tools geodata-test docs-check backlog-validate backlog-index-check ops-validate ## Everything CI checks (run before every commit)
	@echo "All checks passed."

lint: ## Lint and format-check repo tooling
	uv run --frozen ruff check tools
	uv run --frozen ruff format --check tools

format: ## Auto-format repo tooling and the geodata project
	uv run --frozen ruff check --fix tools
	uv run --frozen ruff format tools
	uv run --frozen --directory tools/geodata ruff check --fix .
	uv run --frozen --directory tools/geodata ruff format .

test-tools: ## Unit tests for repo tooling
	uv run --frozen pytest

geodata-lint: ## Lint and format-check tools/geodata
	uv run --frozen --directory tools/geodata ruff check .
	uv run --frozen --directory tools/geodata ruff format --check .

geodata-test: ## Unit tests for the geodata pipeline
	uv run --frozen --directory tools/geodata pytest

geodata-fetch: ## Download pinned geodata sources and verify SHA-256 (ARGS="--json")
	uv run --frozen --directory tools/geodata geodata fetch $(ARGS)

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
