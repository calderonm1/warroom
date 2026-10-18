---
title: Design system
status: review
owner: ux
last_reviewed: 2026-10-18
related: [design/tokens.json, docs/04-ux/hud-and-screens.md, docs/05-conventions/unity.md, EP-11]
---

# Design system

The machine-readable source of truth is [`design/tokens.json`](../../design/tokens.json) (W3C Design Tokens format). A build step generates Unity USS variables from it (`ST-11.1.1`). Never hard-code colours, sizes or durations in UXML/USS/C#; use tokens.

## 1. Visual direction

"**Joint operations centre at night.**" Deep slate surfaces, a luminous globe as the hero, crisp data overlays, restrained accents. Information density is high but calm. Think modern defence C2 displays, not sci-fi neon.

## 2. Colour

| Token | Value | Use |
| --- | --- | --- |
| `color.bg.base` | `#0B0F14` | App background, behind the globe |
| `color.bg.surface` | `#121821` | Panels, sheets |
| `color.bg.elevated` | `#1A2230` | Popovers, cards on surfaces |
| `color.border.subtle` | `#263142` | Dividers |
| `color.text.primary` | `#E6EDF5` | Body, titles |
| `color.text.secondary` | `#9AA8BA` | Labels, metadata |
| `color.text.disabled` | `#5B6878` | |
| `color.accent.primary` | `#3FA7FF` | Primary actions, selection |
| `color.accent.warning` | `#FFB020` | Threats, low resources |
| `color.accent.danger` | `#FF4D5E` | Under attack, destructive |
| `color.accent.success` | `#3DDC97` | Completed, captured |
| `color.ocean.deep` / `color.ocean.shallow` | `#0A1A2B` / `#12324F` | Globe water |

**Nation palette:** 24 base hues × 3 lightness steps, tested for minimum ΔE between neighbours. The palette assignment algorithm guarantees adjacent nations differ by ≥ 20 ΔE. **Coalition palette:** 8 colours based on Okabe–Ito (colour-blind safe) with pattern overlays (hatch, dots) as a secondary channel.

## 3. Typography

| Role | Typeface | Size / line (pt) | Notes |
| --- | --- | --- | --- |
| Display (logo, results) | Barlow Condensed SemiBold | 32 / 36 | OFL license |
| Title | Inter SemiBold | 20 / 26 | OFL |
| Body | Inter Regular | 15 / 21 | |
| Label | Inter Medium | 13 / 17 | uppercase tracking +4% for section labels |
| Numeric / timers | JetBrains Mono or Inter tabular figures | 15 / 21 | **tabular numerals mandatory** for counters |
| Map labels | Barlow Condensed Medium (SDF) | scaled by zoom | |

Support Dynamic Type / font scale up to 130% without truncating critical info.

## 4. Spacing, layout, shape

- 4 pt base grid. Tokens `space.1` = 4 through `space.8` = 32, `space.12` = 48.
- Radius: `radius.sm` 6, `radius.md` 10, `radius.lg` 16, `radius.pill` 999.
- **Touch targets ≥ 44 × 44 pt (iOS) / 48 × 48 dp (Android).**
- Respect safe areas (Dynamic Island, home indicator, Android cutouts).
- Layout modes: phone portrait (primary), phone landscape (supported), tablet (two-pane).

## 5. Motion and feedback

| Token | Value | Use |
| --- | --- | --- |
| `motion.fast` | 120 ms | press states |
| `motion.base` | 200 ms | panels, sheets |
| `motion.slow` | 350 ms | camera fly-to easing |
| `motion.easing.standard` | cubic-bezier(0.2, 0, 0, 1) | |

Haptics: light impact on selection, success notification on capture or completion, warning on attack alerts. All motion respects "Reduce Motion".

## 6. Iconography and unit symbology

- UI icons: 24 pt grid, 2 pt stroke, rounded joins (custom set; Lucide as a temporary placeholder, ISC license).
- **Unit symbols:** inspired by NATO **APP-6** frames (friendly rectangle, hostile diamond, neutral square, unknown quatrefoil) with simplified branch glyphs. Genre veterans recognise them instantly. Friend/foe colour **and** shape (colour-blind safe).

## 7. Components (UI Toolkit)

Button (primary, secondary, ghost, destructive), IconButton, Chip, Badge, ProgressBar (timer variant), ResourceCounter, BottomSheet (peek/half/full), Tabs, ListRow, Toast, Dialog, Tooltip (long-press), Countdown, UnitCard, ProvinceCard, AlertRow, ChatBubble, Avatar, NationFlag (insignia), Stepper, Toggle, Slider, SegmentedControl, EmptyState, Skeleton (loading), ErrorState.

Each component has: a UXML template, USS using tokens only, a view-model interface, an EditMode test for bindings, and a gallery entry in the in-app **Component Gallery** dev screen (`ST-11.1.3`).
