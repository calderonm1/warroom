---
title: C# style and code rules
status: accepted
owner: engineering
last_reviewed: 2026-10-18
related: [ADR-0005, .editorconfig, .cursor/rules/20-csharp.mdc]
---

# C# style and code rules

## 1. Language levels

| Area | Target | LangVersion | Notes |
| --- | --- | --- | --- |
| `shared/**` | `netstandard2.1` | **9** | Unity-compatible. No file-scoped namespaces, global usings, `record struct`, `required`, raw string literals, or collection expressions |
| `server/**` | `net10.0` | 14 (default) | Modern C# allowed |
| `client/**` | Unity 6.3 (Mono / IL2CPP) | 9 | Same limits as shared |

## 2. Rules

| ID | Rule | Enforced by |
| --- | --- | --- |
| CONV-CS-001 | `<Nullable>enable</Nullable>` and `<TreatWarningsAsErrors>true</TreatWarningsAsErrors>` in every csproj (`Directory.Build.props`) | build |
| CONV-CS-002 | Analyzers: .NET analyzers (`AnalysisLevel latest-recommended`), `Microsoft.CodeAnalysis.BannedApiAnalyzers`; Roslynator optional | build |
| CONV-CS-003 | `dotnet format --verify-no-changes` passes | CI |
| CONV-CS-004 | Prefer immutability: `readonly` fields, `IReadOnlyList<T>` in APIs, init-only properties | review |
| CONV-CS-005 | No `async void` (except Unity event handlers wrapped with error handling). Every async API takes a `CancellationToken` (server). | analyzer |
| CONV-CS-006 | Errors: exceptions for **bugs** and infrastructure failures; `Result<T, Error>` for **expected** domain failures (command validation). Never use exceptions for control flow in the sim. | review |
| CONV-CS-007 | No `static` mutable state. No service locators. Dependencies via constructor. | review + banned APIs |
| CONV-CS-008 | Public members have XML docs. Comments explain intent and constraints, not mechanics. | analyzer CS1591 in shared/server |
| CONV-CS-009 | Methods ≤ 60 lines, classes ≤ 400 lines (soft). Split by responsibility. | review |
| CONV-CS-010 | No magic numbers for game balance; read from content. Technical constants are named. | review |
| CONV-CS-011 | `DateTime` is forbidden in server code; use `TimeProvider` (testable). `DateTime.Now` and `System.Random` are banned in `shared/` (ADR-0005). | banned APIs |
| CONV-CS-012 | LINQ is allowed outside hot paths. In sim hot paths (step, combat, visibility), use loops over arrays; avoid allocations (benchmarks guard this). | benchmarks |
| CONV-CS-013 | `ConfigureAwait(false)` is not used in ASP.NET Core or Orleans code (no sync context). | review |
| CONV-CS-014 | Use `ILogger<T>` with source-generated `LoggerMessage` methods for hot-path logs. | review |

## 3. Directory.Build.props (to be created in `ST-02.2.1`)

```xml
<Project>
  <PropertyGroup>
    <Nullable>enable</Nullable>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
    <AnalysisLevel>latest-recommended</AnalysisLevel>
    <EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>
    <GenerateDocumentationFile>true</GenerateDocumentationFile>
    <Deterministic>true</Deterministic>
    <ContinuousIntegrationBuild Condition="'$(CI)' == 'true'">true</ContinuousIntegrationBuild>
  </PropertyGroup>
</Project>
```
