# Tunisia Public Transport — Data Sources & Access Directory

**Research date:** 13 November 2026  
**Coverage focus:** Greater Tunis, Sousse, Monastir, Sfax; national and regional connections  
**Purpose:** Reference directory of publicly listed transport datasets, timetables, geographic data, APIs, and download pages.  

> This document is an authoritative data catalogue and reference directory for the Tunisia Mobility Platform.

---

## 1. Main Official Data Portals

| Portal | Contents | Link |
|---|---|---|
| **Ministry of Transport sectoral open-data catalogue** | Transport operators, schedules, routes, stops, fares, geographic resources | https://catalogue-data.transport.tn/ |
| **Ministry catalogue dataset browser** | Search and filter datasets | https://catalogue-data.transport.tn/dataset/ |
| **National Open Data Portal** | Government transport datasets and downloads | https://catalog.data.gov.tn/ |
| **National terrestrial transport datasets** | 62 listed datasets in the catalogue view | https://catalog.data.gov.tn/fr/themes/transport?_organization_limit=0&_tags_limit=0&license_id=OTL&tags=transport+terrestre |
| **National GTFS dataset filter** | GTFS ZIP datasets | https://catalog.data.gov.tn/dataset/?_license_id_limit=0&license_id=OTL&tags=gtfs |
| **Ministry transport API documentation** | CKAN API access | https://data.transport.tn/fr/api-documentation/ |

The sectoral catalogue lists CSV, XLSX, ZIP, GeoJSON, XLS, and other resource formats. The national terrestrial transport view includes tags such as SNCFT, SRTJ, TRANSTU, SORETRAS, SRTB, SNTRI, SRT KEF, SRTGN, SRTM, STS, RFR, TGM, fares, routes, stations, and geographic positions.

---

## 2. CKAN API — Programmatic Dataset Access

The Ministry catalogue and National Portal expose CKAN-style JSON actions.

**Base URLs:**
- Sectoral catalogue: `https://catalogue-data.transport.tn/api/3/action/`
- National portal: `https://catalog.data.gov.tn/api/3/action/`

### Useful Actions
| Action | Purpose |
|---|---|
| `package_search` | Search datasets by keyword / operator |
| `package_show` | Get dataset metadata, schema, license, and resource list |
| `resource_show` | Get a resource's metadata and download URL |
| `resource_search` | Search specific resources |
| `datastore_search` | Query tabular resources where DataStore is enabled |
| `package_list` | List all dataset IDs |

### Query Examples
- Search TRANSTU: `https://catalogue-data.transport.tn/api/3/action/package_search?q=TRANSTU`
- Search SNCFT: `https://catalogue-data.transport.tn/api/3/action/package_search?q=SNCFT`
- Search RFR: `https://catalogue-data.transport.tn/api/3/action/package_search?q=RFR`
- Search SNTRI: `https://catalogue-data.transport.tn/api/3/action/package_search?q=SNTRI`
- Search SORETRAS: `https://catalogue-data.transport.tn/api/3/action/package_search?q=SORETRAS`

---

## 3. TRANSTU — Greater Tunis Buses, Metro/Light Rail, and TGM
* **Operator:** Société des Transports de Tunis (TRANSTU)
* **Main geography:** Greater Tunis

| Dataset | Format | Dataset Page |
|---|---|---|
| Complete TRANSTU GTFS | ZIP | https://catalogue-data.transport.tn/dataset/horaires-des-voyages-de-la-transtu-gtfs |
| Metro timetables | XLSX / CSV | https://catalogue-data.transport.tn/fr/dataset/horaires-des-lignes-metro-de-la-transtu |
| Bus timetables | XLSX / CSV | https://catalogue-data.transport.tn/dataset/horaires-des-bus-de-la-transtu |
| TGM timetables | XLSX / CSV | https://catalogue-data.transport.tn/dataset/horaires-de-la-ligne-tgm-de-la-transtu |
| Metro and bus station geography | XLSX / CSV | https://catalogue-data.transport.tn/fr/dataset/gares-et-stations-du-reseau-metro-et-bus-de-la-transtu |
| Bus route itineraries | XLSX / CSV | https://catalogue-data.transport.tn/dataset/les-itineraires-des-lignes-du-reseau-bus-de-la-transtu |
| TRANSTU organization datasets | Various | https://catalogue-data.transport.tn/fr/organization/transtu |

* **GTFS dataset UUID in Ministry catalogue:** `fe6c29b8-86c8-44cd-b36d-d41b70fab3f2`
* **National portal mirror:** `https://catalog.data.gov.tn/dataset/horaires-des-voyages-de-la-transtu-gtfs` (UUID: `dfe6b078-3fea-4486-8cd0-4bf7b84946cb`)

---

## 4. SNCFT — National Railway and Suburban Railways
* **Operator:** Société Nationale des Chemins de Fer Tunisiens (SNCFT)

### Official Timetable Pages
| Service | Link |
|---|---|
| National trains / Grandes lignes | https://www.sncft.com.tn/voyageurs/horaires/ |
| Tunis suburban railway (Banlieue Tunis) | https://www.sncft.com.tn/voyageurs/banlieue-tunis/ |
| Sahel suburban railway (Banlieue Sahel) | https://www.sncft.com.tn/voyageurs/banlieue-sahel/ |

### GTFS & Geographic Datasets
| Dataset | Format | Link |
|---|---|---|
| Direct Production GTFS Feed (Verified 2026-11-13) | ZIP (24.4 MB) | `https://gps.sncft.com.tn/gps/gtfs_ALL.ZIP` |
| SNCFT rail GTFS catalogue record | ZIP | https://catalog.data.gov.tn/fr/dataset/horaires-du-reseau-ferre-de-la-sncft-gtfs-gtfs |
| National railway station coordinates | CSV | https://catalog.data.gov.tn/dataset/position-geographique-des-stations-du-reseau-grandes-lignes-de-la-sncft |
| All SNCFT datasets | Various | https://catalog.data.gov.tn/fr/dataset/?groups=transport&organization=sncft0 |

* **Legacy SNCFT GTFS UUID:** `bef00987-6fae-4a99-b60d-c5d8e3747221` (Published March 2023).

---

## 5. RFR — Réseau Ferroviaire Rapide de Tunis
* **Geography:** Greater Tunis

| Dataset | Format | Link |
|---|---|---|
| RFR station mapping | CSV | https://catalogue-data.transport.tn/fr/dataset/cartographie-des-stations-du-reseau-ferroviaire-rapide-du-rfr |
| RFR direct CSV resource | CSV | https://catalogue-data.transport.tn/dataset/245e848e-2829-4548-b563-2e8c3bc52e97/resource/4c512d3f-bf5b-41ca-8e50-6d71a932b6fa/download/245e848e-2829-4548-b563-2e8c3bc52e97_43dbb48c-4576-4520-8d93-59c4b6585e01.csv |
| RFR organization datasets | Various | https://catalogue-data.transport.tn/organization/rfr |

---

## 6. SNTRI — Intercity Buses
* **Operator:** Société Nationale de Transport Interurbain (SNTRI)

| Dataset | Format | Link |
|---|---|---|
| SNTRI stations, operating lines, and schedules | CSV / XLSX | https://catalogue-data.transport.tn/fr/dataset/sations-lignes-d-exploitation-et-horaires-des-bus-de-la-sntri |
| SNTRI GTFS | ZIP | https://catalog.data.gov.tn/fr/dataset/horaires-des-bus-de-la-sntri-gtfs1 |
| Government timetable service | Web service | https://services.gov.tn/transport/ |

* **Legacy SNTRI GTFS UUID:** `9ba6669b-3c22-4a5c-b522-1b2c4c4a011e` (Published March 2023).

---

## 7. SORETRAS — Sfax Regional Transport
* **Operator:** Société Régionale de Transport de Sfax (SORETRAS)
* **Geography:** Sfax

| Dataset | Format | Link |
|---|---|---|
| SORETRAS trip schedules | CSV / XLSX | https://catalogue-data.transport.tn/fr/dataset/les-horaires-des-voyages-de-soretras |
| SORETRAS bus station geographic positions | CSV / XLSX | https://catalogue-data.transport.tn/dataset/positions-geographiques-des-stations-du-reseau-bus-de-la-soretras |
| SORETRAS organization datasets | Various | https://catalogue-data.transport.tn/organization/societe-regionale-de-transport-de-sfax-soretras |

---

## 8. STS — Société de Transport du Sahel
* **Geography:** Sahel region (Sousse, Monastir, Mahdia)

| Dataset | Format | Link |
|---|---|---|
| STS bus GTFS | ZIP | https://catalogue-data.transport.tn/dataset/horaires-des-bus-de-la-societe-de-transport-du-sahel |
| National portal STS GTFS record | ZIP | https://catalog.data.gov.tn/fr/dataset/horaires-des-bus-de-la-societe-de-transport-du-sahel |

* **Ministry catalogue UUID:** `6cb0e17c-03bf-48cc-8c6e-581db05732c4`

---

## 9. SORETRAK — Kairouan Regional Transport
| Dataset | Format | Link |
|---|---|---|
| SORETRAK GTFS static | ZIP | https://catalog.data.gov.tn/fr/dataset/gtfs |
| SORETRAK real-time | Protocol Buffer / TXT | https://catalog.data.gov.tn/fr/dataset/soretrak-realtime |

* **GTFS UUID:** `a155c8b7-3104-4298-b326-3f751902e512`
* **Real-time UUID:** `608d95b2-d5ac-401a-b9df-c193d2d7c8e3`

---

## 10. SRTJ, SRT KEF, SRTB, SRTGN (Regional Operators)
* **SRTJ (Jendouba):** `https://catalog.data.gov.tn/dataset/?_license_id_limit=0&license_id=OTL&tags=gtfs`
* **SRT Kef:** `https://catalogue-data.transport.tn/dataset/horaires-des-bus-de-la-srt-kef` (UUID: `300e2add-3785-472d-9db2-aa52ac9bd8db`)
* **SRTB (Bizerte):** `https://catalogue-data.transport.tn/organization/societe-regionale-de-transport-de-bizerte-srtb`
* **SRTGN (Nabeul & Zaghouan):** `https://catalogue-data.transport.tn/dataset/positions-geographiques-des-stations-du-reseau-bus-de-la-srtgn` (UUID: `ede7395f-ad39-448a-a05f-b174d1c15016`)

---

## 11. National Stop Registry — All Transport Modes
* **Dataset:** Référentiel National d'arrêt
* **Producer:** Ministry of Transport
* **Format:** XLSX and CSV
* **Licence:** OTL
* **UUID:** `628f26a4-3ee0-4e9d-b8a1-9bb2c2f5b2ff`
* **Dataset Page:** https://catalog.data.gov.tn/fr/dataset/628f26a4-3ee0-4e9d-b8a1-9bb2c2f5b2ff
* **Contents:** Bus, train, taxi, and louage stops across the national territory with longitude, latitude, stop code/type, municipality, delegation, governorate, and accessibility (PMR) features.

---

## 12. Taxi Collectif Routes
* **Dataset:** Lignes des taxis collectifs
* **Producer:** Ministry of Transport
* **Format:** CSV
* **Licence:** OTL
* **UUID:** `c07055ec-6049-4c02-a713-3174bd1da096`
* **Dataset Page:** https://catalog.data.gov.tn/fr/dataset/taxis-collectifs
* **Contents:** Separate CSV files by governorate (Tunis, Ariana, Ben Arous, Manouba, Sousse, Sfax, Monastir, Nabeul, Mahdia, etc.) with origin, destination, and intermediate routing corridors.

---

## 13. Louage and Rural Transport
* **Dataset family:** Transport public non régulier des personnes
* **Producer:** Agence Technique des Transports Terrestres (ATTT)
* **Filter:** `https://catalogue-data.transport.tn/dataset/?groups=transport-terrestre&res_format=ZIP`
* **Contents:** Blue-band louages, rural transport authorizations, taxi collectif corridors.
