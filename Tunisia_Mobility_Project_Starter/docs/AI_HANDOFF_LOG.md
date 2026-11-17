
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
