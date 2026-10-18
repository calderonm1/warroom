---
title: Intel and fog of war
status: review
owner: design
last_reviewed: 2026-10-18
related: [NFR-SEC-001, SRV-005, EP-16]
---

# Intel and fog of war

| ID | Rule |
| --- | --- |
| GDD-INT-001 | Each nation sees: its own provinces and units; provinces within view range of its units, buildings and radar; whatever coalition members and shared-vision partners see. |
| GDD-INT-002 | Outside current vision, provinces show **last-known** owner and buildings (with an age indicator). Units outside vision are not shown. |
| GDD-INT-003 | Visibility is computed **server-side** each time the relevant state changes. Clients receive only visible data (SRV-005). |
| GDD-INT-004 | Unit identification: at the edge of view range units appear as "unknown ground/air/naval contact". Full composition requires closer range or recon units. |
| GDD-INT-005 | Stealth units are only visible to specific detectors (AWACS, radar buildings at level 3+, ASW for submarines). |
| GDD-INT-006 | **Spies** (post-M2): agents assigned to a target nation for intel (economy, research, army locations) or sabotage (building damage, morale). Counter-intelligence buildings reduce success. |
| GDD-INT-007 | The Command Center subscription's "advanced intel analytics" is **presentation only**: charts and summaries of information the player already legitimately has. It never reveals hidden data. |
