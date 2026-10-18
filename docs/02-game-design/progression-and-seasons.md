---
title: Progression, ranked, seasons and live ops
status: review
owner: design
last_reviewed: 2026-10-18
related: [ADR-0010, ADR-0020, EP-18, EP-22]
---

# Progression, ranked, seasons and live ops

## 1. Account progression (cosmetic only)

| ID | Rule |
| --- | --- |
| GDD-PROG-001 | **Commander level** (XP from match participation, days played, objectives) unlocks cosmetics and profile badges. It never unlocks power. Exception: new players unlock maps gradually (16-player first) to protect onboarding. |
| GDD-PROG-002 | **Service record:** lifetime stats, medals (for example "Held the capital through a 5-day siege") and match history. |

## 2. Ranked

| ID | Rule |
| --- | --- |
| GDD-PROG-010 | Glicko-2 rating per season. Placement by final coalition rank plus individual contribution (VP share, survival). |
| GDD-PROG-011 | Divisions: Recruit, Lieutenant, Captain, Major, Colonel, General, Marshal. End-of-season cosmetic rewards. |
| GDD-PROG-012 | Inactive (AI-taken-over) players receive the worst placement in that match. |

## 3. Seasons and Campaign Pass

| ID | Rule |
| --- | --- |
| GDD-PROG-020 | Season length is about 10 weeks. Each has a theme (for example "Arctic Front"), a new map or mode rotation, and cosmetic sets. |
| GDD-PROG-021 | Campaign Pass: 50 tiers; free track plus premium track. XP from daily and weekly **operations** (missions such as "Capture 3 provinces", "Win an air battle", "Check in on 5 different days"). Operations must be achievable through normal play; no forced modes. |
| GDD-PROG-022 | Premium track rewards: cosmetics, profile items, and cosmetic currency only. Never units, resources or speed-ups. |

## 4. Live ops calendar (template)

| Layer | Cadence | Examples |
| --- | --- | --- |
| Recurring | daily/weekly | operations, login streak cosmetics |
| Feature events | 2 to 3 weeks | limited-time map (Cold War Berlin), special modifiers (no air power) |
| Large events | once a season | world event map with community-wide objectives |

All event configs are AppConfig documents (ADR-0020) validated by schema. Events never alter running matches.
