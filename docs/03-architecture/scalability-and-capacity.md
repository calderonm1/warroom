---
title: Scalability and capacity model
status: review
owner: architecture
last_reviewed: 2026-10-18
related: [NFR-SCALE-001, NFR-PERF-002, EP-25]
---

# Scalability and capacity model

These are initial estimates to validate with load tests (`EP-25`). Update with measured numbers.

## 1. Assumptions

| Parameter | Value |
| --- | --- |
| Average active matches per DAU | 1.6 |
| Average players per match | 32 |
| Concurrent connected share of DAU at peak | 12% |
| Commands per connected player per minute (avg / war peak) | 2 / 15 |
| Sim steps per active match per real minute (1x / 4x) | 30 / 150 |
| Mean step cost (64 nations) | 0.3 ms target |

## 2. Back-of-envelope (100k DAU)

| Quantity | Estimate |
| --- | --- |
| Matches running | 100k × 1.6 ÷ 32 ≈ **5,000** (NFR-SCALE-001) |
| Peak CCU | ≈ **12,000** connected |
| Command rate at peak | 12k × 2/min ≈ 400/s (war peaks 3,000/s) |
| Sim CPU | 5,000 × ~60 steps/min × 0.3 ms ≈ 1.5 core-seconds per second, so **2 cores** plus headroom; memory dominates |
| Match memory | ~4 to 20 MB each, so 20 to 100 GB across the cluster, which means grains must deactivate when idle (SRV-004) |
| Gateways | 12k connections, 2 tasks minimum (HA) |

Takeaway: War Room is **memory- and I/O-bound, not CPU-bound**. Idle deactivation, compact state, and batched command-log writes are the key levers.

## 3. Scaling levers

1. Horizontal silos (Orleans rebalances activations).
2. Grain deactivation for idle matches (snapshot to S3).
3. Command-log write batching (5 ms window) and monthly partitioning.
4. Aurora read replicas for meta reads; Valkey for hot reads.
5. Multi-region (later): matches are region-pinned at creation (queue per region); global services (accounts, store) stay in the home region.

## 4. Load testing

- NBomber scenarios in `server/tests/WarRoom.Server.LoadTests`: connection storm, war-peak commands, resume storm (10k reconnects in 60 s), match creation burst.
- AI-only soak matches at 4x to exercise the full sim.
- Run in staging before each milestone exit from M3 onward.
