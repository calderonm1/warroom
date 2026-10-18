---
title: Game design document (GDD) overview
status: review
owner: design
last_reviewed: 2026-10-18
related: [docs/00-product/vision.md, ADR-0010, ADR-0011]
---

# Game design document

War Room's GDD is split by system. Every rule has a permanent ID (`GDD-<AREA>-NNN`) so stories, code and tests can cite it. **All numbers are initial values.** Tunable values live in `content/` and are referenced here only as defaults.

| Section | Area code | Doc |
| --- | --- | --- |
| Core loop and check-in play | LOOP | [core-loop.md](core-loop.md) |
| Match lifecycle, modes, queues, victory | MATCH | [match-lifecycle.md](match-lifecycle.md) |
| Map, provinces and territory | MAP | [map-and-territory.md](map-and-territory.md) |
| Economy, resources, buildings, production | ECON | [economy.md](economy.md) |
| Military: units, movement, combat | MIL | [military-and-combat.md](military-and-combat.md) |
| Research and doctrines | RES | [research.md](research.md) |
| Diplomacy, coalitions, chat | DIP | [diplomacy-and-coalitions.md](diplomacy-and-coalitions.md) |
| Intel and fog of war | INT | [intel-and-fog-of-war.md](intel-and-fog-of-war.md) |
| AI nations and inactivity | AI | [ai-nations.md](ai-nations.md) |
| Progression, ranked, seasons, live ops | PROG | [progression-and-seasons.md](progression-and-seasons.md) |
| Monetization | MON | [monetization.md](monetization.md) |
| Onboarding and tutorial | ONB | [onboarding.md](onboarding.md) |
| Content model, packs and sensitivity policy | CONT | [content-model.md](content-model.md) |

## Design principles (apply to every system)

1. **Every check-in has a decision** (pillar P1). If a system creates only chores, automate it or cut it.
2. **Readable at a glance on a phone.** If a mechanic cannot be summarized in one HUD line, simplify it.
3. **Counterplay exists for everything.** No unit, tech or strategy without a counter available to a non-paying player.
4. **Comeback without rubber-banding.** Coalitions, morale and logistics create natural comebacks; no hidden catch-up bonuses.
5. **Time is a resource the player controls.** Long timers are fine when they can be planned and queued; surprises that require instant reaction must have defensive automation.
