---
title: Secrets management
status: accepted
owner: ops
last_reviewed: 2026-10-18
related: [CONV-SEC-001, docs/03-architecture/security-and-anti-cheat.md]
---

# Secrets management

| Where | What | Access |
| --- | --- | --- |
| AWS Secrets Manager (`/wr/<env>/...`) | DB credentials (rotated), FCM service account, App Store Server API key, Play API key, Sentry DSN (server) | ECS task roles (per service, least privilege) |
| AWS KMS | session token signing key (asymmetric, non-exportable) | Identity service role (`kms:Sign`) |
| SSM Parameter Store (`/wr/<env>/config/...`) | non-secret config (feature defaults, URLs) | task roles, agents (read) |
| GitHub Actions secrets | CI-only: Unity license, store upload keys, Projects token | workflows |
| Local `.env` (gitignored) | local overrides only. No real cloud secrets needed locally. | developer |
| Password manager (owner) | root credentials, recovery codes, signing keystores backup | owner only |

Rules:

1. Secret names follow `/wr/<env>/<service>/<name>`.
2. Rotation: DB credentials automatic (30 days), API keys yearly, immediately on suspicion.
3. Android upload keystore and iOS signing assets are backed up in two places (password manager plus an encrypted S3 object in `warroom-shared`). Losing the Android upload key is recoverable via Play App Signing, but avoid it.
4. Agents never read secret values (`secretsmanager:GetSecretValue` is denied to agent roles).
