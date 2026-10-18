---
title: Market and technology research (October 2026)
status: accepted
owner: product
last_reviewed: 2026-10-18
related: [ADR-0003, ADR-0007, ADR-0010, ADR-0011]
---

# Market and technology research (October 2026)

This research informed the founding ADRs. Re-run it before soft launch (story `ST-25.1.1`). Each finding has an ID so ADRs and GDD sections can cite it.

## 1. Match size

| ID | Finding | Source |
| --- | --- | --- |
| R-SIZE-01 | Conflict of Nations (now **Supremacy: World War 3**) already runs mixed sizes: 100-player maps (Overkill), 50 (Blood & Oil), alliance maps from 2v2 to 16v16, and small tutorial maps. | [CoN wiki: Campaign Types](https://wiki.conflictnations.com/Campaign_Types) |
| R-SIZE-02 | The same publisher's newest title, **Supremacy: Warhammer 40,000** (iOS, May 2026), chose **32 to 64 player** matches lasting days to weeks. | [Supremacy WH40K FAQ](https://playsupremacy.com/en/news/wh-faq), [iOS launch](https://www.playsupremacy.com/en/news/warhammer40k/i-os-availability-update) |
| R-SIZE-03 | Players say small maps make units "more decisive" and less overwhelming; some request 15 to 20 player regional maps. | [r/ConflictofNations](https://www.reddit.com/r/ConflictofNations/comments/1olxnf4/smaller_maps_devs_suggestion/) |
| R-SIZE-04 | Large maps collapse into a few blocs anyway ("100 players devolves into 5v5v5"). Smaller maps only work when activity is guaranteed. | [r/ConflictofNations](https://www.reddit.com/r/ConflictofNations/comments/1givl7u/players_per_lobby/) |

**Implication:** launch with 16 and 32 player regional maps plus one 64-player world map. Make player count pure configuration. Inactivity takeover by AI is essential to keep matches alive.

## 2. Match length and session patterns

| ID | Finding | Source |
| --- | --- | --- |
| R-TIME-01 | The genre standard remains matches of days to weeks (Supremacy franchise; WH40K "weeks of real time"). | Stillfront AR 2025; WH40K FAQ |
| R-TIME-02 | Strategy had the strongest session-length growth on mobile in 2025 (31.7 to 37.5 min) and +57% session count. | [Adjust 2026 via GameDev Reports](https://gamedevreports.substack.com/p/adjust-gaming-app-insights-report) |
| R-TIME-03 | Mid-core players play many short sessions (6 to 7 per day; 4X top titles 8 to 12+ per day). Top-tier games average 5 to 9 minutes per session. | [GameAnalytics 2025](https://gameindustrylibrary.com/documents/gameanalytics-mobile-gaming-benchmarks-2025); [Funtap 4X data](https://investgame.net/wp-content/uploads/2026/02/2026-02-06-VietnamMobile_Gaming_2025.pdf) |
| R-TIME-04 | Fast speeds (4x+) are popular but exhausting: "you have to be online pretty much 24/7". | [r/ConflictofNations](https://www.reddit.com/r/ConflictofNations/comments/1swd92b/will_they_bring_back_8x_and_10x_games/) |
| R-TIME-05 | Broader 4X players (working adults) increasingly want shorter games and less micromanagement. | [r/4Xgaming](https://www.reddit.com/r/4Xgaming/comments/1uosjco/arent_short_4x_games_contrary_to_the_fantasy/) |

**Implication:** persistent real-time matches as the primary mode. Design every system for 5 to 10 minute check-ins (standing orders, queues, briefings, notifications). Add a 1 to 2 hour skirmish mode post-launch.

## 3. Competitive landscape

| ID | Finding | Source |
| --- | --- | --- |
| R-COMP-01 | The Supremacy franchise earned SEK 880M in 2025 (+8% organic). Twin Harbour Interactive (Bytro + Dorado merged) reports 2M+ MAU across three titles and 90M lifetime players. | [Stillfront AR 2025](https://www.stillfront.com/en/wp-content/uploads/sites/2/2026/02/0417_Stillfront_AR_25_eng.pdf), [GamesMarket](https://www.gamesmarket.global/merger-bytro-and-dorado-games-become-twin-harbour-interactive-36b207c88a443d98a5b43cdc02fd967c/) |
| R-COMP-02 | Supremacy: WW3 US iOS weekly revenue fell from $221K to $71K and active users from 76K to 41K during Q3 2025. | [Sensor Tower](https://sensortower.com/blog/2025-q3-ios-top-5-military%20games-revenue-us-600f8d2b241bc16eb89ce40d) |
| R-COMP-03 | The dominant player complaint in 2026 is pay-to-win "gold" spending (instant units, elite units, officers). Players ask for no-gold queues (and would pay for them) and for spending caps. | [Reddit](https://www.reddit.com/r/ConflictofNations/comments/1ramk63/gold/), [Supremacy forums](https://www.playsupremacy.com/en/forums/world-war-3/world-war-3-suggestions/golding-mrsmnea6), [Reddit](https://www.reddit.com/r/ConflictofNations/comments/1w6adrw/i_genuinely_cant_play_anymore_the_game_has_become/) |
| R-COMP-04 | New 2026 entrants: Order of Kings (RTS+SLG, real 3D terrain combat), Three Kingdoms: Grand Strategy. None offers a modern setting on a 3D globe. | [Pocket Gamer](https://www.pocketgamer.com/order-of-kings/out-now-on-mobile/) |

**Implication:** a fair, modern, globe-first game is a clear positioning gap.

## 4. Engine

| ID | Finding | Source |
| --- | --- | --- |
| R-ENG-01 | Unity holds roughly 48% of active mobile developers and powers about 68 to 70% of top-grossing mobile games. | [AppRadar 2026](https://appradar.com/blog/mobile-game-engines-development-platforms), [VoxBooster](https://voxbooster.com/blog/game-engine-market-share-statistics-2026/) |
| R-ENG-02 | GDC 2026 overall: Unreal 42%, Unity 30%. But in F2P, Unity leads 38% vs 31%; Unreal leads in premium, AA and AAA. | [AUTOMATON / GDC 2026](https://automaton-media.com/articles/newsjp/unreal-engine-20260311-428296/) |
| R-ENG-03 | Unity 6.3 LTS is current (supported to Dec 2027). CoreCLR replaces Mono in Unity 6.8. Players remain .NET Standard 2.1 / C# 9 until Unity 7.x brings .NET 10. | [Unity 6 support](https://unity.com/releases/unity-6/support), [CoreCLR update Oct 2026](https://discussions.unity.com/t/coreclr-scripting-and-net-update-october-2026/1738338) |
| R-ENG-04 | Unity now ships an official CLI with an MCP server (`unity mcp`) and agent skills, which suits an AI-first workflow. | [Unity CLI docs](https://docs.unity.com/en-us/unity-cli/replace-mcp-server-unity-cli) |
| R-ENG-05 | Cesium for Unity (photoreal 3D tiles) has long-standing poor Android performance (3 to 18 fps reports; issue open since 2023). | [GitHub #349](https://github.com/CesiumGS/cesium-unity/issues/349) |

## 5. Cloud

| ID | Finding | Source |
| --- | --- | --- |
| R-CLD-01 | AWS is used by 57% of studios that use a cloud platform (Omdia 2026), the clear leader. Google Cloud and Azure contest second place. | [Omdia Market Radar 2026](https://staticintl.cloudcachetci.com/yehe/backend-news/Omdia%20Market%20Radar%20Cloud%20Platforms%20for%20Games%20%202026.pdf) |
| R-CLD-02 | GameLift targets session-based dedicated servers (FPS-like). Bandwidth has been free on GameLift Gen-6+ since June 2026. | Omdia 2026; [GameLift pricing](https://aws.amazon.com/gamelift/servers/pricing/) |
| R-CLD-03 | Azure PlayFab is client-driven by default, and Microsoft's games division was heavily restructured in 2026. | [Metaplay comparison](https://www.metaplay.io/comparisons/server-authoritative-vs-client-authoritative), Omdia 2026 |
| R-CLD-04 | Cognito Essentials: 10,000 MAU free tier (does not expire); supports Sign in with Apple and Google. | [Cognito pricing](https://aws.amazon.com/cognito/pricing/) |
| R-CLD-05 | AWS Labs publishes MCP servers (CloudWatch, the official AWS MCP server) usable with read-only IAM roles. | [awslabs/mcp](https://awslabs.github.io/mcp/servers/cloudwatch-mcp-server) |

## 6. Monetization

| ID | Finding | Source |
| --- | --- | --- |
| R-MON-01 | Strategy/mid-core: about 90% of revenue from IAP. Battle pass and live-ops events are the standard second layer. Subscriptions are a small but growing layer (about 7% in three-stream games). | [GGA 2026](https://gamegrowthadvisor.com/blog/2026-04-02-f2p-monetization-models-comparison-2026/) |
| R-MON-02 | US iOS strategy payers spend about $600 by D90, above casino. iOS ARPPU is 4 to 5 times Google Play. | [AppMagic](https://appmagic.rocks/blog/IAPs-beyond-99) |
| R-MON-03 | Best practice: avoid selling raw power; sell time-savers, cosmetics and convenience. | [GGA 2026](https://gamegrowthadvisor.com/blog/2026-04-02-f2p-monetization-models-comparison-2026/), [Tekrevol](https://www.tekrevol.com/blogs/how-to-build-mobile-strategy-game/) |
| R-MON-04 | Top-grossing games run layered live ops: daily missions, feature events (passes), and large seasonal events. | [Sensor Tower live ops 2025](https://sensortower.com/blog/top-grossing-mobile-games-live-ops-strategies-2025-report) |

## 7. Naming

See [naming and brand](../00-product/naming-and-brand.md).
