---
title: "ADR-0010: Fair-by-design free-to-play monetization"
status: accepted
owner: product
last_reviewed: 2026-10-18
related: [BR-013, R-MON-01, R-MON-02, R-MON-03, R-COMP-03, docs/02-game-design/monetization.md]
---

# ADR-0010: Fair-by-design monetization

- **Date:** 2026-10-18
- **Deciders:** project owner

## Context

Strategy is the highest-spending mobile genre (R-MON-02) and IAP-led (R-MON-01). The market leader's top complaint is pay-to-win (R-COMP-03), which drives veterans away. Fair monetization is a differentiator (pillar P2), but it must still fund the game.

## Decision

1. Model: **free-to-play**. Revenue layers, in priority order:
   1. **Cosmetics** (unit skins, nation insignia, globe themes, commander portraits, HQ backgrounds, emotes)
   2. **Campaign Pass** (seasonal; free and premium tracks; cosmetic and convenience rewards)
   3. **Command Center** subscription (convenience: more parallel matches, advanced intel analytics, extended standing-order slots, match history and replays, priority queue)
   4. **Starter and supporter bundles** (cosmetics plus pass)
2. **Ranked queues are power-neutral:** nothing purchasable affects combat, economy, research or information in ranked matches.
3. **Casual queues may allow limited acceleration** ("Logistics Boost": speed-ups on production and research) with hard caps per match day, displayed openly to all players in the match. This is configured per queue in AppConfig and can be disabled entirely.
4. **No loot boxes or randomized paid items.** No purchasable units, officers or resources.
5. **No ads** at launch. Rewarded ads may be evaluated later, only for cosmetic currency.
6. Purchases are validated server-side (App Store Server API, Google Play Developer API). Entitlements live on the server.

## Alternatives considered

| Option | Why not |
| --- | --- |
| Premium currency speed-ups without caps (genre standard) | Pay-to-win; the main reason players leave competitors |
| Premium (paid) app | High risk on mobile; limited discovery |
| Ads-led | Low ARPDAU for strategy; hurts premium feel |

## Consequences

Lower revenue per whale than competitors. Better retention, reviews and marketing message, and lower regulatory risk (loot box laws). Requires a strong cosmetics pipeline and live ops cadence (EP-21, EP-22).

## Compliance

Server rule: the entitlement check rejects any purchasable effect in ranked match contexts (`ST-21.2.3`). Content schema forbids `purchasable` on gameplay-affecting items. Review checklist item: "Does this purchasable change match outcomes?"
