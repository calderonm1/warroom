---
title: Client architecture
status: accepted
owner: architecture
last_reviewed: 2026-10-18
related: [ADR-0003, ADR-0005, EP-02, EP-11, docs/05-conventions/unity.md]
---

# Client architecture

## 1. Layers

```
┌─────────────────────────────────────────────────────────────┐
│ Presentation  (MonoBehaviours, UI Toolkit views, shaders)   │  thin adapters only
├─────────────────────────────────────────────────────────────┤
│ View-models   (MatchViewModel, ArmyPanelVM, ...)            │  plain C#, observable state
├─────────────────────────────────────────────────────────────┤
│ Client services (MatchSession, CommandDispatcher, Content,  │  plain C#, testable in EditMode
│                  Auth, Store, Push, Telemetry, Settings)    │
├─────────────────────────────────────────────────────────────┤
│ Shared: WarRoom.Simulation (previews), WarRoom.Contracts    │
├─────────────────────────────────────────────────────────────┤
│ Platform adapters (IAP, push, keychain, haptics, deep links)│  interfaces + per-platform impls
└─────────────────────────────────────────────────────────────┘
```

## 2. Assemblies (`.asmdef`)

| Assembly | References | Notes |
| --- | --- | --- |
| `WarRoom.Contracts` | — | generated protobuf C# (UPM local package from `shared/`) |
| `WarRoom.Simulation` | Contracts | UPM local package from `shared/` |
| `WarRoom.Client.Core` | Contracts, Simulation | services, view-models; **no UnityEngine** references except `UnityEngine.CoreModule` types behind interfaces |
| `WarRoom.Client.Net` | Core | WebSocket transport (NativeWebSocket-style; WebGL-compatible), codec |
| `WarRoom.Client.Globe` | Core | renderer, camera, picking |
| `WarRoom.Client.UI` | Core | UI Toolkit screens and components |
| `WarRoom.Client.Platform.*` | Core | iOS, Android and Editor implementations |
| `WarRoom.Client.App` | all | composition root, boot flow |
| `*.Tests.EditMode` / `*.Tests.PlayMode` | — | tests |

## 3. Composition and state

- **Composition root** in `App/Boot.cs`: constructs services manually (pure DI, no reflection container). This is explicit and agent-readable.
- **State:** `MatchSession` holds the visible-state mirror and applies `StateDelta` in `server_seq` order. View-models subscribe to typed change events.
- **Commands:** `CommandDispatcher` assigns a `client_command_id`, sends, tracks pending, and reconciles ack or reject.
- **Navigation:** a stack-based `ScreenRouter` (UI Toolkit). The globe is always the root layer and screens overlay it.

## 4. Content delivery

- Addressables with remote catalog on CloudFront. The initial install includes the boot scene, UI, and the tutorial map. Other maps download on demand.
- The content pack data (YAML compiled to binary at build time) ships inside Addressables and is versioned. The client verifies the pack hash matches the match's pinned version.

## 5. Platform services

| Service | iOS | Android | Web (later) |
| --- | --- | --- | --- |
| Sign-in | Sign in with Apple (AuthenticationServices) | Google (Credential Manager) | Cognito hosted flows |
| IAP | Unity IAP (StoreKit 2) | Unity IAP (Play Billing) | Web store (Stripe), later |
| Push | FCM (APNs) | FCM | FCM web push |
| Secure storage | Keychain | Keystore | IndexedDB (encrypted) |
| Crash | Sentry | Sentry | Sentry |

## 6. App lifecycle

- **Resume:** reconnect, `Hello` with `last_server_seq`, then a delta replay or snapshot. Show the briefing if more than 15 minutes have passed.
- **Background:** flush telemetry, close the socket gracefully, and schedule no local timers (the server pushes).
- **Low memory:** drop Z3 assets, reduce terrain LOD, and unload non-current-match caches.
