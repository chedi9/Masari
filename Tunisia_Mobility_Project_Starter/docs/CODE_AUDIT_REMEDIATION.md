# Masari — Code Audit Remediation Plan

**Audit date:** 20 November 2026  
**Repository reviewed:** `chedi9/Masari`, branch `main`  
**Audit type:** Static source and documentation review  
**Status:** REVIEW NEEDED — findings documented; implementation not performed  
**Scope:** Expo mobile prototype, Python/SQLite data pipeline, journey query, reporting UI, project execution documentation.

> This document converts the source-code audit into implementation tasks. It does not certify the app, imported datasets, timetable validity, fares, legal rights, or launch readiness. The review was performed against GitHub source; no local databases, Android runtime, package installation, build, or automated test execution was available. Re-check each finding against the current branch before changing code.

## 1. Executive assessment

Masari has a useful Expo/React Native/TypeScript UI prototype and exploratory Python/SQLite transport-data tools. It is not yet an operational journey-planning service. The mobile screens are not connected to a backend; visible route and journey content includes hardcoded demonstration data; passenger reports are local UI simulations; and the Python journey query is a direct-trip prototype with important timetable, station-resolution and fare limitations.

**Release boundary:** Do not present sample routes, sample departures, fares, taxi availability, report submission, emergency escalation, live vehicle information, or straight-line walking estimates as verified operational services. Keep the Phase 0 and source-licensing gates intact.

## 2. Findings and required remediation

### P0 — Trust, data integrity and passenger safety

| ID | Finding | Current evidence | Required remediation | Acceptance criteria |
|---|---|---|---|---|
| AUD-001 | Demo transport content can be mistaken for real network information. | `JourneyHomeScreen.tsx` defines hardcoded `sampleOptions`; `TransitExplorerScreen.tsx` defines `SAMPLE_LINES`. | Keep demonstration data isolated from production data models. Show a persistent, unambiguous demo label and never mix sample records into real search results. Prefer an honest empty/unavailable state when no validated data exists. | Automated UI/data tests prove demo records cannot be returned by production search. Screens clearly label demo mode in FR and AR. No sample fare/time/line is represented as a real service. |
| AUD-002 | Passenger report submission is simulated. | `PassengerReportsScreen.tsx` generates a local random report identifier and has no persistence/API integration. | Keep the UI in explicit demo/unavailable mode until a real report endpoint, persistence, validation, moderation lifecycle and server-generated ID exist. Do not show a success confirmation for an unsubmitted report. | A submitted report is persisted server-side, receives a server ID, survives app restart, and returns a traceable status. Failure states never claim success. |
| AUD-003 | Critical safety reporting could be misunderstood as monitored emergency support. | The UI exposes a safety category/action, but no delivery, escalation or monitored backend was identified. | Preserve the owner-approved guest-accessible safety-reporting direction, but state clearly that the prototype is not monitored and is not an emergency service. Do not imply dispatch, emergency response or guaranteed receipt. Define an owner-approved escalation process before enabling a live safety workflow. | No safety UI claims a report was delivered or help is on the way unless a verified backend response confirms it. The non-emergency limitation is visible before submission. |
| AUD-004 | Import process can replace valid data with an incomplete/invalid import. | The inspected GTFS importer rebuilds tables destructively before a complete replacement has been validated. | Import into a new temporary database; validate required files, schemas, row counts, IDs, coordinates, referential integrity and feed metadata; commit/swap only after all checks pass. Preserve the last-known-good database on any failure. | Fault-injection tests for invalid ZIP, missing required files, malformed rows and interrupted import leave the previous database usable and unchanged. |
| AUD-005 | Invalid or missing stop coordinates may enter the database. | Import code uses fallback coordinate values for absent data in the inspected path. | Reject missing/out-of-range coordinates for routable stops; quarantine invalid rows with source-row diagnostics. Do not silently substitute (0,0). | Import report counts accepted/rejected rows; no invalid coordinate enters the active stop table. |

### P1 — Timetable, routing and fare correctness

| ID | Finding | Current evidence | Required remediation | Acceptance criteria |
|---|---|---|---|---|
| AUD-006 | Service calendars and exceptions are not used to determine whether a trip operates on the requested date. | The inspected importer/query path does not implement complete `calendar.txt` and `calendar_dates.txt` service-date evaluation. | Import calendars and exceptions. Evaluate service in the feed's local timezone and requested service date, including GTFS times after 24:00 and midnight rollover. | Tests cover weekday/weekend, start/end dates, added/removed service exceptions, no-service dates and after-midnight trips. Inactive services never appear. |
| AUD-007 | Stop matching is ambiguous. | `query_journey.py` uses partial `LIKE` matching with `LIMIT 1`. | Use normalized exact/alias matching first, ranked fuzzy matching second, and require passenger selection when multiple plausible stops remain. Include city, operator, mode and proximity context. | Ambiguous queries return candidate choices rather than silently selecting the first row. Arabic, French, transliteration and punctuation variants have fixtures. |
| AUD-008 | Journey search only finds direct trips. | The SQL joins origin and destination stop times on the same `trip_id`. | Keep direct-trip search as a supported initial capability, then add a separately tested transfer planner using explicit interchange rules, transfer-time buffers and bounded search. Do not imply multimodal/transfer coverage until validated. | Tests prove valid one-transfer journeys, reject impossible transfers, prevent loops, and enforce configurable transfer limits. |
| AUD-009 | Fare can be incorrectly reused across returned departures/routes. | The query looks up fare data using the first returned trip's route and reuses that value. | Resolve fare independently for each journey using applicable route, origin/destination zones, fare attributes/rules and source validity. Return `unknown` rather than an invented estimate when rules are absent or unsupported. | Multi-route tests verify each result gets its own correct fare or an explicit unknown value. Fare provenance/date/confidence are returned. |
| AUD-010 | Journey priorities may only change selection/highlighting, not actual ranking. | The UI builds fixed sample options and stores the selected priority. | Implement ranking in the journey domain layer using explicit, testable economic/fastest/balanced scoring. Respect confirmed budget/time/walking preferences; explain trade-offs. | The same candidate set ranks differently for the three priorities in deterministic tests. Missing fare/reliability data is handled transparently, not treated as zero. |
| AUD-011 | Journey results lack sufficient provenance/freshness. | The inspected result object returns trip details/fare but no complete source manifest, validity or confidence contract. | Attach operator/source ID, feed version/hash, retrieval timestamp, service validity, license/clearance status, quality flags and freshness state to network and journey results. | Every result has traceable source metadata; expired/historical/incomplete feeds are visibly marked and cannot be described as live/current. |

### P1 — Backend and mobile integration

| ID | Finding | Current evidence | Required remediation | Acceptance criteria |
|---|---|---|---|---|
| AUD-012 | No implemented API connects the Python data tools to the mobile app. | Repository structure inspection found no implemented backend under the planned API location; mobile screens have no real transport API client. | Implement the owner-approved Python + FastAPI modular monolith in the repository's agreed service location, with typed/versioned contracts. Keep domain logic independent of HTTP and persistence. | Health, stop search, network metadata and journey endpoints have API tests and OpenAPI contracts; mobile client consumes the contract. |
| AUD-013 | Explore is a hardcoded list, not a data-backed network explorer. | `TransitExplorerScreen.tsx` renders local `SAMPLE_LINES`. | Replace it with validated network/route/stop endpoints. Show per-area/per-mode availability and data-quality state; use an empty state when coverage is unavailable. | No hardcoded sample route is included in normal API responses. City/mode coverage is source-backed. |
| AUD-014 | Journey search UI does not call a journey service. | `JourneyHomeScreen.tsx` constructs local sample options. | Replace local results with API-backed search and typed loading/success/empty/error/stale states. Keep manual origin/destination entry and future location permission optional. | Android end-to-end test searches two real, validated stops and displays only returned journeys with source/freshness metadata. |
| AUD-015 | Account preferences are transient UI state. | `AccountScreen.tsx` stores preferences in component state and simulates save feedback. | Persist locally first; sync only after account/backend behavior is defined. Use real save success/failure feedback. | Preferences survive app restart and affect journey ranking. No success toast before persistence succeeds. |

### P1/P2 — Geospatial, reliability and quality controls

| ID | Finding | Current evidence | Required remediation | Acceptance criteria |
|---|---|---|---|---|
| AUD-016 | Nearest-stop straight-line distance is not a walking route. | `nearest_stop.py` uses Haversine distance and a fixed walking-speed estimate. | Label it as approximate straight-line proximity only. Use a pedestrian routing graph/service for walking distance and route geometry; preserve a clear unavailable fallback. | UI distinguishes straight-line distance from routed walking distance. No pedestrian ETA is claimed without a route result. |
| AUD-017 | Stop FTS index rebuild drops the current index before the replacement is ready. | `search_stops.py` drops and recreates index tables in place. | Build a versioned temporary index and atomically switch after integrity checks. Preserve the last working index on failure. | Failure-injection tests leave the old index searchable. |
| AUD-018 | Search does not have a complete multilingual alias model. | The inspected FTS index stores stop names and agency/mode fields but no separate alias/translation table. | Add canonical stop identity and source-preserving localized names, aliases, transliterations and normalization metadata. | Search fixtures cover Arabic/French names, Latin transliteration, diacritics, spelling variants and duplicate stop names. |
| AUD-019 | Download/import pipeline needs bounded network and archive handling. | The inspected downloader uses a network request without a clearly bounded timeout in the reviewed path. | Set connect/read timeouts, retry only transient errors, cap download size, validate ZIP integrity/path entries, use temporary files and clean up failed partial downloads. | Tests cover timeout, retry exhaustion, oversized archive, corrupt ZIP and unsafe archive paths. |
| AUD-020 | Automated validation is insufficiently established. | No Python test suite/CI workflow was identified in the inspected repository; mobile package exposes typecheck but no test/lint scripts. | Add pytest coverage for import/query/search and mobile tests for domain/UI states; add CI for Python tests, TypeScript typecheck and applicable lint/build checks. Pin dependencies with the repository's chosen package manager; do not silently switch package managers. | CI runs on pull requests and fails on test/type errors. Validation commands and results are documented. |

## 3. Implementation sequence and dependencies

Do not attempt all findings in one coding task. Execute one bounded task at a time.

| Order | Task | Priority | Depends on | Deliverable |
|---:|---|---|---|---|
| 1 | TUM-ENG-001 — Demo trust boundary and passenger-report safety | P0 | None | Explicit demo/unavailable behavior; no false journey/report/emergency success claims. |
| 2 | TUM-ENG-002 — Safe GTFS import and data validation | P0 | None | Reversible import, feed validation report, last-known-good preservation. |
| 3 | TUM-ENG-003 — GTFS calendar, stop identity and fare correctness | P0 | ENG-002 | Date-correct direct-trip query, ambiguity handling, correct per-result fare/unknown. |
| 4 | TUM-ENG-004 — Journey-domain engine and deterministic ranking | P1 | ENG-003 | Tested direct journey domain API and Economic/Fastest/Balanced ranking; transfer routing remains a separately gated increment. |
| 5 | TUM-ENG-005 — API vertical slice | P1 | ENG-002, ENG-003; architecture decision details | FastAPI endpoints, versioned schemas, tests and source metadata. |
| 6 | TUM-ENG-006 — Connect mobile Journey and Explore | P1 | ENG-005 | Remove hardcoded data from normal flows; typed API client and truthful UI states. |
| 7 | TUM-ENG-007 — Reports lifecycle and account preferences | P1 | ENG-005; privacy/security review for sensitive workflows | Persistent report lifecycle, moderation boundary and durable preferences. |
| 8 | TUM-ENG-008 — Geospatial walking and multilingual stop search | P1 | Source/coverage validation; ENG-002 | Alias-aware search, routed walking distance, explicit approximate fallback. |
| 9 | TUM-ENG-009 — Automated tests and CI hardening | P1 | Start with ENG-001/002; expand per task | Reproducible tests, typecheck, dependency lock and CI gates. |

**Architecture note:** The active SDD confirms Python + FastAPI and PostgreSQL + PostGIS as the chosen direction, while the approved project structure places the API under `services/api/`. Do not silently introduce `apps/api/`, SQLite as the production database, a new package manager, paid services or a hosting provider. SQLite remains appropriate for local import tools and approved offline packages. Record consequential implementation details in ADRs where the existing SDD leaves them open.

## 4. Non-negotiable safeguards

1. **No fabricated transport facts.** Demo fixtures must be visibly synthetic and excluded from production queries.
2. **No false emergency assurance.** A UI-only safety report is not an emergency channel. Preserve guest access as a product direction, but do not imply monitoring or dispatch.
3. **No silent stale-data use.** Every feed has a source, version, retrieval time and service-validity state.
4. **No destructive replacement.** A failed import/index build must preserve the last known-good dataset/index.
5. **No unlicensed publication.** TUM-P0-004 remains a separate blocker. Technical availability does not grant redistribution rights.
6. **No unreviewed location collection.** Keep GPS optional and permissioned; persistent collection remains subject to TUM-P0-008 and qualified Tunisian legal review.
7. **No paid infrastructure.** Respect the zero-spend policy; no billing, card entry or paid API without explicit owner approval.
8. **No claims of validation without evidence.** Distinguish static source inspection, local tests, CI, device testing and real-data verification.

## 5. Definition of done for each remediation task

- Scope and acceptance criteria are met.
- Tests cover the identified failure modes and relevant edge cases.
- No unrelated changes or product decisions are introduced.
- Arabic/French localization, RTL, accessibility and low-end Android performance are considered.
- Provenance, freshness, license status, privacy and zero-spend constraints remain intact.
- Roadmap and append-only handoff log are updated.
- The next single actionable TODO is named.
- If blocked, the task is marked BLOCKED/REVIEW rather than being called DONE.

## 6. Audit limitations

This is a static review of selected GitHub source files and project documents. It did not include local database inspection, runtime behavior, device testing, dependency installation, typechecking, Python test execution, build execution, security scanning or a legal review. Some earlier audit findings should be revalidated against the current branch before code changes, especially exact importer behavior and line references. No code changes are included in this remediation document.
