---
title: Globe interaction model
status: review
owner: ux
last_reviewed: 2026-10-18
related: [docs/03-architecture/globe-rendering.md, EP-09]
---

# Globe interaction model

| ID | Gesture / input | Action |
| --- | --- | --- |
| GLB-001 | One-finger drag | Rotate the globe (inertia, with damping) |
| GLB-002 | Pinch | Zoom (Z0 to Z3); camera tilts gradually toward the horizon at Z2 and Z3 |
| GLB-003 | Two-finger rotate | Rotate heading (north-up reset button appears) |
| GLB-004 | Tap province | Select province, opening the province sheet (peek) |
| GLB-005 | Tap army icon | Select army, opening the army sheet (peek); shows movement range rings |
| GLB-006 | With army selected: tap province | Shows path preview with ETA and a confirm button (no accidental orders) |
| GLB-007 | With army selected: long-press hostile | Opens a combat preview |
| GLB-008 | Long-press empty | Opens a radial menu: ping (coalition), measure distance, info |
| GLB-009 | Double-tap | Fly-to and zoom one level in centred on the point |
| GLB-010 | Alert tap | Camera flies to the location (`motion.slow`), then selects |
| GLB-011 | Desktop/web (later) | Drag = rotate, wheel = zoom, right-click = context, hotkeys |

Rules:

- Orders always require explicit confirmation (GLB-006). Two-step selection then confirm prevents fat-finger disasters.
- Camera never auto-moves without user intent, except fly-to from alerts or the briefing.
- At Z0 and Z1, tapping a nation selects the nation (diplomacy card) rather than a province.
- Selection highlights use both colour and outline thickness (accessibility).
