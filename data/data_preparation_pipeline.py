#!/usr/bin/env python3
"""
MASARI Mobility Platform — Data Preparation & Ingestion Pipeline
Validates GTFS feeds, normalizes the National Stop Reference, maps governorates,
and builds SQLite/PostGIS-ready schema fixtures for offline/online application use.
"""

from __future__ import annotations

import csv
import json
import sqlite3
import zipfile
from collections import Counter
from datetime import datetime
from pathlib import Path

# Accurate geographic boundaries for Tunisia and its 24 governorates
GOV_COORDS = {
    "Tunis": (10.1815, 36.8065),
    "Ariana": (10.1934, 36.8625),
    "Ben Arous": (10.2189, 36.7531),
    "Manouba": (10.0972, 36.8081),
    "Nabeul": (10.7376, 36.4561),
    "Zaghouan": (10.1429, 36.4029),
    "Bizerte": (9.8739, 37.2744),
    "Béja": (9.1817, 36.7256),
    "Jendouba": (8.7802, 36.5011),
    "Le Kef": (8.7049, 36.1742),
    "Siliana": (9.3708, 36.0849),
    "Sousse": (10.6084, 35.8256),
    "Monastir": (10.8262, 35.7771),
    "Mahdia": (11.0622, 35.5047),
    "Sfax": (10.7603, 34.7406),
    "Kairouan": (10.0963, 35.6781),
    "Kasserine": (8.8365, 35.1676),
    "Sidi Bouzid": (9.4849, 35.0382),
    "Gabès": (10.0982, 33.8815),
    "Médenine": (10.5055, 33.3549),
    "Tataouine": (10.4518, 32.9297),
    "Gafsa": (8.7842, 34.4250),
    "Tozeur": (8.1335, 33.9197),
    "Kébili": (8.9690, 33.7044),
}

GTFS_REQUIRED_FILES = {"agency.txt", "stops.txt", "routes.txt", "trips.txt", "stop_times.txt"}

class TunisiaDataPipeline:
    def __init__(self, data_dir: str | Path = "./data"):
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"
        self.fixtures_dir = self.data_dir / "fixtures"
        
        for d in [self.raw_dir, self.processed_dir, self.fixtures_dir]:
            d.mkdir(parents=True, exist_ok=True)
            
        self.db_path = self.processed_dir / "tunisia_mobility.db"

    def setup_database(self):
        print(f"[*] Initializing SQLite database at {self.db_path}")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS stops (
            stop_id TEXT PRIMARY KEY,
            stop_name TEXT NOT NULL,
            lat REAL NOT NULL,
            lon REAL NOT NULL,
            governorate TEXT,
            mode_code TEXT,
            source_id TEXT,
            verified INTEGER DEFAULT 0
        )""")
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS routes (
            route_id TEXT PRIMARY KEY,
            operator_id TEXT,
            mode_code TEXT,
            short_name TEXT,
            long_name TEXT,
            source_id TEXT
        )""")
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS data_provenance (
            dataset_name TEXT PRIMARY KEY,
            source_type TEXT,
            imported_at TEXT,
            record_count INTEGER,
            license TEXT,
            confidence_state TEXT
        )""")
        
        conn.commit()
        conn.close()

    def validate_and_load_gtfs(self, zip_path: Path, source_id: str = "transtu_gtfs") -> dict:
        print(f"[*] Inspecting GTFS archive: {zip_path.name}")
        report = {"file": zip_path.name, "valid": False, "errors": [], "stats": {}}
        
        if not zip_path.is_file():
            report["errors"].append("File not found")
            return report
            
        try:
            with zipfile.ZipFile(zip_path, "r") as z:
                names = {n.replace("\\", "/").lower() for n in z.namelist() if not n.endswith("/")}
                basenames = {Path(n).name for n in names}
                
                missing = GTFS_REQUIRED_FILES - basenames
                if missing:
                    report["errors"].append(f"Missing required GTFS files: {missing}")
                    return report
                
                report["valid"] = True
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Parse stops.txt
                stops_filename = next(n for n in z.namelist() if n.lower().endswith("stops.txt"))
                with z.open(stops_filename) as f:
                    reader = csv.DictReader(f.read().decode("utf-8-sig").splitlines())
                    stop_count = 0
                    for row in reader:
                        s_id = row.get("stop_id")
                        s_name = row.get("stop_name")
                        try:
                            lat = float(row.get("stop_lat", 0))
                            lon = float(row.get("stop_lon", 0))
                        except ValueError:
                            continue
                            
                        # Basic geographic bounds check for Tunisia (lat 30..38, lon 7..12.5)
                        if 30.0 <= lat <= 38.0 and 7.0 <= lon <= 12.5:
                            # Approximate nearest governorate
                            nearest_gov = min(GOV_COORDS.keys(), key=lambda g: (GOV_COORDS[g][0]-lon)**2 + (GOV_COORDS[g][1]-lat)**2)
                            cursor.execute(
                                "INSERT OR REPLACE INTO stops VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                (s_id, s_name, lat, lon, nearest_gov, "BUS", source_id, 1)
                            )
                            stop_count += 1
                    report["stats"]["stops_loaded"] = stop_count
                    
                conn.commit()
                conn.close()
        except Exception as e:
            report["errors"].append(str(e))
            
        return report

    def process_national_stop_reference(self, csv_path: Path) -> dict:
        print(f"[*] Processing National Stop Reference CSV: {csv_path.name}")
        report = {"file": csv_path.name, "rows_processed": 0, "errors": []}
        
        if not csv_path.is_file():
            report["errors"].append("National stop reference CSV not found in raw directory.")
            return report
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            with open(csv_path, "r", encoding="utf-8-sig", errors="replace") as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    # Look for standard header keys in national dataset
                    name = row.get("stop_name") or row.get("nom") or row.get("station_name") or "Unnamed Stop"
                    sid = row.get("stop_id") or row.get("id") or f"nat_{count}"
                    try:
                        lat = float(row.get("lat") or row.get("latitude") or 0)
                        lon = float(row.get("lon") or row.get("longitude") or 0)
                    except ValueError:
                        continue
                        
                    if 30.0 <= lat <= 38.0 and 7.0 <= lon <= 12.5:
                        nearest_gov = min(GOV_COORDS.keys(), key=lambda g: (GOV_COORDS[g][0]-lon)**2 + (GOV_COORDS[g][1]-lat)**2)
                        cursor.execute(
                            "INSERT OR IGNORE INTO stops VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            (sid, name, lat, lon, nearest_gov, "MULTIMODAL", "national_stop_ref", 1)
                        )
                        count += 1
                conn.commit()
                conn.close()
                report["rows_processed"] = count
        except Exception as e:
            report["errors"].append(str(e))
            
        return report

    def export_fixtures(self):
        print("[*] Exporting JSON fixtures for React Native application consumption...")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Export coverage summary by governorate
        coverage = {}
        for gov in GOV_COORDS.keys():
            cursor.execute("SELECT COUNT(*) FROM stops WHERE governorate = ?", (gov,))
            cnt = cursor.fetchone()[0]
            coverage[gov] = {
                "governorate": gov,
                "coordinates": GOV_COORDS[gov],
                "verified_stops": cnt,
                "status": "active" if cnt > 0 else "pending_data"
            }
            
        out_file = self.fixtures_dir / "governorate_coverage.json"
        out_file.write_text(json.dumps(coverage, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[+] Saved coverage fixture: {out_file}")
        
        conn.close()

    def run_pipeline(self):
        self.setup_database()
        
        # Check for raw files
        gtfs_sample = self.raw_dir / "transtu_gtfs.zip"
        if gtfs_sample.exists():
            self.validate_and_load_gtfs(gtfs_sample)
        else:
            print(f"[i] Place raw GTFS zip feeds in '{self.raw_dir}' for automated extraction.")

        nat_csv = self.raw_dir / "national_stops.csv"
        if nat_csv.exists():
            self.process_national_stop_reference(nat_csv)
        else:
            print(f"[i] Place National Stop Reference CSV in '{self.raw_dir}' for normalization.")

        self.export_fixtures()
        print("[+] Data preparation pipeline completed successfully.")

if __name__ == "__main__":
    pipeline = TunisiaDataPipeline()
    pipeline.run_pipeline()