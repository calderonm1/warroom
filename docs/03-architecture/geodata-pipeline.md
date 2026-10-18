---
title: Geodata and map content pipeline
status: accepted
owner: architecture
last_reviewed: 2026-10-18
related: [ADR-0012, ADR-0015, EP-10, docs/02-game-design/map-and-territory.md]
---

# Geodata and map content pipeline

## 1. Goal

Turn public-domain geographic data into game maps: provinces, sea zones, adjacency graph, travel costs, labels, and the cubemaps used by the globe renderer, reproducibly from a single command: `make map MAP=<map-id>`.

## 2. Sources

| Data | Source | License |
| --- | --- | --- |
| Countries, admin-1 regions, coastlines, populated places | Natural Earth 1:10m / 1:50m | Public domain |
| Elevation (stylized relief) | NOAA ETOPO / GEBCO | Public domain / free with attribution |
| Land cover (terrain class) | ESA WorldCover or MODIS (TBD in `ST-10.1.2`) | Check per source |

Pinned source versions and checksums are recorded in `tools/geodata/sources.lock.yaml`.

## 3. Stages

| # | Stage | Output |
| --- | --- | --- |
| 1 | Fetch and verify sources | `artifacts/geodata/raw/` |
| 2 | Project, clean and simplify geometry (topology-preserving) | cleaned layers |
| 3 | **Provinceization**: split or merge admin-1 polygons to a target province count per nation (by area, population and strategic weight); designer overrides in `content/packs/<pack>/maps/<map>/overrides.yaml` | province polygons |
| 4 | Sea zones from ocean Voronoi seeded by coastal provinces and straits; designer overrides | sea zone polygons |
| 5 | Adjacency graph (land–land, land–sea, sea–sea), strait links, impassable edges; edge travel distance via geodesic between centroids | `adjacency.yaml` |
| 6 | Gameplay attributes: terrain class, urban flag (from populated places), resource seeds | `provinces.yaml` (designer-editable after generation) |
| 7 | Export reviewable GeoJSON | `provinces.geojson` |
| 8 | Bake cubemaps: province ID (R16), albedo, normal, bathymetry; label anchors; border ribbons | `*.wrmap` binary + Addressables |
| 9 | Validate: every province reachable, no slivers below minimum area, IDs stable versus previous version | report JSON |

## 4. Rules

| ID | Rule |
| --- | --- |
| GEO-001 | Province IDs are **stable across pipeline runs** (assigned from a persistent ID registry keyed by source feature plus split index). Changing IDs breaks saved matches and replays. |
| GEO-002 | Generated files are never hand-edited. Designer intent goes into `overrides.yaml`. |
| GEO-003 | Each map has a version. Matches pin the map version. |
| GEO-004 | Borders are **game borders**: they follow de facto control as of the content pack date, and the game shows a disclaimer. Disputed areas use neutral naming. See the [content sensitivity policy](../02-game-design/content-model.md#sensitivity-policy). |
| GEO-005 | Target province counts: 16-player regional map 400 to 800; 32-player 800 to 1,500; 64-player world 2,000 to 3,000. |
