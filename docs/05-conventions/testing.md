---
title: Testing conventions
status: accepted
owner: engineering
last_reviewed: 2026-10-18
related: [ADR-0005, docs/03-architecture/simulation.md]
---

# Testing conventions

## 1. Pyramid

| Level | Scope | Tooling | Runs |
| --- | --- | --- | --- |
| Unit | sim rules, services, view-models | xUnit, FsCheck, Unity EditMode | every PR |
| Golden replay | determinism of sim | xUnit with fixtures | every PR (shared changes), nightly on arm64 |
| Integration | server with real Postgres/Valkey, Orleans TestCluster | Testcontainers, `Microsoft.Orleans.TestingHost` | every PR (server changes) |
| Contract | OpenAPI and protobuf conformance | Schemathesis-style tests, buf | every PR |
| Client PlayMode | scene boot, globe rendering, perf | Unity Test Framework | client PRs + nightly |
| End-to-end | headless bot clients vs dev environment | .NET bot client | nightly + pre-release |
| Load / soak | capacity, AI-only matches | NBomber, AI soak | pre-milestone |
| Device | real-device smoke and perf | local devices + AWS Device Farm | pre-release |

## 2. Rules

| ID | Rule | Enforced by |
| --- | --- | --- |
| CONV-TEST-001 | Test names: `Method_Scenario_ExpectedResult` | review |
| CONV-TEST-002 | Every acceptance criterion maps to at least one test where technically possible; cite the story ID in a trait: `[Trait("story", "ST-05.2.1")]` | review |
| CONV-TEST-003 | Every GDD rule implemented in the sim has a test citing it: `[Trait("rule", "GDD-MIL-011")]`. A coverage report lists untested rule IDs. | tooling (`ST-05.6.2`) |
| CONV-TEST-004 | Coverage gates: `WarRoom.Simulation` ≥ 90% lines; server ≥ 75%; client Core ≥ 70%. | CI |
| CONV-TEST-005 | No sleeps in tests. Use `FakeTimeProvider` and the sim's virtual time. | review |
| CONV-TEST-006 | Tests are hermetic: no network except Testcontainers. No shared state between tests. | review |
| CONV-TEST-007 | Bugs get a failing regression test first. Production bugs get a golden replay fixture when sim-related. | review |
| CONV-TEST-008 | Flaky tests are quarantined within 24 h with a linked bug story, never ignored silently. | CI quarantine list |
