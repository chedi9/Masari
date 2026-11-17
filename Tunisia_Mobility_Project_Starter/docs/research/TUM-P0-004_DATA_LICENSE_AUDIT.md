# TUM-P0-004 — Data licensing and reuse audit

**Date reviewed:** 17 November 2026  
**Status:** BLOCKED — catalogue license labels were found, but exact license text and rights for each underlying transport source were not verifiable from the material available in this audit.  
**Owner:** Data/legal researcher  
**Scope:** Existing candidate public transport datasets for the project rollout areas. This is a desk audit only; no data was republished, imported, or redistributed, and no operator was contacted.  
**Cost check:** Free public sources only; no accounts, paid APIs, or services used.

## Executive finding

The repository's earlier research records identify OTL (described in the catalogue as the Tunisian open-data license) for several Ministry catalogue records. That metadata is evidence of a catalog designation, **not sufficient by itself here to verify the exact legal grant, attribution wording, permitted modifications/redistribution, or that a separately hosted operator feed carries the same terms**. The official license-guide page was located, but its exact license clauses could not be retrieved and validated during this review. Do not treat “OTL” as a blanket permission for all source files.

**Current recommendation:** Do not publish, redistribute, or use these datasets in a public/pilot product until the actual dataset license terms are captured for the exact resource/version and any additional rights for direct operator feeds are confirmed. Internal, non-public analysis should still preserve source metadata and follow the repository's restrictions; this audit is not legal advice.

## Source-by-source status

| Source / candidate | Evidence in the repository | License / reuse finding | Decision for integration or redistribution |
|---|---|---|---|
| **SNCFT direct GTFS** — `https://gps.sncft.com.tn/gps/gtfs_ALL.ZIP` | P0-003 records a 24.39 MB archive retrieved 2026-11-13; feed data says Spring 2021 version D and service dates 2020-09-01–2021-06-30. It is hosted directly by SNCFT, not proven to be the same artifact/terms as a catalogue record. | No license file or exact grant is evidenced for the direct feed in the inspected project record. A third-party catalog or recent fetch timestamp does not establish a license or schedule freshness. | **Blocked.** Obtain exact terms/permission for this URL and version. Do not represent the historical timetable as current. |
| **TRANSTU GTFS / schedules** | P0-003 records a national catalog package and metadata verification; the existing inventory reports an OTL label for the catalog record. The direct host was previously reported unavailable. | OTL catalog metadata is reported, but the exact license clauses and resource/version linkage are not reproduced in the checked evidence. No direct-host rights established. | **Blocked.** Capture package/resource metadata and license text for the precise artifact before integration or redistribution. |
| **STS bus GTFS / Sahel schedules** | P0-002 and the public-data directory describe an official catalog entry; the prior readiness record reports the GTFS listing under OTL. | Catalog label is secondary evidence in this audit; exact terms/resource-level linkage and any operator conditions remain unverified. | **Blocked.** Verify the current record and exact terms for the downloaded resource. |
| **SORETRAS schedules / station positions** | P0-002 records schedule resources; the public-data directory lists CSV/XLSX resources. | The inspected material does not establish the exact license for each resource/version or whether conditions differ between schedule and station files. | **Blocked.** Check each resource's current metadata and terms separately. |
| **National Stop Registry** | The 13 Nov ingest report records the Ministry CKAN dataset and license value `OTL`; XLSX/CSV resource links are listed. The directory describes national mode coverage. | The OTL identifier is present in the saved metadata, but the operative license text and coverage of both resources are not independently validated here. | **Blocked.** Verify the license definition and each resource's terms/version before reuse. |
| **Taxi Collectif Routes** | The 13 Nov ingest report records the Ministry CKAN dataset and license value `OTL`; it lists governorate CSV resources. | Same limitation: the identifier is not a substitute for confirming the exact grant and resource-specific conditions. | **Blocked.** Verify exact terms and each selected governorate resource. |
| **Other louage / rural-transport sources** | The public data directory lists an ATTT dataset family and catalog filter, but not a specific audited artifact/license. | No source-specific license evidence in this task. | **Not cleared.** Audit only after a concrete resource is selected. |

## License interpretation and limits

- The official Ministry transport catalogue has a citizen guide page for licenses: [Licences — data.transport.tn](https://data.transport.tn/fr/guide-citoyen/je-d%C3%A9couvre-les-donn%C3%A9es/licences/). The page was located, but exact clause text could not be reliably extracted for this audit. Therefore this document does **not** assert specific permissions for commercial use, redistribution, modification, attribution format, share-alike, or warranty.
- The national portal's terms page is [Terms of use — data.gov.tn](https://www.data.gov.tn/en/terms). Exact current clauses were not available to verify in this review. Do not infer dataset rights from a portal's general open-data mission.
- A catalog license identifier applies only as far as the catalog's actual metadata and license definition say; it does not automatically cover a different direct URL, third-party mirror, later file version, or operator service.
- A public download, anonymous API access, OTL label in an older inventory, or third-party feed archive is not, alone, proof of permission to redistribute, modify, or commercially reuse.
- Dataset content can also contain third-party rights, personal data, or contractual conditions requiring separate review. No such content/legal review is claimed here.
- Preserve provenance for every source: provider, exact URL/resource ID, retrieval date, version/hash, catalog license identifier and license-text URL, attribution statement, geography/mode, validity dates, and approval status.

## Evidence reviewed

- Repository record [`TUM-P0-003_DATASET_INVENTORY.md`](TUM-P0-003_DATASET_INVENTORY.md): SNCFT source and service dates; catalog status for TRANSTU, STS and SORETRAS.
- Repository record [`TUNISIA_PUBLIC_TRANSPORT_DATA_DIRECTORY.md`](TUNISIA_PUBLIC_TRANSPORT_DATA_DIRECTORY.md): candidate source and catalog URLs.
- Repository file `scripts/ingest_report_2026_11_13.json`: saved Ministry CKAN metadata records `OTL` for the National Stop Registry and Taxi Collectif Routes; this is stored evidence, not a fresh legal verification.
- Official license-guide and national portal terms links above.
- Official catalog records: [TRANSTU GTFS](https://catalogue-data.transport.tn/dataset/horaires-des-voyages-de-la-transtu-gtfs), [STS GTFS](https://catalogue-data.transport.tn/dataset/horaires-des-bus-de-la-societe-de-transport-du-sahel), [SORETRAS schedules](https://catalogue-data.transport.tn/fr/dataset/les-horaires-des-voyages-de-soretras), [National Stop Registry](https://catalog.data.gov.tn/fr/dataset/628f26a4-3ee0-4e9d-b8a1-9bb2c2f5b2ff), and [Taxi collectif routes](https://catalog.data.gov.tn/fr/dataset/taxis-collectifs).

## Required follow-up to unblock

1. Retrieve the current official license text and record the version/date and exact applicable clauses for OTL (including attribution, modification, redistribution, commercial reuse, disclaimer, and any share-alike condition).
2. For each pilot file, save its live catalog package/resource metadata, exact download URL, license identifier, resource update date, checksum, and whether the license is explicitly attached to that resource.
3. For the direct SNCFT production feed, obtain a clear license/permission statement from SNCFT or a confirmed official catalog entry that explicitly covers the direct feed and the selected version. Do not infer rights from Transitland or the feed's accessibility.
4. Review the selected attribution requirements and preserve source notices in any derivative database/app.
5. Have the product owner/legal reviewer approve the resulting source-by-source clearance before public integration or redistribution.

No external party was contacted; contact/permission remains an owner-controlled action. This audit makes no product, pilot, or legal approval.
