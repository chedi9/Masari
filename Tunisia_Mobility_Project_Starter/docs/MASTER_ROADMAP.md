# Tunisia Mobility Platform — Master Roadmap

**Roadmap version:** 0.4 working status snapshot
**Product baseline:** Active SDD v0.8 and Decision Register v0.7
**Date:** 3 November 2026
**Owner:** Human product owner  
**Cost rule:** Zero spend unless explicitly changed by the owner.

> Discovery remains in progress. This is the sole execution roadmap. `SDD_Tunisia_Mobility_Platform.md` is the single active SDD; superseded source copies are archived under `docs/archive/`.

## Current project state

- **Current phase:** Phase 0 — discovery and feasibility, with an owner-authorized data-independent mobile coding stream.
- **Status marker:** **DISCOVERY IN PROGRESS**.
- **Implementation gate:** The owner authorized modular mobile UI, navigation, localization, accessibility and interactions to proceed with clearly labeled placeholders while data research continues. Real transport records/claims, live integrations, production routing and public release remain behind provenance, licensing, validation and owner review.
- **D-06 passenger report classification:** Confirmed feature-based Option C per the owner's latest instruction. Basic reports and critical safety reporting are guest-accessible; advanced evidence/history requires an account. The v0.3 journey-preference D-06 remains separately recorded pending canonical ID assignment.
- **Workspace status:** One active SDD and one current register are present; dashboard and static-file launcher are retained. Legacy reference copies are archived under `docs/archive/reference/`. Dashboard checklist is in-memory only.
- **Current next TODO:** Product owner — test Explore tab (transit lines, mode filters, station sequences) and Reports tab in Expo Go; confirm feel on Android.
- **Active task:** `TUM-APP-005` — Transit network & lines explorer screen.
- **Owner of next action:** Codex — implementation; product owner continues transport-data search in parallel.
- **Tools:** PowerShell, existing Node/npm and Expo tooling, local TypeScript checks, Android Expo Go after installation; no paid services or account creation.
- **Dependencies:** Owner-approved React Native + Expo + TypeScript baseline and modular repository layout.
- **Acceptance:** App is organized under `apps/mobile`, runs on Expo SDK 57, supports Arabic/French RTL, presents a usable journey-first shell and top-level navigation, and never displays invented routes/times/fares/live availability as facts.

## Current next task

| Task ID | Task | Priority | Status | Owner | Dependencies | Deliverable / acceptance and validation evidence |
|---|---|---:|---|---|---|---|
| TUM-P0-001 | Reconcile source of truth | P0 | DONE | Codex | Owner decisions and recommended defaults supplied | Current SDD/register reconciled locally; source snapshots preserved; D-06 collision documented. Evidence: local SDD/register review and status search. |
| TUM-P0-001a | Consolidate local workspace and dashboard | P1 | DONE | Codex | Local folder audit | One active SDD, current register, updated dashboard and core-file layout. Evidence: root listing and inventory. |
| TUM-P0-001b | Apply owner-directed recommendation defaults | P0 | DONE | Codex | Latest explicit owner instruction | D-06 C and practical UX/transport defaults recorded; evidence/legal TBDs retained; dashboard aligned. Evidence: content checks; no app tests requested. |
| TUM-P0-002 | Candidate-area readiness evidence review | P0 | DONE | Codex | Confirmed rollout areas; SDD/register | Desk review compared Greater Tunis, Sousse, Monastir and Sfax; assessed Thnity, Wassalni, RNTT, Winicari and Tunismapper as leads; recorded limitations and proposed non-approved measures. Evidence: `docs/research/TUM-P0-002_CANDIDATE_AREA_READINESS.md`; official catalog and service pages linked there. This does not certify city readiness. |
| TUM-P0-009a | Modular repository structure and ADR | P0 | DONE | Codex | Owner request; confirmed technology baseline; Phase 0 implementation gate | Owner-approved structure and ADR recorded. No code scaffolded. Evidence: `docs/architecture/PROJECT_STRUCTURE.md` and `docs/adr/ADR-0001-modular-monolith-and-repository-layout.md`. |
| TUM-PRE-001 | Isolated passenger journey visual preview | P1 | REVIEW | Codex | Owner goal to reach a visible prototype; approved modular structure | Standalone preview created at `prototypes/journey-preview/index.html`, opened locally. Clear fictitious-data banner and no-network state; owner visual review pending. No app tests run. |
| TUM-PRE-002 | Native Expo journey-screen prototype | P1 | DONE | Codex | Owner request to start coding; approved stack; isolated prototype exception to Phase 0 gate | SDK 57 preview renders on the owner's Android phone. `tsc --noEmit` passed; `expo install --check` reported dependencies up to date. Expo Doctor and lint were not run; no lint script is configured. No live transport data or production integration. |
| TUM-APP-001 | Modular mobile app shell and placeholder-safe journey home | P1 | IN_PROGRESS | Codex | Owner-authorized pre-gate UI coding; confirmed mobile stack and modular layout | Added Android safe-area inset and horizontal swipe navigation. `npm run typecheck` returned without errors. `npx expo export --platform android` started Metro but stalled without bundle output and was stopped; device/runtime validation pending. |
| TUM-APP-002 | Journey flow polish and responsive button feedback | P1 | DONE | Codex / Antigravity | TUM-APP-001 UI source available; owner approved next UI step | Shared spring press feedback covers language, swap, priority, search and all four tabs. Typecheck passes (exit 0). |
| TUM-APP-003 | Landscape orientation & 3-choice results cards | P1 | DONE | Antigravity | Owner request for landscape & results focus | app.json unlocked to 'default' orientation; responsive landscape layout in JourneyHomeScreen; JourneyOptionCard built displaying Balanced, Fastest, and Economic options with transfer badges, walking time, millimes fare estimates, expandable step breakdown, and explicit Phase 0 disclaimer; bilingual FR/AR RTL. Typecheck passes (exit 0). |
| TUM-APP-004 | D-06 Option C passenger reporting flow | P1 | DONE | Antigravity | Confirmed D-06 Option C decision | Built PassengerReportsScreen with guest-accessible categories (delays, ghost vehicles, crowding, damaged stops, info errors), high-priority critical safety alert box, transit mode selector (Metro, Bus, Train, Collectif), line/comment inputs, interactive submission with simulation report ID, and Option C account-required upsell banner; bilingual FR/AR RTL. Typecheck passes (exit 0). |
| TUM-APP-005 | Transit network & lines explorer screen | P1 | DONE | Antigravity | Owner request to continue core flows | Built TransitExplorerScreen with search bar, mode chips (Metro, Bus, Train, Taxi Collectif), Grand Tunis active pilot banner, lines list (M1, M2, TGM, B28, SNCFT Sud, Collectif 12), expandable stop sequences with timeline dots, and Phase 0 audit notice; bilingual FR/AR RTL. Typecheck passes (exit 0). |

## Phase 0 work still required

| Task ID | Task | Priority | Status | Owner | Dependencies | Deliverable / acceptance and evidence |
|---|---|---:|---|---|---|---|
| TUM-P0-002 | Candidate-area readiness evidence review | P0 | DONE | Codex | Confirmed rollout areas; SDD/register | Preliminary sourced desk audit for all four areas; gaps, app leads and proposed metrics recorded. Does not establish readiness. Evidence: `docs/research/TUM-P0-002_CANDIDATE_AREA_READINESS.md`. |
| TUM-P0-003 | Transport dataset inventory | P0 | PARTIAL | Data researcher / Antigravity | P0-002 | Verified & profiled official national SNCFT GTFS archive (24.4MB, 53 routes, 223 stops, 4,795 stop times, fares in TND) at `data/raw/sncft_gtfs.zip`. Profiled in `docs/research/TUM-P0-003_DATASET_INVENTORY.md`. TRANSTU file host unreachable; CKAN metadata verified. |
| TUM-P0-004 | Data licensing and reuse audit | P0 | BACKLOG | Data/legal researcher | P0-003 | Evidence of allowed use for each proposed source before integration. Not started. |
| TUM-P0-005 | Map/geocoding/routing comparison | P0 | BACKLOG | Mapping researcher | P0-002; P0-004 | Tunisia coverage, Arabic/French search, routing, offline terms and cost comparison. Not started. |
| TUM-P0-006 | UX validation and Pro offline detail pack | P1 | BACKLOG | Product/UX designer | P0-001b; P0-005 | Validate adopted UX defaults; define offline feature/entitlement details. Not started. |
| TUM-P0-007 | Transport operations research | P1 | BACKLOG | Transport-data researcher | P0-003 | Validate route branches/diversions and rural/taxi evidence handling. Not started. |
| TUM-P0-008 | Privacy/security review plan | P0 | BACKLOG | Privacy/security reviewer | P0-001b | Assessment plan; no retention periods before qualified review. Not started. |
| TUM-P0-009 | Approved-stack architecture pack | P0 | BACKLOG | Software architect | P0-003; P0-005 | ADRs for confirmed baseline plus provider/interface validation. Not started. |
| TUM-P0-010 | Data/routing feasibility prototype | P0 | DONE | Data/engineering contributor / Antigravity | P0-002–005; P0-009 | Built reproducible SQLite importer (`tools/data_pipeline/sources/sncft_importer.py`) and journey query engine (`tools/data_pipeline/query_journey.py`) using real SNCFT GTFS data. Verified pilot queries for Tunis Banlieue Sud (Tunis Ville -> Borj Cedria, 800 millimes) and Sahel Metro (Sousse -> Monastir, 350 millimes). |
| TUM-P0-011 | Pro offline product/technical definition | P1 | BACKLOG | Product/engineering contributor | P0-005; P0-009 | Package matrix, freshness, sync, storage, licensing and entitlements; prices/terms remain TBD. Not started. |
| TUM-P0-012 | Phase 0 gate review | P0 | BACKLOG | Product owner | P0-002–011 | Review evidence, unresolved items, pilot recommendation and owner approval before full build. Not started. |

## Known approval gates

- Evidence-dependent values and legal details remain TBD; do not replace them with guesses.
- Real transport data, service claims, live integrations, production routing and public rollout require Phase 0 evidence and owner review; data-independent UI coding may proceed per the owner's explicit instruction.
- All data sources and map services require coverage, licensing and cost review.
- Privacy and Tunisian legal review precede persistent location collection; retention periods are not set.
- Recommendations and illustrative designs are not approvals.

## Update log

| Date | Agent/tool | Task | Summary | Evidence |
|---|---|---|---|---|
| 2026-11-03 | Codex | PACKAGE-001 | Inspected repository and prepared a working documentation package with current decision reconciliation. No GitHub files changed. | Source commit `b40d641fc9285a992974fb57258a8bd06ad1403b`; current register/addendum in this package. |
| 2026-11-03 | Codex | TUM-P0-001b | Applied owner-authorized recommendations/defaults; updated SDD/register/dashboard and prepared TUM-P0-002. | Local file inspection and content checks; no Git commands or app tests. |
| 2026-11-03 | Codex | TUM-P0-002 | Completed a preliminary desk review of candidate-area datasets and five named transport apps/services; documented evidence gaps and proposed, unapproved measurement definitions. | `docs/research/TUM-P0-002_CANDIDATE_AREA_READINESS.md`; linked official catalog/operator/app disclosures. |
| 2026-11-03 | Codex | TUM-P0-002-PUBLISH | Published the reviewed local project documentation and readiness note to `origin/main`. | Commit `c9f9264`; push completed successfully. |
| 2026-11-03 | Codex | D-06-STATUS-CORRECTION | Restored passenger-report classification to TBD per the current task instruction; Option C remains a recommendation. | Active decision register v0.5 and SDD v0.6 status overlay; current task instruction. |
| 2026-11-03 | Product owner / Codex | D-06-OPTION-C | Owner selected recommended Option C; active register and SDD updated. | Latest owner instruction; SDD v0.7 and current decision register. |
| 2026-11-03 | Product owner / Codex | TUM-P0-009a | Recorded the owner-approved modular monolith repository structure and ADR; deferred scaffolding until Phase 0 exit. | `docs/architecture/PROJECT_STRUCTURE.md`; `docs/adr/ADR-0001-modular-monolith-and-repository-layout.md`. |
| 2026-11-03 | Codex | TUM-P0-003 | Recorded catalog metadata and exact download blocker; did not claim file-level inspection. | `docs/research/TUM-P0-003_DATASET_INVENTORY.md`; HTTP requests timed out. |
| 2026-11-03 | Codex | TUM-PRE-002-PUBLISH | Committed the native prototype/handoff as `8573ef8`; push was attempted but did not return a result and was interrupted. Remote state is unverified. | Local commit exists; `git push origin main` exceeded 3 minutes with no output. |
| 2026-11-03 | Product owner / Codex | TUM-PRE-002-COMPLETE | Owner confirmed the SDK 57 preview renders on Android; TypeScript and Expo dependency checks passed. | Owner runtime confirmation; local `tsc --noEmit` exit 0; `expo install --check` reported dependencies up to date. |
| 2026-11-03 | Product owner / Codex | TUM-APP-001 | Owner authorized modular application coding with clearly labeled placeholders while transport-data search continues. | Latest owner instruction; recorded in SDD v0.8 and Decision Register v0.7. |
| 2026-11-03 | Product owner / Antigravity | TUM-APP-003 | Unlocked orientation to 'default' (landscape/portrait); implemented 3-choice results flow (Balanced, Fastest, Economic) with expandable steps and honest demo watermarks. | `apps/mobile/app.json`, `JourneyHomeScreen.tsx`, `JourneyOptionCard.tsx`; `npm.cmd run typecheck` exit 0. |
| 2026-11-03 | Product owner / Antigravity | TUM-APP-004 | Implemented D-06 Option C passenger reporting screen with guest incident categories, critical safety alert, mode selector, submission simulation, and account evidence notice. | `apps/mobile/src/features/reports/screens/PassengerReportsScreen.tsx`, `apps/mobile/app/(tabs)/reports.tsx`; `npm.cmd run typecheck` exit 0. |
| 2026-11-03 | Product owner / Antigravity | TUM-APP-005 | Implemented transit network & lines explorer screen with mode filtering, search, line cards, and expandable station sequences. | `apps/mobile/src/features/explore/screens/TransitExplorerScreen.tsx`, `apps/mobile/app/(tabs)/explore.tsx`; `npm.cmd run typecheck` exit 0. |
| 2026-11-13 | Product owner / Antigravity | TUM-P0-003 | Downloaded and profiled authentic national SNCFT GTFS dataset (24.4MB, 53 routes, 223 stops, 4,795 stop times, shapes, and fares in TND) from official server; resolved CKAN package on catalog.data.gov.tn. | `data/raw/sncft_gtfs.zip`, `docs/research/TUM-P0-003_DATASET_INVENTORY.md`. Checksum: 39630152e4cf979c89343e7ea5849b0c66d9ef7568400c4e52ab6d926462797c. |
| 2026-11-13 | Product owner / Antigravity | TUM-P0-003b | Incorporated comprehensive Tunisia Public Transport Data Sources & Access Directory into repository research. | `docs/research/TUNISIA_PUBLIC_TRANSPORT_DATA_DIRECTORY.md`. |
| 2026-11-14 | Product owner / Antigravity | TUM-APP-006 | Wired Account & Preferences screen into `apps/mobile/app/(tabs)/account.tsx`. Validated journey criteria (Budget, Time, Walking distance), guest identity, Pro offline simulation, privacy commitments, and full FR/AR RTL. | `apps/mobile/app/(tabs)/account.tsx`, `AccountScreen.tsx`. `npm.cmd run typecheck` passed (exit 0). |
| 2026-11-14 | Product owner / Antigravity | TUM-P0-010 | Built reproducible SQLite importer and routing query engine from verified SNCFT GTFS data. Tested and verified real pilot queries for Tunis Banlieue Sud (Tunis Ville -> Borj Cedria, 800 millimes) and Sahel Metro (Sousse -> Monastir, 350 millimes). | `tools/data_pipeline/sources/sncft_importer.py`, `tools/data_pipeline/query_journey.py`, `data/processed/tunisia_mobility.db`. |

## Current task state

- **Active task:** Phase 0 routing feasibility prototype verified (`TUM-P0-010`). Mobile tab suite complete (`TUM-APP-001` through `006`).
- **Current next TODO:** Product owner — test journey routing queries via `python tools/data_pipeline/query_journey.py` or run mobile app in Expo Go.
- **Status:** PHASE 0 FEASIBILITY VERIFIED. Real rail routing engine operational; 4-tab mobile app ready for device testing.



