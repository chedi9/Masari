# Tunisia Mobility Platform — SDD Owner-Decision Addendum

**Document ID:** TUM-SDD-001 addendum  
**Version:** 0.4 working addendum  
**Date:** 3 November 2026  
**Status:** Discovery in progress; not a final implementation contract  
**Applies to:** `reference/SDD_v0.3_Tunisia_Mobility_Platform.md`

## Authority

This addendum records explicit product-owner decisions supplied after the repository's SDD v0.3 was written. It supersedes v0.3 only where the same decision is answered below. All other confirmed v0.3 requirements remain in force. Recommendations remain recommendations; TBDs remain TBD.

## Approved decision updates

### Mobile framework and visual quality — D-45

**Confirmed:** React Native + Expo + TypeScript (option A), with a premium, highly customized visual standard. Use this as the mobile starting stack. Confirm actual map SDK, animation/performance approach, and platform-specific components through engineering validation. Test lower-end Android devices and preserve the planned iOS path.

**Not approved:** the suggested palette, logo/brand identity, specific component designs, or a final visual system. The colors `#142D3B`, `#16A085`, `#F5F3ED`, `#E9B85B` are exploratory only.

### Launch order and coverage — D-01 / D-01b

**D-01 confirmed:** Greater Tunis → Sousse → Monastir → Sfax, sequentially, with readiness gates at each stage.

**D-01b confirmed:** define geographic coverage using verified transport-service areas (validated routes, stops, stations and service areas). Do not represent an entire governorate as covered without validated service. Track coverage readiness per launch area.

### Seventeen selected questions

The owner selected the following answers. These are approved directions, subject to the validation boundaries in the current register:

- D-15 offline packages: C — select city, region and transport modes independently.
- D-15 offline freshness: D — source-specific expiration rules and warn before information becomes unreliable.
- D-69 billing: B — monthly and yearly periods. Prices/payment provider/terms are not set.
- D-69 additional Pro benefits: D — offline first; add benefits only after research. No ad-free benefit is approved.
- D-16 bus route branches/diversions: D — hybrid variants, trip patterns and temporary diversions; validate on actual data.
- D-26 vehicle matching: D — hybrid multi-signal matching with confidence; accuracy gates TBD.
- D-43 advertising: C — contextual by default; personalized only with explicit opt-in.
- D-46 backend: A — Python + FastAPI.
- D-47 database: A — PostgreSQL + PostGIS.
- D-48 maps: C — open geographic data plus managed tiles/routing where economical; verify coverage, terms and cost.
- D-49 hosting: A — free tiers during development/early beta; low-cost production is intended. No provider or spend ceiling is approved.
- D-50 offline architecture: D — SQLite, versioned regional packages and cached map tiles; detailed design remains open.
- D-54 moderation: C — automatic low-risk handling, evidence-based verification and human review for material changes; thresholds remain open.
- D-56 operator interface: D — read-only first, managed capabilities after partnerships.
- D-57 retention: D — privacy impact assessment and qualified Tunisian legal review before collection; periods remain TBD.
- D-60 security: D — stage baseline security, threat modeling/code review and independent penetration testing according to release risk.

## D-06 passenger report classification remains TBD

The answer was not provided. The known boundary remains: basic reports can be submitted as a guest; advanced contributions require an account. The feature-based split (option C) was recommended but was not selected. Do not implement it as an approved classification.

The v0.3 decision register uses D-06 for journey preferences, while the supplied current conversation uses D-06 for passenger report classification. Keep both contextual references until the product owner resolves the identifier collision.

## Discovery status and implementation gate

Discovery is still active. The source repository's Phase 0 feasibility and approval gate remains in effect. Do not interpret this documentation ZIP or the technology selections as authorization to build the full production application. Continue with evidence gathering, data/licensing checks, prototypes, UX decisions, privacy/legal review and the remaining TBDs in the master roadmap.
