# TUM-P0-002 — Candidate-area readiness evidence review

**Reviewed:** 3 November 2026  
**Status:** PRELIMINARY DESK AUDIT — DISCOVERY IN PROGRESS  
**Decision:** This is not a city-readiness approval or permission to launch.  
**Scope:** Greater Tunis → Sousse → Monastir → Sfax; public transport data, public app disclosures, operator access leads, and evidence still needed.

## Summary

The transport ministry's open-data catalog exposes relevant scheduled or network datasets for all four rollout areas. That is enough to begin a source inventory, but not enough to declare any area operationally ready: the available catalog descriptions do not establish full route/stop coverage, current service accuracy, field validity, or an operator feed agreement. The app and service disclosures below are leads for corroboration or future integration conversations; they are not substitutes for licensed source data.

No data was imported into the product. No app accounts, APIs requiring credentials, paid services, or personal/location data were accessed. No operator was contacted.

## Area-by-area evidence

| Rollout area | Publicly documented evidence | Readiness finding | Evidence still needed |
|---|---|---|---|
| **Greater Tunis** | The catalog lists TRANSTU planned bus, metro and TGM schedules, plus route/stop resources. The bus-schedule listing specifically describes the Ben Arous depot, so it does not demonstrate complete Greater Tunis bus coverage. Several records show 25 January 2026 metadata updates and OTL licensing. | Candidate source data is available; coverage is visibly partial/uncertain from catalog metadata. | Download and inspect every relevant resource; map routes/stops to verified service areas; verify license text, service calendar and freshness; field-check a stratified sample. |
| **Sousse** | The STS catalog entry describes regional bus routes, stops and schedules in a GTFS ZIP under OTL. The Winicari site identifies STS Sousse as a client and describes real-time GPS/operator functions. SNCFT says the Métro du Sahel links Sousse and Mahdia through Monastir. | Useful static-data lead and possible operator-system lead; neither completeness nor access to live data is established. | Inspect GTFS contents and dates; validate Sousse-area coverage and service; determine whether an authorized Winicari/STS export or API is available, its terms and cost; verify Sahel rail schedules and stations. |
| **Monastir** | STS regional bus data is listed. SNCFT's public network description includes the Sahel line serving Monastir. | Network existence is supported by public descriptions; stop-level and timetable completeness remain unverified. | Inspect STS package, locate Monastir routes/stops and service dates, check SNCFT station/timetable resources, and validate the selected operational boundary with local evidence. |
| **Sfax** | SORETRAS publishes journey/departure-time resources in CSV and XLSX under OTL; the CSV resource is described as an active datastore containing all source-file records and shows a 25 January 2026 update. | A usable schedule candidate exists, but route geometry, stop locations, service calendars and field accuracy are not established by that metadata. | Download and profile CSV/XLSX; compare all route/stop references and operating dates; seek current route maps/field evidence; evaluate only data needed for pilot journeys. |

The SNCFT catalog also lists a national GTFS resource described as empty. Treat the empty resource as unavailable until a real, populated and permitted feed is verified; do not infer schedules from the catalog entry. SNCFT public pages can corroborate network existence, but are not a substitute for a machine-readable, validated schedule.

## Apps and services named by the owner

Use these as public discovery and cross-check leads. Do not scrape app users, reverse engineer private endpoints, copy proprietary schedules, or treat app output as approved source data.

| Service | Public evidence found | Safe project use now | Not established |
|---|---|---|---|
| **Thnity** | The transport ministry reuse register identifies Thnity and lists TRANSTU bus, metro, route and station datasets. Its own site describes combining open data, authority data and user contributions, starting in Tunis. | Identify TRANSTU datasets worth auditing; compare public coverage claims with official datasets. | Current feed endpoints, access rights beyond listed open datasets, update guarantees, and permission to reuse Thnity-specific user or derived data. |
| **Wassalni** | The ministry register lists Wassalni as a transport-data reuse. The reuse page was intermittently unavailable during this review. | Revisit the register and inspect its linked datasets in the next inventory task. | Feed/API availability, current data provenance, reuse terms for its derived or live information. |
| **RNTT** | The App Store listing describes national SNCFT and SNTRI information, Greater Tunis TRANSTU, and several regional operator networks; the public listing does not identify authoritative feed URLs or data licenses. | Use its claimed geographic/operator scope to create a checklist for independent validation against official data. | Current data rights, feeds, freshness, and actual service quality in the four selected rollout areas. |
| **Winicari** | Its operator site describes GPS-backed live passenger information, GTFS/Excel/custom imports, third-party connectors, and lists STS Sousse among its customers. | Record as a potential Sousse/STS integration lead, subject to the operator and vendor's written authorization and zero-cost constraint. | Public API/export, feed rights, price, service-level terms, and approval to integrate. Its website describes a deployed commercial system, not an open dataset. |
| **Tunismapper** | Its help page claims nationwide lines/stations and says data is GTFS and updated regularly, but does not disclose source feed links, license, or update cadence. | Treat nationwide and real-time statements as claims to cross-check; compare independently with catalog and field evidence. | The underlying GTFS, rights to reuse, provenance, refresh cadence, and real-time feed access. |

The ministry's current reuse register lists Thnity and Wassalni as external reusers. A reuse entry is evidence of a declared use, not a blanket license for all app-generated/live information. Prefer the original catalog resources and their per-dataset terms.

## Proposed readiness measurements — NOT APPROVED

These are proposed measurement definitions for the next evidence pass, not approved numeric thresholds. Establish baselines from actual source files and field checks, then ask the owner to approve pass thresholds.

- **Coverage:** validated candidate stops and route segments divided by the inventory of candidate stops and segments for the defined service area.
- **Source compliance:** proportion of pilot records with source, license/permission, retrieval date, and freshness rule documented; target value remains TBD.
- **Schedule validity:** sampled trips and service calendars that match current operator/public evidence and field observations.
- **Journey validity:** feasible itinerary legs confirmed by the source network and representative origin/destination checks; target value remains TBD.
- **Freshness:** age of each dataset relative to its own published update cadence; expiry/warning rules remain TBD.
- **Operator access:** written permission/API/export status, cost, scope, and refresh commitment for every non-open feed.
- **Field feasibility:** named local validation method, sample design, and evidence collection plan; no field visit or operator agreement is claimed here.

## Sources consulted

- [Tunisia Transport Open Data Portal](https://data.transport.tn/fr/) and [Thnity reuse record](https://data.transport.tn/fr/reuses/thnity/); [Wassalni reuse record](https://data.transport.tn/fr/reuses/wassalni/).
- [TRANSTU OTL catalog listing](https://catalogue-data.transport.tn/dataset/?_organization_limit=0&license_id=OTL&organization=transtu); catalog entries for [TRANSTU bus schedules](https://catalogue-data.transport.tn/dataset/horaires-des-bus-de-la-transtu), metro and TGM schedules.
- [STS regional bus schedule / GTFS listing](https://catalogue-data.transport.tn/dataset/horaires-des-bus-de-la-societe-de-transport-du-sahel).
- [SORETRAS schedules](https://catalogue-data.transport.tn/fr/dataset/les-horaires-des-voyages-de-soretras) and [CSV resource metadata](https://catalogue-data.transport.tn/fr/dataset/les-horaires-des-voyages-de-soretras/resource/88a00d8e-48ef-4d6c-b0ef-3e2e68750086).
- [SNCFT passenger network presentation](https://www.sncft.com.tn/voyageurs/presentation/) and [official schedules page](https://www.sncft.com.tn/voyageurs/horaires/).
- [Thnity](https://www.thnity.com/); [RNTT App Store listing](https://apps.apple.com/us/app/rntt/id1450177743); [Winicari operator platform](https://www.winicari.tn/); [Tunismapper help/FAQ](https://tunismapper.com/aide.php).
- [Transport catalog CKAN API documentation](https://data.transport.tn/fr/api-documentation/) documents anonymous read access for public catalog endpoints; per-dataset terms still apply.

## Next action

`TUM-P0-003` — download the public catalog candidate files locally and inventory their schemas, record counts, geographic coverage, service dates, license metadata and obvious quality issues. Keep original files and checksums, do not publish unvalidated passenger-facing transport facts, and stop if a resource requires credentials, has unclear reuse terms, or creates cost.
