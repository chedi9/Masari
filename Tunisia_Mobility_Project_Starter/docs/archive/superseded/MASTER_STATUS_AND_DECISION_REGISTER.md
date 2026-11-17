# Tunisia Mobility Platform — Master Status & Decision Register

**Version:** 0.4 working register  
**Date:** 3 November 2026  
**Status:** **DISCOVERY IN PROGRESS**  
**Authority:** Product-owner selections and instructions supplied in the 3 November 2026 conversation take precedence over earlier repository snapshots.  
**Repository baseline inspected:** `main` at `b40d641fc9285a992974fb57258a8bd06ad1403b`.

## Status definitions

- **Confirmed** — explicitly selected or stated by the product owner.
- **TBD** — unanswered, incomplete, or awaiting evidence/review; do not infer an answer.
- **Confirmed direction; validation pending** — the direction is approved, while implementation thresholds, provider choice or legal/data verification remain open.
- **Proposed** — recommendation or design suggestion not approved.

## Project status

The project remains in product discovery and feasibility. This ZIP consolidates current decisions and the inspected repository baseline; it does not close discovery or authorize full application implementation. The repository's Phase 0 gate remains applicable unless the owner explicitly changes it.

## Decisions confirmed in the latest answer batch

| Decision | Owner selection | Current status / boundaries |
|---|---|---|
| D-01 — Launch rollout order | **B — Greater Tunis → Sousse → Monastir → Sfax** | Confirmed sequential order; apply readiness gates at each stage. |
| D-15 — Offline download packages | **C — choose city, region and transport modes independently** | Confirmed product direction; package design and licensing still need validation. |
| D-15 — Offline information freshness | **D — source-specific expiration rules and advance warnings** | Confirmed direction; age thresholds by source/type remain to be defined. |
| D-69 — Pro billing periods | **B — monthly and yearly** | Confirmed direction; price, payment provider, terms and applicable legal review remain TBD. |
| D-69 — Additional Pro benefits | **D — offline first; expand benefits after research** | Confirmed; no additional benefit (including ad-free use) is approved. |
| D-16 — Bus branches/diversions | **D — hybrid route model** | Confirmed direction covering variants, trip patterns and temporary diversions; validate with real datasets. |
| D-26 — Vehicle matching | **D — hybrid multi-signal matching with confidence scoring** | Confirmed direction; precision/false-positive thresholds require field validation before positions are published. |
| D-43 — Advertising personalization | **C — contextual by default; personalization only with explicit opt-in** | Confirmed; do not profile users by default. Legal/privacy implementation review remains. |
| D-46 — Backend framework | **A — Python + FastAPI** | Confirmed direction; detailed architecture and operational validation remain. |
| D-47 — Database | **A — PostgreSQL + PostGIS** | Confirmed direction; migration, hosting and spatial workload details remain. |
| D-48 — Mapping infrastructure | **C — open geographic data + managed tiles/routing where economical** | Confirmed direction; provider, coverage, licensing and cost checks remain. |
| D-49 — Hosting | **A — free tiers for development/early beta; migrate when needed** | Confirmed; low-cost production is intended. Provider, migration triggers and budget ceiling remain TBD. No paid spend is authorized by this choice. |
| D-50 — Offline implementation | **D — SQLite + versioned regional packages + cached map tiles** | Confirmed architecture direction; entitlements, sync, storage, freshness and licensing need design/prototype. |
| D-54 — Community moderation | **C — automate low-risk cases; evidence-based verification and human review for major changes** | Confirmed direction; abuse controls, case lifecycle, appeals and thresholds remain to be specified. |
| D-56 — Operator dashboard | **D — read-only first, managed capabilities after partnerships** | Confirmed phased direction; partner access and exact capabilities remain future work. |
| D-57 — Location-data retention | **D — privacy impact assessment and qualified Tunisian legal review before collection** | Confirmed process; retention periods remain TBD. Do not infer them. |
| D-60 — Security controls | **D — baseline, threat modeling/code review and independent penetration testing, staged by risk** | Confirmed direction; controls and release gates need specialist validation. |

## Other decisions explicitly confirmed in the supplied conversation

| Decision | Confirmed choice | Status / boundary |
|---|---|---|
| D-45 — Mobile framework and visual quality | **A — React Native + Expo + TypeScript**, with a premium, highly customized visual standard | Confirmed by the owner. Performance, map SDK and platform behavior still need prototyping on target devices. |
| D-01b — Geographic coverage boundaries | **D — verified transport-service areas** | Confirmed. Coverage follows validated routes, stops, stations and service areas; do not imply blanket governorate coverage. Maintain readiness by launch area. |
| Launch areas | **Greater Tunis, Sousse, Monastir and Sfax** | Confirmed in the prior project conversation; rollout order is D-01 above. |

## D-06 — Passenger report classification: TBD

No option was selected. Keep this unresolved.

The existing confirmed boundary is that basic reports can be submitted by guests while advanced contributions require an account. The classification of report types/features remains unanswered. Option C (feature-based access) appeared as a recommendation only; it is **not approved**. Critical safety access was proposed in that option, not separately confirmed as the final classification policy.

**Identifier collision:** the repository's v0.3 register uses `D-06` for passenger-adjustable journey preferences (budget, time and walking distance), already recorded there as confirmed. The supplied current conversation uses `D-06` for passenger-report classification. Preserve both labels with their context until the owner assigns a canonical ID. Do not overwrite the journey-preference decision.

## Other confirmed baseline decisions retained

The repository's inspected v0.3 SDD and register remain included unchanged under `reference/`; their confirmed product requirements remain part of the project baseline unless specifically superseded above. Key examples include:

- Tunisia-focused multimodal mobility platform; Android-first with future iOS path.
- Arabic and French at launch; English may follow later.
- Buses and metro are initial priorities; activate every mode/area only when data and quality are validated.
- Guest-first core journey planning; basic reports are guest-accessible and advanced contributions require an account (classification still TBD).
- Hybrid official/community/consented GPS/operator data; preserve provenance and uncertainty.
- Journey options include Economic, Fastest and Balanced/Recommended; passenger preferences are budget, time and walking distance.
- Fare/source/date/confidence transparency; do not fabricate routes, live positions, schedules, fares, taxi availability or partner integrations.
- Optional trip detection and GPS contribution require explicit consent; no all-day tracking; retention periods await review.
- Ads are deferred until coverage/trust readiness; sponsored content must never affect journey ranking.
- Taxi discovery and estimates are progressive; booking waits for verified partners and legal/operational validation.
- Project cost policy is zero-spend for tools/services unless the owner changes it explicitly.

See the full v0.3 reference files for all previously recorded requirements and confirmed decisions. Where their unresolved-state tables conflict with the newer confirmations above, this current register governs.

## Remaining known TBDs and validation work

- **D-06 report classification** (unanswered; do not treat the recommendation as approved).
- Exact Pro price, payment provider, subscription terms and entitlement details.
- Pro offline feature matrix, data age thresholds, synchronization behavior, storage limits and map/data licensing.
- Candidate-city readiness thresholds and detailed coverage boundaries within the confirmed service areas.
- Real permitted transport datasets, data freshness, licensing and routing feasibility.
- Map/tile/geocoding/routing providers, Arabic search quality and operating costs.
- Vehicle matching accuracy and false-positive release thresholds.
- Bus branch/diversion schema validated against real data.
- Hosting provider, production budget ceiling and migration conditions.
- Privacy assessment and qualified local legal review before persistent location collection; retention periods remain TBD.
- Moderation workflow, evidence thresholds, appeals and abuse controls.
- Security threat model, code review practices, penetration-test scope and release gates.
- Home-screen composition, detailed accessibility feature scope, visual tokens/brand identity and other UX choices listed as open in the source register.
- Rural transport operating model, taxi availability display, exact operator portal scope and other open items from the source register.

## Proposed visual direction — not an approved brand system

The owner approved the **premium custom visual standard** for D-45. The supplied colors `#142D3B`, `#16A085`, `#F5F3ED`, `#E9B85B`, editorial typography, map styling and motion are illustrative proposals only. They are **not** an approved palette, logo, final UI or design system. Arabic/French typography, lower-end Android readability and performance remain requirements for design work.

## Recordkeeping note

This current register is a reconciliation layer, not a rewrite of the repository's v0.3 baseline. The v0.3 files are preserved unchanged as historical reference. No new product choice has been inferred from recommendations.
