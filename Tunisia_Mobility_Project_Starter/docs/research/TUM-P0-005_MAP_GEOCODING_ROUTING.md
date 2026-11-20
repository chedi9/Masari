# TUM-P0-005: Free Map, Geocoding & Routing Evaluation for Tunisia

**Document Version:** 1.0  
**Date:** 20 November 2026  
**Status:** PROPOSED / RESEARCH REVIEW  
**Cost Constraint:** Strict zero-spend policy ($0 / zero billable APIs / no credit card required)

---

## 1. Executive Summary & Recommended Stack

For a zero-cost, privacy-first Tunisian mobility platform supporting French and Arabic, commercial mapping APIs (Google Maps Platform, Mapbox, HERE) are excluded due to mandatory credit cards, metered billing, and restrictive caching terms.

The recommended open-source stack is:
1. **Map Display & Rendering:** **MapLibre GL** + **CartoDB Positron / OSM Raster/Vector Tiles** (Free tiers / open caching).
2. **Geocoding & Autocomplete:** **Photon (Komoot)** fallback to **Nominatim (OSM)**, pre-filtered with Tunisia bounding box (`viewbox=7.5,30.0,11.6,37.6`).
3. **Walking / Transfer Routing:** **OSRM (Open Source Routing Machine)** public demo or bundled client-side / local engine.

---

## 2. Component Evaluation

### 2.1 Map Rendering & Tile Display

| Option | Cost / Limits | Licensing / Terms | Tunisia Coverage | Arabic / RTL Support | Recommendation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **OpenStreetMap Standard (Tilenik)** | Free for low volume; strict tile usage policy (no bulk/commercial apps) | ODbL / CC-BY-SA | Excellent base street coverage | Bilingual labels present in OSM data | Good for development/prototyping |
| **CartoDB (Positron / Dark Matter)** | Free for standard web/mobile views with attribution | CC-BY 4.0 / Carto ToS | Good clean cartography | Standard UTF-8 / Arabic rendering | **Recommended for Transit UI** (low visual clutter) |
| **MapLibre Native (Vector Tiles via Protomaps / PMTiles)** | 100% Free self-hosted / local file (Zero cloud costs) | BSD-3-Clause | Full Tunisia OSM PBF (~65 MB compressed) | Full client-side Arabic glyph support | **Best for Future Pro Offline Mode** |
| *Google Maps SDK* | Pay-as-you-go ($200 credit, requires CC, charges after) | Commercial proprietary | High | Full | **REJECTED** (Violates zero-spend policy) |
| *Mapbox GL* | Free tier (50k loads), requires CC for signup | Commercial | High | Full | **REJECTED** (Billing risk) |

---

### 2.2 Geocoding & Place Search (French + Arabic)

A critical requirement in Tunisia is searching in both French (*"Gare Barcelone"*, *"Avenue Habib Bourguiba"*) and Arabic (*"محطة برشلونة"*, *"شارع الحبيب بورقيبة"*), as well as colloquial transliterations.

| Service | Protocol / API | Cost & Rate Limits | Strengths | Weaknesses | Recommendation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Photon (by Komoot)** | REST (`photon.komoot.io/api`) | 100% Free, no API key, permissive rate limits | Based on OSM data; fast elasticsearch; excellent typo tolerance; supports `lang=fr` and `lang=ar` | Occasional server maintenance downtime | **Primary Search Candidate** |
| **Nominatim (OSM)** | REST (`nominatim.openstreetmap.org`) | Max 1 req/sec; User-Agent mandatory; strict usage policy | Exhaustive administrative & transit hierarchy; exact matches | Slow autocomplete; rate limit too low for typing | **Fallback / Stop Resolution** |
| **Local SQLite Station Index (FTS5)** | In-App SQLite Full-Text Search | 0 ms latency, 100% offline, $0 cost | Instant auto-complete for all known rail/bus/metro stations | Only searches transit network, not arbitrary house numbers | **Primary Transit Stop Autocomplete** |

---

### 2.3 Pedestrian / Walking Routing (First & Last Mile)

To connect passengers from their GPS position to the nearest transit stop:

| Option | Technology | Hosting | License | Tunisia Routing Quality | Recommendation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **OSRM Foot Profile** | HTTP / C++ | Public demo (`router.project-osrm.org`) or local binary | 2-clause BSD | Fast walking distance and turn-by-turn paths on OSM ways | **Recommended for Walking ETA** |
| **Valhalla** | HTTP / C++ | Self-hostable or FOSS docker | MIT | Highly customizable multi-modal pedestrian costing | Excellent for complex transit transfers |
| **Straight-line / Euclidean fallback** | Client math | In-app TypeScript | Free | Instant; no network | **Safe offline fallback** |

---

## 3. Recommended Architecture for Mobile & Backend

```
[ Passenger Query (Arabic / French) ]
               │
               ▼
   [ 1. Local Transit Stop FTS5 Index ]  ──(Found: Instant Transit Stop)──► [ Route Planner ]
               │ (Not a transit stop)
               ▼
   [ 2. Photon Geocoding API ]           ──(Resolved GPS Coordinate)──────► [ Nearest Stop Matcher ]
   (lang=fr/ar, bbox=Tunisia)
               │
               ▼
   [ 3. OSRM Walking Engine ]            ──(Walking minutes + polyline)───► [ Journey Results Card ]
```

---

## 4. Next Action Items
1. Prototype Photon geocoding with a Tunisia bounding box script (`tools/data_pipeline/search_places.py`).
2. Build an in-app SQLite Full-Text Search index (FTS5) for all imported stops (SNCFT, RFR, SRT Médenine).
3. Test pedestrian walking calculation between a coordinate and the closest station.


---

## 5. Community & Open-Data Map Assets (Updated 20 Nov 2026)

The following three community/open-source assets have been evaluated and integrated into the project's data directory:

1. **[Geofabrik Tunisia Regional Extract](https://download.geofabrik.de/africa/tunisia.html)**:
   - **Format**: `tunisia-latest.osm.pbf` (~81 MB) and `tunisia-latest-free.gpkg.zip` (~170 MB).
   - **Value**: Complete national network of walkable paths, tracks, streets, railway lines, and transit POIs.
   - **License**: Open Database License (ODbL 1.0). Attribution required (`© OpenStreetMap contributors`).
   - **Use**: Offline routing graph for first/last-mile walking routes, station snapping, and offline Pro mapping.

2. **[Map Tunisia by Alaa Taieb](https://github.com/Alaa-Taieb/map-tunisia)**:
   - **Format**: GeoJSON and JSON metadata (`cities.json`, `governorates.json`, `delegations.json`, `municipalities.json`).
   - **Coverage**: 24 governorates, 279 delegations, 2,083 imadas, and 338 municipalities.
   - **Value**: Provides canonical administrative polygons and bilingual French/Arabic reference names for search disambiguation and localized geocoding without external paid API calls.

3. **[Public Transport to GeoJSON API](https://openstreetmap.tools/public_transport_geojson/docs)**:
   - **Value**: Converts complex OSM transit route relations (PTv2 relations) into clean, ready-to-render GeoJSON line strings and platform stops.
   - **Use**: Ingesting visual route traces into our mobile map layer (e.g. rendering Metro Line 1 or TGM on the map).
