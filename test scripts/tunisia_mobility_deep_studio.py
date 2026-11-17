"""
MASARI | Tunisia Unified Mobility Platform - Deep Automated Data Studio (v3.0)
Performs deep automated CKAN resource harvesting, ZIP/GTFS extraction, CSV/GeoJSON coordinate parsing,
SQLite database normalization with full provenance, and React Native fixture export.
"""
from __future__ import annotations

import os
import io
import csv
import json
import math
import hashlib
import zipfile
import sqlite3
import requests
import threading
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
import customtkinter as ctk
from tkinter import messagebox
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

DB_PATH = Path("tunisia_mobility.db")
DATA_DIR = Path("data")
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
FIXTURES_DIR = DATA_DIR / "fixtures"

for d in [RAW_DIR, PROCESSED_DIR, FIXTURES_DIR]:
    d.mkdir(parents=True, exist_ok=True)

CKAN_BASE = "https://catalog.data.gov.tn/api/3/action"
USER_AGENT = "TunisiaMobilityDeepStudio/3.0"

# Tunisia Geographic Bounding Box (WGS84 / SRID 4326)
TN_LAT_MIN, TN_LAT_MAX = 30.0, 38.0
TN_LON_MIN, TN_LON_MAX = 7.0, 12.5

GOV_COORDS = {
    "Tunis": (10.1815, 36.8065), "Ariana": (10.1934, 36.8625), "Ben Arous": (10.2189, 36.7531),
    "Manouba": (10.0972, 36.8081), "Nabeul": (10.7376, 36.4561), "Zaghouan": (10.1429, 36.4029),
    "Bizerte": (9.8739, 37.2744), "Béja": (9.1817, 36.7256), "Jendouba": (8.7802, 36.5011),
    "Le Kef": (8.7049, 36.1742), "Siliana": (9.3708, 36.0849), "Sousse": (10.6360, 35.8256),
    "Monastir": (10.8113, 35.7643), "Mahdia": (11.0622, 35.5047), "Sfax": (10.7603, 34.7406),
    "Kairouan": (10.0963, 35.6711), "Kasserine": (8.8304, 35.1677), "Sidi Bouzid": (9.4821, 35.0382),
    "Gabès": (10.1004, 33.8815), "Medenine": (10.5055, 33.3549), "Tataouine": (10.4518, 32.9297),
    "Gafsa": (8.7842, 34.4250), "Tozeur": (8.1335, 33.9197), "Kebili": (8.9715, 33.7044)
}

def nearest_governorate(lon: float, lat: float) -> str:
    best_gov = "Tunis"
    best_dist = float("inf")
    for gov, (glon, glat) in GOV_COORDS.items():
        d = (lon - glon) ** 2 + (lat - glat) ** 2
        if d < best_dist:
            best_dist = d
            best_gov = gov
    return best_gov

def valid_tn_coord(lon: float, lat: float) -> bool:
    return (TN_LON_MIN <= lon <= TN_LON_MAX) and (TN_LAT_MIN <= lat <= TN_LAT_MAX)

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

class TunisiaDeepStudio(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MASARI | Deep Automated Mobility Data Studio (v3.0)")
        self.geometry("1320x820")
        self.minsize(1080, 720)
        self.stop_event = threading.Event()
        
        self.init_database()
        self.build_ui()
        
    def init_database(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.executescript("""
        CREATE TABLE IF NOT EXISTS dataset_sources (
            source_id TEXT PRIMARY KEY,
            name TEXT,
            source_type TEXT,
            url TEXT,
            license TEXT,
            content_hash TEXT,
            status TEXT,
            imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS downloaded_resources (
            resource_id TEXT PRIMARY KEY,
            package_id TEXT,
            package_title TEXT,
            resource_name TEXT,
            format TEXT,
            url TEXT,
            local_path TEXT,
            file_size_bytes INTEGER,
            content_hash TEXT,
            extraction_status TEXT,
            downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS stops_registry (
            stop_id TEXT PRIMARY KEY,
            source_id TEXT,
            name_ar TEXT,
            name_fr TEXT,
            stop_type TEXT,
            governorate TEXT,
            lon REAL,
            lat REAL,
            verification_status TEXT DEFAULT 'EXTRACTED'
        );
        CREATE TABLE IF NOT EXISTS routes_registry (
            route_id TEXT PRIMARY KEY,
            operator_id TEXT,
            mode_code TEXT,
            short_name TEXT,
            long_name TEXT,
            governorate TEXT,
            status TEXT DEFAULT 'ACTIVE'
        );
        CREATE TABLE IF NOT EXISTS trips_registry (
            trip_id TEXT PRIMARY KEY,
            route_id TEXT,
            service_id TEXT,
            headsign TEXT,
            direction_id TEXT,
            source_id TEXT
        );
        CREATE TABLE IF NOT EXISTS stop_times_registry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_id TEXT,
            stop_id TEXT,
            stop_sequence INTEGER,
            arrival_time TEXT,
            departure_time TEXT,
            source_id TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_stops_gov ON stops_registry(governorate);
        CREATE INDEX IF NOT EXISTS idx_routes_gov ON routes_registry(governorate);
        CREATE INDEX IF NOT EXISTS idx_stoptimes_trip ON stop_times_registry(trip_id);
        """)
        conn.commit()
        conn.close()

    def build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        sidebar = ctk.CTkFrame(self, width=290, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(7, weight=1)

        lbl_title = ctk.CTkLabel(sidebar, text="MASARI DEEP STUDIO", font=ctk.CTkFont(size=20, weight="bold"))
        lbl_title.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")

        lbl_sub = ctk.CTkLabel(sidebar, text="Automated Deep Harvesting & GTFS/GIS", font=ctk.CTkFont(size=12), text_color="gray70")
        lbl_sub.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")

        self.btn_run = ctk.CTkButton(
            sidebar, text="🚀 Start Deep Extraction", height=40,
            fg_color="#1f538d", hover_color="#14375e", font=ctk.CTkFont(weight="bold"),
            command=self.start_deep_pipeline
        )
        self.btn_run.grid(row=2, column=0, padx=20, pady=8, sticky="ew")

        self.btn_stop = ctk.CTkButton(
            sidebar, text="⏹ Stop Pipeline", height=36,
            fg_color="#8b2635", hover_color="#611924", state="disabled",
            command=self.stop_pipeline
        )
        self.btn_stop.grid(row=3, column=0, padx=20, pady=8, sticky="ew")

        self.btn_refresh = ctk.CTkButton(
            sidebar, text="🔄 Refresh Database Stats", height=36,
            fg_color="gray30", command=self.refresh_stats
        )
        self.btn_refresh.grid(row=4, column=0, padx=20, pady=8, sticky="ew")

        self.lbl_stage = ctk.CTkLabel(sidebar, text="Stage: Idle", font=ctk.CTkFont(size=12), wraplength=240, justify="left")
        self.lbl_stage.grid(row=5, column=0, padx=20, pady=(20, 5), sticky="w")

        self.progress = ctk.CTkProgressBar(sidebar)
        self.progress.grid(row=6, column=0, padx=20, pady=(5, 20), sticky="ew")
        self.progress.set(0.0)

        # Main Display
        main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        # Metric Cards
        stats_header = ctk.CTkFrame(main_frame, height=105)
        stats_header.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        stats_header.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        self.stat_files = self.create_stat_card(stats_header, 0, "Downloaded Files", "0")
        self.stat_stops = self.create_stat_card(stats_header, 1, "Extracted Stops", "0")
        self.stat_routes = self.create_stat_card(stats_header, 2, "Active Routes", "0")
        self.stat_trips = self.create_stat_card(stats_header, 3, "GTFS Trips", "0")
        self.stat_stoptimes = self.create_stat_card(stats_header, 4, "Stop Times", "0")

        # Live Execution Terminal
        terminal_frame = ctk.CTkFrame(main_frame)
        terminal_frame.grid(row=1, column=0, sticky="nsew")
        terminal_frame.grid_columnconfigure(0, weight=1)
        terminal_frame.grid_rowconfigure(1, weight=1)

        lbl_term = ctk.CTkLabel(terminal_frame, text="Deep Extraction & GTFS/GeoJSON Parser Terminal", font=ctk.CTkFont(size=14, weight="bold"))
        lbl_term.grid(row=0, column=0, padx=15, pady=10, sticky="w")

        self.log_box = ctk.CTkTextbox(terminal_frame, font=ctk.CTkFont(family="Consolas", size=12))
        self.log_box.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")
        self.log_box.insert("end", "[INFO] Deep Studio v3.0 ready. Click 'Start Deep Extraction' to crawl, download, and parse real transport archives.\n")

        self.refresh_stats()

    def create_stat_card(self, parent, col, title, initial_val):
        card = ctk.CTkFrame(parent, fg_color=("gray85", "gray17"))
        card.grid(row=0, column=col, padx=8, pady=10, sticky="nsew")
        lbl_title = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=11), text_color="gray60")
        lbl_title.pack(anchor="w", padx=12, pady=(8, 0))
        lbl_val = ctk.CTkLabel(card, text=initial_val, font=ctk.CTkFont(size=20, weight="bold"))
        lbl_val.pack(anchor="w", padx=12, pady=(2, 8))
        return lbl_val

    def log(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.after(0, lambda: self._append_log(f"[{timestamp}] {msg}\n"))

    def _append_log(self, text):
        self.log_box.insert("end", text)
        self.log_box.see("end")

    def set_stage(self, text, prog=None):
        self.after(0, lambda: self.lbl_stage.configure(text=f"Stage: {text}"))
        if prog is not None:
            self.after(0, lambda: self.progress.set(prog))

    def refresh_stats(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM downloaded_resources")
            files_c = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM stops_registry")
            stops_c = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM routes_registry")
            routes_c = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM trips_registry")
            trips_c = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM stop_times_registry")
            st_c = cursor.fetchone()[0]
            conn.close()

            self.stat_files.configure(text=f"{files_c:,}")
            self.stat_stops.configure(text=f"{stops_c:,}")
            self.stat_routes.configure(text=f"{routes_c:,}")
            self.stat_trips.configure(text=f"{trips_c:,}")
            self.stat_stoptimes.configure(text=f"{st_c:,}")
        except Exception as e:
            self.log(f"[ERROR] Stats refresh failed: {e}")

    def start_deep_pipeline(self):
        self.stop_event.clear()
        self.btn_run.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        self.log("=== STARTING DEEP AUTOMATED HARVESTING & EXTRACTION PIPELINE ===")
        threading.Thread(target=self.run_deep_pipeline, daemon=True).start()

    def stop_pipeline(self):
        self.stop_event.set()
        self.log("[WARN] Stop requested by user. Finishing active download...")

    def parse_csv_stream(self, raw_bytes: bytes, source_id: str, cursor: sqlite3.Cursor) -> tuple[int, int]:
        stops_added = 0
        routes_added = 0
        text = None
        for enc in ("utf-8-sig", "utf-8", "latin-1", "cp1256"):
            try:
                text = raw_bytes.decode(enc)
                break
            except Exception:
                continue
        if not text:
            return 0, 0

        try:
            sample = text[:4096]
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
        except Exception:
            dialect = csv.excel

        reader = csv.DictReader(io.StringIO(text), dialect=dialect)
        if not reader.fieldnames:
            return 0, 0

        headers = {h.strip().lower(): h for h in reader.fieldnames if h}
        lat_col = next((headers[k] for k in headers if k in {"stop_lat", "lat", "latitude", "y", "coord_y"}), None)
        lon_col = next((headers[k] for k in headers if k in {"stop_lon", "lon", "lng", "longitude", "x", "coord_x"}), None)
        name_col = next((headers[k] for k in headers if k in {"stop_name", "name", "nom", "libelle", "arret", "station", "title"}), None)
        id_col = next((headers[k] for k in headers if k in {"stop_id", "id", "code", "code_arret"}), None)

        if lat_col and lon_col:
            batch = []
            for idx, row in enumerate(reader):
                try:
                    lat = float(str(row.get(lat_col, "")).replace(",", ".").strip())
                    lon = float(str(row.get(lon_col, "")).replace(",", ".").strip())
                    if not valid_tn_coord(lon, lat):
                        continue
                    sname = str(row.get(name_col) or f"Stop {idx+1}").strip()
                    sid = str(row.get(id_col) or f"{source_id}_csv_{idx}_{round(lat,5)}_{round(lon,5)}").strip()
                    gov = nearest_governorate(lon, lat)
                    batch.append((sid, source_id, sname, sname, "EXTRACTED_STOP", gov, lon, lat, "VERIFIED_GEO"))
                except Exception:
                    continue
            if batch:
                cursor.executemany(
                    "INSERT OR REPLACE INTO stops_registry (stop_id, source_id, name_ar, name_fr, stop_type, governorate, lon, lat, verification_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    batch
                )
                stops_added += len(batch)
        return stops_added, routes_added

    def parse_geojson_bytes(self, raw_bytes: bytes, source_id: str, cursor: sqlite3.Cursor) -> int:
        stops_added = 0
        try:
            obj = json.loads(raw_bytes.decode("utf-8", errors="ignore"))
        except Exception:
            return 0

        features = obj.get("features", []) if isinstance(obj, dict) else []
        batch = []
        for idx, feat in enumerate(features):
            if not isinstance(feat, dict):
                continue
            geom = feat.get("geometry") or {}
            props = feat.get("properties") or {}
            gtype = geom.get("type")
            coords = geom.get("coordinates")
            if gtype == "Point" and isinstance(coords, list) and len(coords) >= 2:
                try:
                    lon, lat = float(coords[0]), float(coords[1])
                    if valid_tn_coord(lon, lat):
                        name = str(props.get("name") or props.get("nom") or props.get("libelle") or props.get("stop_name") or f"GeoStop {idx+1}")
                        sid = str(props.get("id") or props.get("stop_id") or f"{source_id}_geo_{idx}")
                        gov = nearest_governorate(lon, lat)
                        batch.append((sid, source_id, name, name, "GEOJSON_POINT", gov, lon, lat, "VERIFIED_GEO"))
                except Exception:
                    continue
        if batch:
            cursor.executemany(
                "INSERT OR REPLACE INTO stops_registry (stop_id, source_id, name_ar, name_fr, stop_type, governorate, lon, lat, verification_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                batch
            )
            stops_added += len(batch)
        return stops_added

    def parse_gtfs_or_zip(self, zip_path: Path, source_id: str, cursor: sqlite3.Cursor) -> dict:
        counts = {"stops": 0, "routes": 0, "trips": 0, "stop_times": 0}
        try:
            with zipfile.ZipFile(zip_path, "r") as z:
                names = {Path(n).name.lower(): n for n in z.namelist() if not n.endswith("/")}
                
                # 1. stops.txt
                if "stops.txt" in names:
                    text = z.read(names["stops.txt"]).decode("utf-8-sig", errors="ignore")
                    reader = csv.DictReader(io.StringIO(text))
                    batch = []
                    for r in reader:
                        try:
                            lat = float(r.get("stop_lat", 0))
                            lon = float(r.get("stop_lon", 0))
                            if not valid_tn_coord(lon, lat):
                                continue
                            sid = f"{source_id}_{r.get('stop_id', '')}"
                            sname = r.get("stop_name", "Unknown Stop").strip()
                            gov = nearest_governorate(lon, lat)
                            batch.append((sid, source_id, sname, sname, "GTFS_STOP", gov, lon, lat, "OFFICIAL_GTFS"))
                        except Exception:
                            continue
                    if batch:
                        cursor.executemany(
                            "INSERT OR REPLACE INTO stops_registry (stop_id, source_id, name_ar, name_fr, stop_type, governorate, lon, lat, verification_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            batch
                        )
                        counts["stops"] += len(batch)

                # 2. routes.txt
                if "routes.txt" in names:
                    text = z.read(names["routes.txt"]).decode("utf-8-sig", errors="ignore")
                    reader = csv.DictReader(io.StringIO(text))
                    batch = []
                    mode_map = {"0": "METRO", "1": "METRO", "2": "TRAIN", "3": "BUS"}
                    for r in reader:
                        rid = f"{source_id}_{r.get('route_id', '')}"
                        mcode = mode_map.get(str(r.get("route_type", "3")), "BUS")
                        sname = r.get("route_short_name", "").strip()
                        lname = r.get("route_long_name", "").strip()
                        gov = "Tunis" if "transtu" in source_id.lower() else "National"
                        batch.append((rid, source_id, mcode, sname, lname, gov, "ACTIVE"))
                    if batch:
                        cursor.executemany(
                            "INSERT OR REPLACE INTO routes_registry (route_id, operator_id, mode_code, short_name, long_name, governorate, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            batch
                        )
                        counts["routes"] += len(batch)

                # 3. trips.txt
                if "trips.txt" in names:
                    text = z.read(names["trips.txt"]).decode("utf-8-sig", errors="ignore")
                    reader = csv.DictReader(io.StringIO(text))
                    batch = []
                    for r in reader:
                        tid = f"{source_id}_{r.get('trip_id', '')}"
                        rid = f"{source_id}_{r.get('route_id', '')}"
                        sid = r.get("service_id", "")
                        head = r.get("trip_headsign", "")
                        did = r.get("direction_id", "0")
                        batch.append((tid, rid, sid, head, did, source_id))
                    if batch:
                        cursor.executemany(
                            "INSERT OR REPLACE INTO trips_registry (trip_id, route_id, service_id, headsign, direction_id, source_id) VALUES (?, ?, ?, ?, ?, ?)",
                            batch
                        )
                        counts["trips"] += len(batch)

                # 4. stop_times.txt (capped at 150,000 rows per archive for fast desktop SQLite performance)
                if "stop_times.txt" in names:
                    text = z.read(names["stop_times.txt"]).decode("utf-8-sig", errors="ignore")
                    reader = csv.DictReader(io.StringIO(text))
                    batch = []
                    for idx, r in enumerate(reader):
                        if idx >= 150000:
                            break
                        tid = f"{source_id}_{r.get('trip_id', '')}"
                        sid = f"{source_id}_{r.get('stop_id', '')}"
                        seq = int(r.get("stop_sequence", 0) or 0)
                        arr = r.get("arrival_time", "")
                        dep = r.get("departure_time", "")
                        batch.append((tid, sid, seq, arr, dep, source_id))
                    if batch:
                        cursor.executemany(
                            "INSERT INTO stop_times_registry (trip_id, stop_id, stop_sequence, arrival_time, departure_time, source_id) VALUES (?, ?, ?, ?, ?, ?)",
                            batch
                        )
                        counts["stop_times"] += len(batch)

                # Also inspect any nested CSV or GeoJSON files inside non-GTFS zip archives
                if "stops.txt" not in names:
                    for fname, full_name in names.items():
                        if fname.endswith(".csv"):
                            s_add, r_add = self.parse_csv_stream(z.read(full_name), source_id, cursor)
                            counts["stops"] += s_add
                            counts["routes"] += r_add
                        elif fname.endswith((".geojson", ".json")):
                            counts["stops"] += self.parse_geojson_bytes(z.read(full_name), source_id, cursor)

        except Exception as e:
            self.log(f"[WARN] Archive extraction error on {zip_path.name}: {e}")
        return counts

    def run_deep_pipeline(self):
        try:
            self.set_stage("Discovering CKAN Packages", 0.05)
            queries = [
                "transport", "transtu", "sntri", "sncft", "arret", "louage",
                "bus", "metro", "ferroviaire", "mobilite", "Tunis", "Sousse", "Sfax", "Monastir"
            ]
            packages = {}
            for idx, q in enumerate(queries):
                if self.stop_event.is_set():
                    break
                try:
                    res = requests.get(
                        f"{CKAN_BASE}/package_search",
                        params={"q": q, "rows": 50},
                        headers={"User-Agent": USER_AGENT},
                        timeout=15,
                        verify=False
                    )
                    if res.status_code == 200 and res.json().get("success"):
                        for pkg in res.json()["result"].get("results", []):
                            packages[pkg["id"]] = pkg
                except Exception as e:
                    self.log(f"[WARN] Search query '{q}' notice: {e}")
                self.set_stage(f"Discovering ({idx+1}/{len(queries)})", 0.05 + 0.15 * ((idx + 1) / len(queries)))

            self.log(f"Discovered {len(packages)} unique CKAN transport packages.")

            # Collect all downloadable resources
            resources_to_fetch = []
            for pkg_id, pkg in packages.items():
                pkg_title = pkg.get("title") or pkg.get("name") or pkg_id
                pkg_license = pkg.get("license_title") or pkg.get("license_id") or "Unknown"
                for res in pkg.get("resources", []):
                    url = res.get("url") or res.get("cache_url")
                    if not url or not url.startswith(("http://", "https://")):
                        continue
                    fmt = str(res.get("format") or "").upper().strip()
                    resources_to_fetch.append({
                        "resource_id": res.get("id") or sha256_bytes(url.encode())[:16],
                        "package_id": pkg_id,
                        "package_title": pkg_title,
                        "license": pkg_license,
                        "resource_name": res.get("name") or Path(urlparse(url).path).name or "resource",
                        "format": fmt,
                        "url": url
                    })

            self.log(f"Identified {len(resources_to_fetch)} downloadable resource endpoints across all packages.")
            self.set_stage("Downloading & Extracting Files", 0.25)

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            total_res = max(len(resources_to_fetch), 1)
            for idx, r in enumerate(resources_to_fetch):
                if self.stop_event.is_set():
                    break

                prog = 0.25 + 0.65 * ((idx + 1) / total_res)
                self.set_stage(f"Processing {idx+1}/{len(resources_to_fetch)}", prog)

                url = r["url"]
                rid = r["resource_id"]
                src_slug = f"{r['package_id'][:20]}_{rid[:8]}"

                try:
                    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=25, verify=False)
                    if resp.status_code != 200 or not resp.content:
                        self.log(f"[SKIP] HTTP {resp.status_code} for {r['resource_name']}")
                        continue

                    data = resp.content
                    fhash = sha256_bytes(data)
                    ext = Path(urlparse(url).path).suffix.lower()
                    if not ext:
                        if data[:4] == b"PK\x03\x04":
                            ext = ".zip"
                        elif r["format"] in {"CSV", "JSON", "GEOJSON", "XLSX"}:
                            ext = f".{r['format'].lower()}"
                        else:
                            ext = ".dat"

                    safe_fname = f"{src_slug}{ext}"
                    local_file = RAW_DIR / safe_fname
                    local_file.write_bytes(data)

                    cursor.execute(
                        "INSERT OR REPLACE INTO dataset_sources (source_id, name, source_type, url, license, content_hash, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (src_slug, r["package_title"], r["format"] or ext.upper(), url, r["license"], fhash, "INGESTED")
                    )

                    extracted_summary = "Stored raw file"
                    if ext == ".zip" or data[:4] == b"PK\x03\x04":
                        res_counts = self.parse_gtfs_or_zip(local_file, src_slug, cursor)
                        extracted_summary = f"ZIP/GTFS: +{res_counts['stops']} stops, +{res_counts['routes']} routes, +{res_counts['trips']} trips"
                        if any(res_counts.values()):
                            self.log(f"[EXTRACTED] {r['resource_name']} -> {extracted_summary}")
                    elif ext == ".csv":
                        s_add, r_add = self.parse_csv_stream(data, src_slug, cursor)
                        extracted_summary = f"CSV: +{s_add} stops"
                        if s_add:
                            self.log(f"[EXTRACTED] {r['resource_name']} -> {extracted_summary}")
                    elif ext in {".geojson", ".json"}:
                        s_add = self.parse_geojson_bytes(data, src_slug, cursor)
                        extracted_summary = f"GeoJSON: +{s_add} stops"
                        if s_add:
                            self.log(f"[EXTRACTED] {r['resource_name']} -> {extracted_summary}")

                    cursor.execute(
                        "INSERT OR REPLACE INTO downloaded_resources (resource_id, package_id, package_title, resource_name, format, url, local_path, file_size_bytes, content_hash, extraction_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (rid, r["package_id"], r["package_title"], r["resource_name"], r["format"], url, str(local_file), len(data), fhash, extracted_summary)
                    )
                    conn.commit()
                    self.after(0, self.refresh_stats)

                except Exception as e:
                    self.log(f"[WARN] Failed downloading/parsing {r['resource_name']}: {e}")

            # Generate comprehensive React Native fixtures from real extracted SQLite tables
            self.set_stage("Generating React Native Fixtures", 0.92)
            self.log("Building React Native JSON fixtures from extracted SQLite database...")

            cursor.execute("SELECT governorate, COUNT(*) FROM stops_registry GROUP BY governorate ORDER BY COUNT(*) DESC")
            gov_stop_counts = dict(cursor.fetchall())

            cursor.execute("SELECT stop_id, name_ar, name_fr, stop_type, governorate, lon, lat, verification_status FROM stops_registry LIMIT 5000")
            stops_export = [
                {
                    "id": row[0], "name_ar": row[1], "name_fr": row[2],
                    "type": row[3], "governorate": row[4], "lon": row[5], "lat": row[6], "status": row[7]
                }
                for row in cursor.fetchall()
            ]

            cursor.execute("SELECT route_id, operator_id, mode_code, short_name, long_name, governorate FROM routes_registry LIMIT 2000")
            routes_export = [
                {
                    "id": row[0], "operator": row[1], "mode": row[2],
                    "short_name": row[3], "long_name": row[4], "governorate": row[5]
                }
                for row in cursor.fetchall()
            ]
            conn.close()

            (FIXTURES_DIR / "governorate_coverage.json").write_text(
                json.dumps({"generated_at": datetime.now().isoformat(), "stops_by_governorate": gov_stop_counts}, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
            (FIXTURES_DIR / "stops_fixture.json").write_text(
                json.dumps(stops_export, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
            (FIXTURES_DIR / "routes_fixture.json").write_text(
                json.dumps(routes_export, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )

            self.set_stage("Completed", 1.0)
            self.log(f"Exported {len(stops_export)} stops and {len(routes_export)} routes to {FIXTURES_DIR}/")
            self.log("=== DEEP EXTRACTION PIPELINE FINISHED SUCCESSFULLY ===")
            self.after(0, self.refresh_stats)
            self.after(0, lambda: messagebox.showinfo("Deep Extraction Complete", f"Extracted {len(stops_export):,} stops and {len(routes_export):,} routes into SQLite & React Native fixtures!"))

        except Exception as e:
            self.log(f"[ERROR] Fatal pipeline error: {e}")
            self.set_stage("Error", 0.0)
        finally:
            self.after(0, lambda: self.btn_run.configure(state="normal"))
            self.after(0, lambda: self.btn_stop.configure(state="disabled"))

if __name__ == "__main__":
    app = TunisiaDeepStudio()
    app.mainloop()
