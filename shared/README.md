# shared/: code shared by client and server

Contracts for the real-time channel live here (`ST-07.1.1`). The simulation tree is created by `ST-05.1.1`. C# codegen (`buf.gen.yaml`, `make contracts-gen`) is `ST-07.1.2`. OpenAPI is `ST-07.1.3`.

```
shared/
  simulation/                    not yet scaffolded (ST-05.1.1)
  contracts/
    proto/warroom/realtime/v1/   ClientEnvelope, ServerEnvelope and bodies
    buf.yaml                     STANDARD lint, FILE breaking
    openapi/                     not yet scaffolded (ST-07.1.3)
  content-schema/                not yet scaffolded
```

Hard constraints (see [ADR-0005](../docs/adr/0005-shared-deterministic-simulation.md)):

- Must compile under Unity 6.3 (netstandard2.1, C# 9) **and** .NET 10.
- Deterministic: fixed-point math, injected seeded RNG, ordered collections, no I/O, no clocks.
