---
title: Map, provinces and territory
status: review
owner: design
last_reviewed: 2026-10-18
related: [ADR-0012, docs/03-architecture/geodata-pipeline.md, EP-09, EP-10]
---

# Map, provinces and territory

| ID | Rule |
| --- | --- |
| GDD-MAP-001 | The world is a globe of **provinces** (land) and **sea zones** (water). Every land province has exactly one owner nation or is neutral. |
| GDD-MAP-002 | Province types: **rural** (resource producer, 1 building slot), **urban** (city: higher output, 3 building slots, higher VP), **capital** (urban, +morale aura, highest VP). |
| GDD-MAP-003 | Terrain classes affect movement speed and combat: `plains`, `forest`, `hills`, `mountains`, `urban`, `desert`, `jungle`, `arctic`, `wetland`. Values live in content. |
| GDD-MAP-004 | Movement follows the province adjacency graph. Land units cross seas only by **embarking** at a port (becoming transport ships) or via **strait links**. |
| GDD-MAP-005 | **Strategic sites** (oil fields, refineries, launch sites, research labs, chokepoint ports) give unique bonuses and extra VP. Each map defines 8 to 16. |
| GDD-MAP-006 | **Capture:** a hostile land army that stays in a province with no defending army for the capture time (default 1 game hour, 2 for urban, 4 for capital) captures it. |
| GDD-MAP-007 | **Core vs occupied:** provinces originally owned by a nation are "core". Occupied provinces produce 50% and have reduced morale until integrated (research-gated). |
| GDD-MAP-008 | Distances are geodesic, computed by the geodata pipeline between province centroids along graph edges. |
| GDD-MAP-009 | Antarctica and the Arctic exist on world maps as hard-to-reach, resource-rich late-game regions. |
