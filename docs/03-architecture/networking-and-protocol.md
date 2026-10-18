---
title: Networking and protocol
status: accepted
owner: architecture
last_reviewed: 2026-10-18
related: [ADR-0006, EP-07, docs/05-conventions/api-and-contracts.md]
---

# Networking and protocol

## 1. Channels

| Channel | Transport | Encoding | Used for |
| --- | --- | --- | --- |
| Real-time | WSS `/v1/ws` | Protobuf `ClientEnvelope` / `ServerEnvelope` | commands, acks, state deltas, chat, presence, in-app notifications |
| Meta | HTTPS `/v1/*` | JSON (OpenAPI 3.1) | login, profile, match list, store, settings, telemetry |
| Content | HTTPS CloudFront | Addressables bundles + signed manifest | maps, art, content pack data |

## 2. Envelopes

```proto
// shared/contracts/proto/warroom/net/v1/envelope.proto (sketch)
message ClientEnvelope {
  uint64 client_seq = 1;          // per-connection, monotonically increasing
  oneof body {
    Hello hello = 10;             // token, client version, last_server_seq per match
    SubscribeMatch subscribe = 11;
    CommandSubmit command = 12;   // client_command_id (UUIDv7) + warroom.match.v1.Command
    ChatSend chat = 13;
    Ping ping = 14;
  }
}

message ServerEnvelope {
  uint64 server_seq = 1;          // per-match stream sequence (for resync)
  oneof body {
    Welcome welcome = 10;         // session info, server time, signed client config
    MatchSnapshot snapshot = 11;  // full visible state (on subscribe/resync)
    StateDelta delta = 12;        // SimEvents filtered by visibility
    CommandAck ack = 13;
    CommandRejected rejected = 14;
    ChatMessage chat = 15;
    Notification notification = 16;
    Pong pong = 17;
    Error error = 18;
  }
}
```

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
