---
title: "ADR-0003: Unity 6 LTS as the client engine"
status: accepted
owner: architecture
last_reviewed: 2026-10-18
related: [R-ENG-01, R-ENG-02, R-ENG-03, R-ENG-04, ADR-0005, ADR-0012, docs/03-architecture/client-architecture.md]
---

# ADR-0003: Unity 6 LTS as the client engine

- **Date:** 2026-10-18
- **Deciders:** project owner

## Context

War Room needs a performant 3D globe on mid-range phones, iOS and Android from one codebase, mature IAP/push/analytics SDKs, a later web build, and an AI-friendly workflow. Research: Unity powers about 70% of top-grossing mobile games (R-ENG-01) and leads F2P (R-ENG-02). Unity 6.3 LTS is supported until Dec 2027, and the CoreCLR migration keeps .NET Standard 2.1 / C# 9 for players (R-ENG-03). Unity ships an official CLI and MCP server for agents (R-ENG-04).

## Decision

1. The client is built with **Unity 6.3 LTS** (`6000.3.x`) using **URP**, **UI Toolkit** for all UI, the **Input System**, and **Addressables** for content delivery.
2. Upgrade to the next LTS (6.7 LTS, then the CoreCLR line) via an explicit backlog story, never ad hoc.
3. Architecture is **code-first**: scenes are thin; logic lives in plain C# assemblies (`.asmdef`) testable without the Editor. MonoBehaviours are adapters only.
4. The client consumes the shared simulation (ADR-0005) for previews and prediction, but never decides outcomes.
5. Agents interact with the Editor through the **Unity CLI** (`unity command`, `unity eval`) or its MCP server (`unity mcp`).
6. Web: a WebGPU/WebGL build of the same project is the first web target (EP-26). The protocol and backend are already browser-compatible (ADR-0006).

## Alternatives considered

| Option | Pros | Cons | Why not |
| --- | --- | --- | --- |
| Unreal Engine 5 | Best visual ceiling | Heavier on mid-range mobile; C++ slows iteration; weaker mobile SDK ecosystem; poor web story | Overkill for a stylized strategy map |
| Godot 4.6 | MIT, no fees, improving mobile | Smaller 3D mobile ecosystem; fewer production references at this scale; weaker IAP/ads SDK support | Higher risk for a commercial live game |
| TypeScript + Babylon.js/Three.js in Capacitor/React Native | Web is trivial; very AI-friendly; one language with web | Weaker mobile 3D performance and tooling; WebView constraints; smaller game-specific SDK ecosystem | Mobile is the primary platform |
| Custom engine | Total control | Unbounded effort | Not viable solo |

## Consequences

- Unity Personal is free until $200K revenue or funding, then Pro (seat-based). Budget for it.
- iOS builds require macOS and Xcode (local Mac or macOS CI runners); see [device testing](../06-environments/device-testing.md).
- Unity YAML assets are harder for agents to edit. Mitigated by the code-first rule, UXML/USS text UI, and the Unity CLI.

## Compliance

`ProjectSettings/ProjectVersion.txt` is pinned and checked in CI. Assembly boundaries are validated by an EditMode test (`ST-02.3.3`). Review checklist: "No game logic in MonoBehaviours."
