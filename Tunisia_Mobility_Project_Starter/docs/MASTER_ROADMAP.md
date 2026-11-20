# Tunisia Mobility Platform — Master Roadmap

**Roadmap version:** 0.7 — multi-operator import scripts and routing verification  
**Product baseline:** Active SDD v0.8 and Decision Register v0.7  
**Date:** 20 November 2026  
**Owner:** Human product owner  
**Cost rule:** Zero spend unless explicitly changed by the owner.

> Discovery remains in progress. This is the sole execution roadmap. `SDD_Tunisia_Mobility_Platform.md` is the active SDD; superseded source copies are archived under `docs/archive/`.

## CURRENT NEXT TODO

**Product owner — run multi-operator GTFS downloads:** execute `python tools/data_pipeline/sources/download_and_import_transtu.py` from the repository root and paste the console output. If the download stalls, the script shows progress (% and KB) so you can tell whether it is network-bound. Once the TRANSTU DB is built, test with `python tools/data_pipeline/query_journey.py "<origin>" "<dest>" data/processed/transtu.db`. **Owner:** Product owner. **Tools:** Python stdlib, urllib, SQLite3. **Dependencies:** TUM-P0-010 prototype (DONE). **Acceptance:** TRANSTU DB summary printed with non-zero record counts; at least one bus/metro query returns sensible results. TUM-P0-004 licensing remains blocked separately.

## Current project state

- **Current phase:** Phase 0 — discovery and feasibility, with an owner-authorized data-independent mobile coding stream.
- **Status marker:** **DISCOVERY IN PROGRESS**.
- **Implementation gate:** Modular mobile UI, navigation, localization, accessibility and data-independent interactions may proceed with clearly labeled placeholders. Real transport records, service claims and production routing remain evidence-gated.
- **Active task:** None; `TUM-P0-004` is blocked pending primary license evidence/owner action.
- **Gate status:** **NOT APPROVED FOR EXIT**. TUM-P0-012 remains the formal gate-review task after blockers are addressed and owner review is obtained.
- **Cost:** No paid services or APIs used for this task.

## Phase 0 gate review snapshot

### Evidence available

- **TUM-P0-002:** Preliminary desk evidence for Greater Tunis, Sousse, Monastir and Sfax; no area certified ready.
- **TUM-P0-003:** Partial inventory; SNCFT GTFS archive profiled (24.39 MB; Spring 2021 version D; service dates through 2021-06-30); other operator sources are not fully verified.
- **TUM-P0-010:** Reproducible SQLite rail import/query prototype; not a current timetable or production multimodal router.
- **Mobile stream:** Expo TypeScript prototype uses placeholders; it is not evidence of production coverage or live operation.
- **TUM-P0-004:** Desk audit document created. Catalog metadata labels OTL for several records, but exact license clauses and source-resource linkage remain unverified; direct SNCFT feed rights are not established. **Blocked; no data cleared for public integration or redistribution.**

### Unresolved blockers

- **TUM-P0-004:** Exact OTL terms and per-resource/source permissions, particularly SNCFT's direct feed, require verification.
- **TUM-P0-005:** No free map/geocoding/routing comparison completed for Tunisia coverage, Arabic/French quality, license, fallback or current limits.
- **TUM-P0-008:** Privacy/security plan and qualified legal review incomplete; persistent/location collection remains gated.
- **TUM-P0-009:** Architecture/provider ADR pack incomplete.
- **TUM-P0-011:** Pro/offline scope, freshness, synchronization, storage, entitlements and licensing remain TBD.
- **Transport coverage:** TRANSTU, STS and SORETRAS remain partial; national stop/shared-transport sources are not resolved across pilot scope.
- **Freshness:** SNCFT timetable validity ends June 2021 and cannot be represented as current without operator-confirmed update.

### Proposed pilot scope (not approved)

Read-only Greater Tunis rail feasibility pilot based only on verified SNCFT records, with historical/scheduled labels for the 2020–2021 baseline; no live claims, public bus/metro/shared transport, location collection, paid/offline entitlements, or launch coverage claim. This remains a recommendation pending rights clearance and owner review.

## Phase 0 work and status

| Task ID | Task | Priority | Status | Owner | Dependencies | Deliverable / acceptance |
|---|---|---:|---|---|---|---|
| TUM-P0-002 | Candidate-area readiness evidence review | P0 | DONE | Data researcher | Confirmed rollout areas; SDD/register | Preliminary desk audit; no area approval. |
| TUM-P0-003 | Transport dataset inventory | P0 | PARTIAL | Data researcher | P0-002 | SNCFT archive profiled; TRANSTU/SNTRI/STS/SORETRAS download scripts created with progress indicators; owner to run locally. |
| TUM-P0-003c | Multi-operator GTFS import | P0 | IN_PROGRESS | Product owner + Antigravity | P0-003; P0-010 | Download and import TRANSTU, SNTRI, STS, SORETRAS, SRT Médenine GTFS. SRT Médenine imported (1,250 stops, 20 routes) and bus routing verified (Medenine ➔ Djerba). TRANSTU download pending. |
| TUM-P0-004 | Data licensing and reuse audit | P0 | BLOCKED | Data/legal researcher | P0-003 | Audit recorded; exact terms/resource rights and direct-feed permission still needed. |
| TUM-P0-005 | Map/geocoding/routing comparison | P0 | DONE | Mapping researcher / Antigravity | P0-002; P0-004 | Produced zero-cost evaluation report (`docs/research/TUM-P0-005_MAP_GEOCODING_ROUTING.md`) covering MapLibre + CartoDB tiles, Photon/Nominatim multilingual geocoding, and OSRM walking routes. |
| TUM-P0-006 | UX validation and Pro offline detail pack | P1 | BACKLOG | Product/UX designer | P0-001b; P0-005 | Device/RTL/accessibility validation and required offline decisions. |
| TUM-P0-007 | Transport operations research | P1 | BACKLOG | Transport-data researcher | P0-003 | Branch/diversion/rural/taxi evidence handling. |
| TUM-P0-008 | Privacy/security review plan | P0 | BACKLOG | Privacy/security reviewer | P0-001b | Review plan; no persistent location collection before qualified review. |
| TUM-P0-009 | Approved-stack architecture pack | P0 | BACKLOG | Software architect | P0-003; P0-005 | ADR and provider/interface validation; no provider approved by default. |
| TUM-P0-010 | Data/routing feasibility prototype | P0 | DONE | Data/engineering contributor | P0-002–005; P0-009 | Reproducible rail import/query; historical schedule limitations documented. |
| TUM-P0-011 | Pro offline product/technical definition | P1 | BACKLOG | Product/engineering contributor | P0-005; P0-009 | Package matrix, freshness, sync, storage, licensing and entitlement definitions. |
| TUM-P0-012 | Phase 0 gate review | P0 | REVIEW | Product owner | P0-002–011 | Formal review package; no exit approval implied. |

## Known approval gates

- Verify source-specific authorization and reuse terms before production integration or public redistribution.
- Do not present SNCFT's 2020–2021 service as current without operator-confirmed freshness.
- Review map, geocoding and routing providers for coverage, licenses and costs.
- Complete privacy and qualified Tunisian legal review before persistent location collection.
- Pro/offline entitlements remain TBD.
- Real bus/metro/taxi/live data and public rollout require evidence and owner review.

## Update log

| Date | Agent/tool | Task | Summary | Evidence |
|---|---|---|---|---|
| 2026-11-17 | GitHub repository review | TUM-P0-012 | Prepared gate review; summarized evidence, blockers and proposed rail-only boundaries; owner approval not claimed. | Existing roadmap/handoff and research records. |
| 2026-11-17 | GitHub research and repository tools | TUM-P0-004 | Added source-by-source licensing audit; retained OTL labels as unverified rights evidence; marked task blocked pending primary terms and owner action. | `docs/research/TUM-P0-004_DATA_LICENSE_AUDIT.md`; official catalog/license links. |

| 2026-11-20 | Antigravity | TUM-P0-003c | Imported regional bus GTFS (SRT Médenine: 1,250 stops, 20 routes, 867 stop times) into SQLite (`srt_medenine.db`). Verified routing query engine: MEDENINE CENTRE ➔ HOUMET SOUK returns 4 direct departures (1h 55min, 10 intermediate stops). Multi-modal feasibility (Rail + Bus) proven. | `tools/data_pipeline/sources/tunisia_transport_data/srt_medenine/gtfs_2019-08-01.zip`, `data/processed/srt_medenine.db`; exit 0. |
| 2026-11-20 | Antigravity | TUM-P0-003c | Created `download_and_import_transtu.py` with download progress, retry logic, and SQLite import. Re-verified SNCFT routing prototype (5 direct options Tunis Ville → Borj Cédria, 800 millimes). Dashboard and roadmap updated. | `tools/data_pipeline/sources/download_and_import_transtu.py`; routing output verified exit 0. |

## Current task state

- **Active task:** TUM-P0-003c — multi-operator GTFS import (scripts created, owner to run downloads).
- **Gate determination:** Phase 0 exit is not approved. TUM-P0-004 licensing still blocked.
- **Current next TODO:** TRANSTU GTFS download deferred to backlog TODO (pending reliable host/source). Multi-modal feasibility evaluated across 3 independent live networks (National & Banlieue Rail, Sahel Metro, Regional Bus, RFR Rapid Rail). Proceed to Phase 0 gate evaluation (TUM-P0-012) and next architectural steps.
- **Validation:** Multi-modal data & routing verified across:
  1. SNCFT Banlieue Sud (Tunis Ville ➔ Borj Cédria, 800 millimes)
  2. SNCFT Sahel Metro (Sousse Bab Jdid ➔ Monastir, 350 millimes)
  3. SRT Médenine Regional Bus (Medenine Centre ➔ Houmet Souk Djerba, 4 departures)
  4. RFR Tunis Rapid Rail (Line E Barcelone ➔ Bougatfa, Line D Barcelone ➔ Gobaa)
