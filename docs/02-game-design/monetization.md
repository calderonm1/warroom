---
title: Monetization design
status: review
owner: product
last_reviewed: 2026-10-18
related: [ADR-0010, R-MON-01, R-MON-02, R-MON-03, EP-21]
---

# Monetization design

The binding policy is [ADR-0010](../adr/0010-monetization-fair-by-design.md). This doc covers the product detail.

## 1. Catalog (launch)

| SKU family | Price tiers (USD) | Contents |
| --- | --- | --- |
| Cosmetic currency "Insignia" | 4.99 / 9.99 / 19.99 / 49.99 / 99.99 | Used only for cosmetics |
| Cosmetic sets (direct purchase or Insignia) | 2.99 to 14.99 | Unit skin set per branch, nation insignia, globe theme, commander portrait, HQ background |
| Campaign Pass (premium) | 9.99 per season; 19.99 bundle with +10 tiers | Premium track |
| Command Center subscription | 6.99 / month; 59.99 / year | Convenience perks (below) |
| Starter bundle (one-time) | 4.99 | Cosmetic set + Insignia + 7-day Command Center |
| Supporter pack | 29.99 | Exclusive "Founder" cosmetics (soft launch / launch only) |

## 2. Command Center perks (convenience, never power)

| Perk | Why it is not power |
| --- | --- |
| 6 parallel matches (vs 3) | Breadth, not strength within a match |
| Queue length 10 (vs 5) | Same throughput; fewer check-ins needed |
| 6 standing-order slots (vs 3) | Automation of actions any player can do manually |
| Advanced intel analytics (charts of known info) | Presentation of already-visible data (GDD-INT-007) |
| Full replays and match history | Post-match |
| Priority matchmaking | Faster fill, same match |

*Review flag:* standing-order slots and queue length are the closest to the power line. Monitor win-rate deltas between subscribers and non-subscribers in ranked; if the delta is > 2% after controlling for skill, move these perks to everyone (story `ST-21.4.2`).

## 3. Casual Logistics Boost (optional per queue)

- Earned through play (Operations) **and** purchasable with Insignia in casual queues only.
- Cap: at most 2 hours of total production/research time skipped per nation per game day. Usage is shown publicly in the match's nation list.
- Disabled by default at soft launch; enable via config experiment and measure retention impact.

## 4. Principles

| ID | Rule |
| --- | --- |
| GDD-MON-001 | Prices are shown in local currency through the store APIs; no obfuscated conversion (Insignia packs show the real-money value of items). |
| GDD-MON-002 | No randomized paid rewards. |
| GDD-MON-003 | No purchase prompts during combat or within 60 s of a loss. |
| GDD-MON-004 | Refunds and chargebacks revoke the entitlement; negative balances block further cosmetic spending, never gameplay. |
| GDD-MON-005 | Web store (post-launch) may offer the same SKUs at a discount where platform rules allow. |
