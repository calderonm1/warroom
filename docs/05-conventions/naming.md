---
title: Naming conventions
status: accepted
owner: engineering
last_reviewed: 2026-10-18
related: [docs/00-product/glossary.md, docs/00-product/naming-and-brand.md]
---

# Naming conventions

| ID | Thing | Convention | Example | Enforced by |
| --- | --- | --- | --- | --- |
| CONV-NAME-001 | Domain terms | Use [glossary](../00-product/glossary.md) terms exactly | `Army`, not `Stack` | review |
| CONV-NAME-002 | C# namespaces | `WarRoom.<Component>.<Area>` mirroring folders | `WarRoom.Simulation.Military` | analyzer IDE0130 |
| CONV-NAME-003 | C# types / methods / properties | PascalCase; interfaces `I` prefix; async methods `Async` suffix | `IMatchRepository.LoadAsync` | .editorconfig |
| CONV-NAME-004 | C# private fields | `_camelCase`; constants PascalCase | `_scheduler`, `MaxQueueLength` | .editorconfig |
| CONV-NAME-005 | C# files | One public type per file; filename = type name | `MatchGrain.cs` | analyzer |
| CONV-NAME-006 | Projects / assemblies | `WarRoom.<Component>[.<Sub>]` | `WarRoom.Server.Gateway`, `WarRoom.Client.Globe` | review |
| CONV-NAME-007 | Commands / events (sim) | Commands: imperative verb-noun; events: past tense | `MoveArmy`, `ArmyArrived` | review |
| CONV-NAME-008 | Protobuf | package `warroom.<domain>.v<N>`; messages PascalCase; fields snake_case; enums `UPPER_SNAKE` with `<ENUM>_UNSPECIFIED = 0` | `warroom.match.v1.MoveArmy.target_province_id` | buf lint |
| CONV-NAME-009 | HTTP routes | `/v<N>/<plural-resource>/{id}/<sub-resource>`, kebab-case | `/v1/matches/{matchId}/nations` | OpenAPI lint (spectral) |
| CONV-NAME-010 | JSON fields | camelCase | `matchId` | OpenAPI lint |
| CONV-NAME-011 | DB tables / columns | snake_case, singular tables, `_id` suffix for keys, `_at` for timestamps (timestamptz) | `match_nation.joined_at` | migration review |
| CONV-NAME-012 | Content IDs | lowercase dotted `<type>.<category>.<name>` | `unit.air.stealth_fighter` | content schema |
| CONV-NAME-013 | Localization keys | content ID + `.name` / `.desc`, or `ui.<screen>.<element>` | `ui.store.buy_button` | l10n lint |
| CONV-NAME-014 | Telemetry events | `wr.<domain>.<past_tense_verb>` | `wr.match.joined` | event schema |
| CONV-NAME-015 | Metrics | `<domain>.<object>.<measure>` lowercase dotted | `command.ack.latency` | review |
| CONV-NAME-016 | AWS resources | `wr-<env>-<component>[-<qualifier>]` | `wr-prod-silo`, `wr-dev-snapshots` | tflint custom rule |
| CONV-NAME-017 | Terraform | snake_case resource names; module dirs kebab-case | `aws_ecs_service.gateway`, `modules/ecs-service` | tflint |
| CONV-NAME-018 | Env vars | `WR_<AREA>_<NAME>` | `WR_DB_CONNECTION_STRING` | review |
| CONV-NAME-019 | Branches | `<type>/<story-id>-<slug>` | `feat/ST-05.1.2-fixed-point` | CI check |
| CONV-NAME-020 | Docs files | kebab-case `.md`; ADRs `NNNN-kebab-title.md` | `globe-rendering.md` | docs-check |
| CONV-NAME-021 | Unity assets | PascalCase with type prefix for non-code assets | `M_Globe_Ocean.mat`, `T_Insignia_DE.png`, `UI_ArmySheet.uxml` | asset validator (`ST-02.3.4`) |
| CONV-NAME-022 | Backlog IDs | `EP-NN`, `FE-NN.N`, `ST-NN.N.N`; permanent | `ST-09.2.1` | backlog validator |
| CONV-NAME-023 | Requirement IDs | `<DOC>-<AREA>-NNN` | `GDD-ECON-004`, `NFR-PERF-001` | review |
