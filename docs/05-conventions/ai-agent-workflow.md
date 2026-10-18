---
title: AI agent workflow
status: accepted
owner: engineering
last_reviewed: 2026-10-18
related: [AGENTS.md, ADR-0014, ADR-0018, backlog/README.md]
---

# AI agent workflow

This expands [AGENTS.md §4](../../AGENTS.md#4-how-to-pick-up-and-complete-work) with practices that keep agent output high quality.

## 1. Task sizing for agents

| Size | Meaning | Agent guidance |
| --- | --- | --- |
| XS | trivial, one file | do directly |
| S | a few files, one component | do directly; tests required |
| M | one feature slice across 1 to 2 components | write a plan first (story `agent_notes` or PR description) |
| L | multiple components or new subsystem | split into S/M stories before starting |
| XL | epic-level | never start; refine into stories |

## 2. Rules

| ID | Rule |
| --- | --- |
| CONV-AI-001 | One story per branch and PR. If you discover extra work, add a new story (status `draft`) instead of expanding scope. |
| CONV-AI-002 | Before coding, list the docs and ADRs you read in the PR description ("Context loaded"). |
| CONV-AI-003 | Prefer adding tests that encode acceptance criteria **before** implementation (test-first) for sim and server work. |
| CONV-AI-004 | Do not modify generated code, lockfiles (except via the package manager), or `backlog/INDEX.md` by hand. |
| CONV-AI-005 | If a doc is wrong or missing, fix it in the same PR, or open a `docs` story if it's large. |
| CONV-AI-006 | Record non-obvious decisions taken during implementation in the story's `agent_notes`; escalate to an ADR if significant. |
| CONV-AI-007 | Use machine-readable outputs for verification (`--json`, JUnit XML, `terraform plan -json`) and cite them in the PR. |
| CONV-AI-008 | For environment work, read `ops/environments/<env>.yaml` first and obey its `agent_policy`. |
| CONV-AI-009 | When parallelizing work across multiple agents, assign stories with no dependency edges between them and disjoint `area` labels. |

## 3. Story readiness (Definition of Ready)

A story may be marked `ready` only when it has: a clear user/system story statement, testable acceptance criteria, `docs:` links to the governing doc sections, size ≤ M, dependencies listed, and, for UI stories, loading/empty/error states defined.

## 4. Recommended tools for the owner

| Tool | Use |
| --- | --- |
| Cursor (agents, rules, MCP) | primary IDE and agent host; reads `AGENTS.md` and `.cursor/rules/` |
| Cursor Cloud Agents | parallel background stories (one story per agent) |
| Unity CLI + `unity mcp` | agent control of the Unity Editor |
| AWS MCP / CloudWatch MCP | read-only cloud inspection |
| Sentry MCP | crash triage |
| GitHub MCP / Projects | board view, PR management |
