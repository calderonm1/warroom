---
title: Core loop and check-in play
status: review
owner: design
last_reviewed: 2026-10-18
related: [PR-003, R-TIME-03, R-TIME-04, EP-19]
---

# Core loop and check-in play

## Loops

| Loop | Cadence | Player activity |
| --- | --- | --- |
| **Check-in loop** | 5 to 10 min, 4 to 10 times per day | Read the briefing, respond to threats, queue production and research, issue moves, chat with the coalition |
| **Day loop** | 1 game day (24 h at 1x) | Research unlocks, economic growth, campaign objectives, VP standings |
| **Match loop** | 1 to 4 weeks | Expand, ally, fight, win or lose, then results and rating |
| **Season loop** | ~10 weeks | Ranked season, Campaign Pass, season events and cosmetics |

## Check-in loop detail

1. **Open app**, which shows the **Briefing** (GDD-LOOP-001) for the most urgent match.
2. **Respond:** the threats list jumps the camera to each alert.
3. **Plan:** queues (production, construction, research) with ETAs.
4. **Command:** move, attack, set standing orders.
5. **Coordinate:** coalition chat and shared map pings.
6. **Leave:** confirm the "Next important event" countdown.

## Rules

| ID | Rule |
| --- | --- |
| GDD-LOOP-001 | **Briefing:** on opening a match after ≥ 15 min away, show a summary of events since the last check-in: battles, captures, completions, diplomatic messages, threats detected. Each item links to its location. |
| GDD-LOOP-002 | **Queues:** production, construction and research each support a queue (default 5 items each, 10 with Command Center subscription; this is convenience, not power, since the total throughput is identical). |
| GDD-LOOP-003 | **Standing orders** per army: *Hold* / *Retreat when HP < X%* / *Engage targets of type T in range* / *Return to base when fuel < X%* / *Patrol between A and B*. Default 3 slots per nation, 6 with subscription. AI nations use the same system. |
| GDD-LOOP-004 | **Defensive automation:** every province with an air defence or garrison automatically engages hostile units entering range. There is no "must be online to defend" case. |
| GDD-LOOP-005 | **Notifications** (opt-in per category): under attack, army arrived, production/research complete, diplomatic proposal, coalition ping, match ending soon. Quiet hours default 23:00 to 07:00 local; critical "capital under attack" can bypass if the user opts in. |
| GDD-LOOP-006 | **Next important event:** HUD chip that always shows the soonest owned-event ETA ("Armor Bn arrives Kyiv in 2h 14m"). |
| GDD-LOOP-007 | **Rest mode:** a player may declare up to 8 h rest per game day. During rest, their units get a +25% defence bonus and cannot launch attacks; their provinces cannot be targeted by missiles. Rest is visible to others. (Prevents "3 a.m. wipe" while keeping the world live.) |
| GDD-LOOP-008 | **Pacing target:** in a normal day, a player who checks in 4 times at 1x should not lose a province they could have defended with reasonable standing orders. Validated by AI-simulation playtests. |
