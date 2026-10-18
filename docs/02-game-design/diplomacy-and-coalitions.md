---
title: Diplomacy, coalitions and chat
status: review
owner: design
last_reviewed: 2026-10-18
related: [PR-006, EP-15, EP-23]
---

# Diplomacy, coalitions and chat

## 1. Relations

| State | Meaning |
| --- | --- |
| War | Units engage automatically; provinces capturable |
| Ceasefire | No combat; 24 game-hour minimum before declaring war again |
| Peace (default for AI neighbours at start) | No combat; declaring war costs morale |
| Right of passage | Units may traverse the other's territory |
| Shared vision | See what the other nation sees |
| Coalition | Formal team (see below) |

## 2. Coalitions

| ID | Rule |
| --- | --- |
| GDD-DIP-001 | Coalition size cap is per map (2 to 4). Coalitions share victory, vision, chat and research visibility. |
| GDD-DIP-002 | Creating a coalition requires ≥ 2 nations; invites must be accepted; members may leave (24 game-hour cooldown before joining another coalition). |
| GDD-DIP-003 | Coalition leader roles: founder can invite and kick; any member can propose a coalition-wide war declaration (majority vote). |
| GDD-DIP-004 | Coalition victory requires the coalition to exist at match end. Last-minute joins (within the final 3 game days) do not share victory. |

## 3. Treaties and messaging

| ID | Rule |
| --- | --- |
| GDD-DIP-010 | Treaties: right of passage, shared vision, trade agreement (recurring resource transfer), non-aggression pact (breaking it costs morale and is announced to all). |
| GDD-DIP-011 | **Diplomatic messages** are structured proposals (accept, decline, counter), separate from free chat, so they are clear on mobile. |
| GDD-DIP-012 | Chat channels: match (all), coalition, and private 1:1. Profanity filter, report, mute and block (EP-23). Rate limit 1 msg/s. |
| GDD-DIP-013 | **Map pings:** coalition members can place temporary markers ("Attack here", "Defend", "Enemy spotted") that appear on teammates' globes and generate a notification. |
| GDD-DIP-014 | Newspaper / world news feed: a daily, server-generated summary of major world events (wars declared, capitals fallen, coalitions formed). |
