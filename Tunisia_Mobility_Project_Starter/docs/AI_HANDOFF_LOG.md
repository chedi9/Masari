
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
