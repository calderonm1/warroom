---
title: Networking and protocol
status: accepted
owner: architecture
last_reviewed: 2026-10-20
related: [ADR-0006, EP-07, docs/05-conventions/api-and-contracts.md]
---

# Networking and protocol

## 1. Channels

| Channel | Transport | Encoding | Used for |
| --- | --- | --- | --- |
| Real-time | WSS `/v1/ws` | Protobuf `ClientEnvelope` / `ServerEnvelope` | commands, acks, state deltas. Chat (EP-15) and notifications (EP-19) join this channel later |
| Meta | HTTPS `/v1/*` | JSON (OpenAPI 3.1) | login, profile, match list, store, settings, telemetry |
| Content | HTTPS CloudFront | Addressables bundles + signed manifest | maps, art, content pack data |

## 2. Envelopes

Package `warroom.realtime.v1` in `shared/contracts/proto/warroom/realtime/v1/`. `make contracts-lint` runs buf format, STANDARD lint and FILE breaking against `main`.

| Message | Direction | Contents |
| --- | --- | --- |
| `ClientEnvelope` | client → server | `client_seq` plus one body |
| `ServerEnvelope` | server → client | `server_seq` plus one body |
| `Hello` | client | `token`, `client_version`, per-match `last_server_seq` (NET-001, NET-003, NET-007) |
| `SubscribeMatch` | client | `match_id` |
| `CommandSubmit` | client | `client_command_id` (UUIDv7) plus one command (NET-004). First command: `MoveArmy` |
| `Pong` | client | Reply to server `Ping` |
| `Welcome` | server | `session_id`, `server_time_unix_ms`, `signed_client_config` (NET-008) |
| `MatchSnapshot` | server | Full visible state for one match, plus `view_hash` |
| `StateDelta` | server | Visible sim events for one match, plus `view_hash` |
| `CommandAck` | server | `client_command_id`, `server_seq`, `game_time_ms` |
| `CommandRejected` | server | `client_command_id`, `reason_code` |
| `Ping` | server | Keepalive (NET-005) |
| `Error` | server | Codes in NET-009, including upgrade required |

`ClientEnvelope` field 13 (`chat`) and `ServerEnvelope` fields 15–16 (`chat`, `notification`) are reserved. The server sends `Ping`; the client answers with `Pong` (NET-005). `MoveArmy.mode` is a string: simulation.md names the parameter and does not list the values. Snapshot and delta payloads are opaque bytes until the simulation serialization schema exists.

## 3. Rules

| ID | Rule |
| --- | --- |
| NET-001 | The first client message must be `Hello` within 5 s, or the server closes the connection (code 4401). |
| NET-002 | Each subscribed match has its own `server_seq` stream. The client tracks the last applied seq per match. |
| NET-003 | On reconnect, the client sends `last_server_seq`. The server replays buffered deltas (last 10 minutes) or sends a fresh `MatchSnapshot`. |
| NET-004 | Commands are idempotent by `client_command_id`. Clients retry unacknowledged commands after reconnect. |
| NET-005 | The server sends `Ping` every 20 s. Clients missing two pings consider the connection dead. |
| NET-006 | Max message size: 256 KB client→server, 4 MB server→client (snapshots). Snapshots above 512 KB are zstd-compressed. |
| NET-007 | Version negotiation: `Hello.client_version` is checked against the minimum supported version (remote config). Too old means `Error{UPGRADE_REQUIRED}`. |
| NET-008 | All times on the wire are `GameTime` (int64 ms) plus a `server_time_unix_ms` anchor in `Welcome`, so clients compute countdowns locally. |
| NET-009 | WebSocket close codes: 4401 unauthenticated, 4403 banned, 4408 timeout, 4426 upgrade required, 4429 rate limited, 4500 server error. |

## 4. Bandwidth budget

| Situation | Target |
| --- | --- |
| Idle subscribed match | < 1 KB/min |
| Active war, 64 players | < 20 KB/min per client |
| Full snapshot, 64-player world map | < 400 KB compressed |

## 5. Mobile realities

- Apps are suspended in the background, so the client must assume disconnection on every resume and resync quickly (target: playable < 1.5 s after resume on 4G).
- Push notifications cover the offline gap (ADR-0019).
- Clients must handle network switches (Wi-Fi to cellular) through reconnect with exponential backoff and jitter (0.5 s base, 30 s cap).
