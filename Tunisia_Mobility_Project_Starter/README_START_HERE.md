# Tunisia Mobility Platform

**Status: DISCOVERY IN PROGRESS.** The owner has authorized modular mobile UI coding with clearly labeled placeholders while transport-data research continues. Real transport facts, integrations, production routing and public rollout remain behind the Phase 0 evidence and review gate.

## Core files
- `SDD_Tunisia_Mobility_Platform.md` — single current SDD v0.8 and owner-approved direction.
- `Tunisia_Mobility_Decision_Register.md` — confirmed choices, adopted defaults and evidence/legal TBDs.
- `dashboard.html` — local dashboard; open directly or use `start_todo_board.bat`.
- `docs/MASTER_ROADMAP.md` and `docs/AI_HANDOFF_LOG.md` — project plan and handoffs.
- `docs/research/TUM-P0-002_CANDIDATE_AREA_READINESS.md` — preliminary evidence review for the four rollout areas and the five named transport apps/services.
- `docs/architecture/PROJECT_STRUCTURE.md` — approved modular working structure for the app, API and data packages.
- `docs/adr/ADR-0001-modular-monolith-and-repository-layout.md` — records the modular monolith decision and the limited pre-gate mobile UI authorization.
- `apps/mobile/` — modular Expo Router app under construction. To run it, open a terminal here, run `cd apps\mobile`, `npm install`, then `npx expo start`. All transport content remains explicitly unconnected until real datasets are validated.
- `prototypes/journey-preview/index.html` — standalone visual preview; all map artwork and content are illustrative, not real service data.
- `prototypes/native-journey-preview-sdk57/` — isolated Android-first Expo Go prototype; install its dependencies with `npm install`, then run `npx expo start` and scan the QR code in Expo Go. No live transport data is connected.
- `AGENTS.md` and `CLAUDE.md` — working rules.

Discovery remains in progress. D-06 is confirmed as feature-based Option C. Public catalog metadata for candidate datasets has been reviewed, but actual data-file inspection is blocked by download timeouts; no rollout area is certified ready. The original native visual prototype remains separate and untouched while `apps/mobile/` is built. Dashboard checklist marks reset on reload.
