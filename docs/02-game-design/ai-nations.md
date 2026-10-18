---
title: AI nations and inactivity
status: review
owner: design
last_reviewed: 2026-10-18
related: [PR-005, GDD-MATCH-004, EP-17]
---

# AI nations and inactivity

| ID | Rule |
| --- | --- |
| GDD-AI-001 | AI nations run **inside the simulation** using the same commands as players (no cheats, no hidden information). |
| GDD-AI-002 | AI personalities (content-defined): *Passive* (defends, rarely expands), *Opportunist* (attacks weak neighbours), *Aggressor* (expands actively), *Caretaker* (inactive-player stand-in: defends only, keeps economy running). |
| GDD-AI-003 | Difficulty is per map and queue: practice matches allow Easy, Normal and Hard; online matches use Normal. AI difficulty changes decision quality and reaction time, never resource bonuses. |
| GDD-AI-004 | AI planning runs on the daily tick (strategic) and economy tick (tactical), using utility-based decision making with deterministic tie-breaking. |
| GDD-AI-005 | A human taking over an AI nation (late join, GDD-MATCH-001) inherits its full state. |
| GDD-AI-006 | AI performance budget: ≤ 2 ms per AI nation per economy tick on server hardware. |
| GDD-AI-007 | AI-only matches double as **automated playtests and soak tests** (balance telemetry, determinism, performance). |
