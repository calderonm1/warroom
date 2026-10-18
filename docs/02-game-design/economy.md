---
title: Economy, resources, buildings and production
status: review
owner: design
last_reviewed: 2026-10-18
related: [EP-12, docs/03-architecture/simulation.md]
---

# Economy

## 1. Resources

| Resource | ID | Produced by | Used for |
| --- | --- | --- | --- |
| Treasury | `res.treasury` | taxes from provinces (scaled by morale) | everything; upkeep |
| Manpower | `res.manpower` | population; barracks | units |
| Materials | `res.materials` | rural provinces, factories | buildings, ground units |
| Fuel | `res.fuel` | oil provinces, refineries | air and naval units, mechanized movement upkeep |
| Electronics | `res.electronics` | urban provinces, tech parks | advanced units, drones, research |
| Rare earths | `res.rare_earths` | specific provinces and strategic sites | high-tier units, missiles, stealth |

## 2. Rules

| ID | Rule |
| --- | --- |
| GDD-ECON-001 | Production happens on the **economy tick** (each game hour, SIM-012). Output = base × terrain × buildings × morale × occupation modifier. |
| GDD-ECON-002 | **Upkeep:** every unit costs treasury (and fuel for mechanized, air and naval) per tick. If a resource goes negative, the affected units lose strength gradually rather than being deleted. |
| GDD-ECON-003 | **Storage cap** per resource (scaled by buildings) prevents infinite hoarding. |
| GDD-ECON-004 | **Morale** (0 to 100%) per province drifts toward a target set by distance to capital, war weariness, recent bombardment, occupation and buildings. Below 30%: output −50% and revolt risk. |
| GDD-ECON-005 | **Trade:** nations can exchange resources by treaty (DIP), with a 10% transport loss; blockaded by naval control of connecting sea zones. |
| GDD-ECON-006 | **Market** (post-launch candidate): a match-wide market with dynamic prices. Out of scope for M2. |

## 3. Buildings (initial set)

| Building | ID | Slots | Effect |
| --- | --- | --- | --- |
| Factory | `bld.factory` | rural/urban | +materials; unlocks ground unit production |
| Barracks | `bld.barracks` | any | unlocks infantry; +manpower |
| Airbase | `bld.airbase` | urban or rural with level | unlocks and stations aircraft |
| Naval base | `bld.naval_base` | coastal | unlocks and repairs ships |
| Refinery | `bld.refinery` | oil province | +fuel |
| Tech park | `bld.tech_park` | urban | +electronics; +research speed |
| Air defence site | `bld.air_defence` | any | auto-engages air and missiles in range |
| Fortifications | `bld.fortifications` | any | +defence for garrisons |
| Command bunker | `bld.command_bunker` | capital | morale aura; reduces capital capture effects |
| Missile silo | `bld.missile_silo` | research-gated | stores and launches strategic missiles |

Buildings have levels 1 to 5. Construction time and cost scale per level. Damaged buildings (bombardment) lose output until repaired.

## 4. Production

| ID | Rule |
| --- | --- |
| GDD-ECON-010 | Units are produced in provinces with the required building. Cost is reserved at queue time. Cancel refunds 75%. |
| GDD-ECON-011 | Production time is fixed per unit type and building level. There are **no paid instant-completes in ranked**. Casual Logistics Boost may cut remaining time by a capped percentage per day (ADR-0010). |
| GDD-ECON-012 | Mobilization: a nation can declare mobilization (+50% manpower, −20% treasury income, −morale over time), and demobilize to recover. |
