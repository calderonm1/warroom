---
title: Unity conventions
status: accepted
owner: engineering
last_reviewed: 2026-10-18
related: [ADR-0003, docs/03-architecture/client-architecture.md]
---

# Unity conventions

| ID | Rule | Enforced by |
| --- | --- | --- |
| CONV-UNITY-001 | Unity version pinned in `ProjectSettings/ProjectVersion.txt` (6000.3.x LTS). Upgrades only via backlog story. | CI check |
| CONV-UNITY-002 | Asset serialization: **Force Text**. Visible meta files. UnityYAMLMerge configured as the git merge driver. | project settings check |
| CONV-UNITY-003 | All code lives under `Assets/WarRoom/` in assemblies with `.asmdef`. No code in `Assets/` root or `Assets/Scripts`. | EditMode test |
| CONV-UNITY-004 | **MonoBehaviours are adapters**: they forward Unity callbacks to plain C# services or view-models. No game rules in MonoBehaviours. | review |
| CONV-UNITY-005 | No `GameObject.Find`, `FindObjectOfType`, `SendMessage`, or `Resources.Load` in runtime code. Use the composition root and Addressables. | banned API test |
| CONV-UNITY-006 | UI is **UI Toolkit** (UXML + USS). uGUI only for world-space elements if unavoidable. USS uses token variables only. | USS lint |
| CONV-UNITY-007 | Scenes: `Boot`, `Main` (globe + UI root), `Dev_Gallery`. Everything else is spawned from code or Addressables. | review |
| CONV-UNITY-008 | Prefabs are small and composable. Never edit prefab YAML by hand except trivial fields. Prefer generating via Editor scripts (agent-friendly). | review |
| CONV-UNITY-009 | Input via the **Input System** with action maps (`Globe`, `UI`). No legacy `Input` class. | banned API test |
| CONV-UNITY-010 | No per-frame allocations in `Update` paths (GC.Alloc = 0 in profiler captures for the globe idle scenario). | PlayMode perf test |
| CONV-UNITY-011 | Textures: ASTC on mobile. Max 2048² except globe cubemaps. Mipmaps on 3D, off on UI. | asset validator |
| CONV-UNITY-012 | Audio: Vorbis compressed for music, ADPCM for short SFX. | asset validator |
| CONV-UNITY-013 | Every platform service is behind an interface in `WarRoom.Client.Core` with Editor/Fake implementations so the game runs in the Editor without devices or stores. | review |
| CONV-UNITY-014 | Agents drive the Editor via Unity CLI (`unity command`, `unity eval`) or `unity mcp`; batch builds via `-batchmode -executeMethod WarRoom.Editor.Build.<Target>`. | docs |
| CONV-UNITY-015 | Tests: EditMode for logic (fast, run on every PR), PlayMode for integration and perf (nightly plus on client PRs). | CI |
