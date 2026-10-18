---
title: "ADR-0012: Custom stylized globe renderer (province ID map), not photoreal tiles"
status: accepted
owner: architecture
last_reviewed: 2026-10-18
related: [R-ENG-05, NFR-PERF-001, docs/03-architecture/globe-rendering.md]
---

# ADR-0012: Custom stylized globe renderer

- **Date:** 2026-10-18
- **Deciders:** project owner

## Context

The globe is the core interface (pillar P3). It must render thousands of provinces with ownership colours, borders, fog of war, selection and overlays at 60 fps on reference devices and 30+ on minimum spec (NFR-PERF-001). Photoreal streaming tiles (Cesium) perform poorly on Android (R-ENG-05), need network streaming, and do not read well as a game board.

## Decision

1. A **custom globe renderer in Unity URP**:
   - Base sphere: a cube-sphere mesh with LOD rings (quadtree per face).
   - **Province ID cubemap**: each texel encodes a province ID (RG16). Shaders look up per-province data (owner colour, visibility, highlight) from a small **province data texture** updated at runtime, giving one draw call for all territory colouring.
   - Borders: generated in the shader from ID discontinuities, plus pre-baked vector border meshes for crisp close-up coastlines.
   - Terrain: stylized albedo/normal cubemaps (baked offline from public-domain sources), with an optional height displacement at close zoom.
   - Units and markers: GPU-instanced billboards (NATO APP-6-inspired symbols) at far and mid zoom, and 3D models at close zoom.
   - Paths: great-circle and graph-edge arcs rendered as instanced ribbon meshes.
2. Picking via the province ID cubemap (CPU-side copy) gives O(1) tap-to-province.
3. All map assets are produced by the **geodata pipeline** (ADR via `EP-10`) from public-domain data (Natural Earth) into versioned content.

## Alternatives considered

| Option | Why not |
| --- | --- |
| Cesium for Unity / Google Photorealistic 3D Tiles | Mobile performance problems, streaming costs, licensing, poor game-board readability |
| Flat map projected onto a sphere at runtime | Distortion and seam issues at the poles; same complexity |
| Per-province meshes (one per province) | Thousands of draw calls and materials; slow updates |

## Consequences

More upfront rendering work (EP-09) but full control over performance and art direction. The province-ID approach is a proven technique in grand strategy games.

## Compliance

Performance budgets in [globe rendering](../03-architecture/globe-rendering.md) are measured by automated on-device benchmarks in CI (`ST-09.5.2`).
