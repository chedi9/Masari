# TUM-P0-003 — Public transport dataset inventory & profiling

**Date:** 13 November 2026 (Updated from 3 November 2026 initial pass)  
**Status:** PARTIAL (SNCFT verified & profiled; TRANSTU direct host down, CKAN metadata reconciled)  
**Scope:** Candidate public files for Greater Tunis, Sahel (Sousse/Monastir), and national rail.  
**Cost check:** 100% free / open data sources. No paid APIs, no credentials exposed.  

---

## 1. Verified & Profiled Datasets

### 1.1 SNCFT National & Suburban Rail GTFS Archive (`data/raw/sncft_gtfs.zip`)
* **Source URL:** `https://gps.sncft.com.tn/gps/gtfs_ALL.ZIP` (referenced via Transitland Atlas `feeds/gps.sncft.com.tn.dmfr.json`)
* **Retrieval Timestamp:** `2026-11-13T21:08:55Z`
* **File Size:** `24,391,145 bytes` (24.39 MB)
* **SHA-256 Checksum:** `39630152e4cf979c89343e7ea5849b0c66d9ef7568400c4e52ab6d926462797c`
* **Storage Policy:** Stored locally in `data/raw/sncft_gtfs.zip` (gitignored per project architecture rules).
* **Publisher / Provenance:** Official SNCFT server (`Microsoft-IIS/8.0`). Publisher contact: `bousrih.hatem@sncft.com.tn`.
* **Feed Version / Dates:** `Spring 2021 version D`, service dates `2020-09-01` to `2021-06-30`.

#### Archive Members & Record Counts:
| File | Records / Lines | Description |
|---|---|---|
| `agency.txt` | 3 agencies | `1`: UABS-Banlieue Sahel, `2`: UABT-Banlieue Tunis, `3`: UAGL-Grande Ligne |
| `routes.txt` | 53 routes | Suburban rail + intercity rail corridors across Tunisia |
| `stops.txt` | 223 stops | Physical railway stations with exact GPS coordinates (latitude/longitude) |
| `trips.txt` | 248 trips | Scheduled train trips |
| `stop_times.txt` | 4,795 stop times | Scheduled arrival/departure timestamps per trip |
| `calendar.txt` | 8 service profiles | Day-of-week service masks (Mon-Sun, Mon-Fri, etc.) |
| `calendar_dates.txt` | Active | Service exceptions / holidays |
| `shapes.txt` | Present | Detailed track geometry polyline coordinates |
| `fare_attributes.txt` | 14 fare tiers | Prices in TND (0.35 TND to 2.50 TND / 350 to 2,500 millimes) |
| `fare_rules.txt` | 1,400+ rules | Origin-destination zone fare mappings |
| `feed_info.txt` | 1 record | Publisher metadata and validity period |

#### Operational Coverage Highlights:
* **UABT - Banlieue Tunis (19 stations):** Tunis Ville (36.7947, 10.1803), Depot Farhat Hached, Djebel Jelloud, Megrine Ryad, Megrine, Sidi Rezig, Lycée Technique Rades, Rades, Rades Mel, Ezzahra, Ezzahra Lycée, Bou Kornine, Hammam Lif, Arrêt du Stade, Tahar Sfar, Hammam Chatt, Bir El Bey, Borj Cédria, and Erriadh (36.6982, 10.4215).
* **UABS - Banlieue Sahel (Sahel Metro):** Sousse Bab Jdid, Monastir, Mahdia, Moknine, Sousse Sud, Bekalta.
* **UAGL - Grande Ligne:** National lines connecting Tunis, Sousse, Sfax, Gafsa, Metlaoui, Gabès, Tozeur.

#### Known Limitations:
* Timetable service dates end in June 2021. Physical station coordinates, track geometries (`shapes.txt`), stop sequences, and fare structures are authoritative and verified, but trip frequencies and exact departure minutes require validation against contemporary 2026 SNCFT schedules.

---

## 2. Catalog Status for Other Operators

| Area / Operator | Catalog / Resource Record | Status & Findings | Action / Next Step |
|---|---|---|---|
| **Greater Tunis — TRANSTU** | National Portal `catalog.data.gov.tn`, package `dfe6b078-3fea-4486-8cd0-4bf7b84946cb` | CKAN metadata verified: Title *"Horaires des voyages de la TRANSTU (GTFS)"*, license `OTL`, contains planned bus, metro, and TGM data. Underlying file URL `http://data.transport.tn/.../transtu_gtfs1.zip` is currently unreachable/timed out. | Ingest OpenStreetMap rail/metro stop layers as baseline; monitor transport portal recovery. |
| **Sousse / Monastir — STS** | Package `6cb0e17c-03bf-48cc-8c6e-581db05732c4` | STS bus network described in catalog. | Pending ministry catalog connectivity. Rail coverage in Sahel is already fulfilled by SNCFT UABS feed above. |
| **Sfax — SORETRAS** | Package `62332d69-180d-4209-86b1-c0c3aa0a8f99` | SORETRAS regional journeys cataloged. | Rail connection to Sfax is verified via SNCFT UAGL. Bus timetable extraction pending. |

---

## 3. Resume & Verification Summary
* **TUM-P0-003 status:** Upgraded from `BLOCKED` to `PARTIAL`.
* **Milestone:** The platform now possesses an authentic, complete, 11-table GTFS dataset for all Tunisian railway operations (Tunis Banlieue, Sahel Metro, and national rail) with 223 GPS-mapped stations and official fare rules.
