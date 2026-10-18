---
title: Content model, packs and sensitivity policy
status: review
owner: design
last_reviewed: 2026-10-18
related: [ADR-0011, BR-007, EP-10, content/README.md]
---

# Content model, packs and sensitivity policy

## 1. Content packs

| ID | Rule |
| --- | --- |
| GDD-CONT-001 | All setting-specific content belongs to a content pack (`content/packs/<pack-id>/`). The engine knows only generic types. |
| GDD-CONT-002 | Launch pack: `modern` (present-day nations, modern units). Future packs: `cold_war`, `ww2`, `near_future`, `fictional`. |
| GDD-CONT-003 | A pack is versioned (`pack.yaml: version`). Matches pin `pack_id@version`. |
| GDD-CONT-004 | Content files are YAML validated against JSON Schemas in `shared/content-schema/`. CI fails on invalid content, unknown references, or balance values outside declared bounds. |
| GDD-CONT-005 | Content IDs are permanent: `unit.armor.mbt`, `bld.factory`, `res.fuel`, `research.air.stealth_1`, `nation.de`. |

## 2. Example unit definition

```yaml
# content/packs/modern/units/armor.yaml
- id: unit.armor.mbt
  branch: armor
  armor_class: heavy
  name_key: unit.armor.mbt.name
  cost: { res.treasury: 1200, res.materials: 800, res.fuel: 200, res.manpower: 300 }
  upkeep_per_hour: { res.treasury: 12, res.fuel: 3 }
  build_time_hours: 10
  requires: { building: bld.factory@3, research: research.armor.mbt_1 }
  strength: 25
  attack: { light: 6.0, heavy: 4.5, air_low: 0.5, air_high: 0, naval: 1.0, drone: 0.5, building: 2.0 }
  defence: { light: 5.0, heavy: 4.0, air_low: 2.0, air_high: 1.5, naval: 2.0, missile: 1.0 }
  range_km: 0
  view_range_km: 30
  speed_kmh: { plains: 45, forest: 30, hills: 30, mountains: 15, urban: 35, desert: 40 }
  levels: [research.armor.mbt_1, research.armor.mbt_2, research.armor.mbt_3, research.armor.mbt_4]
```

## 3. Sensitivity policy

| ID | Rule |
| --- | --- |
| GDD-CONT-010 | Real countries are represented by **nations with real names and flags-inspired insignia** (stylized, not official flags) to reduce legal and rating risk. |
| GDD-CONT-011 | No real living political or military leaders, parties, or real-world atrocities. |
| GDD-CONT-012 | Borders reflect de facto control at the pack's reference date. Disputed areas are labelled neutrally. A disclaimer appears in the settings and store description. |
| GDD-CONT-013 | No nuclear weapons, chemical weapons or targeting of civilians in the modern pack. Strategic missiles damage infrastructure and morale only. |
| GDD-CONT-014 | Store distribution in specific countries may require regional map variants. Tracked as a launch-readiness risk (see [risks](../07-planning/risks.md)). |
| GDD-CONT-015 | Age rating target: **12+ (App Store) / Teen (ESRB-IARC) / PEGI 12**. |
