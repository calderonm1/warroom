---
title: Local development setup
status: review
owner: ops
last_reviewed: 2026-10-18
related: [ops/environments/local.yaml, EP-02, docs/06-environments/device-testing.md]
---

# Local development setup

## 1. Workstation prerequisites

| Tool | Version | Why | Required for |
| --- | --- | --- | --- |
| macOS (Apple Silicon recommended) | 15+ | **iOS builds require Xcode on macOS** | iOS builds |
| Xcode | latest stable supported by Unity 6.3 | iOS build, simulator, device deploy | iOS |
| Unity Hub + Unity 6.3 LTS (`6000.3.x`) | pinned in `client/ProjectSettings/ProjectVersion.txt` | client | client |
| Unity modules | iOS Build Support, Android Build Support (incl. OpenJDK, SDK & NDK) | builds | client |
| Unity CLI | latest | agent control of the Editor, `unity mcp` | AI workflow |
| Android Studio | latest stable | emulator (AVD), Logcat, profilers | Android |
| .NET SDK | 10.0.x (pinned in `global.json`) | server, shared | server |
| Docker Desktop / OrbStack | latest | Postgres, Valkey | server |
| uv | latest | repo tooling | all |
| Terraform | 1.10+ (pinned in `.terraform-version`) | infra | infra |
| AWS CLI v2 + SSO profile | latest | cloud access | cloud |
| buf | pinned | protobuf | contracts |
| Git LFS | latest | assets | all |

Windows or Linux works for server, Android and Editor work. iOS builds then need macOS CI runners or a cloud Mac (see [device testing](device-testing.md)).

## 2. First-time setup (target: one command per area)

```bash
git clone <repo> warroom && cd warroom
git lfs install && git lfs pull
make setup                # repo tooling (uv sync)
make server-setup         # dotnet restore, docker pull     (added by ST-02.2.1)
make client-setup         # Unity project checks, packages  (added by ST-02.3.1)
cp .env.example .env      # local overrides                 (added by ST-02.4.1)
```

## 3. Daily loop

```bash
make dev-up               # Postgres + Valkey in Docker            (ST-02.4.1)
make server-dev           # DevHost: gateway+silo+workers, hot reload (ST-02.4.2)
make sim-test             # fast simulation tests                  (ST-05.1.1)
# Unity: open client/ in Editor → Boot scene → Play (connects to local DevHost)
make check                # before committing
```

## 4. Local service map

| Service | URL | Notes |
| --- | --- | --- |
| Gateway WS | `ws://localhost:47100/v1/ws` | uncommon port to avoid clashes |
| Meta API | `http://localhost:47100/v1/` | OpenAPI UI at `/docs` in dev |
| Admin/debug API | `http://localhost:47101/admin/v1/` | full access locally |
| Postgres | `localhost:47432` | user `warroom`, db `warroom` |
| Valkey | `localhost:47379` | |
| Fake identity | built into DevHost | `/v1/auth/dev?player=alice` issues tokens (dev builds only) |

Devices on the same Wi-Fi reach the host's LAN IP. The Android emulator uses `10.0.2.2`. The client debug menu allows setting the host.

## 5. Running without cloud credentials

Everything in `local` runs offline: blob storage is the filesystem (`IBlobStore`), remote config is files (`IRemoteConfig`), push is a log sink, IAP is a fake store, and identity is the fake provider. No AWS account is needed to develop gameplay.
