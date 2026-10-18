---
title: Open questions
status: draft
owner: product
last_reviewed: 2026-10-18
related: [docs/07-planning/risks.md, docs/00-product/naming-and-brand.md, AGENTS.md]
---

# Open questions

Decisions that only the project owner can make. Agents must **not** guess answers to these (AGENTS.md: no invented product decisions). When you answer one, record the answer here, update the affected docs and ADRs in the same PR, and mark the row `answered`.

| ID | Question | Why it matters | Blocks | Status |
| --- | --- | --- | --- | --- |
| OQ-001 | Will you have regular access to a Mac (owned, borrowed or rented in the cloud)? | Local iOS builds, Xcode debugging and signing setup; otherwise iOS is CI-only | EP-04, ST-02.5.4 | open |
| OQ-002 | What is the monthly AWS budget ceiling for dev and staging before launch? | Sets budget alarms, Aurora minimum capacity, NAT strategy | EP-03 | open |
| OQ-003 | Which markets for soft launch (for example Canada, Australia, Philippines, Nordics)? | Localization, pricing tiers, legal review, server region | EP-25 | open |
| OQ-004 | How will art be sourced: asset store, contract artists, AI-assisted with licence review, or in-house? | Pipeline, budget and the visual style lock in the design system | EP-11, EP-09 | open |
| OQ-005 | Which legal entity publishes the game (individual or LLC) and is a D-U-N-S number available? | Apple organisation developer account, store seller name, liability | ST-01.4.1 | open |
| OQ-006 | What reverse-domain bundle ID root should be used (for example `com.<company>.warroom`)? | Bundle IDs are permanent once published | ST-01.4.2 | open |
| OQ-007 | Which domain will host the website, API and support pages? | Certificates, Cognito domain, deep links, privacy policy URL | EP-03, EP-08 | open |
| OQ-008 | Will you engage a trademark attorney for classes 9 and 41 before store submission? | Name risk RISK-006 | ST-01.4.1 | open |
| OQ-009 | Minimum supported OS versions (proposed: iOS 16, Android 10 / API 29)? | Device test matrix and API availability | EP-02, EP-04 | open |
| OQ-010 | Is real-money spend allowed for players under 18, or do you rate the game 17+/Mature? | Age rating, parental controls, compliance work | EP-21, EP-23 | open |

## Answered

None yet.
