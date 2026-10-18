---
title: Globe rendering
status: accepted
owner: architecture
last_reviewed: 2026-10-18
related: [ADR-0012, EP-09, docs/04-ux/globe-interaction.md, docs/03-architecture/geodata-pipeline.md]
---

# Globe rendering

## 1. Layers (bottom to top)

| # | Layer | Technique |
| --- | --- | --- |
| 1 | Ocean | Sphere with stylized water shader (depth tint from bathymetry cubemap, subtle waves) |
| 2 | Land terrain | Cube-sphere quadtree mesh; albedo + normal cubemaps (stylized, baked offline); optional height displacement at zoom ≥ Z3 |
| 3 | Territory | **Province ID cubemap** + **province data texture**: owner colour, visibility state and highlight flags are looked up per texel in a single pass |
| 4 | Borders | Shader edge detection on ID discontinuities (far), vector border ribbons (near); coalition borders thicker |
| 5 | Fog of war | Per-province visibility flag gives desaturated, hatched overlay; unknown provinces show last-known owner |
| 6 | Labels | Nation and city labels in SDF text, placed from precomputed anchors, decluttered by zoom |
| 7 | Paths and arcs | Instanced ribbon meshes along province-graph edges; missile arcs as great-circle splines |
| 8 | Units and markers | GPU-instanced billboards (APP-6-inspired icons) at Z0 to Z2; 3D models at Z3+ (max 64 visible, LOD'd) |
| 9 | Atmosphere and lighting | Rim atmosphere shader, optional day/night terminator from game time |

## 2. Zoom levels

| Level | Altitude (Earth radii) | Shows |
| --- | --- | --- |
| Z0 Orbit | > 2.0 | Whole hemisphere, nations, coalitions, major alerts |
| Z1 Theatre | 0.8 to 2.0 | Nations, capitals, army stacks as single icons |
| Z2 Region | 0.25 to 0.8 | Provinces, cities, army icons with counts, paths |
| Z3 Operational | 0.05 to 0.25 | Province detail, buildings, unit models, terrain relief |

## 3. Province data texture

- Size: 4096 × 1 (or 64 × 64) RGBA32. Index = provinceId.
- Channels: R = owner nation palette index, G = visibility (0 unknown, 1 last-known, 2 visible), B = flags (selected, hovered, contested, under attack), A = coalition palette index.
- Updated from state deltas through `Texture2D.SetPixelData` plus `Apply` for dirty ranges only.

## 4. Picking

- The CPU keeps a downsampled province-ID cubemap (6 × 1024² × uint16, about 12 MB) for ray-to-sphere then UV then ID lookup.
- Unit and marker picking uses screen-space hit tests on instanced icons first, then falls back to province.

## 5. Performance budgets

| ID | Budget | Reference device | Min-spec device |
| --- | --- | --- | --- |
| NFR-PERF-001a | Frame rate, globe idle and pan | 60 fps | 30 fps |
| NFR-PERF-001b | Frame time GPU | ≤ 12 ms | ≤ 28 ms |
| NFR-PERF-001c | Draw calls (globe view) | ≤ 150 | ≤ 150 |
| NFR-PERF-001d | Memory (total app) | ≤ 1.5 GB | ≤ 900 MB |
| NFR-PERF-001e | Cold start to interactive globe | ≤ 6 s | ≤ 12 s |
| NFR-PERF-001f | Province data update (64 provinces changed) | ≤ 1 ms CPU | ≤ 3 ms CPU |
| NFR-PERF-001g | Install size (initial download) | ≤ 250 MB | ≤ 250 MB |

Device tiers (revisit before beta):

| Tier | iOS | Android |
| --- | --- | --- |
| Reference (high) | iPhone 16 and newer (owner's iPhone 18 Pro Max) | Snapdragon 8 Gen 2+ |
| Mid | iPhone 13 to 15 | Snapdragon 7 Gen 1 / Dimensity 7000-class, 6 GB RAM |
| Min-spec | iPhone 12 (A14), iOS 17 | Snapdragon 680 / Helio G85-class, 4 GB RAM, Android 10 (API 29) |

## 6. Quality settings

Automatic tiering at first launch (GPU family + RAM), user-overridable: `Low` (no terrain normals, no atmosphere, 30 fps cap), `Medium`, `High` (3D units at Z3, displacement, 60 fps).
