---
title: HUD and screen inventory
status: review
owner: ux
last_reviewed: 2026-10-18
related: [docs/04-ux/design-system.md, docs/04-ux/globe-interaction.md, EP-11]
---

# HUD and screen inventory

## 1. In-match HUD (phone portrait)

```
┌───────────────────────────────────────┐
│ [≡] Match: World Conflict · Day 6 ⏱    │  top bar: menu, match name, game day, speed
│ 💰 12.4k  👥 3.1k  ⚙ 8.2k  ⛽ 2.0k  🔌 950 │  resource strip (tap → economy sheet)
│                                       │
│                GLOBE                  │
│                                       │
│ ⚠ 2 threats   ▸ Next: Armor Bn 2h14m  │  alert chip + next-event chip (GDD-LOOP-006)
├───────────────────────────────────────┤
│  🌍 Map  🏭 Build  🔬 Research  🤝 Diplo  💬 │  bottom nav (5 max)
└───────────────────────────────────────┘
```

Selection opens a **bottom sheet** (peek: summary; half: actions; full: details). The globe stays interactive above the sheet.

## 2. Screens

| ID | Screen | Purpose | States to design |
| --- | --- | --- | --- |
| SCR-001 | Boot / splash | Load, version check | loading, upgrade required, maintenance |
| SCR-002 | Home (Command Hub) | Active matches list with urgency badges, join match, season banner | empty (no matches), loading, error/offline |
| SCR-003 | Match finder | Queues: map, speed, casual/ranked | queue wait, no matches available |
| SCR-004 | Nation select | Choose a nation in a forming match | slot taken race condition |
| SCR-005 | In-match globe + HUD | Primary gameplay | connecting, resyncing, rest mode, eliminated |
| SCR-006 | Briefing | Since-last-check-in summary | nothing new |
| SCR-007 | Province sheet | Buildings, production, garrison | own / foreign / unknown |
| SCR-008 | Army sheet | Units, orders, standing orders, combat preview | in combat, moving, idle |
| SCR-009 | Production / construction queues | Queue management | empty, insufficient resources |
| SCR-010 | Research tree | Browse, queue | locked (day-gated) |
| SCR-011 | Diplomacy | Relations, treaties, proposals, coalition | no contacts |
| SCR-012 | Chat | Match / coalition / private | muted, reported, rate-limited |
| SCR-013 | World news | Daily events feed | |
| SCR-014 | Results | Placement, stats, rating, rewards | victory / defeat / eliminated |
| SCR-015 | Profile & service record | Level, medals, history | |
| SCR-016 | Store | Cosmetics, pass, subscription | purchase pending, failed, restored |
| SCR-017 | Campaign Pass | Tiers, operations | |
| SCR-018 | Settings | Account (link, delete), notifications, quality, language, accessibility, legal | |
| SCR-019 | Tutorial overlay | Guided steps | skip confirmation |
| SCR-020 | Dev: component gallery & debug | Internal builds only | |

Every screen must define **loading, empty, error/offline** states before implementation (Definition of Ready for UI stories).
