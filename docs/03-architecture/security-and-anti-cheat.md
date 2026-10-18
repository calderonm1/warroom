---
title: Security, privacy and anti-cheat
status: accepted
owner: architecture
last_reviewed: 2026-10-18
related: [NFR-SEC-001, NFR-PRIV-001, ADR-0009, ADR-0018, EP-23, docs/05-conventions/security-and-privacy.md]
---

# Security, privacy and anti-cheat

## 1. Threat model (STRIDE summary)

| Threat | Example | Mitigation |
| --- | --- | --- |
| Spoofing | Stolen refresh token | Rotation with reuse detection, device binding, short access tokens |
| Tampering | Modified client sends illegal commands | Server validates every command against authoritative state (SIM-003) |
| Repudiation | "I never attacked" | Command log with server timestamps |
| Information disclosure | Client memory reveals hidden armies | Server never sends non-visible data (SRV-005) |
| DoS | Command or connection floods | WAF, rate limits, per-connection queues, ALB limits |
| Elevation | Player calls admin API | Admin API on internal ALB plus IAM auth; separate identity plane |

## 2. Anti-cheat stance

War Room is turn-free but slow-paced and fully server-authoritative, so classic cheats (speed hacks, wallhacks, aimbots) have no effect. The remaining risks:

| Risk | Mitigation |
| --- | --- |
| Multi-accounting (one person, several nations in a match) | Device/IP heuristics at match join, same-coalition limits, report flow, ranked requires a linked account |
| Bots and automation scripts | Rate limits; standing orders make scripts pointless; anomaly detection on command cadence |
| Collusion across coalitions | Diplomacy logs, reporting, ranked-only penalties |
| Purchase fraud | Server-side receipt validation, refund webhooks revoke entitlements |
| Chat abuse | Filter, report, mute, block, moderation queue (EP-23) |

## 3. Privacy

| ID | Rule |
| --- | --- |
| PRV-001 | Data minimization: no email in game DB; IP addresses are stored only in transient logs (30 d). |
| PRV-002 | Analytics use a pseudonymous `player_id`. No advertising IDs collected, so no ATT prompt is needed (re-evaluate if ads or UA attribution are added). |
| PRV-003 | Data subject requests (export/delete) are automated through the DeletionWorker and an export job. |
| PRV-004 | Privacy policy and App Store privacy nutrition labels are maintained in `docs/legal/` (story `ST-23.3.1`). |
| PRV-005 | Chat is retained 90 days for moderation, then deleted. |

## 4. Secrets and keys

KMS for the token signing key (asymmetric, never exported). Secrets Manager for store and FCM credentials, rotated yearly or on suspicion. No secrets in environment manifests, logs or the repo.
