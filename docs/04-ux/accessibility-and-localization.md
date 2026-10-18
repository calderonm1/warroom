---
title: Accessibility and localization
status: review
owner: ux
last_reviewed: 2026-10-18
related: [docs/04-ux/design-system.md, EP-11]
---

# Accessibility and localization

## Accessibility (target: WCAG 2.2 AA where applicable to games)

| ID | Requirement |
| --- | --- |
| A11Y-001 | Text contrast ≥ 4.5:1 (body) and 3:1 (large text, icons). Checked by a token-contrast test in CI (`ST-11.1.2`). |
| A11Y-002 | Never convey information by colour alone: friend/foe shape (APP-6 frames), coalition patterns, status icons. |
| A11Y-003 | Colour-blind modes: deuteranopia, protanopia and tritanopia palettes for nations and coalitions. |
| A11Y-004 | Font scaling up to 130%. Layouts reflow. |
| A11Y-005 | Reduce Motion: disable camera inertia overshoot, atmosphere shimmer and parallax. |
| A11Y-006 | Screen reader labels on all UI Toolkit controls (Unity 6.3 native screen reader support). The globe exposes a "list view" alternative for provinces and armies. |
| A11Y-007 | Haptics and sounds always have visual equivalents, and can be disabled. |
| A11Y-008 | Hold-to-confirm option for destructive actions. |

## Localization

| ID | Requirement |
| --- | --- |
| L10N-001 | All user-facing strings use keys in `content/localization/<lang>/*.yaml`. No literals in code (lint rule `ST-11.2.2`). |
| L10N-002 | Launch languages: EN. Wave 2: DE, FR, ES, PT-BR, PL, TR, JA, KO. |
| L10N-003 | ICU MessageFormat for plurals and gender. |
| L10N-004 | Layouts tolerate +40% text expansion. |
| L10N-005 | Numbers, dates and durations formatted by locale. Game time shown as "Day 6, 14:00". |
| L10N-006 | RTL (Arabic, Hebrew) is post-launch. Avoid layout decisions that block it (use logical start/end). |
