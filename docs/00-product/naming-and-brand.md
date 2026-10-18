---
title: Naming, brand and identifiers
status: accepted
owner: product
last_reviewed: 2026-10-18
related: [BR-001, ST-01.4.1, ST-01.4.2]
---

# Naming, brand and identifiers

## Decision

- **Product name:** War Room
- **Store title (confirmed by the project owner):** **War Room: Global Theater** (24 characters, within the 30-character limits of both the App Store name and the Google Play title)
- **App Store subtitle / Play short description lead (confirmed):** "Real-Time Global Strategy"
- **Internal names:** `War Room` (prose), `warroom` (identifiers, packages, domains), `wr` (short prefix for cloud resources), `WarRoom` (C# root namespace)

The store title and subtitle are decided. What remains open is clearance, not naming: the trademark search, store name reservation and fallback subtitles below are a safety net in case clearance surfaces a conflict (tracked in `ST-01.4.1`).

## Why a subtitle is needed

Findings from a preliminary search (2026-10-18). This is not legal advice.

| Finding | Risk | Notes |
| --- | --- | --- |
| **"War Room" on Steam** (app 1175880), a single-player RTS set in Afghanistan by Wastelands Interactive / Binge Gaming, released Nov 2020, $29.99, roughly 20 to 50k owners, very low current CCU | **Medium.** Same name, same genre family, so possible unregistered (common-law) rights and store search confusion | Different platform (PC) and model (premium single-player). A distinct subtitle and brand mark reduce confusion. |
| USPTO "WAR ROOM" (VirnetX), live, **Class 38** telecom/conferencing | Low | Different goods/services class |
| USPTO "WAR ROOM" (Business Enterprise Mapping), Class 41, **dead** | None | — |
| USPTO "THE WAR ROOM" (Monument Traders), Class 41 finance newsletters, **abandoned** | None | — |
| "War Room" is a common phrase (2015 film, political media shows) | Medium | A common phrase makes a **weak** mark alone; the subtitle and logo strengthen it |
| No Google Play app titled exactly "War Room" found in the genre | Low | App Store names must be unique; this is only confirmed by reserving |

## Required actions before soft launch

These are tracked in backlog epic `EP-01` (feature `FE-01.4`) and `EP-25`.

1. **Reserve store names early.** Creating the App Store Connect app record reserves the name. Create the Play Console app as soon as the developer account exists.
2. **Professional trademark clearance.** Commission a knockout search and opinion from a trademark attorney for the US (USPTO) and EU (EUIPO) in **Nice classes 9** (downloadable game software) **and 41** (online game services). File for "WAR ROOM: GLOBAL THEATER" (word mark), and optionally the logo.
3. **Domains and handles.** Check and secure a primary domain (for example `warroom.game`, `playwarroom.com` or `warroomgame.com`) and social handles (`@playwarroom`).
4. **Fallback subtitles**, in order, if conflicts appear: "War Room: World Command", "War Room: Global Conflict", "War Room: Command the World".

## Identifiers

| Thing | Value | Notes |
| --- | --- | --- |
| Bundle ID (iOS) / applicationId (Android) | `TBD.warroom` (for example `com.<studio>.warroom`) | Needs the studio/legal entity reverse domain. **Permanent once published.** See [open questions](../07-planning/open-questions.md). |
| C# root namespace | `WarRoom` | `WarRoom.Simulation`, `WarRoom.Server.Gateway`, `WarRoom.Client.Globe` |
| Protobuf package root | `warroom` | `warroom.match.v1` |
| AWS resource prefix | `wr-<env>-` | `wr-dev-gateway`, `wr-prod-aurora` |
| AWS account names | `warroom-<purpose>` | `warroom-dev`, `warroom-staging`, `warroom-prod` |
| Repository | `warroom` | Monorepo |
| Telemetry event namespace | `wr.` | `wr.match.joined` |

## Brand direction (summary; see the [design system](../04-ux/design-system.md))

- **Mood:** a modern joint operations centre at night. Dark slate, crisp data overlays, a glowing globe, restrained accent colours.
- **Voice:** terse, confident, military-briefing style. Never glorifies real-world atrocities. No real-world political figures.
- **Logo concept:** wordmark "WAR ROOM" in a condensed geometric typeface, with a globe-meridian motif in the "O".
