# Tunisia Mobility Platform — Workspace Organization Guide

This repository follows the owner-approved **Modular Monolith & Mobile Monorepo** layout defined in `docs/architecture/PROJECT_STRUCTURE.md`.

---

## 🗂️ Clean Directory Layout

```text
.
├── apps/
│   └── mobile/                       # React Native + Expo SDK 57 mobile application
│       ├── app/                      # Expo Router screens ((tabs): index, explore, reports, account)
│       └── src/                      # Features, shared tokens, RTL i18n, elastic components
│
├── tools/
│   └── data_pipeline/                # Python standard library data tools & routing engines
│       ├── sources/                  # Importers (sncft, transtu, rfr, map harvester)
│       │   ├── sncft_importer.py     # National & suburban train GTFS importer
│       │   ├── rfr_importer.py       # RFR rapid rail importer
│       │   ├── transtu_importer.py   # General GTFS importer (SRT Médenine / TRANSTU)
│       │   └── harvest_tunisia_maps.py # OpenStreetMap & Map Tunisia harvester
│       ├── query_journey.py          # Unified multi-modal journey planning CLI
│       ├── search_stops.py           # In-app SQLite FTS5 multilingual stop search
│       └── nearest_stop.py           # Pedestrian walking distance & stop snapping
│
├── data/                             # All transit datasets (kept clean & separated)
│   ├── raw/                          # Downloaded GTFS archives (*.zip) — gitignored
│   │   ├── sncft_gtfs.zip
│   │   └── transtu_gtfs.zip (pending)
│   └── processed/                    # Generated SQLite databases (*.db) — rebuildable
│       ├── tunisia_mobility.db       # SNCFT Train & Sahel Metro
│       ├── rfr_tunis.db              # RFR Lines D & E
│       ├── srt_medenine.db           # Regional Bus (Djerba / Zarzis)
│       └── unified_stops_fts.db      # Unified FTS5 autocomplete index (1,487 stops)
│
├── tunisia_map_harvest/              # Harvested OSM PBF, GeoJSON layers, Overpass stops
│   ├── raw/geofabrik/                # tunisia-latest.osm.pbf (81.0 MB)
│   ├── geojson/administrative/       # 24 governorates, 279 delegations, 338 municipalities
│   └── geojson/{tunis,sousse,...}/   # 2,493 OSM stops & route segments
│
├── docs/                             # Single Source of Truth project memory
│   ├── MASTER_ROADMAP.md             # Master execution plan & phase gates
│   ├── AI_HANDOFF_LOG.md             # Sequential agent handoff log
│   ├── architecture/                 # PROJECT_STRUCTURE.md, ADRs
│   └── research/                     # Sourced technical & data evaluations
│
└── dashboard.html                    # Visual project dashboard & status tracking
```

---

## ⚡ Quick Command Reference

| Action | Command |
| :--- | :--- |
| **Start Mobile App** | `cd apps/mobile && npx.cmd expo start` |
| **Search Stops (FTS5)** | `python tools/data_pipeline/search_stops.py "Barcelone"` |
| **Nearest Stop from GPS** | `python tools/data_pipeline/nearest_stop.py` |
| **Query Rail Journeys** | `python tools/data_pipeline/query_journey.py "Tunis Ville" "Borj Cedria"` |
| **Query Sahel Metro** | `python tools/data_pipeline/query_journey.py "Sousse Bab Jdid" "Monastir"` |
| **Query Regional Bus** | `python tools/data_pipeline/query_journey.py "MEDENINE CENTRE" "HOUMET SOUK" data/processed/srt_medenine.db` |
| **Query RFR Rapid Rail** | `python tools/data_pipeline/query_journey.py "Barcelone" "Bougatfa" data/processed/rfr_tunis.db` |
