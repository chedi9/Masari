# Tunisia Mobility Platform — Master Roadmap

**Roadmap version:** 0.7 — multi-operator import scripts and routing verification  
**Product baseline:** Active SDD v0.8 and Decision Register v0.7  
**Date:** 20 November 2026  
**Owner:** Human product owner  
**Cost rule:** Zero spend unless explicitly changed by the owner.

> Discovery remains in progress. This is the sole execution roadmap. `SDD_Tunisia_Mobility_Platform.md` is the active SDD; superseded source copies are archived under `docs/archive/`.

## CURRENT NEXT TODO

**TUM-ENG-001 — Review implemented demo trust boundary and passenger-report safety changes.** Implementation is committed on `docs/code-audit-remediation`; review the changed Journey, Explore, Reports and FR/AR messages, run `npm run typecheck` from `apps/mobile/`, and perform a focused Android screen review. If checks pass, mark the task DONE; otherwise fix the reported issues and repeat validation. **Owner:** Product owner / mobile reviewer. **Priority:** P0. **Dependencies:** Current implementation on the audit PR branch. **Acceptance:** TypeScript check passes; synthetic transport fixtures cannot appear in Journey or Explore; no fake report ID or success state exists; submission remains disabled until a backend confirms persistence; safety limitation is explicit in French and Arabic. **Data boundary:** TUM-P0-004 remains blocked; no dataset is approved for public integration.

## Current project state

- **Current phase:** Phase 0 — discovery and feasibility, with an owner-authorized data-independent mobile coding stream.
- **Status marker:** **DISCOVERY IN PROGRESS**.
- **Implementation gate:** Modular mobile UI, navigation, localization, accessibility and data-independent interactions may proceed with clearly labeled placeholders. Real transport records, service claims and production routing remain evidence-gated.
- **Active engineering task:** TUM-ENG-001 — REVIEW; implementation committed to `docs/code-audit-remediation`, pending local typecheck and Android review.
- **Phase 0 blocker:** `TUM-P0-004` remains blocked pending primary license evidence/owner action.
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
- **TUM-P0-005:** A research comparison exists, but candidate providers, Tunisia coverage, Arabic/French quality, current terms, usage limits, fallback behavior and on-device performance are not yet validated or approved for production.
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
| TUM-P0-003c | Multi-operator GTFS import | P0 | PARTIAL | Product owner + Antigravity | P0-003; P0-010 | Download and import TRANSTU, SNTRI, STS, SORETRAS, SRT Médenine GTFS. SRT Médenine imported (1,250 stops, 20 routes) and bus routing verified (Medenine ➔ Djerba). TRANSTU download pending. |
| TUM-P0-004 | Data licensing and reuse audit | P0 | BLOCKED | Data/legal researcher | P0-003 | Audit recorded; exact terms/resource rights and direct-feed permission still needed. |
| TUM-P0-005 | Map/geocoding/routing comparison | P0 | DONE | Mapping researcher / Antigravity | P0-002; P0-004 | Produced zero-cost evaluation report (`docs/research/TUM-P0-005_MAP_GEOCODING_ROUTING.md`) covering MapLibre + CartoDB tiles, Photon/Nominatim multilingual geocoding, and OSRM walking routes. |
| TUM-P0-006 | UX validation and Pro offline detail pack | P1 | BACKLOG | Product/UX designer | P0-001b; P0-005 | Device/RTL/accessibility validation and required offline decisions. |
| TUM-P0-007 | Transport operations research | P1 | BACKLOG | Transport-data researcher | P0-003 | Branch/diversion/rural/taxi evidence handling. |
| TUM-P0-008 | Privacy/security review plan | P0 | BACKLOG | Privacy/security reviewer | P0-001b | Review plan; no persistent location collection before qualified review. |
| TUM-P0-009 | Approved-stack architecture pack | P0 | BACKLOG | Software architect | P0-003; P0-005 | ADR and provider/interface validation; no provider approved by default. |
| TUM-P0-010 | Data/routing feasibility prototype | P0 | DONE | Data/engineering contributor | P0-002–005; P0-009 | Reproducible rail import/query; historical schedule limitations documented. |
| TUM-P0-011 | Pro offline product/technical definition | P1 | BACKLOG | Product/engineering contributor | P0-005; P0-009 | Package matrix, freshness, sync, storage, licensing and entitlement definitions. |
| TUM-P0-012 | Phase 0 gate review | P0 | REVIEW | Product owner | P0-002–011 | Formal review package; no exit approval implied. |

## Engineering remediation stream

The source-code audit is recorded in `docs/CODE_AUDIT_REMEDIATION.md`. These engineering tasks are a separate, owner-authorized implementation stream; they do not approve Phase 0 exit, public data use, production routing, location collection, deployment or monetization.

| Task ID | Task | Priority | Status | Owner | Dependencies | Deliverable / acceptance |
|---|---|---:|---|---|---|---|
| TUM-ENG-001 | Demo trust boundary and passenger-report safety | P0 | REVIEW | GPT-6 (GitHub) | None; active SDD and audit plan | Removed hardcoded journey cards and Explore lines; report submission disabled; FR/AR unavailable and safety disclaimers added. Awaiting local typecheck and Android review. |
| TUM-ENG-002 | Safe GTFS import and data validation | P0 | BACKLOG | Data engineer | Existing importer/schema review | Reversible import, feed validation report, and last-known-good database preserved on failure. |
| TUM-ENG-003 | GTFS calendars, stop identity and fare correctness | P0 | BACKLOG | Data engineer | ENG-002 | Service-date/exception correctness, ambiguous-stop handling and per-result fare or explicit unknown. |
| TUM-ENG-004 | Journey-domain engine and deterministic ranking | P1 | BACKLOG | Routing engineer | ENG-003 | Tested direct journeys and real Economic/Fastest/Balanced ranking; transfers are a separately validated increment. |
| TUM-ENG-005 | FastAPI data-backed vertical slice | P1 | BACKLOG | Backend engineer | ENG-002, ENG-003; SDD v0.8 | Versioned API contracts, source metadata, endpoint tests and modular domain boundaries. |
| TUM-ENG-006 | Connect mobile Journey and Explore | P1 | BACKLOG | Mobile engineer | ENG-005 | Typed API client; hardcoded sample records removed from normal flows; loading/empty/error/stale states. |
| TUM-ENG-007 | Reports lifecycle and persistent preferences | P1 | BACKLOG | Backend + mobile engineers | ENG-005; privacy/security review for sensitive workflows | Server-persisted reports and preferences; moderation boundary; no false success. |
| TUM-ENG-008 | Geospatial walking and multilingual stop search | P1 | BACKLOG | Geospatial engineer | Source/coverage validation; ENG-002 | Alias-aware stop search and routed pedestrian distance; straight-line estimates explicitly labeled. |
| TUM-ENG-009 | Automated tests and CI hardening | P1 | BACKLOG | Engineering | Start with ENG-001/002 | Reproducible Python/mobile tests, TypeScript checks, dependency lock and CI gates. |

**Execution rule:** one active executor and one bounded task at a time, following `AGENTS.md`. Do not change the approved architecture or product decisions silently. The SDD's chosen backend direction is Python + FastAPI and PostgreSQL + PostGIS; the approved repository structure places the API under `services/api/`. Provider selection, operational details and any paid infrastructure remain gated by evidence and owner approval.

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

- **Active task:** None currently in execution. The next ready engineering task is TUM-ENG-001.
- **Engineering next TODO:** Review TUM-ENG-001 implementation, run `npm run typecheck` from `Tunisia_Mobility_Project_Starter/apps/mobile/`, and verify Journey/Explore/Reports in an Android preview. Mark DONE only after those checks pass.
- **Phase 0 next gate:** TUM-P0-012 remains in REVIEW; Phase 0 exit is not approved. TUM-P0-004 licensing remains BLOCKED.
- **Data import follow-up:** TUM-P0-003c remains PARTIAL. The TRANSTU download/import still requires a successful, reproducible local run against a verified source. Do not treat the downloader script or an old local archive as proof of current service.
- **Historical prototype evidence only:** Previous local query runs were recorded for SNCFT Banlieue Sud, SNCFT Sahel Metro, SRT Médenine and a synthesized RFR feed. These results demonstrate that prototype queries ran against those particular local datasets; they do not establish current timetables, live services, national coverage, legal clearance or a production multimodal router.
- **Validation evidence:** See dated TUM-P0-003c/TUM-P0-010 handoff entries and the source-specific dataset inventory. Re-run all checks against the actual local database versions before relying on them.


| 2026-11-20 | GPT-6 / GitHub repository review | TUM-ENG-AUDIT | Added a source-code audit remediation plan and a bounded engineering backlog. Corrected the roadmap's current next action and clarified that prior local route-query results are historical prototype evidence, not live service verification. | `docs/CODE_AUDIT_REMEDIATION.md`; static GitHub source inspection only; no code/runtime tests. |
| 2026-11-20 | GPT-6 / GitHub repository tools | TUM-ENG-001 | Removed synthetic journey results and Explore sample routes; disabled simulated passenger-report submission; added explicit FR/AR availability and non-emergency disclaimers. Status REVIEW pending local validation. | JourneyHomeScreen.tsx; TransitExplorerScreen.tsx; PassengerReportsScreen.tsx; messages.ts; static source verification only. |\n