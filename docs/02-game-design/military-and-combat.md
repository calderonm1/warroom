---
title: Military, movement and combat
status: review
owner: design
last_reviewed: 2026-10-18
related: [EP-13, docs/03-architecture/simulation.md]
---

# Military, movement and combat

## 1. Unit classes (modern pack)

| Branch | Units (initial) | Armor class |
| --- | --- | --- |
| Infantry | Motorized infantry, Mechanized infantry, Special forces, Airborne | `light` |
| Armor | Armored recon, MBT, Tank destroyer | `heavy` |
| Artillery & support | Towed artillery, SP artillery, MLRS, Mobile SAM, Combat engineers | `light` |
| Drones & EW (signature) | Recon drone, Loitering munition, Strike UAV, EW unit | `drone` |
| Rotary | Attack helicopter, Transport helicopter, ASW helicopter | `air_low` |
| Fixed-wing | Air superiority fighter, Strike fighter, Bomber, AWACS, Stealth fighter | `air_high` |
| Naval | Corvette, Frigate, Destroyer, Cruiser, Carrier, Attack submarine, Ballistic submarine | `naval` / `sub` |
| Missiles | Cruise missile, Ballistic missile, Hypersonic missile (late) | `missile` |

Every unit has: `strength` (HP), `attack[armor_class]`, `defence[armor_class]`, `range` (km), `view_range`, `speed[terrain]`, `upkeep`, `cost`, `build_time`, `required_building`, `required_research`. All values live in content.

## 2. Movement

| ID | Rule |
| --- | --- |
| GDD-MIL-001 | Armies move along province-graph paths at the speed of their slowest unit, modified by terrain and roads (urban edges). |
| GDD-MIL-002 | Air units fly from airbases or carriers, with a **mission range**: patrol (stay over target), strike (attack then return), relocate. |
| GDD-MIL-003 | Naval units move through sea zones and can blockade (contest) adjacent ports and trade routes. |
| GDD-MIL-004 | **Supply:** ground armies in hostile or non-connected territory lose 2% strength per game hour beyond 3 provinces from friendly supply (a connected province with a depot or urban province). |
| GDD-MIL-005 | **Fuel upkeep** applies to mechanized movement; out of fuel halves speed. |

## 3. Combat

| ID | Rule |
| --- | --- |
| GDD-MIL-010 | An **engagement** begins when hostile armies are within range of each other (ranged units can bombard without contact). |
| GDD-MIL-011 | Combat resolves in **rounds every 15 game minutes** (SIM-013). Each round, every unit deals damage = attack[target armor class] × strength ratio × modifiers (terrain, fortification, morale, doctrine, supply) × RNG(0.9 to 1.1). |
| GDD-MIL-012 | Damage is distributed by target priority (front-line classes absorb first; artillery is protected unless flanked). |
| GDD-MIL-013 | Units retreat (per standing order) or are destroyed at 0 strength. Retreating units take one free round of fire. |
| GDD-MIL-014 | **Combat preview:** before attacking, players see the projected outcome (odds band, not exact) computed by the shared simulation on visible information only. |
| GDD-MIL-015 | **Air defence** automatically engages air, drone and missile units in range (GDD-LOOP-004). |
| GDD-MIL-016 | **Electronic warfare:** EW units reduce enemy drone effectiveness and view range in adjacent provinces. Counters: anti-radiation strike, EW research. |
| GDD-MIL-017 | **Strategic missiles** (late game) damage buildings and morale. Interception chance depends on air defence level. Nuclear weapons are **not** in the modern launch pack (content and rating sensitivity). |

## 4. Rock-paper-scissors summary

`Infantry` > urban defence · `Armor` > infantry in open terrain · `Tank destroyer / attack helo` > armor · `SAM / fighters` > air · `Drones` > artillery and soft targets · `EW` > drones · `Submarines` > surface ships · `ASW` > submarines · `Strike fighters / cruise missiles` > buildings and ships.
