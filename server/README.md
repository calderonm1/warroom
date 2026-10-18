# server/: .NET backend

.NET 10 backend. Not yet scaffolded. Created by story `ST-02.2.1`.

Planned layout (see [server runtime](../docs/03-architecture/server-runtime.md) and [server conventions](../docs/05-conventions/server.md)):

```
server/
  WarRoom.Server.sln
  src/
    WarRoom.Server.Gateway/      WebSocket gateway + meta HTTP API (ASP.NET Core), Orleans client
    WarRoom.Server.Silo/         Orleans silo host: MatchGrain, PlayerGrain, LobbyGrain, ...
    WarRoom.Server.Grains/       grain implementations (no hosting code)
    WarRoom.Server.Persistence/  Postgres (EF Core / Npgsql), snapshot store (S3), command log
    WarRoom.Server.Identity/     token verification (Cognito/guest), session token issuing
    WarRoom.Server.Workers/      background jobs: notifications, analytics export, receipts
    WarRoom.Server.Admin/        admin + debug API (dev/staging full, prod read-only)
  tests/
    WarRoom.Server.UnitTests/
    WarRoom.Server.IntegrationTests/   Testcontainers (Postgres, Valkey)
    WarRoom.Server.LoadTests/          NBomber scenarios
  docker/
    compose.yaml                 local stack
```
