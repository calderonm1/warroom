---
title: API and contract conventions
status: accepted
owner: engineering
last_reviewed: 2026-10-20
related: [ADR-0006, docs/03-architecture/networking-and-protocol.md]
---

# API and contract conventions

| ID | Rule | Enforced by |
| --- | --- | --- |
| CONV-API-001 | Schema-first: change `.proto` / OpenAPI first, regenerate (`make contracts-gen`), then implement. | CI (generated code drift check) |
| CONV-API-002 | `buf lint` (STANDARD rules) and `buf breaking` (FILE) against `main`. | `make contracts-lint` (CI: `repo-checks.yml` until `contracts.yml`, ST-04.1.4) |
| CONV-API-003 | Never reuse or renumber protobuf field numbers. Removed fields become `reserved`. | buf breaking |
| CONV-API-004 | Every enum has `*_UNSPECIFIED = 0`; receivers treat unknown values safely. | buf lint |
| CONV-API-005 | IDs on the wire: `string` UUIDs for players/matches; `uint32` for map-scoped IDs (province, nation, army). | review |
| CONV-API-006 | Times on the wire: `int64` game-time milliseconds or `int64` Unix ms (suffix `_unix_ms`). No `google.protobuf.Timestamp` in hot messages. | review |
| CONV-API-007 | OpenAPI 3.1, linted with Spectral (`.spectral.yaml`). Every operation has `operationId`, examples and error responses. | CI |
| CONV-API-008 | Pagination: cursor-based (`?cursor=&limit=`), max limit 100. | Spectral rule |
| CONV-API-009 | Idempotency: mutating meta endpoints that can be retried accept an `Idempotency-Key` header. | contract tests |
| CONV-API-010 | Breaking change process: new version alongside old (`v2` package or `/v2` route), clients migrate, old version removed after min-supported-version passes. Recorded in an ADR if it affects more than one message. | review |
| CONV-API-011 | Internal async messages (SQS) use versioned JSON Schemas in `shared/contracts/messages/`. | CI |
