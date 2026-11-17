# Tunisia Mobility Platform — Modular Project Structure

**Status:** OWNER-APPROVED WORKING STRUCTURE
**Date:** 3 November 2026
**Architecture:** Monorepo, modular monolith for the API, feature modules for mobile, and separately testable data/routing packages.
**Implementation gate:** Per the owner's 3 November 2026 instruction, data-independent mobile UI and interaction work may proceed before Phase 0 exit using clearly labeled placeholders. Real transport data, service claims, integrations and deployment remain gated by evidence and owner review.

## Structure

```text
.
├── apps/
│   └── mobile/                         # React Native + Expo + TypeScript app
│       ├── app/                         # Expo Router route files and layouts
│       ├── src/
│       │   ├── features/
│       │   │   ├── journeys/             # Search, results, saved routines
│       │   │   ├── explore/              # Map and validated transport layers
│       │   │   ├── stops/                # Stop/station details
│       │   │   ├── reports/              # D-06 Option C passenger reports
│       │   │   ├── offline/               # Download, freshness, sync UI
│       │   │   ├── account/               # Account and consent settings
│       │   │   └── support/               # Passenger support flows
│       │   ├── shared/                   # Reusable UI, localization, formatters
│       │   └── platform/                 # Android/iOS adapters and permissions
│       └── tests/                        # Mobile unit and UI tests
├── services/
│   └── api/                              # Python + FastAPI modular monolith
│       ├── app/
│       │   ├── modules/
│       │   │   ├── network/              # Cities, operators, routes, stops
│       │   │   ├── schedules/            # Calendars, trips, service changes
│       │   │   ├── journeys/             # Journey search and ranking
│       │   │   ├── reports/              # Passenger report lifecycle/moderation
│       │   │   ├── accounts/             # Identity, consent, preferences
│       │   │   ├── offline/              # Versioned package manifests
│       │   │   └── support/              # Support cases
│       │   ├── adapters/                 # External provider/operator interfaces
│       │   ├── platform/                 # Settings, auth, database, logging
│       │   └── main.py                   # API composition and route mounting
│       └── tests/                        # Module, API and integration tests
├── packages/
│   ├── api-client/                       # Generated TypeScript client from OpenAPI
│   └── contracts/                        # Versioned public API/data contracts
├── tools/
│   └── data_pipeline/                    # Reproducible import/validation tooling
│       ├── sources/                       # Source-specific parsers
│       ├── validation/                    # Schema and quality checks
│       └── manifests/                     # Source IDs, versions and provenance
├── data/
│   ├── raw/                               # Local-only source files; gitignored
│   └── processed/                         # Rebuildable, versioned outputs
├── infra/                                 # Local development and deployment config
├── docs/
│   ├── adr/
│   ├── architecture/
│   ├── research/
│   └── ...
└── tests/
    └── end_to_end/                        # Cross-module journey and data checks
```

## Boundary rules

- Keep the backend a **single deployable modular monolith** initially. Modules communicate through explicit Python interfaces and domain events; no module imports another module's persistence internals.
- Keep operator, map, geocoding and routing integrations behind adapters. A provider can be replaced without rewriting journey or product modules.
- Keep the transport domain and routing logic testable without FastAPI, network calls or a live database.
- Keep imports reproducible and reversible. Preserve source identifiers, licenses, retrieval timestamps, dataset versions and validation results.
- Keep mobile features grouped by user capability. Shared UI/i18n/platform code must not become a second home for product rules.
- Generate the TypeScript API client from the backend OpenAPI contract; do not manually duplicate request/response types.
- Store no downloaded raw datasets in Git. Keep only manifests, schemas, small synthetic fixtures and permitted derived artifacts under source control.
- Keep storage, Pro entitlements and payment concerns separate from transport records; do not implement paid access until its terms are approved.
- Arabic RTL, French, provenance/freshness, user consent and low-end Android performance are cross-module requirements.

## Still TBD

Package manager/workspace tool, exact module decomposition, API versioning policy, job/queue needs, deployment topology, provider adapters, data retention, dataset storage locations and numerical quality thresholds remain TBD until the relevant Phase 0 evidence and owner review. This structure does not select a vendor or authorize cost.

## Intended build order

1. Build data-independent mobile screens, navigation, localization and shared accessible UI with explicit placeholder states.
2. Continue the Phase 0 data and routing feasibility work in parallel.
3. Add import/validation tooling before relying on production transport records.
4. After owner gate review, implement the first evidence-backed vertical slice: permitted import → validated network → journey query → provenance-aware mobile result.
5. Add backend, provider integrations and other modules when their requirements and evidence are ready.
