---
title: Local development setup
status: review
owner: ops
last_reviewed: 2026-10-20
related: [ops/environments/local.yaml, EP-02, docs/06-environments/device-testing.md, ADR-0015]
---

# Local development setup

## 1. Workstation prerequisites

| Tool | Version | Why | Required for |
| --- | --- | --- | --- |
| macOS (Apple Silicon recommended) | 15+ | **iOS builds require Xcode on macOS** | iOS builds |
| Xcode | latest stable supported by Unity 6.3 | iOS build, simulator, device deploy | iOS |
| Unity Hub + Unity 6.3 LTS (`6000.3.x`) | `.unity-version`, then exact `m_EditorVersion` in `client/ProjectSettings/ProjectVersion.txt` | client | client |
| Unity modules | iOS Build Support, Android Build Support (incl. OpenJDK, SDK & NDK) | builds | client |
| Unity CLI | latest | agent control of the Editor, `unity mcp` | AI workflow |
| Android Studio | latest stable | emulator (AVD), Logcat, profilers | Android |
| Python | 3.12.3+ within 3.12.x (`.tool-versions`) | repo tooling | all |
| .NET SDK | 10.0.402+ within 10.0.x (`global.json`) | server, shared | server |
| Docker Desktop / OrbStack | latest (presence check) | Postgres, Valkey | server |
| uv | 0.13.2 (`.tool-versions`) | repo tooling | all |
| Terraform | 1.16.6 (`.terraform-version` and `.tool-versions`; 1.10+ required) | infra | infra |
| AWS CLI v2 + SSO profile | latest | cloud access | cloud |
| buf | 1.74.0 (`.tool-versions`) | protobuf | contracts |
| Git LFS | latest (presence check) | assets | all |

Node.js is not a repo dependency ([ADR-0015](../adr/0015-repo-tooling-python-uv.md)) and is not pinned. `make doctor` checks it only if `.tool-versions` gains a `node` line.

### Toolchain pins

| File | What it pins |
| --- | --- |
| `global.json` | .NET SDK `10.0.402`, `rollForward: latestFeature` (an installed 10.0.x SDK at or above that version) |
| `.tool-versions` | Python `3.12.3` (any newer 3.12 patch), uv `0.13.2`, Terraform `1.16.6`, buf `1.74.0` |
| `.terraform-version` | Terraform `1.16.6` (same version as `.tool-versions`, for tfenv) |
| `.unity-version` | Unity editor band `6000.3` (any `6000.3.x` build) until the Unity project exists |
| `client/ProjectSettings/ProjectVersion.txt` | Exact `m_EditorVersion` once `ST-02.3.1` scaffolds the project. It overrides `.unity-version` |

### Check

```bash
make doctor                 # table
make doctor ARGS="--json"  # one JSON object for agents
```

`make doctor` checks dotnet, uv, docker, terraform, git-lfs, buf, the Unity editor and Python. The default output is a table. `ARGS="--json"` (or `wr doctor --json`) prints JSON. A missing or wrong version exits non-zero. Each failing row names this section: `docs/06-environments/local-development.md#1-workstation-prerequisites`.

`make doctor` is not part of `make check`. CI does not need a full workstation.

| Tool | Install |
| --- | --- |
| .NET SDK 10.0.x | <https://dotnet.microsoft.com/download/dotnet/10.0> |
| Python 3.12 and uv | <https://docs.astral.sh/uv/getting-started/installation/> then `uv python install 3.12` |
| Docker | Docker Desktop, OrbStack, or the Docker engine |
| Terraform 1.16.6 | <https://developer.hashicorp.com/terraform/install> |
| Git LFS | <https://git-lfs.com/> then `git lfs install` |
| buf 1.74.0 | <https://buf.build/docs/cli/installation/> |
| Unity 6.3 LTS (`6000.3.x`) | Unity Hub |

Windows or Linux works for server, Android and Editor work. iOS builds then need macOS CI runners or a cloud Mac (see [device testing](device-testing.md)).

## 2. First-time setup (target: one command per area)

```bash
git clone <repo> warroom && cd warroom
git lfs install && git lfs pull
make setup                # repo tooling and tools/geodata (uv sync)
make doctor               # missing or wrong toolchain versions (ST-02.1.1)
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
