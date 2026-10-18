---
title: Glossary
status: accepted
owner: product
last_reviewed: 2026-10-18
related: [docs/05-conventions/naming.md]
---

# Glossary

Use these terms exactly, in code, docs, UI copy and telemetry. If you need a new domain term, add it here first. Code identifiers are shown in `code`.

| Term | Code | Definition |
| --- | --- | --- |
| Match | `Match` | One game instance from lobby to results. Has a map, a player count, a speed tier, and a fixed set of nations. |
| Map | `MapDefinition` | Content describing provinces, nations, coalition size and victory settings for a match. |
| Nation | `Nation` | A playable country slot in a match. Controlled by a player, the AI, or nobody (neutral). |
| Player | `Player` | A human account. One player controls at most one nation per match. |
| Commander | (UI only) | UI term for the player in-match ("Commander, your units have arrived"). |
| Coalition | `Coalition` | A formal team of nations with a size cap; it shares victory and vision. |
| Treaty | `Treaty` | A bilateral agreement between nations (passage, shared vision, trade, non-aggression). |
| Province | `Province` | The atomic territory unit. Land provinces have an owner, terrain and buildings. |
| Sea zone | `SeaZone` | A water territory used for naval movement and fishing/oil resources. Not ownable. |
| Urban province | `Province.IsUrban` | A province with a city: produces more, holds high-tier buildings, and is worth more VP. |
| Capital | `Province.IsCapital` | A nation's core urban province. Losing it applies morale penalties. |
| Strategic site | `StrategicSite` | A special location (refinery, launch site, research lab) with bonuses and VP. |
| Unit | `Unit` | A single military entity (an MBT company, a fighter squadron). |
| Army / Stack | `Army` | A group of units that moves and fights together. UI term: "Army". |
| Order | `Command` | A player instruction submitted to the server (move, build, research, ...). In code always `Command`. |
| Standing order | `StandingOrder` | A conditional rule that triggers commands automatically ("retreat if HP < 40%"). |
| Game time | `GameTime` | Simulation time. At 1x, one game day equals one real day. |
| Speed tier | `SpeedTier` | Time multiplier for a match: `1x`, `2x`, `4x`. |
| Tick | `EconomyTick` | Periodic economic update (every game hour). Movement and combat are event-driven, not ticked. |
| Combat round | `CombatRound` | Discrete combat resolution step between engaged armies. |
| Fog of war | `Visibility` | Server-computed per-nation visibility of provinces, units and intel. |
| Intel | `Intel` | Information about other nations obtained through scouting, spies or shared vision. |
| Victory points | `VictoryPoints` (VP) | Score from provinces and sites; reaching the threshold wins. |
| Morale | `Morale` | Per-province stability that scales production and can trigger revolts. |
| Resource | `ResourceType` | Treasury, manpower, materials, fuel, electronics, rare earths. |
| Building | `Building` | A province upgrade (factory, barracks, airbase, ...). |
| Research | `ResearchItem` | A tech unlocked over time that enables or upgrades units/buildings. |
| Doctrine | `Doctrine` | A nation-wide playstyle choice that modifies units and research. |
| AI nation | `AiController` | A nation controlled by the server AI (bot). |
| Inactivity takeover | `InactivityPolicy` | When a player has been inactive past the threshold, AI takes control of their nation. |
| Check-in | (telemetry) | A short play session; the core rhythm of War Room. |
| Briefing | `Briefing` | Server-generated summary of what happened since your last check-in. |
| Content pack | `ContentPack` | A versioned bundle of content (nations, units, maps) defining a setting. |
| Snapshot | `MatchSnapshot` | Serialized full match state at a point in game time. |
| Command log | `CommandLog` | Ordered, append-only log of accepted commands for a match; with the seed it reproduces the match. |
| Replay | `Replay` | Snapshot + command log, used for debugging, tests and spectating. |
| Queue | `MatchQueue` | Matchmaking pool: `casual` or `ranked`, per map type and speed tier. |
| Season | `Season` | A fixed period for ranked ratings and the seasonal pass. |
| Campaign Pass | `SeasonPass` | The seasonal pass (free and premium tracks). |
| Command Center | `Subscription` | The convenience subscription. |
| Gateway | `Gateway` | The server process that terminates player WebSockets and routes to grains. |
| Grain | `Grain` | An Orleans virtual actor (`MatchGrain`, `PlayerGrain`, ...). |
| Silo | `Silo` | An Orleans host process. |
