---
title: "ADR-0009: Identity via Amazon Cognito with first-party guest accounts and War Room session tokens"
status: accepted
owner: architecture
last_reviewed: 2026-10-18
related: [R-CLD-04, NFR-PRIV-001, docs/03-architecture/identity-and-accounts.md]
---

# ADR-0009: Identity

- **Date:** 2026-10-18
- **Deciders:** project owner

## Context

Mobile players expect to start instantly as a guest, then link Apple, Google or email to keep progress. Apple requires Sign in with Apple when other social logins are offered, plus in-app account deletion. Game sessions need short-lived tokens carrying game claims (player ID, entitlements, ban state) independent of the IdP. Cognito Essentials is free to 10k MAU, supports Apple and Google federation, and is AWS-native (R-CLD-04).

## Decision

1. **Amazon Cognito user pool (Essentials)** per environment for federated sign-in: Sign in with Apple, Google, and email with passkey or OTP. Hosted UI is not used in-game; the client uses native SDK flows (AuthenticationServices on iOS, Credential Manager on Android) and exchanges provider tokens with Cognito.
2. **Guest accounts are first-party**: on first launch the backend creates a `Player` with a device-bound credential (random 256-bit secret stored in iOS Keychain / Android Keystore). Guests can later **link** a Cognito identity; the `Player` ID never changes.
3. The **War Room Identity service** (`WarRoom.Server.Identity`) verifies either a Cognito ID token or a guest credential and issues **War Room session tokens**: JWT, ES256, signed with a KMS-held key, 15-minute access plus rotating refresh. All game services trust only War Room tokens.
4. Admin and ops access uses IAM Identity Center (humans) and is never the player IdP.
5. Account deletion: in-app flow that hard-deletes PII within 30 days and anonymizes match history.

## Alternatives considered

| Option | Why not |
| --- | --- |
| Cognito only (guests via identity pools / unauthenticated identities) | Awkward linking semantics; identity pool guest IDs are not a good primary key |
| Auth0 / Clerk | Cost scales poorly at game MAU volumes |
| Firebase Auth | Good anonymous auth, but another cloud for a core dependency |
| Unity Authentication (UGS) | Ties identity to the engine vendor; less control |
| Fully self-built auth | Security risk; reinventing OAuth flows |

## Consequences

The backend owns a small but security-critical token service. It needs a threat model and tests (`EP-08`). Swapping IdPs later does not touch game services.

## Compliance

Security review checklist for `EP-08`. Integration tests for token validation, refresh rotation, revocation, and account linking.
