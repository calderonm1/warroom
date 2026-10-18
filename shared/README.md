# shared/: code shared by client and server

Not yet scaffolded. Created by stories `ST-05.1.1` (simulation) and `ST-07.1.1` (contracts).

```
shared/
  simulation/
    WarRoom.Simulation/          netstandard2.1, LangVersion 9, zero dependencies except contracts
    WarRoom.Simulation.Tests/    xUnit + FsCheck property tests + golden replay tests
  contracts/
    proto/warroom/<domain>/v1/*.proto    real-time protocol (buf-managed)
    openapi/meta-api.v1.yaml             meta HTTP API
    buf.yaml, buf.gen.yaml
  content-schema/                JSON Schemas for content/ YAML (units, nations, research, maps)
```

Hard constraints (see [ADR-0005](../docs/adr/0005-shared-deterministic-simulation.md)):

- Must compile under Unity 6.3 (netstandard2.1, C# 9) **and** .NET 10.
- Deterministic: fixed-point math, injected seeded RNG, ordered collections, no I/O, no clocks.
