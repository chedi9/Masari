# Tunisia Mobility Platform — Decision Register

**Version:** 0.3  
**Date:** 3 November 2026  
**Source of truth:** `SDD_v0.3_Tunisia_Mobility_Platform.md`

This register consolidates the product-owner decisions from the 71-question discovery questionnaire. Confirmed directions, delegated recommendations and unresolved decisions are kept separate. A delegated decision is not an implementation approval.

## Status rules

- **Confirmed:** explicitly selected or stated by the product owner.
- **Delegated:** architect/specialist must recommend an approach; approval is still required.
- **TBD:** unanswered, not evidenced or dependent on further review.

# 21. Open decisions and assumptions register

The register below reflects the product owner's questionnaire submission. A selected direction is not the same as a finalized technical specification. Delegated choices require a recommendation and decision record. TBD items must remain unresolved until explicitly decided or validated.

| ID | Decision / assumption | Current state | Recommended next action |
|---|---|---|---|
| D-01 | Initial launch city list | TBD; UX-01 was marked Other but no city details were supplied | Evaluate several candidate cities using measurable data coverage, demand, operator cooperation and field results; ask product owner to name/exclude candidates when ready |
| D-02 | Home-screen composition | TBD | Develop UX alternatives and ask the product owner to select one |
| D-03 | Passenger navigation | Context-aware navigation selected | Specify task states, navigation hierarchy, back behavior and accessibility |
| D-04 | Origin selection | Auto-detect current location with manual override selected | Define denied permission, low accuracy, unavailable GPS and manual map/search flows |
| D-05 | Journey result presentation | Adaptive layout selected | Define responsive breakpoints and complexity rules |
| D-06 | Passenger-adjustable journey preferences | Budget, time and walking distance selected | Define units, defaults, validation and interaction; do not add other user filters without approval |
| D-07 | Waiting experience and disruption recovery | Combined prediction/confidence, alternatives, alerts and recalculation selected | Specify triggering thresholds and suppress unsupported delay claims |
| D-08 | Journey instruction detail | User-selectable simple/detailed views selected | Specify what each level contains |
| D-09 | During-journey experience | Progress, next-stop alerts and disruption recovery selected | Define optional location use, alert behavior and battery constraints |
| D-10 | Saved travel profiles | Multiple routines/personal profiles selected | Define profile fields, limits and guest/account behavior |
| D-11 | Explore map layers | All available layers with customizable filters selected | Define layer list, filter controls, defaults and map performance |
| D-12 | Stop page scope | Core first view is name, location and served lines | Decide whether schedules, reports, alerts and alternatives are separate sections and when they are shown |
| D-13 | Search localization | Arabic/French names, transliteration, aliases, suggestions and typo tolerance selected | Build a verified Tunisian place-name/alias data strategy |
| D-14 | Accessibility product scope | UX-15 remains TBD | Ask a dedicated accessibility question set; preserve baseline accessibility obligations independently |
| D-15 | Pro offline experience | Full offline capability intended under Pro; details TBD | Define exact offline feature matrix, data packages, sync, storage, freshness, licensing, plan/billing terms and free-tier behavior |
| D-16 | Bus route branches and diversions | Architecture delegated | Build data-model prototype using real bus datasets and recommend route/variant representation |
| D-17 | Metro/light-rail operating data | Include schedules, headways, interruptions and live updates where data permits | Audit data sources; do not claim a live layer absent a live feed |
| D-18 | Train information | Progressive schedules, train categories, connections and disruption data according to verified SNCFT sources | Validate current SNCFT data availability and permissions |
| D-19 | Taxi collectif representation | Routes, pickup areas, fares and passenger-reported availability selected | Validate service patterns and distinguish reported availability from verified supply |
| D-20 | Louage representation | Stations, destinations, fares and approximate departure patterns selected | Validate stations, destinations, fares and how departure observations may be collected |
| D-21 | Rural transport | OPS-06 remains TBD | Research service types and representative areas before selecting a data model |
| D-22 | Mode activation criteria | Different requirements per mode selected | Define auditable coverage/data-quality gates per mode and city |
| D-23 | Fare provenance | Show source, date and confidence selected | Define display states for unknown, estimated, stale and conflicting fares |
| D-24 | Source conflict reconciliation | Confidence-based reconciliation selected | Specify source authority, confidence calculation, freshness and non-destructive provenance rules |
| D-25 | Optional automatic trip detection | Selected with explicit consent | Prototype Android feasibility and perform privacy/legal review before background behavior is approved |
| D-26 | Vehicle matching algorithm | Architect to recommend after prototype | Compare matching approaches on labeled field data; set precision/false-positive thresholds |
| D-27 | Live vehicle labels | Every position must show confidence and source | Define public confidence vocabulary and suppression thresholds |
| D-28 | Arrival prediction display | Range, confidence and source selected | Validate prediction error by mode/region before publishing estimates |
| D-29 | Stale/conflicting observations | Expiry, confidence decay and moderation selected | Configure per-source/per-mode policies and human escalation criteria |
| D-30 | Guest/basic versus advanced contribution boundary | Basic reports guest; advanced contributions require account | Classify report types and define guest abuse controls |
| D-31 | Contribution activation | All contribution types progressively enabled | Define per-type rollout gates, dependencies and moderation coverage |
| D-32 | Contribution verification | Combine reports, GPS and official data | Define independent evidence rules and confidence thresholds; retain each source separately |
| D-33 | Reward model | Mixed gamification and partner benefits selected | Define ledger, points/levels and partner approval process; reward values TBD |
| D-34 | Leaderboards | Separate reporting, GPS and verified-contribution categories selected | Define privacy, opt-in visibility, anti-abuse and ranking rules |
| D-35 | Referral qualifying event | First completed journey search selected | Define valid-search conditions, attribution window, reward value/cap and anti-fraud controls |
| D-36 | Taxi discovery | Full discovery experience, capabilities added progressively | Scope discovery components while keeping unverified availability claims prohibited |
| D-37 | Taxi availability display | BIZ-03 remains TBD | Decide whether and how to show community or partner availability, with timestamps and confidence |
| D-38 | Taxi fare estimator | Combine available inputs according to reliability | Validate tariff rules, distance/time inputs, traffic and historical data; estimates must disclose basis and range |
| D-39 | Taxi booking | Progressive booking after partner/legal/operational validation | Keep future; define partner, driver, cancellation, support and payment requirements before launch |
| D-40 | Advertising readiness | Sufficient coverage and passenger trust required | Define measurable readiness thresholds; no MVP ad integration |
| D-41 | Advertising formats | Useful non-intrusive combination selected | Define accepted formats and exclusions |
| D-42 | Advertising placements | Multiple placements with strict frequency caps selected | Choose exact surfaces, caps and suppression rules; all numeric values TBD |
| D-43 | Advertising personalization | Architect recommendation for privacy-first model | Compare contextual-only and explicit opt-in models; no profiling assumed |
| D-44 | Sponsored content | Must be clearly labeled and never influence ranking | Enforce technical ranking firewall and presentation tests |
| D-45 | Mobile framework | TECH-01 remains TBD | Compare React Native/Expo, Flutter and native Android against the product constraints; prepare ADR |
| D-46 | Backend framework | TECH-02 remains TBD | Compare Python/FastAPI, TypeScript/NestJS and alternatives after routing/data spike |
| D-47 | Database | TECH-03 remains TBD; PostgreSQL/PostGIS is only a recommendation | Validate spatial queries, data integrity, operational cost and hosting options before selection |
| D-48 | Mapping infrastructure | Free/open-source first selected | Evaluate data/tile/geocoding licenses, Tunisia coverage, Arabic search, routing quality and offline terms |
| D-49 | Hosting | Free development, low-cost production selected | Set production budget ceiling and choose provider after architecture/region review |
| D-50 | Offline implementation architecture | TECH-06 remains TBD | Design local storage, regional downloads, sync, entitlements, licensing and stale-data behavior for Pro |
| D-51 | External data integration | Hybrid adapters, validation and automated monitoring selected | Standardize adapter contracts, import reports, versioning and alerts |
| D-52 | Admin roles | Administrator and moderator selected | Define permissions, separation of duties and audit actions |
| D-53 | Dataset approvals | Safe updates auto-approved; major changes manually reviewed | Define and test safe-update classes, approval thresholds, rollback and publication records |
| D-54 | Community moderation | ADM-03 remains TBD | Define case lifecycle, escalation, appeals, trusted contributors and automation boundaries |
| D-55 | Passenger support | Ticketing with categories, statuses and escalation selected | Define categories, SLAs, ownership, notifications and escalation policy |
| D-56 | Operator dashboard | ADM-05 remains TBD | Decide whether to provide none, read-only portal or managed partner portal after operator research |
| D-57 | Location data retention | SEC-02 remains TBD | Complete privacy impact review and qualified local legal review before production collection |
| D-58 | Registration fields | Minimum information; optional profile details selected | Define account recovery and whether email/phone is needed for each feature |
| D-59 | Consent UX | One onboarding consent screen selected | Design a clear onboarding summary plus separate feature/OS permissions where required; do not use blanket consent |
| D-60 | Security controls | Security specialist/architect to recommend after review | Conduct threat model and security review; document required controls before public beta |
| D-61 | Legal/compliance process | Documented checklist with qualified local review selected | Create checklist covering privacy, transport data, consumer obligations, advertising and partner booking |
| D-62 | Beta audience | Daily commuters and university students selected | Recruit representative pilot participants and define consent/testing protocol |
| D-63 | Initial mode priority | Buses and metro selected | Prioritize validated bus/metro routes; add others according to verified coverage |
| D-64 | City support gate | Measurable data-quality and passenger-testing thresholds selected | Set numeric release gates after baseline measurement |
| D-65 | Success metrics | Balanced usage/trust/coverage/community dashboard selected | Define metric formulas, privacy-safe aggregation and target baselines |
| D-66 | Field testing | Structured journey/disruption/GPS/offline testing selected | Produce field protocols and labeled ground-truth datasets |
| D-67 | City expansion | Phased by demand, operator cooperation and readiness selected | Define stage gates and city onboarding checklist |
| D-68 | Initial city names | Not provided in the custom UX-01 answer | Obtain city candidates from the product owner; do not infer them from the estimated location |
| D-69 | Pro commercial model | Pro plan direction stated; paid mechanics not specified | Confirm price, billing frequency, trial/refund terms and whether Pro contains any benefit beyond offline use |


---

## 32.1 Unresolved items that must remain TBD

1. UX-01: actual initial city names; no details were provided with “Other”.
2. UX-02: home-screen composition.
3. UX-15: specific accessibility features.
4. UX-16: complete Pro offline feature matrix, technical implementation and plan terms.
5. OPS-06: rural transport operating model.
6. BIZ-03: taxi availability display policy.
7. TECH-01: mobile framework.
8. TECH-02: backend framework.
9. TECH-03: database selection.
10. TECH-06: offline storage/caching/synchronization architecture.
11. ADM-03: community moderation model.
12. ADM-05: operator dashboard.
13. SEC-02: location/contribution retention periods.

Delegated decisions—such as bus-branch modeling, vehicle matching, advertising personalization and security controls—also require recommendations and documented approval; delegation is not final selection.


---

# Appendix C — Current decision log summary

| ID | Decision | State |
|---|---|---|
| DEC-001 | Several-city launch strategy | Confirmed; city list TBD |
| DEC-002 | Android-first passenger app | Confirmed; framework TBD |
| DEC-003 | Daily commuter and occasional traveller audiences | Confirmed |
| DEC-004 | All transport modes represented; progressive activation | Confirmed; buses and metro have initial priority |
| DEC-005 | Hybrid official/community/opt-in GPS/operator data approach | Confirmed |
| DEC-006 | Guest-first passenger access | Confirmed; basic reports guest, advanced contributions account-based |
| DEC-007 | Arabic and French at launch; English later | Confirmed |
| DEC-008 | Editorial + technical + approachable design direction | Confirmed; visual tokens TBD |
| DEC-009 | Architect recommends technology balance | Confirmed process; implementation choices remain open |
| DEC-010 | Free core passenger access and later advertising | Confirmed; ads deferred until coverage and trust readiness |
| DEC-011 | Individual taxi discovery first, booking progressively | Confirmed; taxi availability display TBD |
| DEC-012 | Mixed gamified and partner reward model | Confirmed; values/partners TBD |
| DEC-013 | Context-aware navigation, automatic origin detection and adaptive results | Confirmed |
| DEC-014 | Journey preferences limited to budget, time and walking distance | Confirmed |
| DEC-015 | Waiting, disruption recovery and in-journey assistance bundle | Confirmed; evidence/alert thresholds TBD |
| DEC-016 | Simple/detailed instructions and multiple saved travel routines | Confirmed |
| DEC-017 | All available Explore map layers with customizable filters | Confirmed; layer inventory TBD |
| DEC-018 | Stop detail first view: name, location and served lines | Confirmed |
| DEC-019 | Tunisian Arabic/French/transliteration/alias search | Confirmed |
| DEC-020 | Comprehensive offline capability under a Pro plan | Confirmed direction; details and commercial mechanics TBD |
| DEC-021 | Transport operations and activation are mode-specific | Confirmed; rural model and individual thresholds TBD |
| DEC-022 | Confidence-based reconciliation and confidence/source labels | Confirmed; formulas/thresholds TBD |
| DEC-023 | Optional automatic trip detection with explicit consent and privacy dashboard | Confirmed direction; implementation/legal review required |
| DEC-024 | Basic reports available to guests; advanced contribution requires account | Confirmed; classification TBD |
| DEC-025 | Separate community leaderboard categories | Confirmed; privacy/ranking rules TBD |
| DEC-026 | Referral reward after first completed journey search | Confirmed; validation and anti-fraud definitions TBD |
| DEC-027 | Advertising formats/placements direction and ranking firewall | Confirmed; exact formats/surfaces/caps TBD |
| DEC-028 | Free/open-source maps first; low-cost production hosting | Confirmed preferences; providers TBD |
| DEC-029 | Administrator/moderator roles; safe auto-approval and major-change review | Confirmed; permissions/thresholds TBD |
| DEC-030 | Passenger support ticketing | Confirmed |
| DEC-031 | Privacy-by-design, minimum account data and onboarding consent screen | Confirmed direction; separate feature/OS permissions still required where applicable |
| DEC-032 | Daily commuters/university students as beta audience; bus/metro priority | Confirmed |
| DEC-033 | Measurable city readiness, structured field testing and phased expansion | Confirmed; thresholds TBD |
