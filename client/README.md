# client/: Unity mobile client

Unity 6.3 LTS project for iOS and Android (WebGL/WebGPU later). Not yet scaffolded. Created by story `ST-02.3.1`.

Planned layout (see [client architecture](../docs/03-architecture/client-architecture.md) and [Unity conventions](../docs/05-conventions/unity.md)):

```
client/
  Assets/
    WarRoom/
      Runtime/
        App/            composition root, boot flow, service wiring
        Globe/          globe mesh, province rendering, camera (WarRoom.Client.Globe.asmdef)
        Match/          match view-model, command dispatch, state sync
        Net/            WebSocket transport, protobuf codec, reconnect
        UI/             UI Toolkit screens and components (UXML/USS)
        Platform/       IAP, push, auth providers, haptics (per-platform adapters)
      Editor/           editor tooling, content importers, build scripts
      Tests/
        EditMode/
        PlayMode/
    Plugins/            third-party SDKs
  Packages/manifest.json
  ProjectSettings/
```

The client references `shared/simulation` and `shared/contracts` generated C# as source or DLL through a UPM local package (see ADR-0005).
