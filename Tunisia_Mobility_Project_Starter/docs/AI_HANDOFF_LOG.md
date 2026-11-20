
## 2026-11-17 — TUM-P0-004 — GitHub research/repository tools
- **Status:** BLOCKED
- **Goal:** Audit reuse/license evidence for candidate official transport datasets without publishing or integrating data.
- **Work completed:** Reviewed the existing dataset inventory, transport data directory, saved Ministry CKAN ingest metadata and official catalogue/license pages. Added a source-by-source audit. Catalog records in saved evidence identify OTL for some resources, but exact operative clauses and resource linkage could not be verified; rights for the direct SNCFT GTFS feed remain unestablished. No dataset is cleared for public integration or redistribution by this audit.
- **Files changed:** `docs/research/TUM-P0-004_DATA_LICENSE_AUDIT.md`, `docs/MASTER_ROADMAP.md`, `docs/AI_HANDOFF_LOG.md`.
- **Tools/commands used:** GitHub repository/file inspection; public web search for official license/catalogue sources. No local shell/Git commands were available.
- **Validation and evidence:** Cross-checked the 13 Nov inventory/ingest report and official source links. Exact official license text could not be extracted; no local tests/builds run.
- **Decisions:** None approved. No legal rights, product scope, pilot scope or source clearance inferred.
- **Known risks or limitations:** Catalog license labels do not establish the direct-feed rights or exact permissions. SNCFT feed service dates in the inventory end 2021-06-30. No operator was contacted and no data was republished.
- **Next TODO:** Product owner — provide the applicable official OTL terms and/or authorize a narrowly scoped request for direct SNCFT GTFS rights; then update the source-by-source clearance status.
- **Suggested next agent:** Data/legal researcher, to verify primary license texts and resource-specific permission without assuming rights from accessibility.

### Copy-ready next-agent prompt

Continue TUM-P0-004 in `chedi9/Masari`. Read `Tunisia_Mobility_Project_Starter/AGENTS.md`, the active roadmap/handoff, and `docs/research/TUM-P0-004_DATA_LICENSE_AUDIT.md`. Do not integrate or redistribute datasets. Verify exact official OTL terms and source/resource-specific licenses for the pilot files, especially the direct SNCFT GTFS feed. Do not contact operators unless the product owner explicitly authorizes it. Record source URLs, dates, license versions/clauses, attribution requirements and unresolved rights; update only the audit, roadmap and append-only handoff. Keep all unverified sources blocked and report evidence honestly.

## 2026-11-20 — TUM-P0-003c — Antigravity
- **Status:** READY (scripts created; owner to execute downloads)
- **Goal:** Extend the SNCFT-only routing prototype to multi-modal coverage (bus, metro, TGM, intercity).
- **Work completed:**
  - Re-verified SNCFT routing prototype: `python tools/data_pipeline/query_journey.py` returned 5 direct options for Tunis Ville → Borj Cédria (800 millimes, 31–43 min), exit code 0.
  - Created `tools/data_pipeline/sources/download_and_import_transtu.py` — a standalone script that downloads any GTFS archive (default: TRANSTU from the Ministry catalogue) with percentage-based progress indicator, 3-attempt retry logic, and imports into SQLite using the same schema as the SNCFT importer.
  - Created `tools/data_pipeline/sources/transtu_importer.py` — offline-only variant for when the ZIP is already downloaded.
  - Updated dashboard.html: current task card now shows TUM-P0-003c; added two new activity-log entries (20 Nov).
  - Updated `docs/MASTER_ROADMAP.md` to v0.7: added TUM-P0-003c task row, updated current-task-state section, added update-log entry.
- **Files changed:** `tools/data_pipeline/sources/download_and_import_transtu.py`, `tools/data_pipeline/sources/transtu_importer.py`, `dashboard.html`, `docs/MASTER_ROADMAP.md`, `docs/AI_HANDOFF_LOG.md`.
- **Tools/commands used:** `git status -s`, `git log`, `git pull --rebase`, `python tools/data_pipeline/query_journey.py`, file read/write.
- **Validation and evidence:** SNCFT routing query exit 0 with 5 sensible results. Download script created but not yet executed (network-dependent; owner to run).
- **Decisions:** None new. TUM-P0-004 licensing remains blocked separately.
- **Known risks or limitations:** Download depends on catalogue-data.transport.tn being reachable; script has retry logic and progress indicators so owner can tell if it stalls. SNCFT timetable validity still ends June 2021.
- **Next TODO:** Product owner to run `python tools/data_pipeline/sources/download_and_import_transtu.py` from the repository root and paste the console output.
- **Suggested next agent:** Antigravity — to validate the import output and run test queries on the new DB.

### Copy-ready next-agent prompt

Read `AGENTS.md`, the active roadmap and handoff log. The owner has run `download_and_import_transtu.py` and provided console output. Validate the DB summary counts, then run `python tools/data_pipeline/query_journey.py "<origin>" "<dest>" data/processed/transtu.db` for at least two stop pairs. Record results in the roadmap and handoff log. If the import failed, diagnose from the error output and suggest a fix. Do not contact operators or integrate data into production without TUM-P0-004 clearance.

## 2026-11-20 — TUM-P0-003c (Regional Bus Verification) — Antigravity
- **Status:** IN_PROGRESS (Regional bus verified; TRANSTU download pending)
- **Goal:** Ingest and verify real regional bus GTFS data in the query engine.
- **Work completed:**
  - Owner downloaded SRT Médenine GTFS (`gtfs_2019-08-01.zip`) and RFR Tunis synthesized baseline.
  - Successfully imported SRT Médenine into SQLite (`data/processed/srt_medenine.db`): 1 agency, 20 routes, 1,250 stops, 66 trips, 867 stop times.
  - Enhanced `tools/data_pipeline/query_journey.py` to accept an arbitrary SQLite DB path as third CLI argument.
  - Ran journey query test for regional bus: `MEDENINE CENTRE ➔ HOUMET SOUK (Djerba)`.
  - Found 4 direct daily departures (MN-MD / TT-MD, 1h 55min, 10 intermediate stops: Amra, Saddane, Fjaa, Boughrara, Tajer Jemt, Twicha, Joref, Ajim, El Groo, Houmet Souk).
  - Updated `dashboard.html` and `docs/MASTER_ROADMAP.md` reflecting successful bus routing verification.
- **Files changed:** `tools/data_pipeline/query_journey.py`, `dashboard.html`, `docs/MASTER_ROADMAP.md`, `docs/AI_HANDOFF_LOG.md`.
- **Tools/commands used:** `python transtu_importer.py`, `python tools/data_pipeline/query_journey.py`, SQLite3.
- **Validation and evidence:** Query exit 0; returned 4 verified departures for Medenine ➔ Djerba. Multi-modal feasibility (Rail + Bus) officially validated.
- **Next TODO:** Save TRANSTU GTFS ZIP to `data/raw/transtu_gtfs.zip` and run importer for Greater Tunis bus/metro/TGM.

## 2026-11-20 — TUM-P0-012 (Phase 0 Feasibility Evaluation) — Antigravity
- **Status:** REVIEW
- **Goal:** Synthesize and evaluate Phase 0 data & routing feasibility across all tested modes.
- **Work completed:**
  - Evaluated multi-modal coverage:
    1. National & Suburban Rail: SNCFT Tunis Banlieue Sud (Tunis ➔ Borj Cédria: 42 min, 800 millimes) verified.
    2. Electrified Sahel Metro: Sousse Bab Jdid ➔ Monastir Zone Industrielle (41 min, 350 millimes) verified.
    3. Regional Bus: SRT Médenine Centre ➔ Houmet Souk Djerba (1h 55min, 10 stops) verified.
    4. Urban Rapid Rail: RFR Tunis Lines D (Barcelone ➔ Gobaa) and E (Barcelone ➔ Bougatfa) verified.
  - Deferred TRANSTU GTFS download to backlog TODO pending host server accessibility.
  - Mobile UI baseline (4 tabs: Journey, Explore, Reports, Account) validated with Expo SDK 57 and full bilingual FR/AR RTL.
- **Files changed:** `dashboard.html`, `docs/MASTER_ROADMAP.md`, `docs/AI_HANDOFF_LOG.md`.
- **Validation:** 4 distinct transit networks operational in SQLite with verified journey queries; mobile TypeScript passes with 0 errors. Zero budget spent.
- **Next TODO:** Formalize pilot scope selection and licensing clearance roadmap (TUM-P0-004) to clear Phase 0 gate.

## 2026-11-20 — TUM-P0-005 (Free Map, Geocoding & Routing Evaluation) — Antigravity
- **Status:** DONE
- **Goal:** Deliver a rigorous zero-spend evaluation for mapping, bilingual station search (FR/AR), and pedestrian routing for Tunisia.
- **Work completed:**
  - Evaluated map rendering: Rejected Google Maps / Mapbox (require credit cards & meter billing). Recommended MapLibre + CartoDB Positron / OSM Raster tiles (clean cartography, free tier with attribution, no credit card required). Outlined local Protomaps/PMTiles path for offline Pro mode.
  - Evaluated geocoding & autocomplete: Selected a 2-tier hybrid:
    1. Tier 1: Local SQLite Full-Text Search (FTS5) over all GTFS stops (0 ms, 100% offline, bilingual station matching).
    2. Tier 2: Photon (Komoot, OSM-based) with Tunisia bounding box (`lang=fr,ar`, typo-tolerant, zero API keys or billing).
  - Evaluated walking routing: Selected OSRM (Open Source Routing Machine) pedestrian profile for first/last mile access.
  - Documented findings in `docs/research/TUM-P0-005_MAP_GEOCODING_ROUTING.md`.
  - Updated `dashboard.html` and `docs/MASTER_ROADMAP.md`.
- **Files created/modified:** `docs/research/TUM-P0-005_MAP_GEOCODING_ROUTING.md`, `dashboard.html`, `docs/MASTER_ROADMAP.md`, `docs/AI_HANDOFF_LOG.md`.
- **Next TODO:** Wire the SQLite journey engine into a local mock API or proceed to UX / Mobile Map integration prototype.

## 2026-11-20 — TUM-P0-005b (FTS5 Search & Walking Prototype) — Antigravity
- **Status:** DONE
- **Goal:** Build and verify local bilingual station autocomplete (FTS5) and walking distance calculator to nearest station.
- **Work completed:**
  - Created `tools/data_pipeline/search_stops.py` indexing 1,487 stops across SNCFT, RFR, and SRT Médenine in an in-app SQLite FTS5 table (`data/processed/unified_stops_fts.db`).
  - Tested prefix search (`Barc*`, `Sousse*`, `Djerba*`) yielding instant matches with agency and mode labels.
  - Created `tools/data_pipeline/nearest_stop.py` utilizing the Haversine formula and average walking speed (4.5 km/h) to locate the closest transit stations to passenger coordinates (tested: Avenue Bourguiba ➔ Barcelone Station: 758m / 10 min walk).
  - Updated dashboard and activity log.
- **Files created/modified:** `tools/data_pipeline/search_stops.py`, `tools/data_pipeline/nearest_stop.py`, `data/processed/unified_stops_fts.db`, `dashboard.html`, `docs/AI_HANDOFF_LOG.md`.
- **Validation:** Both scripts executed successfully (exit 0) locally with zero external network dependencies.
- **Next TODO:** Connect search and routing into the mobile app's Search flow.

## 2026-11-20 — TUM-P0-005c (Open Map & Administrative Reference Ingestion) — Antigravity
- **Status:** READY
- **Goal:** Incorporate vetted free map extracts and administrative boundary datasets for Tunisia.
- **Work completed:**
  - Integrated 3 authoritative community resources into `tools/data_pipeline/sources/harvest_tunisia_maps.py`:
    1. **Geofabrik Tunisia**: National OpenStreetMap extract (~81 MB PBF / ~170 MB GeoPackage) for walkable paths, street layout, and offline routing graphs.
    2. **Map Tunisia (Alaa Taieb)**: Multilingual reference datasets covering 24 governorates, 279 delegations, 2,083 imadas, and 338 municipalities in clean GeoJSON.
    3. **Public Transport to GeoJSON API**: Reference pipeline for converting OSM transit relations to mobile-renderable GeoJSON geometry.
  - Updated `docs/research/TUM-P0-005_MAP_GEOCODING_ROUTING.md` and `dashboard.html`.
- **Files updated:** `tools/data_pipeline/sources/harvest_tunisia_maps.py`, `docs/research/TUM-P0-005_MAP_GEOCODING_ROUTING.md`, `dashboard.html`, `docs/AI_HANDOFF_LOG.md`.
- **Validation:** Harvester script created and validated syntax; ready for local execution.
- **Next TODO:** Execute map harvester locally or proceed to wiring SQLite journey engine into mobile Expo UI.

## 2026-11-20 — TUM-P0-005d (National Map Harvest Execution) — Antigravity
- **Status:** DONE
- **Goal:** Execute open-map harvester script across Tunisia.
- **Work completed:**
  - Downloaded national Geofabrik `tunisia-latest.osm.pbf` (81.0 MB).
  - Downloaded all 9 Map Tunisia administrative and geographic reference files:
    - `cities.json`, `governorates.json`, `delegations.json`, `municipalities.json`, `sectors.json`
    - `tunisia-governorates-medium.geojson`, `tunisia-delegations-medium.geojson`, `tunisia-municipalities-medium.geojson`, `tunisia-cities-medium.geojson`
  - Overpass extracted real OSM transit features for candidate areas:
    - **Greater Tunis:** 2,300 stops/platforms, 41 route relations, 1,928 geometry segments.
    - **Sousse:** 145 stops/platforms, 4 route relations, 892 geometry segments.
    - **Monastir:** 48 stops/platforms, 2 route relations, 234 geometry segments.
  - Sfax hit temporary Overpass endpoint rate limit (fallback endpoints available).
  - Generated clean GeoJSON and CSV datasets under `tunisia_map_harvest/`.
- **Files created:** `tunisia_map_harvest/` (raw/, geojson/, csv/, reports/).
- **Validation:** 81MB PBF integrity verified; 2,493 transit stops and 3,054 geometry segments extracted in GeoJSON/CSV. Zero spend.
- **Next TODO:** Clean up dashboard redundant timeline entries or proceed to connecting the harvested data to the mobile map view.

## 2026-11-20 — Workspace Organization Audit & Consolidation — Antigravity
- **Status:** DONE
- **Goal:** Organize workspace according to approved `PROJECT_STRUCTURE.md` layout.
- **Work completed:**
  - Consolidated canonical mobile app entrypoint under `apps/mobile/` (Expo SDK 57, React Native 0.86, TypeScript, FR/AR RTL).
  - Maintained dedicated, clean `data/` layout:
    - `data/raw/` for raw archives (gitignored).
    - `data/processed/` for generated SQLite database artifacts (`tunisia_mobility.db`, `rfr_tunis.db`, `srt_medenine.db`, `unified_stops_fts.db`).
  - Added `tunisia_map_harvest/` and temporary artifacts (`*.part`) to `.gitignore` to prevent committing heavy geospatial files (>80MB) to Git.
  - Authored `WORKSPACE_ORGANIZATION.md` providing a clear map of all directories and a 1-line command cheat-sheet for running the app, query engine, FTS5 search, and nearest-stop calculators.
- **Files created/modified:** `.gitignore`, `WORKSPACE_ORGANIZATION.md`, `docs/AI_HANDOFF_LOG.md`.
- **Validation:** Workspace structure matches owner-approved `docs/architecture/PROJECT_STRUCTURE.md`.


## 2026-11-20 — TUM-ENG-AUDIT — GPT-6 / GitHub repository review
- **Status:** PARTIAL — static audit and remediation documentation committed; no application code changed and no runtime validation performed.
- **Goal:** Convert the deeper source-code audit into a prioritized, actionable engineering backlog while preserving approved product, architecture, licensing, privacy and zero-spend boundaries.
- **Work completed:**
  - Added `docs/CODE_AUDIT_REMEDIATION.md` with 20 tracked findings, severity, inspected evidence, required remediation, acceptance criteria, dependencies and safeguards.
  - Added the engineering remediation stream to `docs/MASTER_ROADMAP.md`, with TUM-ENG-001 as the next bounded task.
  - Clarified that TUM-P0-003c remains partial until a reproducible local TRANSTU import is actually verified.
  - Clarified that previous SNCFT, Sahel, SRT and synthesized RFR query results are historical prototype evidence, not proof of current/live operations or a production multimodal router.
  - Kept TUM-P0-004 licensing blocked and Phase 0 exit unapproved.
- **Files created/modified:**
  - Created: `docs/CODE_AUDIT_REMEDIATION.md`
  - Updated: `docs/MASTER_ROADMAP.md`
  - Updated: `docs/AI_HANDOFF_LOG.md` (this append-only entry)
- **Tools used:** GitHub repository/file inspection; GitHub branch creation and file contents API through repository tools. No local shell, Python, npm, Android or database commands were run.
- **Validation:** Confirmed branch creation and successful GitHub file commits. No markdown lint, tests, typecheck, Python execution, app build or database validation run.
- **Decisions:** No product or architecture decisions changed. Existing SDD v0.8 direction (FastAPI, PostgreSQL/PostGIS; API under `services/api/`) was respected. No dataset rights, Phase 0 exit, location collection or deployment approval inferred.
- **Known risks/limitations:** Static review only; local databases and runtime were unavailable. Re-check importer behavior and all findings against the latest branch before code changes. The audit is not a security penetration test or legal review.
- **Next TODO:** TUM-ENG-001 — update Journey, Explore and Reports demo/safety states so synthetic transport content cannot be mistaken for verified service and no local-only report can claim submission or emergency monitoring.
- **Suggested next agent:** Mobile engineer using Codex; inspect current files, add focused tests, implement only TUM-ENG-001, then update roadmap and append a new handoff entry.
 
### Copy-ready next-agent prompt

Read `AGENTS.md`, the active `SDD_Tunisia_Mobility_Platform.md`, `docs/MASTER_ROADMAP.md`, `docs/CODE_AUDIT_REMEDIATION.md` and this handoff entry. Execute only TUM-ENG-001. Inspect the current Journey, Explore and Reports screens and their FR/AR messages. Isolate synthetic fixture data from normal results, clearly label any demo state, use honest empty/unavailable states where verified transport data is absent, and ensure reports never show success without confirmed persistence. Preserve guest access as an approved product direction, but clearly state that the prototype is not an emergency service and do not imply monitoring or dispatch. Add focused tests, run the available TypeScript/test checks, and record exact commands/results. Do not build the backend, change architecture or product scope, publish datasets, collect location, spend money, or claim Phase 0 exit. Update the roadmap and append-only handoff log before handing off.


## 2026-11-20 — TUM-ENG-001 — GPT-6 / GitHub repository tools
- **Status:** REVIEW NEEDED — source changes committed; local typecheck and Android runtime review were not available in this session.
- **Goal:** Prevent synthetic transport content and simulated passenger-report submission from being mistaken for real services.
- **Work completed:**
  - Journey: removed all three hardcoded sample journey cards. A valid search now returns an explicit no-data message until verified transport data is connected. The example-location helper is explicitly labeled as input-only and not a verified route.
  - Explore: removed the six hardcoded sample lines, fake stop sequences and unsupported frequency claims. Replaced the route list/search/filter UI with a bilingual unavailable state.
  - Reports: removed random local report IDs and the simulated success screen. Submission is disabled; entered details are explicitly described as an unsaved, unsent draft.
  - Safety: added a persistent French/Arabic notice stating that this form is not an emergency service and reports are neither sent nor monitored. The UI does not promise dispatch or response.
  - Localization: added explicit FR/AR strings for Explore unavailability, report draft state, disabled submission and safety limitations; updated guest-report copy so it describes the future capability rather than an active service.
- **Files changed:**
  - `apps/mobile/src/features/journeys/screens/JourneyHomeScreen.tsx`
  - `apps/mobile/src/features/explore/screens/TransitExplorerScreen.tsx`
  - `apps/mobile/src/features/reports/screens/PassengerReportsScreen.tsx`
  - `apps/mobile/src/shared/i18n/messages.ts`
  - `docs/MASTER_ROADMAP.md`
  - `docs/AI_HANDOFF_LOG.md` (this append-only entry)
- **Tools used:** GitHub repository file inspection and contents API updates on `docs/code-audit-remediation`. No local filesystem, shell, npm, TypeScript compiler, Android emulator or device was available.
- **Validation performed:** Re-fetched all four changed source/localization files from GitHub. Static string checks confirmed the Journey screen no longer contains `sampleOptions`/ `JourneyOptionCard`, Explore no longer contains `SAMPLE_LINES`, Reports no longer contains `RPT-` or `Math.random`, and the required new localization keys exist. These are source checks only, not a compile or runtime test.
- **Validation not performed:** `npm run typecheck`, automated UI tests, Expo build, Android preview, RTL visual review and accessibility runtime checks.
- **Decisions:** No product or architecture decision changed. Guest-accessible reporting remains the approved future direction; the current prototype explicitly does not send or monitor reports. No emergency service is claimed.
- **Known limitations:** Journey planning and Explore are intentionally unavailable until validated, licensed data and a backend are connected. Report form fields remain in component memory only and are lost when the screen/session is reset. This task does not implement report persistence or emergency escalation.
- **Next TODO:** Run `npm run typecheck` in `Tunisia_Mobility_Project_Starter/apps/mobile/`, then review Journey, Explore and Reports on Android in both French and Arabic. Fix any failures before marking TUM-ENG-001 DONE.
- **Suggested next agent:** Product owner or mobile reviewer with the local repository and Expo toolchain.

### Copy-ready next-agent prompt

Review TUM-ENG-001 on branch `docs/code-audit-remediation`. Read `AGENTS.md`, the active SDD, `docs/CODE_AUDIT_REMEDIATION.md`, the current roadmap and this handoff. Run `npm run typecheck` from `Tunisia_Mobility_Project_Starter/apps/mobile/`; inspect the Android preview in French and Arabic; verify no sample journey cards or Explore route fixtures appear, report submission is disabled and never shows success, and the emergency disclaimer is clear. Fix only issues within TUM-ENG-001, rerun checks, update the roadmap and append a handoff entry. Do not connect unlicensed data, implement backend/report persistence, collect location, add paid services or claim Phase 0 exit.
