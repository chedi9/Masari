# Tunisia Mobility Platform — Master Roadmap

**Roadmap version:** 0.5 gate-review update
**Product baseline:** Active SDD v0.8 and Decision Register v0.7
**Date:** 17 November 2026
**Owner:** Human product owner
**Cost rule:** Zero spend unless explicitly changed by the owner.

> Discovery remains in progress. This is the sole execution roadmap. `SDD_Tunisia_Mobility_Platform.md` is the active SDD; superseded source copies are archived under `docs/archive/`.

## Current project state

- **Current phase:** Phase 0 — discovery and feasibility, with an owner-authorized data-independent mobile coding stream.
- **Status marker:** **DISCOVERY IN PROGRESS**.
- **Implementation gate:** The owner authorized modular mobile UI, navigation, localization, accessibility and interactions to proceed with clearly labeled placeholders while data research continues.
- **Active task:** `TUM-P0-012` — Phase 0 gate review.
- **Gate status:** **READY FOR FORMAL OWNER REVIEW, NOT OWNER-APPROVED FOR EXIT**.
- **Evidence basis:** `TUM-P0-002` is complete as a preliminary desk audit; `TUM-P0-003` is partial with verified SNCFT rail data; `TUM-P0-010` is complete for a reproducible rail import/query prototype.
- **Owner of next action:** Product owner — decide whether to accept the pilot scope and authorize completion of the remaining gate work.
- **Tools:** Repository Markdown review and GitHub source retrieval; no paid services or paid APIs.
- **Dependencies:** Owner decisions on pilot scope, source licensing, map/provider, privacy/security and Pro/offline boundaries.

## Gate review summary

### Evidence available

- **TUM-P0-002:** Preliminary desk evidence exists for Greater Tunis, Sousse, Monastir and Sfax. It distinguishes catalog evidence from operator authorization and does not approve an area or launch threshold.
- **TUM-P0-003:** A 24.39 MB official SNCFT GTFS archive was downloaded and profiled: 53 routes, 223 stops, 248 trips, 4,795 stop times and 14 fare tiers. The data is a 2020–2021 Spring 2021 service baseline, not proof of current schedules.
- **TUM-P0-010:** Reproducible SQLite import and direct-query scripts exist. Pilot rail queries return exact stored sequences and source fares. The prototype does not provide transfers, walking, bus/metro integration or a complete journey ranking engine.
- **Mobile stream:** A four-tab Expo TypeScript prototype exists with placeholder data and explicitly labeled illustrative content. It is not evidence for production route coverage or live operations.

### Unresolved blockers

- **TUM-P0-004:** No data licensing/reuse decision record proves integration or redistribution rights beyond source-level catalog metadata.
- **TUM-P0-005:** No free map, geocoding or routing comparison has been completed for Tunisia coverage, Arabic/French quality, license, fallback or current limits.
- **TUM-P0-008:** No privacy/security review plan or qualified legal review is complete. Persistent/location collection remains gated.
- **TUM-P0-009:** A modular repository direction exists, but a final architecture/provider stack and implementation ADR pack remains incomplete.
- **TUM-P0-011:** Pro offline scope, freshness, synchronization, storage, entitlements and licensing remain TBD.
- **Transport coverage:** TRANSTU, STS and SORETRAS remain partially inventoried. The national stop registry and shared transport sources are not resolved across the full pilot scope.
- **Freshness:** SNCFT timetable validity ends in June 2021 and cannot be represented as current without an operator-confirmed update.

### Proposed pilot scope

The smallest evidence-based pilot is a **read-only Greater Tunis rail feasibility pilot** based on reproducible official SNCFT rail data, with the following boundaries:

- Include only verified SNCFT routes/stops/fare records already present in the prototype.
- Clearly label the 2020–2021 schedule baseline and any result as scheduled/historical rather than current.
- Exclude live/real-time vehicle claims.
- Exclude public bus, metro or shared-transport claims until their source/permission/freshness evidence passes review.
- Exclude location collection and paid/offline entitlements until separate approvals and reviews.
- Use the pilot to validate route data quality and direct rail query behavior, not to claim product launch coverage.

This scope is a recommendation for owner review, not an approved pilot decision.

### Owner decisions required before Phase 0 exit

1. Approve or revise the proposed Greater Tunis rail-only pilot boundary.
2. Decide whether to proceed with transport dataset and license audits before the next implementation phase.
3. Assign a priority to P0-004, P0-005 and P0-008.
4. Approve whether P0-009 should proceed with the confirmed React Native/Expo, FastAPI and PostgreSQL/PostGIS directions while keeping provider choices delegated.
5. Decide whether P0-011 remains a later detail pack or is required before public pilot implementation.
6. Confirm the evidence threshold for declaring an area/mode ready; no numeric threshold is currently approved.

## Current next task

| Task ID | Task | Priority | Status | Owner | Dependencies | Deliverable / acceptance and validation evidence |
|---|---|---:|---|---|---|---|
| TUM-P0-012 | Phase 0 gate review | P0 | REVIEW | Product owner | P0-002, P0-003, P0-010; P0-004/005/008/009/011 unresolved | This review establishes whether formal owner consideration is ready. Gate exit remains unapproved. |

## Phase 0 work still required

| Task ID | Task | Priority | Status | Owner | Dependencies | Deliverable / acceptance |
|---|---|---:|---|---|---|---|
| TUM-P0-002 | Candidate-area readiness evidence review | P0 | DONE | Codex | Confirmed rollout areas; SDD/register | Preliminary desk audit completed; no area approval. |
| TUM-P0-003 | Transport dataset inventory | P0 | PARTIAL | Data researcher | P0-002 | SNCFT archive profiled; TRANSTU/STS/SORETRAS and license/freshness work incomplete. |
| TUM-P0-004 | Data licensing and reuse audit | P0 | BACKLOG | Data/legal researcher | P0-003 | Evidence of permitted use for every pilot source. |
| TUM-P0-005 | Map/geocoding/routing comparison | P0 | BACKLOG | Mapping researcher | P0-002; P0-004 | Zero-spend provider comparison with license and Tunisia coverage evidence. |
| TUM-P0-006 | UX validation and Pro offline detail pack | P1 | BACKLOG | Product/UX designer | P0-001b; P0-005 | Device/RTL/accessibility validation and required offline decisions. |
| TUM-P0-007 | Transport operations research | P1 | BACKLOG | Transport-data researcher | P0-003 | Branch/diversion/rural/taxi evidence handling. |
| TUM-P0-008 | Privacy/security review plan | P0 | BACKLOG | Privacy/security reviewer | P0-001b | Privacy/security review plan; no persistent location collection before qualified review. |
| TUM-P0-009 | Approved-stack architecture pack | P0 | BACKLOG | Software architect | P0-003; P0-005 | ADR and provider/interface validation; no provider approval by default. |
| TUM-P0-010 | Data/routing feasibility prototype | P0 | DONE | Data/engineering contributor | P0-002–005; P0-009 | Reproducible rail import/query prototype completed. It remains schedule-baseline evidence, not current service. |
| TUM-P0-011 | Pro offline product/technical definition | P1 | BACKLOG | Product/engineering contributor | P0-005; P0-009 | Package matrix, freshness, sync, storage, licensing and entitlement definition. |
| TUM-P0-012 | Phase 0 gate review | P0 | REVIEW | Product owner | P0-002–011 | Formal review package prepared; owner approval of exit not claimed. |

## Known approval gates

- Data source authorization and reuse terms must be reviewed for each source before production integration.
- The SNCFT 2020–2021 feed must not be presented as current without operator-confirmed freshness.
- Map, geocoding and routing providers require coverage, licensing and cost review.
- Privacy and Tunisian legal review precede persistent location collection.
- Pro/offline entitlement details remain TBD.
- Real bus/metro/taxi/live data and public rollout require evidence and owner review.

## Update log

| Date | Agent/tool | Task | Summary | Evidence |
|---|---|---|---|---|
| 2026-11-17 | GitHub repository review | TUM-P0-012 | Prepared gate review: evidence summarized, blockers identified, proposed rail-only pilot boundaries documented, and formal owner approval left pending. | Repository roadmap, handoff, SDD/register, P0-002/P0-003 and P0-010 source review. |

## Current task state

- **Active task:** `TUM-P0-012` — Phase 0 gate review.
- **Gate determination:** Formal owner review is preparable; Phase 0 exit is not approved.
- **Current next TODO:** Product owner — review the proposed rail-only pilot scope and decide which P0 task is authorized next.
- **Status:** P0 gate evidence sufficient for formal review consideration, but incomplete for unconditional Phase 0 exit.
