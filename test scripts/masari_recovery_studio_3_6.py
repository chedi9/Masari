
from __future__ import annotations

import csv
import ctypes
import hashlib
import io
import json
import logging
import math
import mimetypes
import os
import queue
import re
import shutil
import sqlite3
import threading
import time
import zipfile
from collections import Counter
from datetime import datetime
from email.message import Message
from pathlib import Path
from urllib.parse import urlparse, unquote

import truststore
truststore.inject_into_ssl()
import requests
import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox

# Setup logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("MASARI_3_6")

APP_TITLE = "MASARI | Recovery & Deep Database Studio 3.6"
VERSION = "3.6.0"
CKAN_BASE = "https://catalog.data.gov.tn/api/3/action"
USER_AGENT = f"MASARI-Recovery-Studio/{VERSION}"
KNOWN_UNREACHABLE_HOSTS = {"data.transport.tn", "catalogue-data.transport.tn"}
MAX_FILE_MB = 300
MAX_PAGES_PER_QUERY = 12
CSV_ROW_LIMIT = 250000
ARCHIVE_MEMBER_LIMIT = 10000
MAX_TEXT_MB = 100

# Tunisia Geographic Bounding Box (WGS84 / SRID 4326)
TN_LAT_MIN, TN_LAT_MAX = 30.0, 38.0
TN_LON_MIN, TN_LON_MAX = 7.0, 12.5

# Accurate geographic centroids (lon, lat) for all 24 Tunisian governorates
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

TUNISIA_OUTLINE = [
    (8.62, 36.94), (8.95, 37.12), (9.45, 37.25), (9.87, 37.34), (10.18, 37.18),
    (10.22, 36.85), (10.35, 36.75), (10.85, 37.05), (11.05, 36.85), (10.80, 36.42),
    (10.52, 36.22), (10.62, 35.85), (10.88, 35.78), (11.08, 35.50), (11.02, 35.12),
    (10.82, 34.74), (10.45, 34.45), (10.12, 34.10), (10.12, 33.85), (10.55, 33.68),
    (11.12, 33.48), (11.55, 33.18), (11.35, 32.65), (10.95, 32.15), (10.45, 31.65),
    (10.05, 30.85), (9.55, 30.24), (9.05, 31.15), (8.65, 32.10), (8.35, 33.05),
    (7.75, 33.85), (7.65, 34.35), (8.15, 34.85), (8.35, 35.45), (8.28, 36.05),
    (8.42, 36.55), (8.62, 36.94)
]

GOVERNORATES = list(GOV_COORDS.keys())
GOV_ALIASES = {
    "Tunis": ["tunis"], "Ariana": ["ariana"], "Ben Arous": ["ben arous"],
    "Manouba": ["manouba", "la manouba"], "Nabeul": ["nabeul", "nabuel"],
    "Zaghouan": ["zaghouan"], "Bizerte": ["bizerte"], "Béja": ["beja", "béja"],
    "Jendouba": ["jendouba"], "Le Kef": ["le kef", "el kef", "kef"],
    "Siliana": ["siliana"], "Sousse": ["sousse"], "Monastir": ["monastir"],
    "Mahdia": ["mahdia"], "Sfax": ["sfax"], "Kairouan": ["kairouan"],
    "Kasserine": ["kasserine"], "Sidi Bouzid": ["sidi bouzid"],
    "Gabès": ["gabes", "gabès"], "Médenine": ["medenine", "médenine"],
    "Tataouine": ["tataouine"], "Gafsa": ["gafsa"], "Tozeur": ["tozeur"],
    "Kébili": ["kebili", "kébili"]
}

OPERATORS = ["TRANSTU", "SNCFT", "RFR", "SNTRI", "SORETRAS", "SORETRAK", "SONOTRAK", "STS", "SRTJ", "SRT KEF", "SRT Béja", "SRTB", "SRTGN", "SRTM", "SRTG"]
TRANSPORT_TERMS = ["transport public", "transport collectif", "transport terrestre", "bus", "autobus", "métro", "metro léger", "train", "ferroviaire", "chemin de fer", "taxi collectif", "louage", "gare routière", "gare ferroviaire", "arrêt bus", "arret bus", "ligne bus", "horaires transport", "horaire bus", "horaire train", "tarif transport", "GTFS", "timetable", "stop_times", "stops.txt", "routes.txt"]
GEO_TERMS = ["découpage administratif Tunisie", "gouvernorats Tunisie", "délégations Tunisie", "municipalités Tunisie", "communes Tunisie", "limites administratives", "frontières administratives", "localités Tunisie", "villes Tunisie", "codes géographiques Tunisie", "référentiel géographique", "GeoJSON Tunisie", "shapefile Tunisie", "carte administrative Tunisie"]
ADMIN_STRONG = ["découpage de la tunisie par gouvernorat", "decoupage de la tunisie par gouvernorat", "découpage géographique des gouvernorats", "decoupage geographique des gouvernorats", "liste des gouvernorats", "liste des délégations", "liste des delegations", "limites des gouvernorats", "limites des délégations", "limites des delegations", "codes des gouvernorats", "découpage de la tunisie par délégation", "decoupage de la tunisie par delegation", "découpage de la tunisie par municipalité", "decoupage de la tunisie par municipalite", "découpage de la tunisie par circonscription", "circonsciptions", "administrative boundaries", "découpage administratif", "decoupage administratif", "limites administratives", "frontières administratives", "frontieres administratives", "gouvernorat boundary", "limite de gouvernorat", "délégations de tunisie", "delegations de tunisie", "municipalités de tunisie", "communes de tunisie"]
USEFUL_GEO_TERMS = ["localité", "localite", "ville", "villes", "poi", "point of interest", "lieu-dit", "localisation", "geolocalisation", "geolocation", "coordonnées des stations", "coordonnees des stations", "station de transport", "arrêt de bus", "arret de bus"]
EXCLUDE_TERMS = ["agriculture", "agricole", "agronomie", "miel", "apiculture", "irrigation", "barrage", "barrages", "eau potable", "eaux usées", "eaux usees", "pluviométrie", "pluviometrie", "précipitation", "precipitation", "nappe phréatique", "nappe phreatique", "musée", "musee", "archéologie", "archeologie", "festival", "école", "ecole", "scolaire", "santé", "sante", "hôpital", "hopital", "incubateur", "technopole", "centre médical", "centre medical", "football", "sport", "pétrole", "petrole", "hydrocarbure", "hydrocarbures", "gaz naturel"]
GTFS_REQUIRED = {"agency.txt", "stops.txt", "routes.txt", "trips.txt", "stop_times.txt"}

def now_iso(): return datetime.now().astimezone().isoformat(timespec="seconds")
def norm(v): return re.sub(r"\s+", " ", str(v or "").lower().replace("’", "'")).strip()
def safe_name(v):
    s = unquote(str(v or "item"))
    s = re.sub(r"[^\w.\-]+", "_", s, flags=re.UNICODE).strip("._")
    return s[:110] or "item"

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()

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

def has_phrase(text, phrase):
    phrase = norm(phrase)
    if re.fullmatch(r"[a-z0-9]+", phrase):
        return re.search(r"(?<![a-z0-9])" + re.escape(phrase) + r"(?![a-z0-9])", text) is not None
    return phrase in text

def gov_matches(text):
    t = norm(text)
    found = []
    for official, aliases in GOV_ALIASES.items():
        if any(re.search(r"(?<!\w)" + re.escape(norm(a)) + r"(?!\w)", t) for a in aliases):
            found.append(official)
    return found

def classify_resource(row):
    title = norm(row.get("dataset_title") or row.get("title"))
    name = norm(row.get("name"))
    org = norm(row.get("organization"))
    tags = " ".join(norm(x.get("name") if isinstance(x, dict) else x) for x in (row.get("tags") or []))
    desc = norm(row.get("description") or row.get("dataset_notes") or row.get("notes"))
    url = norm(row.get("url"))
    primary = " ".join([title, name, org, tags])
    alltext = " ".join([primary, desc, url])
    exclusions = [x for x in EXCLUDE_TERMS if has_phrase(primary, x)]
    operator_terms = ["transtu", "sncft", "rfr", "sntri", "soretras", "soretrak", "sonotrak", "sts", "srtj", "srt kef", "srt béja", "srtb", "srtgn", "srtm", "srtg"]
    weighted = [
        ("gtfs", 55), ("stop_times", 55), ("agency.txt", 45), ("stops.txt", 45), ("routes.txt", 45), ("trips.txt", 45),
        ("lignes des taxis collectifs", 42), ("taxis collectifs", 36), ("taxi collectif", 30), ("louage", 30),
        ("sncft", 32), ("transtu", 32), ("sntri", 30), ("rfr", 30), ("soretras", 30), ("soretrak", 30), ("sonotrak", 28),
        ("horaires", 24), ("horaire", 24), ("timetable", 24), ("schedule", 20), ("transport public", 26),
        ("transport collectif", 26), ("transport terrestre", 20), ("transport rural", 24), ("métro léger", 28),
        ("metro léger", 28), ("autobus", 22), ("chemin de fer", 24), ("réseau ferré", 24), ("reseau ferre", 24)
    ]
    score = 0
    evidence = []
    for op in operator_terms:
        if has_phrase(primary, op):
            score += 28
            evidence.append("operator:" + op)
            break
    for phrase, points in weighted:
        if has_phrase(primary, phrase):
            score += points
            evidence.append("strong:" + phrase)
    for phrase, points in [("itinéraire", 10), ("itineraire", 10), ("ligne", 7), ("gare", 7), ("arrêt", 8), ("arret", 8), ("station", 5), ("tarif", 8), ("fare", 8), ("position géographique", 8), ("position geographique", 8)]:
        if has_phrase(primary, phrase):
            score += points
            evidence.append("title:" + phrase)
    desc_hits = [x for x in ["bus", "train", "transport", "horaire", "station"] if has_phrase(desc, x)]
    score += min(8, len(desc_hits) * 2)
    evidence += ["description:" + x for x in desc_hits]
    strong_transport = any(has_phrase(primary, x) for x in ["transport public", "transport collectif", "transport terrestre", "lignes des taxis collectifs", "taxis collectifs", "sncft", "transtu", "sntri", "rfr", "soretras", "soretrak", "gtfs"])
    if exclusions and not strong_transport:
        score = 0
    admin_hits = [x for x in ADMIN_STRONG if has_phrase(primary, x)]
    admin_score = len(admin_hits) * 30
    geo_hits = [x for x in USEFUL_GEO_TERMS if has_phrase(primary, x)]
    geo_score = len(geo_hits) * 9
    ext = Path(urlparse(str(row.get("url") or "")).path).suffix.lower()
    if ext in {".geojson", ".gpkg", ".kml", ".gpx"}:
        geo_score += 5
    if score >= 20 and score >= admin_score:
        category = "Transport"
        sub = []
        if any(x in alltext for x in ["horaire", "horaires", "timetable", "schedule"]): sub.append("timetables")
        if any(x in alltext for x in ["tarif", "fare", "prix"]): sub.append("fares")
        if any(x in alltext for x in ["arrêt", "arret", "stop", "station", "gare"]): sub.append("stops_stations")
        if any(x in alltext for x in ["ligne", "route", "itinéraire", "itineraire"]): sub.append("routes_lines")
        if not sub: sub = ["transport_reference"]
        mode = []
        for label, terms in [
            ("Bus", ["bus", "autobus", "transtu", "soretras", "soretrak", "srtb", "srtgn", "srtj"]),
            ("Metro / Light rail", ["métro", "metro", "rfr", "tgm"]),
            ("Train", ["sncft", "train", "ferroviaire", "réseau ferré", "reseau ferre"]),
            ("Taxi collectif", ["taxi collectif", "taxis collectifs"]),
            ("Louage", ["louage"]),
            ("Coach / Intercity", ["sntri", "interurbain"])
        ]:
            if any(has_phrase(alltext, x) for x in terms): mode.append(label)
        mode = "; ".join(mode) or "General transport"
        final = score
    elif admin_score >= 30 and not exclusions:
        category = "Administrative geography"
        sub = ["administrative_reference"]
        if any("gouvernorat" in x for x in admin_hits): sub.append("governorates")
        if any("délégation" in x or "delegation" in x for x in admin_hits): sub.append("delegations")
        if any("municipalité" in x or "municipalite" in x for x in admin_hits): sub.append("municipalities")
        if any(any(y in x for y in ["limite", "frontière", "frontiere", "boundary"]) for x in admin_hits): sub.append("boundary_candidate")
        mode = "Administrative reference"
        final = admin_score
    elif geo_score >= 12 and not exclusions:
        category = "Useful geography"
        sub = ["geographic_reference"]
        mode = "Geographic reference"
        final = geo_score
    else:
        category = "Other"
        sub = []
        mode = "Not classified"
        final = max(score, admin_score, geo_score)
    govs = gov_matches(alltext)
    return {
        "category": category, "subcategories": sub, "mode": mode, "relevance_score": final,
        "relevance": "Very high" if final >= 55 else "High" if final >= 32 else "Medium" if final >= 20 else "Low",
        "governorates": govs, "coverage_confidence": "Metadata mention only" if govs else "Not identified",
        "excluded_topic_matches": exclusions,
        "classification_evidence": evidence + ["admin:" + x for x in admin_hits] + ["geo:" + x for x in geo_hits]
    }

def sniff_bytes(head, path=None, content_type=""):
    h = head.lstrip(b"\xef\xbb\xbf\x00\t\r\n ")
    if head.startswith(b"PK\x03\x04"):
        if path:
            try:
                with zipfile.ZipFile(path) as z:
                    names = {n.replace("\\", "/").lower() for n in z.namelist() if not n.endswith("/")}
                    bases = {Path(n).name for n in names}
                    if "[content_types].xml" in bases and any(n.startswith("xl/") for n in names): return "XLSX"
                    if GTFS_REQUIRED.issubset(bases): return "GTFS-ZIP"
                    if any(n.endswith(".shp") for n in names): return "SHAPEFILE-ZIP"
                    if any(n.endswith((".geojson", ".json")) for n in names): return "GEOJSON-ZIP"
            except Exception:
                return "CORRUPT-ZIP"
        return "ZIP"
    if head.startswith(b"Rar!\x1a\x07"): return "RAR"
    if head.startswith(b"%PDF-"): return "PDF"
    if head.startswith(bytes.fromhex("D0CF11E0A1B11AE1")): return "XLS"
    if head.startswith(b"SQLite format 3\x00"): return "SQLITE/GPKG"
    if h.startswith((b"{", b"[")):
        try:
            obj = json.loads(h.decode("utf-8-sig"))
            if isinstance(obj, dict) and obj.get("type") in {"FeatureCollection", "Feature", "GeometryCollection"}: return "GEOJSON"
            return "JSON"
        except Exception:
            pass
    try:
        sample = h.decode("utf-8-sig")
        if len(sample.splitlines()) >= 2 and any(d in sample for d in [",", ";", "\t", "|"]): return "CSV"
    except Exception:
        pass
    ct = norm(content_type)
    if "json" in ct: return "JSON"
    if "csv" in ct: return "CSV"
    if "excel" in ct or "spreadsheet" in ct: return "XLSX"
    if "pdf" in ct: return "PDF"
    if "html" in ct: return "HTML"
    if "xml" in ct: return "XML"
    return "UNKNOWN"

def sniff_file(path, content_type=""):
    with open(path, "rb") as f:
        head = f.read(16384)
    return sniff_bytes(head, path, content_type)

def detect_encoding(sample):
    for enc in ("utf-8-sig", "cp1252", "cp1256", "latin-1"):
        try:
            text = sample.decode(enc)
            if "\ufffd" not in text and text.count("\x00") < 2:
                return enc
        except UnicodeDecodeError:
            continue
    return "utf-8"

def csv_info(path, limit=CSV_ROW_LIMIT):
    sample = Path(path).read_bytes()[:256000]
    enc = detect_encoding(sample)
    text = sample.decode(enc, errors="replace")
    try:
        delimiter = csv.Sniffer().sniff(text, delimiters=",;\t|").delimiter
    except Exception:
        counts = {d: text.count(d) for d in [",", ";", "\t", "|"]}
        delimiter = max(counts, key=counts.get) if max(counts.values()) else ","
    with open(path, "r", encoding=enc, errors="replace", newline="") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        headers = reader.fieldnames or []
        if not headers: raise ValueError("CSV has no header row")
        if len(set(headers)) != len(headers): raise ValueError("CSV contains duplicate column names")
        count = 0
        def rows():
            nonlocal count
            for row in reader:
                count += 1
                yield row
        return headers, enc, delimiter, rows(), lambda: count

def inspect_geojson_obj(obj):
    typ = obj.get("type") if isinstance(obj, dict) else None
    if typ == "FeatureCollection": features = obj.get("features", [])
    elif typ == "Feature": features = [obj]
    else: features = []
    geom = Counter(); props = Counter(); bounds = [float("inf"), float("inf"), float("-inf"), float("-inf")]; points = 0
    def walk(c):
        nonlocal points
        if isinstance(c, (list, tuple)) and len(c) >= 2 and isinstance(c[0], (int, float)) and isinstance(c[1], (int, float)):
            x, y = float(c[0]), float(c[1])
            bounds[0] = min(bounds[0], x); bounds[1] = min(bounds[1], y)
            bounds[2] = max(bounds[2], x); bounds[3] = max(bounds[3], y)
            points += 1
        elif isinstance(c, (list, tuple)):
            for x in c: walk(x)
    if typ == "GeometryCollection":
        geoms = obj.get("geometries", [])
        for g in geoms: geom[g.get("type", "null")] += 1; walk(g.get("coordinates", []))
        feature_count = len(geoms)
    else:
        for f in features:
            g = f.get("geometry") or {}
            geom[g.get("type", "null")] += 1
            walk(g.get("coordinates", []))
            props.update((f.get("properties") or {}).keys())
        feature_count = len(features)
    bbox = bounds if points else None
    plausible = bool(bbox and 7.0 <= bbox[0] <= 12.5 and 30.0 <= bbox[1] <= 38.0 and 7.0 <= bbox[2] <= 12.5 and 30.0 <= bbox[3] <= 38.0)
    return {
        "geojson_type": typ, "feature_count": feature_count, "geometry_types": dict(geom),
        "property_names": sorted(props), "coordinate_count": points, "bbox_lonlat": bbox,
        "geographic_extent_verified": plausible
    }


class DeepSQLiteStore:
    """
    Enhanced Deep SQLite & React Native Fixture Engine (v3.6).
    Now includes robust route extraction from non-GTFS CSV transport files and GeoJSON line/route features,
    along with full debug tracing and SQL metrics.
    """
    def __init__(self, out_dir: Path):
        self.out_dir = out_dir
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.out_dir / "tunisia_mobility.db"
        self.fixtures_dir = self.out_dir / "react_native_fixtures"
        self.fixtures_dir.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_schema(self):
        conn = self._connect()
        cur = conn.cursor()
        cur.executescript("""
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

    def get_counts(self) -> dict:
        if not self.db_path.exists():
            return {"stops": 0, "routes": 0, "trips": 0, "stop_times": 0}
        conn = self._connect()
        cur = conn.cursor()
        res = {}
        for key, tbl in [("stops", "stops_registry"), ("routes", "routes_registry"), ("trips", "trips_registry"), ("stop_times", "stop_times_registry")]:
            cur.execute(f"SELECT COUNT(*) FROM {tbl}")
            res[key] = cur.fetchone()[0]
        conn.close()
        return res

    def register_source(self, source_id: str, name: str, source_type: str, url: str, license_str: str, content_hash: str):
        conn = self._connect()
        conn.execute(
            "INSERT OR REPLACE INTO dataset_sources (source_id, name, source_type, url, license, content_hash, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (source_id, name, source_type, url, license_str, content_hash, "INGESTED")
        )
        conn.commit()
        conn.close()

    def ingest_csv_bytes(self, raw_bytes: bytes, source_id: str) -> dict:
        text = None
        for enc in ("utf-8-sig", "utf-8", "cp1256", "latin-1"):
            try:
                text = raw_bytes.decode(enc)
                break
            except Exception:
                continue
        if not text:
            return {"stops": 0, "routes": 0}
        try:
            dialect = csv.Sniffer().sniff(text[:4096], delimiters=",;\t|")
        except Exception:
            dialect = csv.excel
        reader = csv.DictReader(io.StringIO(text), dialect=dialect)
        if not reader.fieldnames:
            return {"stops": 0, "routes": 0}
        
        headers = {h.strip().lower(): h for h in reader.fieldnames if h}
        lat_col = next((headers[k] for k in headers if k in {"stop_lat", "lat", "latitude", "y", "coord_y"}), None)
        lon_col = next((headers[k] for k in headers if k in {"stop_lon", "lon", "lng", "longitude", "x", "coord_x"}), None)
        name_col = next((headers[k] for k in headers if k in {"stop_name", "name", "nom", "libelle", "arret", "station", "title"}), None)
        id_col = next((headers[k] for k in headers if k in {"stop_id", "id", "code", "code_arret"}), None)

        # Route / Line headers in CSV transport files
        route_id_col = next((headers[k] for k in headers if k in {"route_id", "ligne", "line", "code_ligne", "itineraire", "route_short_name"}), None)
        route_name_col = next((headers[k] for k in headers if k in {"route_long_name", "nom_ligne", "libelle_ligne", "destination", "description_ligne"}), None)

        stops_batch = []
        routes_batch = []

        for idx, row in enumerate(reader):
            if idx >= CSV_ROW_LIMIT:
                break
            # 1. Parse Stop if coords present
            if lat_col and lon_col:
                try:
                    lat = float(str(row.get(lat_col, "")).replace(",", ".").strip())
                    lon = float(str(row.get(lon_col, "")).replace(",", ".").strip())
                    if valid_tn_coord(lon, lat):
                        sname = str(row.get(name_col) or f"Stop {idx+1}").strip()
                        sid = str(row.get(id_col) or f"{source_id}_csv_{idx}_{round(lat,5)}_{round(lon,5)}").strip()
                        gov = nearest_governorate(lon, lat)
                        stops_batch.append((sid, source_id, sname, sname, "CSV_STOP", gov, lon, lat, "VERIFIED_GEO"))
                except Exception as e:
                    logger.debug(f"CSV stop parse error at row {idx}: {e}")

            # 2. Parse Route if route/line identifiers present
            if route_id_col or route_name_col:
                try:
                    rid = str(row.get(route_id_col) if route_id_col else f"{source_id}_route_{idx}").strip()
                    rshort = str(row.get(route_id_col) or "").strip()
                    rlong = str(row.get(route_name_col) or row.get(route_id_col) or f"Route {idx+1}").strip()
                    if rid:
                        full_rid = f"{source_id}_{rid}"
                        routes_batch.append((full_rid, source_id, "BUS", rshort, rlong, "Tunis", "ACTIVE"))
                except Exception as e:
                    logger.debug(f"CSV route parse error at row {idx}: {e}")

        conn = self._connect()
        cur = conn.cursor()
        if stops_batch:
            cur.executemany(
                "INSERT OR REPLACE INTO stops_registry (stop_id, source_id, name_ar, name_fr, stop_type, governorate, lon, lat, verification_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                stops_batch
            )
        if routes_batch:
            cur.executemany(
                "INSERT OR REPLACE INTO routes_registry (route_id, operator_id, mode_code, short_name, long_name, governorate, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                routes_batch
            )
        conn.commit()
        conn.close()
        logger.info(f"Ingested CSV [{source_id}]: +{len(stops_batch)} stops, +{len(routes_batch)} routes")
        return {"stops": len(stops_batch), "routes": len(routes_batch)}

    def ingest_geojson_obj(self, obj: dict, source_id: str) -> dict:
        features = obj.get("features", []) if isinstance(obj, dict) and obj.get("type") == "FeatureCollection" else ([obj] if isinstance(obj, dict) and obj.get("type") == "Feature" else [])
        stops_batch = []
        routes_batch = []

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
                        stops_batch.append((sid, source_id, name, name, "GEOJSON_POINT", gov, lon, lat, "VERIFIED_GEO"))
                except Exception as e:
                    logger.debug(f"GeoJSON point parse error at feature {idx}: {e}")
            elif gtype in {"LineString", "MultiLineString"} and coords:
                try:
                    rid = str(props.get("id") or props.get("route_id") or props.get("ligne") or f"{source_id}_line_{idx}")
                    name = str(props.get("name") or props.get("nom") or props.get("ligne") or f"Line {idx+1}")
                    full_rid = f"{source_id}_{rid}"
                    routes_batch.append((full_rid, source_id, "BUS", name, name, "Tunis", "ACTIVE"))
                except Exception as e:
                    logger.debug(f"GeoJSON line parse error at feature {idx}: {e}")

        conn = self._connect()
        cur = conn.cursor()
        if stops_batch:
            cur.executemany(
                "INSERT OR REPLACE INTO stops_registry (stop_id, source_id, name_ar, name_fr, stop_type, governorate, lon, lat, verification_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                stops_batch
            )
        if routes_batch:
            cur.executemany(
                "INSERT OR REPLACE INTO routes_registry (route_id, operator_id, mode_code, short_name, long_name, governorate, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                routes_batch
            )
        conn.commit()
        conn.close()
        logger.info(f"Ingested GeoJSON [{source_id}]: +{len(stops_batch)} stops, +{len(routes_batch)} routes")
        return {"stops": len(stops_batch), "routes": len(routes_batch)}

    def ingest_gtfs_or_zip(self, zip_path: Path, source_id: str) -> dict:
        counts = {"stops": 0, "routes": 0, "trips": 0, "stop_times": 0}
        conn = self._connect()
        cur = conn.cursor()
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
                        cur.executemany(
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
                        cur.executemany(
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
                        cur.executemany(
                            "INSERT OR REPLACE INTO trips_registry (trip_id, route_id, service_id, headsign, direction_id, source_id) VALUES (?, ?, ?, ?, ?, ?)",
                            batch
                        )
                        counts["trips"] += len(batch)

                # 4. stop_times.txt
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
                        cur.executemany(
                            "INSERT INTO stop_times_registry (trip_id, stop_id, stop_sequence, arrival_time, departure_time, source_id) VALUES (?, ?, ?, ?, ?, ?)",
                            batch
                        )
                        counts["stop_times"] += len(batch)

                # Nested files
                if "stops.txt" not in names and "routes.txt" not in names:
                    for fname, full_name in names.items():
                        if fname.endswith(".csv"):
                            res = self.ingest_csv_bytes(z.read(full_name), source_id)
                            counts["stops"] += res["stops"]
                            counts["routes"] += res["routes"]
                        elif fname.endswith((".geojson", ".json")):
                            try:
                                obj = json.loads(z.read(full_name).decode("utf-8-sig", errors="ignore"))
                                res = self.ingest_geojson_obj(obj, source_id)
                                counts["stops"] += res["stops"]
                                counts["routes"] += res["routes"]
                            except Exception:
                                pass
            conn.commit()
        finally:
            conn.close()
        return counts

    def export_react_native_fixtures(self) -> dict:
        conn = self._connect()
        cur = conn.cursor()

        cur.execute("SELECT governorate, COUNT(*) FROM stops_registry GROUP BY governorate ORDER BY COUNT(*) DESC")
        gov_stop_counts = dict(cur.fetchall())

        cur.execute("SELECT stop_id, name_ar, name_fr, stop_type, governorate, lon, lat, verification_status FROM stops_registry LIMIT 10000")
        stops_export = [
            {
                "id": r[0], "name_ar": r[1], "name_fr": r[2],
                "type": r[3], "governorate": r[4], "lon": r[5], "lat": r[6], "status": r[7]
            }
            for r in cur.fetchall()
        ]

        cur.execute("SELECT route_id, operator_id, mode_code, short_name, long_name, governorate FROM routes_registry LIMIT 5000")
        routes_export = [
            {
                "id": r[0], "operator": r[1], "mode": r[2],
                "short_name": r[3], "long_name": r[4], "governorate": r[5]
            }
            for r in cur.fetchall()
        ]
        conn.close()

        (self.fixtures_dir / "governorate_coverage.json").write_text(
            json.dumps({"generated_at": now_iso(), "stops_by_governorate": gov_stop_counts}, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        (self.fixtures_dir / "stops_fixture.json").write_text(
            json.dumps(stops_export, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        (self.fixtures_dir / "routes_fixture.json").write_text(
            json.dumps(routes_export, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        return {"stops_exported": len(stops_export), "routes_exported": len(routes_export), "fixtures_dir": str(self.fixtures_dir)}


class RecoveryEngine:
    def __init__(self, out_dir, events, stop_event):
        self.root = Path(out_dir)
        self.out = self.root / ("run_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
        self.events = events
        self.stop = stop_event
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self.datasets = {}
        self.resources = {}
        self.stats = Counter()
        self.quality = []
        self.gtfs = []
        self.extractions = []
        self.started = time.time()
        self.stamp = now_iso()
        self.host_status = {}
        self.seen_hashes = {}
        self.map_features = []
        self.deep_db = DeepSQLiteStore(self.out)

    def emit(self, kind, **kw): self.events.put({"kind": kind, **kw})
    def log(self, level, msg):
        logger.info(f"[{level}] {msg}")
        self.emit("log", level=level, message=msg)

    def _emit_db_metrics(self):
        c = self.deep_db.get_counts()
        self.stats["db_stops"] = c["stops"]
        self.stats["db_routes"] = c["routes"]
        self.stats["db_trips"] = c["trips"]
        self.stats["db_stop_times"] = c["stop_times"]
        self.emit("db_metrics", counts=c)

    def api(self, action, params=None, timeout=25):
        if self.stop.is_set(): return None
        try:
            r = self.session.get(f"{CKAN_BASE}/{action}", params=params or {}, timeout=(8, timeout))
            r.raise_for_status()
            j = r.json()
            if j.get("success"): return j.get("result")
            self.stats["api_errors"] += 1
        except Exception as e:
            self.stats["api_errors"] += 1
            self.log("WARN", f"CKAN {action}: {str(e)[:150]}")
        return None

    def load_21_exports(self, folder):
        folder = Path(folder)
        p = folder / "resources.json"
        if not p.exists(): raise FileNotFoundError(f"resources.json not found in {folder}")
        rows = json.loads(p.read_text(encoding="utf-8-sig"))
        self.resources = {str(r.get("id") or r.get("url") or i): r for i, r in enumerate(rows)}
        q = folder / "datasets.json"
        if q.exists():
            try: self.datasets = {str(d.get("id") or i): d for i, d in enumerate(json.loads(q.read_text(encoding="utf-8-sig")))}
            except Exception: pass
        q = folder / "quality_issues.json"
        if q.exists():
            try: self.quality = json.loads(q.read_text(encoding="utf-8-sig"))
            except Exception: pass
        self.stats["imported_resources"] = len(self.resources)
        self.stats["imported_datasets"] = len(self.datasets)
        manifest = folder / "download_manifest.json"
        if manifest.exists():
            try:
                for item in json.loads(manifest.read_text(encoding="utf-8-sig")):
                    if item.get("sha256") and item.get("local_path"):
                        self.seen_hashes[item["sha256"]] = item["local_path"]
            except Exception:
                pass
        self.log("SUCCESS", f"Imported {len(self.resources)} resource records; discovery not repeated")
        self.reanalyse_resources()
        self.inspect_existing_downloads()

    def discover(self):
        terms = list(dict.fromkeys(OPERATORS + TRANSPORT_TERMS + GEO_TERMS))
        for gov in GOVERNORATES:
            terms.extend([f"transport {gov} Tunisie", f"données géographiques {gov}"])
        terms = list(dict.fromkeys(terms))
        self.emit("stage", name="Nationwide catalogue discovery", detail=f"{len(terms)} queries · all 24 governorates")
        found = {}
        total = len(terms)
        for i, term in enumerate(terms, 1):
            if self.stop.is_set(): break
            start = 0
            for _ in range(MAX_PAGES_PER_QUERY):
                result = self.api("package_search", {"q": term, "rows": 100, "start": start})
                if not result: break
                items = result.get("results", []) or []
                count = int(result.get("count") or 0)
                for d in items:
                    if d.get("id"): found[d["id"]] = d
                self.stats["search_pages"] += 1
                if not items or start + len(items) >= count: break
                start += len(items)
            self.stats["searches"] += 1
            if i % 5 == 0 or i == total:
                self.emit("progress", value=12 * i / total, detail=f"Searching {i}/{total}: {term}")
        self.datasets.update(found)
        self.stats["datasets_found"] = len(found)
        self.log("SUCCESS", f"Found {len(found)} unique datasets")
        ids = list(found)
        self.stats["dataset_details_ok"] = 0
        self.stats["dataset_details_failed"] = 0
        for i, did in enumerate(ids, 1):
            if self.stop.is_set(): break
            detail = self.api("package_show", {"id": did})
            if detail:
                self.stats["dataset_details_ok"] += 1
                self.datasets[did] = detail
                org = (detail.get("organization") or {}).get("title", "")
                lic = detail.get("license_title") or detail.get("license_id") or "Unknown"
                for raw in detail.get("resources", []) or []:
                    rid = str(raw.get("id") or raw.get("url") or "")
                    if not rid: continue
                    row = dict(raw)
                    row.update({"dataset_id": did, "dataset_title": detail.get("title", ""), "dataset_notes": detail.get("notes", ""), "organization": org, "license": lic, "retrieved_at": self.stamp})
                    if rid not in self.resources:
                        self.resources[rid] = row
                    else:
                        for k, v in row.items():
                            if self.resources[rid].get(k) in (None, "", []):
                                self.resources[rid][k] = v
            else:
                self.stats["dataset_details_failed"] += 1
            if i % 10 == 0 or i == len(ids):
                self.emit("progress", value=12 + 28 * i / max(1, len(ids)), detail=f"Dataset details {i}/{len(ids)}")
        self.stats["dataset_details_attempted"] = self.stats["dataset_details_ok"] + self.stats["dataset_details_failed"]
        self.stats["resources_found"] = len(self.resources)
        self.log("SUCCESS", f"Indexed {len(self.resources)} resources")
        self.reanalyse_resources()

    def reanalyse_resources(self):
        self.emit("stage", name="Evidence-based classification", detail="Separating transport, administrative references, useful geography and unrelated resources")
        counts = Counter()
        for i, r in enumerate(self.resources.values(), 1):
            r.setdefault("v2_original_category", r.get("category"))
            r.setdefault("v2_original_relevance_score", r.get("relevance_score"))
            result = classify_resource(r)
            r.update(result)
            r["host"] = urlparse(str(r.get("url") or "")).hostname or ""
            r.setdefault("download_status", "Not attempted")
            r.setdefault("validation_status", "Not inspected")
            counts[result["category"]] += 1
            if i % 100 == 0:
                self.emit("progress", value=42 + 8 * i / max(1, len(self.resources)), detail=f"Classifying {i}/{len(self.resources)}")
        self.stats.update({"category_" + k.lower().replace(" ", "_"): v for k, v in counts.items()})
        self.emit("metrics", counts=dict(counts), datasets=len(self.datasets), resources=len(self.resources))
        self.log("INFO", f"Classification: {dict(counts)}")

    def inspect_existing_downloads(self):
        existing = [r for r in self.resources.values() if r.get("local_path") and Path(str(r["local_path"])).is_file()]
        self.emit("stage", name="Inspecting existing downloads & extracting to SQLite", detail=f"{len(existing)} existing files")
        for i, r in enumerate(existing, 1):
            if self.stop.is_set(): break
            try:
                p = Path(str(r["local_path"]))
                digest = r.get("sha256") or sha256_file(p)
                r["sha256"] = digest
                self.seen_hashes.setdefault(digest, str(p))
                r["detected_format"] = sniff_file(p)
                self.inspect_resource_file(p, r)
                self.stats["existing_files_inspected"] += 1
            except Exception as e:
                self.quality.append({"resource_id": r.get("id"), "local_path": r.get("local_path"), "error": str(e)})
            if i % 10 == 0 or i == len(existing):
                self.emit("progress", value=50 + 10 * i / max(1, len(existing)), detail=f"Existing files {i}/{len(existing)}")
        self.stats["missing_local_files"] = sum(1 for r in self.resources.values() if r.get("local_path") and not Path(str(r["local_path"])).is_file())

    def host_check(self, host, scheme="https"):
        if not host or host in KNOWN_UNREACHABLE_HOSTS: return False
        key = f"{scheme}://{host}"
        if key in self.host_status: return self.host_status[key]
        try:
            self.session.get(f"{scheme}://{host}/", timeout=(3, 4), allow_redirects=True, stream=True).close()
            ok = True
        except Exception:
            ok = False
        self.host_status[key] = ok
        return ok

    def _filename(self, r, response, idx):
        disp = response.headers.get("content-disposition", "")
        name = ""
        if disp:
            m = Message()
            m["content-disposition"] = disp
            name = m.get_filename() or ""
        if not name:
            name = r.get("name") or Path(urlparse(response.url).path).name
        return safe_name(name or f"resource_{idx}")

    def recover(self, max_items=500):
        candidates = [
            r for r in self.resources.values()
            if r.get("category") in {"Transport", "Administrative geography", "Useful geography"}
            and r.get("relevance_score", 0) >= 18
            and r.get("url")
            and not (r.get("local_path") and Path(str(r["local_path"])).is_file())
        ]
        candidates.sort(key=lambda r: (r.get("category") == "Transport", r.get("relevance_score", 0)), reverse=True)
        self.emit("stage", name="Resource recovery & deep SQLite extraction", detail=f"{len(candidates)} candidates · max {max_items}")
        base = self.out / "raw"
        base.mkdir(parents=True, exist_ok=True)
        for i, r in enumerate(candidates[:max_items], 1):
            if self.stop.is_set(): break
            urls = list(dict.fromkeys([str(r.get("url") or ""), str(r.get("cache_url") or "")]))
            urls = [u for u in urls if u.startswith(("http://", "https://"))]
            if not urls:
                r["download_status"] = "Skipped · no valid URL"
                continue
            url = urls[0]
            host = urlparse(url).hostname or ""
            if host in KNOWN_UNREACHABLE_HOSTS and len(urls) > 1 and urlparse(urls[1]).hostname not in KNOWN_UNREACHABLE_HOSTS:
                url = urls[1]; host = urlparse(url).hostname or ""; r["recovery_url_source"] = "CKAN cache_url"
            if host in KNOWN_UNREACHABLE_HOSTS:
                r["download_status"] = "Blocked · known unreachable source host"
                self.stats["blocked_unreachable"] += 1
                continue
            if not self.host_check(host, urlparse(url).scheme):
                if len(urls) > 1 and url != urls[1] and urlparse(urls[1]).hostname not in KNOWN_UNREACHABLE_HOSTS and self.host_check(urlparse(urls[1]).hostname or "", urlparse(urls[1]).scheme):
                    url = urls[1]; host = urlparse(url).hostname or ""; r["recovery_url_source"] = "CKAN cache_url"
                else:
                    r["download_status"] = "Host probe failed · not retried"
                    self.stats["host_probe_failed"] += 1
                    continue
            tmp = None
            try:
                with self.session.get(url, timeout=(8, 35), stream=True, allow_redirects=True) as resp:
                    resp.raise_for_status()
                    finalhost = urlparse(resp.url).hostname or ""
                    if finalhost in KNOWN_UNREACHABLE_HOSTS:
                        raise RuntimeError("Redirected to known unreachable host")
                    length = int(resp.headers.get("content-length") or 0)
                    if length > MAX_FILE_MB * 1024 * 1024:
                        raise RuntimeError("File exceeds size limit")
                    folder = base / {"Transport": "transport", "Administrative geography": "admin_geography", "Useful geography": "useful_geography"}[r["category"]]
                    folder.mkdir(parents=True, exist_ok=True)
                    suggested = self._filename(r, resp, i)
                    tmp = folder / (safe_name(r.get("id") or str(i)) + ".part")
                    size = 0
                    h = hashlib.sha256()
                    with tmp.open("wb") as f:
                        for chunk in resp.iter_content(128 * 1024):
                            if self.stop.is_set(): break
                            if chunk:
                                size += len(chunk)
                                if size > MAX_FILE_MB * 1024 * 1024:
                                    raise RuntimeError("Streaming size limit exceeded")
                                f.write(chunk)
                                h.update(chunk)
                    if self.stop.is_set():
                        tmp.unlink(missing_ok=True)
                        r["download_status"] = "Stopped"
                        continue
                    digest = h.hexdigest()
                    if digest in self.seen_hashes:
                        tmp.unlink(missing_ok=True)
                        r.update({"sha256": digest, "duplicate_of": self.seen_hashes[digest], "download_status": "Duplicate content"})
                        self.stats["duplicates"] += 1
                        continue
                    fmt = sniff_file(tmp, resp.headers.get("content-type", ""))
                    ext = {"GTFS-ZIP": ".zip", "SHAPEFILE-ZIP": ".zip", "GEOJSON-ZIP": ".zip", "ZIP": ".zip", "CORRUPT-ZIP": ".zip", "RAR": ".rar", "GEOJSON": ".geojson", "JSON": ".json", "CSV": ".csv", "PDF": ".pdf", "XLS": ".xls", "XLSX": ".xlsx", "SQLITE/GPKG": ".gpkg", "HTML": ".html", "XML": ".xml"}.get(fmt, Path(suggested).suffix or ".bin")
                    final = folder / (safe_name(r.get("id") or str(i)) + "_" + safe_name(Path(suggested).stem) + ext)
                    n = 2
                    while final.exists():
                        final = folder / (safe_name(r.get("id") or str(i)) + "_" + safe_name(Path(suggested).stem) + f"_{n}" + ext)
                        n += 1
                    tmp.replace(final)
                    tmp = None
                    r.update({"sha256": digest, "detected_format": fmt, "local_path": str(final), "bytes_downloaded": size, "final_url": resp.url, "download_status": "Downloaded"})
                    self.seen_hashes[digest] = str(final)
                    self.stats["downloaded"] += 1
                    self.stats["bytes_downloaded"] += size
                    self.inspect_resource_file(final, r)
                    self.emit("metric", name="inspected")
                    self.log("SUCCESS", f"Downloaded & Parsed {fmt}: {final.name}")
            except Exception as e:
                if tmp and tmp.exists(): tmp.unlink(missing_ok=True)
                r["download_status"] = "Failed · " + str(e)[:160]
                self.stats["failed"] += 1
                self.log("WARN", f"Download failed {r.get('name')}: {str(e)[:120]}")
            if i % 5 == 0 or i == min(max_items, len(candidates)):
                self.emit("progress", value=50 + 35 * i / max(1, min(max_items, len(candidates))), detail=f"Recovery & DB Ingestion {i}/{min(max_items, len(candidates))}")

    def inspect_resource_file(self, path, r):
        path = Path(path)
        meta = {
            "resource_id": r.get("id"),
            "dataset_id": r.get("dataset_id"),
            "dataset_title": r.get("dataset_title"),
            "path": str(path),
            "format": "UNKNOWN",
            "validation_status": "Not inspected",
            "inspection_errors": [],
            "extracted_rows": 0,
            "extracted_features": 0,
            "db_records_added": 0,
        }

        def record_error(message):
            meta["inspection_errors"].append(str(message))

        def validate_geojson(obj):
            if not isinstance(obj, dict): return False
            geo_type = obj.get("type")
            if geo_type == "FeatureCollection":
                features = obj.get("features")
                return isinstance(features, list) and all(isinstance(f, dict) and f.get("type") == "Feature" for f in features)
            if geo_type == "Feature": return "geometry" in obj
            if geo_type == "GeometryCollection": return isinstance(obj.get("geometries"), list)
            return False

        try:
            fmt = sniff_file(path)
        except Exception as exc:
            fmt = "UNKNOWN"
            record_error(f"Format detection failed: {exc}")

        meta["format"] = fmt
        r["detected_format"] = fmt
        valid = False

        src_slug = safe_name(f"{str(r.get('dataset_id') or 'src')[:24]}_{str(r.get('id') or path.stem)[:12]}")
        self.deep_db.register_source(
            src_slug,
            str(r.get("dataset_title") or path.name),
            fmt,
            str(r.get("url") or str(path)),
            str(r.get("license") or "Unknown"),
            str(r.get("sha256") or "")
        )

        if fmt in {"ZIP", "GTFS-ZIP", "SHAPEFILE-ZIP", "GEOJSON-ZIP"}:
            try:
                with zipfile.ZipFile(path, "r") as z:
                    bad_member = z.testzip()
                    if bad_member:
                        record_error(f"ZIP integrity check failed at {bad_member}")
                        meta["validation_status"] = "Invalid ZIP archive"
                    else:
                        files = [n for n in z.namelist() if not n.endswith("/")]
                        normalized = {n.replace("\\", "/").lower() for n in files}
                        basenames = {Path(n.replace("\\", "/")).name.lower() for n in files}
                        if "[content_types].xml" in basenames and any(n.startswith("xl/") for n in normalized):
                            meta["format"] = "XLSX"; r["detected_format"] = "XLSX"
                            meta["validation_status"] = "Valid XLSX workbook"; valid = True
                        else:
                            db_res = self.deep_db.ingest_gtfs_or_zip(path, src_slug)
                            added = sum(db_res.values())
                            meta["db_records_added"] = added
                            if GTFS_REQUIRED.issubset(basenames):
                                meta["format"] = "GTFS-ZIP"; r["detected_format"] = "GTFS-ZIP"
                                meta["validation_status"] = f"GTFS DB Ingested · +{db_res['stops']} stops, +{db_res['routes']} routes"
                                self.log("SUCCESS", f"GTFS -> SQLite [{path.name}]: +{db_res['stops']} stops, +{db_res['routes']} routes")
                            else:
                                meta["validation_status"] = f"Valid ZIP · +{added} DB records" if added else "Valid ZIP archive"
                            valid = True
            except Exception as exc:
                meta["validation_status"] = "Invalid ZIP archive"
                record_error(f"ZIP inspection failed: {exc}")

        elif fmt in {"GEOJSON", "JSON"}:
            try:
                obj = json.loads(path.read_bytes().decode("utf-8-sig"))
                if validate_geojson(obj):
                    meta["format"] = "GEOJSON"
                    r["detected_format"] = "GEOJSON"
                    geo_info = inspect_geojson_obj(obj)
                    db_res = self.deep_db.ingest_geojson_obj(obj, src_slug)
                    added = sum(db_res.values())
                    meta["extracted_features"] = geo_info["feature_count"]
                    meta["db_records_added"] = added
                    meta["validation_status"] = f"Valid GeoJSON · {geo_info['feature_count']} features" + (f" · +{added} DB records" if added else "")
                    valid = True
                    feats = obj.get("features", []) if obj.get("type") == "FeatureCollection" else ([obj] if obj.get("type") == "Feature" else [])
                    for f in feats[:400]:
                        geom = f.get("geometry") or {}
                        gtype = geom.get("type")
                        coords = geom.get("coordinates")
                        props = f.get("properties") or {}
                        label = next((str(props[k]) for k in props if any(t in k.lower() for t in ["name", "nom", "stop", "station", "gare", "ligne", "lib"]) and props[k]), path.stem)
                        if gtype == "Point" and isinstance(coords, list) and len(coords) >= 2:
                            self.map_features.append({"type": "Point", "coords": [(float(coords[0]), float(coords[1]))], "label": label, "category": r.get("category", "Other"), "source": path.name})
                        elif gtype in {"LineString", "MultiLineString", "Polygon"} and coords:
                            pts = coords if gtype == "LineString" else (coords[0] if coords and isinstance(coords[0], list) else [])
                            clean_pts = [(float(c[0]), float(c[1])) for c in pts[:120] if isinstance(c, (list, tuple)) and len(c) >= 2]
                            if len(clean_pts) >= 2:
                                self.map_features.append({"type": "Line", "coords": clean_pts, "label": label, "category": r.get("category", "Other"), "source": path.name})
                else:
                    meta["validation_status"] = "Valid JSON · not GeoJSON"
            except Exception as exc:
                meta["validation_status"] = "Invalid JSON"
                record_error(f"JSON inspection failed: {exc}")

        elif fmt == "CSV":
            try:
                raw_b = path.read_bytes()
                db_res = self.deep_db.ingest_csv_bytes(raw_b, src_slug)
                added = sum(db_res.values())
                headers, enc, delimiter, rows_iter, _ = csv_info(path)
                low_map = {norm(h): h for h in headers}
                lat_col = next((low_map[k] for k in ["stop_lat", "latitude", "lat", "y"] if k in low_map), None)
                lon_col = next((low_map[k] for k in ["stop_lon", "longitude", "lon", "long", "x"] if k in low_map), None)
                name_col = next((low_map[k] for k in low_map if any(t in k for t in ["name", "nom", "stop", "station", "gare", "ligne"])), None)
                row_cnt = 0
                pts_added = 0
                for row in rows_iter:
                    row_cnt += 1
                    if lat_col and lon_col and pts_added < 400:
                        try:
                            lat_v = float(str(row.get(lat_col, "")).replace(",", "."))
                            lon_v = float(str(row.get(lon_col, "")).replace(",", "."))
                            if valid_tn_coord(lon_v, lat_v):
                                lbl = str(row.get(name_col) or path.stem) if name_col else path.stem
                                self.map_features.append({"type": "Point", "coords": [(lon_v, lat_v)], "label": lbl, "category": r.get("category", "Other"), "source": path.name})
                                pts_added += 1
                        except Exception:
                            pass
                    if row_cnt >= CSV_ROW_LIMIT:
                        break
                meta["extracted_rows"] = row_cnt
                meta["db_records_added"] = added
                meta["validation_status"] = f"CSV · {row_cnt} rows" + (f" · +{added} DB records" if added else "")
                if added:
                    self.log("SUCCESS", f"CSV -> SQLite [{path.name}]: +{db_res['stops']} stops, +{db_res['routes']} routes extracted")
                valid = True
            except Exception as exc:
                meta["validation_status"] = "CSV inspection failed"
                record_error(str(exc))

        elif fmt in {"XLSX", "XLS", "PDF", "SQLITE/GPKG", "RAR"}:
            meta["validation_status"] = f"Valid {fmt} asset"
            valid = True
        else:
            meta["validation_status"] = f"Detected {fmt}"

        if valid:
            self.stats["validated"] += 1

        self._emit_db_metrics()
        r["validation_status"] = meta["validation_status"]
        r["inspection_errors"] = meta["inspection_errors"]
        r["extracted_features"] = meta["extracted_features"]
        r["extracted_rows"] = meta["extracted_rows"]
        r["db_records_added"] = meta["db_records_added"]
        return meta

    def inspect_local_folder(self, folder):
        folder = Path(folder)
        files = [p for p in folder.rglob("*") if p.is_file() and p.suffix.lower() not in {".part", ".pyc"} and self.out not in p.parents]
        self.emit("stage", name="Local file ingestion & deep SQLite extraction", detail=f"Inspecting {len(files)} files; originals remain in place")
        for i, p in enumerate(files, 1):
            if self.stop.is_set(): break
            try:
                rel = p.relative_to(folder)
                parts = [x.lower() for x in rel.parts[:-1]]
                r = {
                    "id": p.stem, "dataset_id": "local_import", "dataset_title": p.parent.name, "name": p.name,
                    "category": "Other", "local_path": str(p), "url": "", "source_type": "local_import",
                    "relative_path": str(rel), "original_filename": p.name, "directory_context": " ".join(parts + [p.stem.lower()])
                }
                r.update(classify_resource(r))
                r["sha256"] = sha256_file(p)
                r["download_status"] = "Existing local file"
                self.resources["local:" + str(p)] = r
                self.inspect_resource_file(p, r)
                self.emit("metric", name="inspected")
            except Exception as e:
                self.quality.append({"file": str(p), "error": str(e)})
            if i % 10 == 0 or i == len(files):
                self.emit("progress", value=90 * i / max(1, len(files)), detail=f"Inspecting local files {i}/{len(files)}")
        self.log("SUCCESS", f"Local inspection & SQLite ingestion completed: {len(files)} files")

    def coverage_report(self):
        result = {}
        rows = list(self.resources.values())
        conn = self.deep_db._connect()
        cur = conn.cursor()
        cur.execute("SELECT governorate, COUNT(*) FROM stops_registry GROUP BY governorate")
        db_stops_by_gov = dict(cur.fetchall())
        conn.close()

        for gov in GOVERNORATES:
            matched = [r for r in rows if gov in (r.get("governorates") or [])]
            db_stops = db_stops_by_gov.get(gov, 0)
            result[gov] = {
                "metadata_matches": len(matched),
                "transport_metadata_matches": sum(r.get("category") == "Transport" for r in matched),
                "administrative_geography_resources": sum(r.get("category") == "Administrative geography" for r in matched),
                "db_extracted_stops": db_stops,
                "evidence": f"{db_stops} verified GPS stops in SQLite" if db_stops else ("Metadata mention only" if matched else "No metadata match found")
            }
        return {
            "scope": "Nationwide Tunisia · all 24 governorates",
            "governorates": result,
            "database_path": str(self.deep_db.db_path),
        }

    def export(self):
        self.out.mkdir(parents=True, exist_ok=True)
        self.emit("stage", name="Generating SQLite & React Native JSON Fixtures", detail="Exporting stops_fixture.json, routes_fixture.json, governorate_coverage.json")
        fixture_stats = self.deep_db.export_react_native_fixtures()
        self.log("SUCCESS", f"Exported React Native fixtures ({fixture_stats['stops_exported']} stops, {fixture_stats['routes_exported']} routes) -> {fixture_stats['fixtures_dir']}")

        def dump(name, obj):
            (self.out / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

        rows = list(self.resources.values())
        datasets = list(self.datasets.values())
        dump("datasets.json", datasets)
        dump("resources.json", rows)
        dump("quality_issues.json", self.quality)
        dump("coverage_by_governorate.json", self.coverage_report())
        for cat, filename in [("Transport", "transport_resources.json"), ("Administrative geography", "administrative_geography.json"), ("Useful geography", "useful_geography.json"), ("Other", "other_resources.json")]:
            dump(filename, [r for r in rows if r.get("category") == cat])

        cols = sorted({k for r in rows for k in r})
        with (self.out / "resources_index.csv").open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)

        db_counts = self.deep_db.get_counts()
        report = {
            "application": APP_TITLE, "version": VERSION, "generated_at": self.stamp,
            "output_run_directory": str(self.out), "sqlite_database": str(self.deep_db.db_path),
            "react_native_fixtures": fixture_stats, "database_record_counts": db_counts,
            "catalogue": CKAN_BASE, "scope": "Nationwide Tunisia; all 24 governorates",
            "datasets": len(datasets), "resources": len(rows),
            "category_counts": dict(Counter(r.get("category", "Other") for r in rows)),
            "downloads": self.stats["downloaded"], "failed": self.stats["failed"],
            "blocked_unreachable": self.stats["blocked_unreachable"], "host_probe_failed": self.stats["host_probe_failed"],
            "duplicates": self.stats["duplicates"], "bytes_downloaded": self.stats["bytes_downloaded"],
            "stopped_by_user": self.stop.is_set()
        }
        dump("recovery_report.json", report)
        manifest = [{"resource_id": r.get("id"), "sha256": r.get("sha256"), "local_path": r.get("local_path"), "url": r.get("url"), "detected_format": r.get("detected_format")} for r in rows if r.get("sha256")]
        dump("download_manifest.json", manifest)
        self.log("SUCCESS", f"All exports & SQLite DB saved to {self.out}")

    def run(self, mode, source=None):
        try:
            self.root.mkdir(parents=True, exist_ok=True)
            self.out.mkdir(parents=True, exist_ok=True)
            if mode == "reanalyse":
                self.load_21_exports(source)
            elif mode == "recover":
                self.emit("stage", name="Connecting to National CKAN", detail="Windows certificate trust store · HTTPS")
                status = self.api("status_show", timeout=20)
                if not status: raise RuntimeError("National CKAN status_show failed")
                self.log("SUCCESS", f"Connected to CKAN {status.get('ckan_version', 'version unknown')}")
                self.discover()
            elif mode == "local":
                self.inspect_local_folder(source)
            if mode in {"reanalyse", "recover"} and not self.stop.is_set():
                self.recover()
            self.export()
            self.emit("done", out_dir=str(self.out), datasets=len(self.datasets), resources=len(self.resources), stats=dict(self.stats), stopped=self.stop.is_set())
        except Exception as e:
            try: self.export()
            except Exception: pass
            self.emit("fatal", message=str(e))


def default_output_dir():
    if os.name == "nt":
        try:
            from ctypes import windll, wintypes
            class GUID(ctypes.Structure):
                _fields_ = [("Data1", wintypes.DWORD), ("Data2", wintypes.WORD), ("Data3", wintypes.WORD), ("Data4", wintypes.BYTE * 8)]
            desktop_guid = GUID(0xB4BFCC3A, 0xDB2C, 0x424C, (wintypes.BYTE * 8)(0xB0, 0x29, 0x7F, 0xE9, 0x9A, 0x87, 0xC6, 0x41))
            path_ptr = ctypes.c_wchar_p()
            if windll.shell32.SHGetKnownFolderPath(ctypes.byref(desktop_guid), 0, None, ctypes.byref(path_ptr)) == 0:
                desktop_path = Path(path_ptr.value)
                windll.ole32.CoTaskMemFree(path_ptr)
                if desktop_path.exists():
                    return desktop_path / "working folder" / "MASARI_Recovery_3_6"
        except Exception:
            pass
    home = Path.home()
    candidates = [home / "Desktop", home / "OneDrive" / "Desktop", home / "OneDrive" / "Bureau", home / "Bureau"]
    desktop = next((p for p in candidates if p.exists()), home / "Desktop")
    return desktop / "working folder" / "MASARI_Recovery_3_6"


class TelemetryCanvas(ctk.CTkCanvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, highlightthickness=0, bd=0, **kwargs)
        self.active = False
        self.phase = 0.0
        self.bind("<Configure>", self._build_grid)
        self._animate()

    def set_active(self, is_active: bool):
        self.active = is_active

    def _build_grid(self, event=None):
        self.delete("static")
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 20 or h < 20: return
        for x in range(0, w, 36): self.create_line(x, 0, x, h, fill="#111C33", width=1, tags="static")
        for y in range(0, h, 36): self.create_line(0, y, w, y, fill="#111C33", width=1, tags="static")
        cy = h // 2
        margin = 28
        pts1 = [margin, cy - 18, w * 0.28, cy - 18, w * 0.34, cy, w * 0.66, cy, w * 0.72, cy + 18, w - margin, cy + 18]
        self.create_line(*pts1, fill="#1C2E4A", width=2, tags="static")
        pts2 = [margin + 40, cy + 24, w * 0.45, cy + 24, w * 0.51, cy + 6, w - margin - 40, cy + 6]
        self.create_line(*pts2, fill="#16253D", width=1.5, dash=(4, 4), tags="static")
        nodes = [
            (margin, cy - 18, "#35C8D0"), (w * 0.28, cy - 18, "#35C8D0"), (w * 0.34, cy, "#45D6A0"),
            (w * 0.50, cy, "#FF7A2F"), (w * 0.66, cy, "#45D6A0"), (w * 0.72, cy + 18, "#35C8D0"), (w - margin, cy + 18, "#35C8D0"),
        ]
        for nx, ny, col in nodes:
            self.create_oval(nx - 4, ny - 4, nx + 4, ny + 4, fill="#0A1020", outline=col, width=2, tags="static")
        cx, d = w * 0.50, 9
        self.create_polygon(cx, cy - d, cx + d, cy, cx, cy + d, cx - d, cy, fill="#1B2A43", outline="#FF7A2F", width=2, tags="static")

    def _animate(self):
        self.delete("dynamic")
        w = self.winfo_width()
        h = self.winfo_height()
        if w > 20 and h > 20:
            speed = 0.045 if self.active else 0.012
            self.phase = (self.phase + speed) % 1.0
            cy = h // 2
            margin = 28
            sx = margin + self.phase * (w - 2 * margin)
            if sx < w * 0.28: sy = cy - 18
            elif sx < w * 0.34: sy = (cy - 18) + ((sx - w * 0.28) / max(1, (w * 0.06))) * 18
            elif sx < w * 0.66: sy = cy
            elif sx < w * 0.72: sy = cy + ((sx - w * 0.66) / max(1, (w * 0.06))) * 18
            else: sy = cy + 18
            glow_col = "#35C8D0" if self.active else "#214D63"
            core_col = "#FF7A2F" if self.active else "#35C8D0"
            if self.active:
                self.create_line(sx, 6, sx, h - 6, fill="#18384A", width=1, dash=(2, 3), tags="dynamic")
            r_outer = 7 + 2.5 * math.sin(self.phase * math.tau * 2) if self.active else 5
            self.create_oval(sx - r_outer, sy - r_outer, sx + r_outer, sy + r_outer, outline=glow_col, width=1.5, tags="dynamic")
            self.create_oval(sx - 3, sy - 3, sx + 3, sy + 3, fill=core_col, outline="", tags="dynamic")
        self.after(33, self._animate)


class SymbolCanvas(ctk.CTkCanvas):
    def __init__(self, master, size=44, **kwargs):
        super().__init__(master, width=size, height=size, highlightthickness=0, bd=0, **kwargs)
        self.size = size
        self.tick = 0.0
        self._draw()

    def _draw(self):
        self.delete("all")
        s = self.size
        c = s / 2.0
        self.tick = (self.tick + 0.04) % math.tau
        pad = 6
        self.create_line(pad, c - 3, pad, pad, c - 3, pad, fill="#35C8D0", width=2.5, capstyle="butt")
        self.create_line(c + 4, pad, s - pad, pad, s - pad, c - 4, fill="#F1F5FA", width=2.5, capstyle="butt")
        self.create_line(s - pad, c + 3, s - pad, s - pad, c + 3, s - pad, fill="#35C8D0", width=2.5, capstyle="butt")
        self.create_line(pad, c + 5, pad, s - pad, c - 5, s - pad, fill="#45D6A0", width=2.0, capstyle="butt")
        pulse = 1.5 * math.sin(self.tick)
        d_outer = 7.5 + pulse
        self.create_polygon(c, c - d_outer, c + d_outer, c, c, c + d_outer, c - d_outer, c, fill="", outline="#6E3B23", width=1)
        d = 5.5
        self.create_polygon(c, c - d, c + d, c, c, c + d, c - d, c, fill="#FF7A2F", outline="")
        self.after(45, self._draw)


class TunisiaMapCanvas(ctk.CTkCanvas):
    def __init__(self, master, on_select_gov=None, **kwargs):
        super().__init__(master, highlightthickness=0, bd=0, **kwargs)
        self.on_select_gov = on_select_gov
        self.gov_stats = {}
        self.features = []
        self.selected_gov = None
        self.hovered_item = None
        self.zoom = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0
        self._drag_start = None
        self.pulse_phase = 0.0
        self.show_govs = True
        self.show_features = True
        self.show_labels = True
        self.bind("<Configure>", lambda e: self.redraw())
        self.bind("<MouseWheel>", self._on_wheel)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Motion>", self._on_hover)
        self._hit_targets = []
        self._animate_pulse()

    def reset_view(self):
        self.zoom = 1.0; self.pan_x = 0.0; self.pan_y = 0.0; self.redraw()

    def set_zoom(self, factor):
        self.zoom = max(0.7, min(8.0, self.zoom * factor)); self.redraw()

    def update_data(self, gov_stats: dict, features: list):
        self.gov_stats = gov_stats or {}; self.features = features or []; self.redraw()

    def _project(self, lon: float, lat: float):
        w = max(100, self.winfo_width()); h = max(100, self.winfo_height())
        min_lon, max_lon = 7.2, 11.9; min_lat, max_lat = 30.0, 37.65; aspect = 0.83
        span_x = (max_lon - min_lon) * aspect; span_y = (max_lat - min_lat); pad = 36.0
        scale = min((w - 2 * pad) / span_x, (h - 2 * pad) / span_y) * self.zoom
        cx = w / 2.0 + self.pan_x; cy = h / 2.0 + self.pan_y
        mid_lon = (min_lon + max_lon) / 2.0; mid_lat = (min_lat + max_lat) / 2.0
        return cx + (lon - mid_lon) * aspect * scale, cy - (lat - mid_lat) * scale

    def _on_wheel(self, event):
        factor = 1.18 if event.delta > 0 else (1.0 / 1.18)
        self.zoom = max(0.7, min(8.0, self.zoom * factor)); self.redraw()

    def _on_press(self, event):
        self._drag_start = (event.x, event.y, self.pan_x, self.pan_y)
        self._pressed_pos = (event.x, event.y)

    def _on_drag(self, event):
        if self._drag_start:
            sx, sy, px0, py0 = self._drag_start
            self.pan_x = px0 + (event.x - sx); self.pan_y = py0 + (event.y - sy); self.redraw()

    def _on_release(self, event):
        if hasattr(self, "_pressed_pos"):
            if abs(event.x - self._pressed_pos[0]) < 5 and abs(event.y - self._pressed_pos[1]) < 5:
                hit = self._find_hit(event.x, event.y)
                if hit and hit[3] == "gov":
                    self.selected_gov = hit[4]
                    if self.on_select_gov: self.on_select_gov(hit[4])
                    self.redraw()
                elif not hit:
                    self.selected_gov = None
                    if self.on_select_gov: self.on_select_gov(None)
                    self.redraw()
        self._drag_start = None

    def _find_hit(self, mx, my):
        best = None; best_dist = 999.0
        for hx, hy, rad, kind, payload in self._hit_targets:
            d = math.hypot(mx - hx, my - hy)
            if d <= rad and d < best_dist:
                best = (hx, hy, rad, kind, payload); best_dist = d
        return best

    def _on_hover(self, event):
        hit = self._find_hit(event.x, event.y)
        if hit != self.hovered_item:
            self.hovered_item = hit; self.redraw()

    def _animate_pulse(self):
        self.pulse_phase = (self.pulse_phase + 0.14) % math.tau
        self.delete("pulse_ring")
        if self.selected_gov and self.selected_gov in GOV_COORDS:
            lon, lat = GOV_COORDS[self.selected_gov]
            px, py = self._project(lon, lat)
            r = 12 + 5 * abs(math.sin(self.pulse_phase))
            self.create_oval(px - r, py - r, px + r, py + r, outline="#FF7A2F", width=1.8, tags="pulse_ring")
        self.after(45, self._animate_pulse)

    def redraw(self):
        self.delete("all"); self._hit_targets.clear()
        w = self.winfo_width(); h = self.winfo_height()
        if w < 30 or h < 30: return
        for lon in range(7, 13):
            x1, y1 = self._project(lon, 30.0); x2, y2 = self._project(lon, 37.8)
            self.create_line(x1, y1, x2, y2, fill="#101B33", width=1)
            self.create_text(x1 + 4, h - 14, text=f"{lon}°E", fill="#33486E", font=("Consolas", 8), anchor="w")
        for lat in range(30, 38):
            x1, y1 = self._project(7.0, lat); x2, y2 = self._project(12.2, lat)
            self.create_line(x1, y1, x2, y2, fill="#101B33", width=1)
            self.create_text(14, y1 - 4, text=f"{lat}°N", fill="#33486E", font=("Consolas", 8), anchor="w")

        poly_pts = []
        for lon, lat in TUNISIA_OUTLINE:
            px, py = self._project(lon, lat); poly_pts.extend([px, py])
        if len(poly_pts) >= 6:
            self.create_polygon(*poly_pts, fill="#0D192E", outline="#284370", width=2)

        if self.show_features and self.features:
            for feat in self.features:
                cat = feat.get("category", "Other")
                col = "#45D6A0" if cat == "Transport" else ("#35C8D0" if "geography" in cat.lower() else "#FFAA55")
                if feat["type"] == "Line":
                    line_pts = []
                    for lon, lat in feat["coords"]:
                        px, py = self._project(lon, lat); line_pts.extend([px, py])
                    if len(line_pts) >= 4: self.create_line(*line_pts, fill=col, width=2)
                elif feat["type"] == "Point":
                    lon, lat = feat["coords"][0]; px, py = self._project(lon, lat)
                    if -20 <= px <= w + 20 and -20 <= py <= h + 20:
                        self.create_oval(px - 2.5, py - 2.5, px + 2.5, py + 2.5, fill=col, outline="")
                        self._hit_targets.append((px, py, 7, "feature", feat))

        if self.show_govs:
            for gov, (lon, lat) in GOV_COORDS.items():
                px, py = self._project(lon, lat)
                info = self.gov_stats.get(gov, {})
                total_m = info.get("metadata_matches", 0)
                tr_m = info.get("transport_metadata_matches", 0)
                db_s = info.get("db_extracted_stops", 0)
                if db_s > 0 or tr_m > 0: fill_col = "#45D6A0"; ring_col = "#1E6B50"
                elif total_m > 0: fill_col = "#35C8D0"; ring_col = "#1B5E69"
                else: fill_col = "#3B4E73"; ring_col = "#1E2B45"
                if gov == self.selected_gov: fill_col = "#FF7A2F"; ring_col = "#FF7A2F"
                rad = min(13, 4.5 + math.sqrt(total_m + db_s) * 1.2)
                self.create_oval(px - rad - 3, py - rad - 3, px + rad + 3, py + rad + 3, outline=ring_col, width=1)
                self.create_oval(px - rad, py - rad, px + rad, py + rad, fill=fill_col, outline="#070C18", width=1.5)
                self._hit_targets.append((px, py, max(10, rad + 4), "gov", gov))
                if self.show_labels and (self.zoom >= 1.15 or total_m > 0 or db_s > 0 or gov in {"Tunis", "Sousse", "Monastir", "Sfax", "Gabès", "Gafsa", "Bizerte", "Tataouine"}):
                    lbl = f"{gov} ({db_s} stops)" if db_s > 0 else (f"{gov} ({total_m})" if total_m > 0 else gov)
                    self.create_text(px + rad + 5, py, text=lbl, fill="#DCE6F7" if (total_m > 0 or db_s > 0) else "#6B80A6", font=("Segoe UI Semibold" if (total_m > 0 or db_s > 0) else "Segoe UI", 8), anchor="w")

        if self.hovered_item:
            hx, hy, _, kind, payload = self.hovered_item
            if kind == "gov":
                info = self.gov_stats.get(payload, {})
                lines = [
                    f"GOVERNORATE: {payload.upper()}",
                    f"SQLite Extracted Stops: {info.get('db_extracted_stops', 0):,}",
                    f"Total Metadata Matches: {info.get('metadata_matches', 0)}",
                    f"Transport Leads: {info.get('transport_metadata_matches', 0)}",
                    f"Admin Geography: {info.get('administrative_geography_resources', 0)}",
                ]
            else:
                lines = [
                    f"FEATURE: {payload.get('label', 'Point')[:34]}",
                    f"Category: {payload.get('category', 'Unknown')}",
                    f"Source: {payload.get('source', '')[:34]}",
                ]
            box_w = 230; box_h = len(lines) * 17 + 14
            tx = min(w - box_w - 12, max(12, hx + 14)); ty = min(h - box_h - 12, max(12, hy - box_h // 2))
            self.create_rectangle(tx, ty, tx + box_w, ty + box_h, fill="#0B1324", outline="#35C8D0", width=1.5)
            for idx, text_line in enumerate(lines):
                col = "#FF7A2F" if idx == 0 else "#E2E8F0"
                fnt = ("Segoe UI Semibold", 9) if idx == 0 else ("Segoe UI", 8)
                self.create_text(tx + 10, ty + 10 + idx * 17, text=text_line, fill=col, font=fnt, anchor="nw")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.title(APP_TITLE)
        self.geometry("1580x960")
        self.minsize(1240, 780)

        self.bg = "#070C18"; self.panel = "#0F172A"; self.card_bg = "#131E36"; self.line = "#223252"
        self.fg = "#F8FAFC"; self.muted = "#8B9EC0"; self.cyan = "#35C8D0"; self.green = "#45D6A0"
        self.orange = "#FF7A2F"; self.amber = "#FFAA55"; self.red = "#FF687E"

        self.events = queue.Queue()
        self.stop_event = threading.Event()
        self.worker = None
        self.engine = None
        self.output_dir = default_output_dir()

        self.metric_targets = {
            "datasets": 0, "resources": 0, "transport": 0, "downloaded": 0, "validated": 0,
            "db_stops": 0, "db_routes": 0, "db_trips": 0, "db_stop_times": 0
        }
        self.metric_display = {k: 0.0 for k in self.metric_targets}
        self.progress_target = 0.0
        self.progress_current = 0.0
        self.pulse_phase = 0.0
        self.is_running = False

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh())
        self.category_var = ctk.StringVar(value="All")

        self.configure(fg_color=self.bg)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._style()
        self._build()
        self.after(120, self._poll)
        self.after(30, self._animate_ui)

    def _style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#0B1324", foreground=self.fg, fieldbackground="#0B1324", rowheight=32, borderwidth=0, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", background="#162440", foreground=self.cyan, relief="flat", font=("Segoe UI Semibold", 9), padding=(8, 6))
        style.map("Treeview", background=[("selected", "#1F3B5C")], foreground=[("selected", "#FFFFFF")])

    def _build(self):
        side = ctk.CTkFrame(self, width=255, fg_color=self.panel, corner_radius=0, border_width=1, border_color="#18243E")
        side.grid(row=0, column=0, sticky="nsw")
        side.grid_propagate(False)

        brand_box = ctk.CTkFrame(side, fg_color="transparent")
        brand_box.pack(fill="x", padx=18, pady=(20, 14))
        self.symbol = SymbolCanvas(brand_box, size=44, bg=self.panel)
        self.symbol.pack(side="left", padx=(0, 10))
        title_stack = ctk.CTkFrame(brand_box, fg_color="transparent")
        title_stack.pack(side="left", fill="y")
        ctk.CTkLabel(title_stack, text="MASARI", font=("Segoe UI Semibold", 22), text_color=self.fg).pack(anchor="w")
        ctk.CTkLabel(title_stack, text="RECOVERY + DEEP DB 3.6", font=("Segoe UI Semibold", 9), text_color=self.orange).pack(anchor="w")

        self.nav = {}
        self.nav_indicators = {}
        self.pages = ctk.CTkFrame(self, fg_color="transparent")
        self.pages.grid(row=0, column=1, sticky="nsew", padx=22, pady=18)
        self.pages.grid_columnconfigure(0, weight=1)
        self.pages.grid_rowconfigure(0, weight=1)

        nav_icons = {
            "Overview": "◈  Overview & Deep DB",
            "Tunisia Map": "✦  Tunisia Map",
            "SQLite Database": "⛁  SQLite Stops & Routes",
            "Resources": "▤  Resources",
            "Transport": "⇄  Transport",
            "Geography": "⌖  Geography",
            "Downloads": "⇣  Downloads",
            "Coverage": "⊞  Coverage (24 Gov)",
            "Activity": "▸  System Activity"
        }

        for name in nav_icons:
            row_f = ctk.CTkFrame(side, fg_color="transparent", height=35)
            row_f.pack(fill="x", padx=12, pady=1.5)
            row_f.pack_propagate(False)
            ind = ctk.CTkFrame(row_f, width=3, height=20, corner_radius=2, fg_color="transparent")
            ind.pack(side="left", padx=(2, 6), pady=7)
            b = ctk.CTkButton(
                row_f, text=nav_icons[name], anchor="w", height=33, corner_radius=8,
                font=("Segoe UI Semibold", 11), fg_color="transparent", hover_color="#182642",
                text_color=self.muted, command=lambda n=name: self.show_page(n)
            )
            b.pack(side="left", fill="both", expand=True)
            self.nav[name] = b
            self.nav_indicators[name] = ind

        ctk.CTkFrame(side, height=1, fg_color=self.line).pack(fill="x", padx=18, pady=(12, 10))

        pill = ctk.CTkFrame(side, fg_color="#0A1020", corner_radius=8, border_width=1, border_color=self.line)
        pill.pack(fill="x", padx=14, pady=(0, 10))
        self.status_dot = ctk.CTkLabel(pill, text="●", font=("Segoe UI", 12), text_color=self.amber)
        self.status_dot.pack(side="left", padx=(12, 6), pady=5)
        self.status = ctk.CTkLabel(pill, text="IDLE · READY", text_color=self.fg, font=("Segoe UI Semibold", 10))
        self.status.pack(side="left", pady=5)

        self.start_btn = ctk.CTkButton(
            side, text="▶  Start Recovery + Deep DB", height=38, corner_radius=8,
            font=("Segoe UI Semibold", 11), fg_color="#147D87", hover_color="#1996A3",
            command=self.start_recovery
        )
        self.start_btn.pack(fill="x", padx=14, pady=(2, 5))

        self.reanalyse_btn = ctk.CTkButton(
            side, text="↻  Reanalyse & Build DB", height=34, corner_radius=8,
            font=("Segoe UI", 11), fg_color="#1B2A47", hover_color="#253961",
            border_width=1, border_color="#2A406B", command=self.reanalyse
        )
        self.reanalyse_btn.pack(fill="x", padx=14, pady=3)

        self.local_btn = ctk.CTkButton(
            side, text="⌕  Inspect Local Folder -> DB", height=34, corner_radius=8,
            font=("Segoe UI", 11), fg_color="#1B2A47", hover_color="#253961",
            border_width=1, border_color="#2A406B", command=self.inspect_local
        )
        self.local_btn.pack(fill="x", padx=14, pady=3)

        self.stop_btn = ctk.CTkButton(
            side, text="■  Stop Safely", height=32, corner_radius=8,
            font=("Segoe UI Semibold", 11), fg_color="#592230", hover_color="#782E40",
            command=self.stop, state="disabled"
        )
        self.stop_btn.pack(fill="x", padx=14, pady=(5, 8))

        out_card = ctk.CTkFrame(side, fg_color="#0A1020", corner_radius=8, border_width=1, border_color="#1B2945")
        out_card.pack(side="bottom", fill="x", padx=14, pady=12)
        ctk.CTkLabel(out_card, text="OUTPUT & SQLITE TARGET", text_color=self.cyan, font=("Segoe UI Semibold", 8)).pack(anchor="w", padx=10, pady=(6, 2))
        self.path_label = ctk.CTkLabel(out_card, text=str(self.output_dir), text_color=self.muted, font=("Segoe UI", 9), wraplength=205, justify="left")
        self.path_label.pack(anchor="w", padx=10, pady=(0, 6))
        ctk.CTkButton(
            out_card, text="Change Output Folder", height=24, corner_radius=6, font=("Segoe UI", 10),
            fg_color="#16223B", hover_color="#213254", text_color=self.fg, command=self.choose_output
        ).pack(fill="x", padx=8, pady=(0, 6))

        self.overview = self._overview()
        self.map_page = self._map_page()
        self.db_page = self._db_page()
        self.resources_page = self._table("Resources", ["category", "dataset_title", "name", "format", "score", "host", "status"], [155, 280, 230, 100, 65, 160, 240])
        self.transport_page = self._table("Transport", ["mode", "dataset_title", "name", "format", "score", "governorates", "status"], [150, 250, 220, 100, 65, 180, 230])
        self.geography_page = self._table("Geography", ["category", "dataset_title", "name", "format", "governorates", "status"], [160, 260, 220, 100, 180, 230])
        self.downloads_page = self._table("Downloads", ["category", "name", "status", "format", "size", "path"], [150, 220, 240, 100, 90, 350])
        self.coverage_page = self._table("Coverage", ["governorate", "metadata_matches", "transport_matches", "admin_geo_resources", "db_extracted_stops", "evidence"], [130, 120, 130, 150, 140, 390])
        self.activity_page = self._activity()
        self.show_page("Overview")

    def _overview(self):
        p = ctk.CTkFrame(self.pages, fg_color="transparent")
        p.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        p.grid_rowconfigure(4, weight=1)

        hdr = ctk.CTkFrame(p, fg_color="transparent")
        hdr.grid(row=0, column=0, columnspan=5, sticky="ew", pady=(0, 12))
        ctk.CTkLabel(hdr, text="Nationwide Discovery, Recovery & Deep GTFS/GIS Database Engine", font=("Segoe UI Semibold", 22), text_color=self.fg).pack(anchor="w")
        ctk.CTkLabel(hdr, text="24 Tunisian Governorates · CKAN Discovery → Download → GTFS/CSV/GeoJSON Unpacking → SQLite Database → React Native Fixtures", text_color=self.muted, font=("Segoe UI", 11)).pack(anchor="w", pady=(2, 0))

        self.metrics = {}
        kpi_row1 = [
            ("datasets", "CKAN DATASETS", self.cyan, "Unique packages indexed"),
            ("resources", "TOTAL RESOURCES", self.cyan, "Files & endpoints catalogued"),
            ("transport", "TRANSPORT LEADS", self.green, "Bus, Rail, Metro, Louage"),
            ("downloaded", "RECOVERED FILES", self.orange, "Verified local payloads"),
            ("validated", "VALIDATED ASSETS", self.green, "Passed structural checks"),
        ]
        for i, (key, label, color, sub) in enumerate(kpi_row1):
            card = ctk.CTkFrame(p, fg_color=self.panel, border_width=1, border_color=self.line, corner_radius=10)
            card.grid(row=1, column=i, sticky="nsew", padx=4, pady=(0, 10))
            ctk.CTkFrame(card, height=3, fg_color=color, corner_radius=2).pack(fill="x", padx=12, pady=(8, 6))
            ctk.CTkLabel(card, text=label, text_color=self.muted, font=("Segoe UI Semibold", 9)).pack(anchor="w", padx=12)
            v = ctk.CTkLabel(card, text="0", font=("Segoe UI Semibold", 24), text_color=self.fg)
            v.pack(anchor="w", padx=12, pady=(1, 1))
            ctk.CTkLabel(card, text=sub, text_color="#64789C", font=("Segoe UI", 9)).pack(anchor="w", padx=12, pady=(0, 8))
            self.metrics[key] = v

        kpi_row2 = [
            ("db_stops", "SQLITE STOPS", self.green, "Geo-validated stations & stops"),
            ("db_routes", "SQLITE ROUTES", self.cyan, "Transit lines & corridors"),
            ("db_trips", "GTFS TRIPS", self.orange, "Scheduled vehicle journeys"),
            ("db_stop_times", "GTFS STOP TIMES", self.amber, "Arrival/departure schedules"),
        ]
        db_strip = ctk.CTkFrame(p, fg_color="transparent")
        db_strip.grid(row=2, column=0, columnspan=5, sticky="ew", pady=(0, 12))
        db_strip.grid_columnconfigure((0, 1, 2, 3), weight=1)
        for i, (key, label, color, sub) in enumerate(kpi_row2):
            card = ctk.CTkFrame(db_strip, fg_color="#0D162B", border_width=1, border_color="#23375E", corner_radius=10)
            card.grid(row=0, column=i, sticky="nsew", padx=4)
            ctk.CTkFrame(card, height=3, fg_color=color, corner_radius=2).pack(fill="x", padx=12, pady=(8, 5))
            ctk.CTkLabel(card, text=label, text_color=color, font=("Segoe UI Semibold", 9)).pack(anchor="w", padx=12)
            v = ctk.CTkLabel(card, text="0", font=("Segoe UI Semibold", 22), text_color=self.fg)
            v.pack(anchor="w", padx=12, pady=(1, 1))
            ctk.CTkLabel(card, text=sub, text_color="#64789C", font=("Segoe UI", 9)).pack(anchor="w", padx=12, pady=(0, 8))
            self.metrics[key] = v

        panel = ctk.CTkFrame(p, fg_color=self.panel, border_width=1, border_color=self.line, corner_radius=12)
        panel.grid(row=3, column=0, columnspan=5, sticky="ew", pady=(0, 12))
        panel.grid_columnconfigure(0, weight=1)

        top_row = ctk.CTkFrame(panel, fg_color="transparent")
        top_row.grid(row=0, column=0, sticky="ew", padx=20, pady=(14, 4))
        self.stage = ctk.CTkLabel(top_row, text="System Ready · Awaiting Command", font=("Segoe UI Semibold", 16), text_color=self.cyan)
        self.stage.pack(side="left")
        self.progress_label = ctk.CTkLabel(top_row, text="0%", font=("Segoe UI Semibold", 13), text_color=self.orange)
        self.progress_label.pack(side="right")

        self.detail = ctk.CTkLabel(panel, text="Unified MASARI 3.6 Pipeline: Discovers CKAN packages, recovers files, and populates SQLite + React Native JSON fixtures.", text_color=self.muted, font=("Segoe UI", 11))
        self.detail.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 10))

        self.progress = ctk.CTkProgressBar(panel, height=10, corner_radius=5, fg_color="#0A1020", progress_color=self.cyan)
        self.progress.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 12))
        self.progress.set(0)

        canvas_frame = ctk.CTkFrame(panel, fg_color="#090F1E", corner_radius=8, border_width=1, border_color="#1A2947")
        canvas_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 14))
        self.telemetry_canvas = TelemetryCanvas(canvas_frame, height=96, bg="#090F1E")
        self.telemetry_canvas.pack(fill="x", padx=2, pady=2)

        info_panel = ctk.CTkFrame(p, fg_color=self.panel, border_width=1, border_color=self.line, corner_radius=12)
        info_panel.grid(row=4, column=0, columnspan=5, sticky="nsew")
        info_panel.grid_columnconfigure((0, 1, 2), weight=1)

        modes_info = [
            ("01 · UNIFIED CKAN + DEEP EXTRACTION", self.cyan, "Discovers datasets across all 24 governorates, downloads valid resources, unpacks GTFS/CSV/GeoJSON archives into SQLite, and builds React Native fixtures."),
            ("02 · OFFLINE REANALYSIS -> SQLITE", self.orange, "Imports existing MASARI resources.json manifests and builds a fresh normalized SQLite database & mobile app fixtures without repeating web discovery."),
            ("03 · LOCAL FOLDER -> SQLITE + FIXTURES", self.green, "Audits any local directory of GTFS zips, CSVs, and GeoJSON files, extracting validated Tunisian stops and routes straight into SQLite.")
        ]
        for idx, (m_title, m_col, m_desc) in enumerate(modes_info):
            box = ctk.CTkFrame(info_panel, fg_color="#0B1324", corner_radius=8, border_width=1, border_color="#1A2742")
            box.grid(row=0, column=idx, sticky="nsew", padx=12, pady=12)
            ctk.CTkLabel(box, text=m_title, font=("Segoe UI Semibold", 10), text_color=m_col).pack(anchor="w", padx=14, pady=(10, 4))
            ctk.CTkLabel(box, text=m_desc, font=("Segoe UI", 10), text_color=self.muted, wraplength=340, justify="left").pack(anchor="w", padx=14, pady=(0, 10))

        return p

    def _db_page(self):
        p = ctk.CTkFrame(self.pages, fg_color=self.panel, corner_radius=12, border_width=1, border_color=self.line)
        p.grid_columnconfigure(0, weight=1)
        p.grid_rowconfigure(1, weight=1)

        bar = ctk.CTkFrame(p, fg_color="transparent")
        bar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=14, pady=12)
        ctk.CTkLabel(bar, text="SQLITE EXTRACTED STOPS & ROUTES PREVIEW (TOP 500)", font=("Segoe UI Semibold", 13), text_color=self.green).pack(side="left", padx=(0, 16))
        ctk.CTkButton(bar, text="↻ Refresh SQLite Preview", width=160, height=30, fg_color="#1A2947", hover_color="#253A63", command=self._refresh_db_preview).pack(side="right")

        cols = ["stop_id", "name_fr", "stop_type", "governorate", "lat", "lon", "verification_status"]
        widths = [180, 260, 130, 130, 110, 110, 140]
        self.db_tree = ttk.Treeview(p, columns=cols, show="headings")
        self.db_tree.tag_configure("odd", background="#0B1324")
        self.db_tree.tag_configure("even", background="#0F192E")
        for col, w in zip(cols, widths):
            self.db_tree.heading(col, text=col.replace("_", " ").upper())
            self.db_tree.column(col, width=w, minwidth=70, anchor="w")

        self.db_tree.grid(row=1, column=0, sticky="nsew", padx=(14, 0), pady=(0, 14))
        sc = ttk.Scrollbar(p, orient="vertical", command=self.db_tree.yview)
        sc.grid(row=1, column=1, sticky="ns", padx=(4, 14), pady=(0, 14))
        self.db_tree.configure(yscrollcommand=sc.set)
        return p

    def _refresh_db_preview(self):
        for item in self.db_tree.get_children():
            self.db_tree.delete(item)
        if not self.engine or not self.engine.deep_db.db_path.exists():
            return
        try:
            conn = self.engine.deep_db._connect()
            cur = conn.cursor()
            cur.execute("SELECT stop_id, name_fr, stop_type, governorate, ROUND(lat, 5), ROUND(lon, 5), verification_status FROM stops_registry LIMIT 500")
            for idx, row in enumerate(cur.fetchall()):
                tag = "even" if idx % 2 == 0 else "odd"
                self.db_tree.insert("", "end", tags=(tag,), values=row)
            conn.close()
        except Exception as e:
            self.log("WARN", f"SQLite preview error: {e}")

    def _map_page(self):
        p = ctk.CTkFrame(self.pages, fg_color=self.panel, corner_radius=12, border_width=1, border_color=self.line)
        p.grid_columnconfigure(0, weight=3)
        p.grid_columnconfigure(1, weight=1)
        p.grid_rowconfigure(1, weight=1)

        bar = ctk.CTkFrame(p, fg_color="transparent")
        bar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=16, pady=(12, 8))
        ctk.CTkLabel(bar, text="INTERACTIVE TUNISIA GEOSPATIAL & COVERAGE MAP", font=("Segoe UI Semibold", 13), text_color=self.fg).pack(side="left", padx=(0, 16))
        ctk.CTkButton(bar, text="+ Zoom In", width=76, height=28, fg_color="#1A2947", hover_color="#253A63", command=lambda: self.tunisia_map.set_zoom(1.25)).pack(side="left", padx=3)
        ctk.CTkButton(bar, text="− Zoom Out", width=80, height=28, fg_color="#1A2947", hover_color="#253A63", command=lambda: self.tunisia_map.set_zoom(0.8)).pack(side="left", padx=3)
        ctk.CTkButton(bar, text="⟲ Reset View", width=88, height=28, fg_color="#1A2947", hover_color="#253A63", command=lambda: self.tunisia_map.reset_view()).pack(side="left", padx=3)

        self.chk_govs = ctk.CTkCheckBox(bar, text="24 Governorates", font=("Segoe UI", 10), fg_color=self.cyan, command=self._toggle_map_layers)
        self.chk_govs.select()
        self.chk_govs.pack(side="right", padx=8)

        self.chk_feats = ctk.CTkCheckBox(bar, text="Extracted Coordinates", font=("Segoe UI", 10), fg_color=self.green, command=self._toggle_map_layers)
        self.chk_feats.select()
        self.chk_feats.pack(side="right", padx=8)

        map_wrap = ctk.CTkFrame(p, fg_color="#070C18", corner_radius=10, border_width=1, border_color="#1D2E4F")
        map_wrap.grid(row=1, column=0, sticky="nsew", padx=(14, 8), pady=(0, 14))
        self.tunisia_map = TunisiaMapCanvas(map_wrap, on_select_gov=self._on_map_gov_select, bg="#070C18")
        self.tunisia_map.pack(fill="both", expand=True, padx=2, pady=2)

        insp = ctk.CTkFrame(p, fg_color="#0B1324", corner_radius=10, border_width=1, border_color="#1D2E4F")
        insp.grid(row=1, column=1, sticky="nsew", padx=(0, 14), pady=(0, 14))
        insp.grid_columnconfigure(0, weight=1)
        insp.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(insp, text="MAP LEGEND & INSPECTOR", font=("Segoe UI Semibold", 10), text_color=self.cyan).grid(row=0, column=0, sticky="w", padx=14, pady=(14, 8))
        legend_box = ctk.CTkFrame(insp, fg_color="#101B33", corner_radius=8)
        legend_box.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 12))
        for dot_c, desc in [
            (self.green, "SQLite Verified Stops / Transport"),
            (self.cyan, "Geography Metadata Matches"),
            ("#FF7A2F", "Selected Governorate Focus"),
            ("#4E6591", "No Data Extracted Yet"),
        ]:
            r_leg = ctk.CTkFrame(legend_box, fg_color="transparent")
            r_leg.pack(fill="x", padx=10, pady=3)
            ctk.CTkLabel(r_leg, text="●", text_color=dot_c, font=("Segoe UI", 11)).pack(side="left", padx=(0, 6))
            ctk.CTkLabel(r_leg, text=desc, text_color=self.muted, font=("Segoe UI", 9)).pack(side="left")

        self.map_gov_title = ctk.CTkLabel(insp, text="Nationwide Overview (All 24)", font=("Segoe UI Semibold", 13), text_color=self.fg)
        self.map_gov_title.grid(row=2, column=0, sticky="w", padx=14, pady=(4, 4))

        self.map_gov_box = ctk.CTkTextbox(insp, fg_color="#080E1C", text_color="#CBD5E1", font=("Segoe UI", 10), border_width=1, border_color="#1A2844")
        self.map_gov_box.grid(row=3, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.map_gov_box.insert("end", "Run recovery or local inspection to populate Tunisia's 24 governorates and SQLite stops.")
        return p

    def _toggle_map_layers(self):
        self.tunisia_map.show_govs = bool(self.chk_govs.get())
        self.tunisia_map.show_features = bool(self.chk_feats.get())
        self.tunisia_map.redraw()

    def _on_map_gov_select(self, gov):
        self.map_gov_box.delete("1.0", "end")
        if not self.engine:
            self.map_gov_title.configure(text=gov or "Nationwide Overview (All 24)")
            self.map_gov_box.insert("end", "No run data loaded yet.")
            return
        cov_all = self.engine.coverage_report()["governorates"]
        if not gov:
            self.map_gov_title.configure(text="Nationwide Overview (All 24)")
            total_pts = len(self.engine.map_features)
            matched_govs = sum(1 for g, d in cov_all.items() if (d["metadata_matches"] > 0 or d["db_extracted_stops"] > 0))
            self.map_gov_box.insert("end", f"Governorates with data: {matched_govs}/24\nMap coordinates plotted: {total_pts}\n\nClick any node to inspect SQLite stops and resources.")
            return
        self.map_gov_title.configure(text=f"{gov} Governorate")
        cov = cov_all.get(gov, {})
        self.map_gov_box.insert("end", f"SQLite Extracted Stops: {cov.get('db_extracted_stops', 0):,}\nMetadata Matches: {cov.get('metadata_matches', 0)}\nTransport Leads: {cov.get('transport_metadata_matches', 0)}\nAdmin Geography: {cov.get('administrative_geography_resources', 0)}\nEvidence: {cov.get('evidence', '')}\n\n--- MATCHING RESOURCES ---\n")
        matches = [r for r in self.engine.resources.values() if gov in (r.get("governorates") or [])]
        for r in matches[:40]:
            self.map_gov_box.insert("end", f"• [{r.get('category')}] {r.get('name')} ({r.get('detected_format') or r.get('format', '')})\n")

    def _table(self, name, cols, widths):
        p = ctk.CTkFrame(self.pages, fg_color=self.panel, corner_radius=12, border_width=1, border_color=self.line)
        p.grid_columnconfigure(0, weight=1)
        p.grid_rowconfigure(1, weight=1)
        bar = ctk.CTkFrame(p, fg_color="transparent")
        bar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=14, pady=12)
        ctk.CTkLabel(bar, text=name.upper(), font=("Segoe UI Semibold", 13), text_color=self.fg).pack(side="left", padx=(0, 16))
        ctk.CTkEntry(bar, textvariable=self.search_var, placeholder_text="⌕  Live filter records…", width=290, height=32, fg_color="#0B1324", border_color=self.line).pack(side="left")
        if name == "Resources":
            ctk.CTkOptionMenu(
                bar, variable=self.category_var,
                values=["All", "Transport", "Administrative geography", "Useful geography", "Other"],
                height=32, fg_color="#1A2947", button_color="#23375E", command=lambda _: self.refresh()
            ).pack(side="left", padx=10)
        tree = ttk.Treeview(p, columns=cols, show="headings")
        tree.tag_configure("odd", background="#0B1324")
        tree.tag_configure("even", background="#0F192E")
        for col, w in zip(cols, widths):
            tree.heading(col, text=col.replace("_", " ").upper())
            tree.column(col, width=w, minwidth=60, anchor="w")
        tree.grid(row=1, column=0, sticky="nsew", padx=(14, 0), pady=(0, 14))
        sc = ttk.Scrollbar(p, orient="vertical", command=tree.yview)
        sc.grid(row=1, column=1, sticky="ns", padx=(4, 14), pady=(0, 14))
        tree.configure(yscrollcommand=sc.set)
        return p, tree

    def _activity(self):
        p = ctk.CTkFrame(self.pages, fg_color=self.panel, corner_radius=12, border_width=1, border_color=self.line)
        p.grid_columnconfigure(0, weight=1)
        p.grid_rowconfigure(1, weight=1)
        hdr = ctk.CTkFrame(p, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 6))
        ctk.CTkLabel(hdr, text="SYSTEM TELEMETRY & EXECUTION LOG", font=("Segoe UI Semibold", 12), text_color=self.cyan).pack(side="left")
        self.logbox = ctk.CTkTextbox(p, fg_color="#080D1A", text_color="#CBD5E1", font=("Cascadia Code", 10), border_width=1, border_color="#1A2844")
        self.logbox.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))
        return p

    def show_page(self, name):
        for w in self.pages.winfo_children():
            w.grid_forget()
        page = {
            "Overview": self.overview,
            "Tunisia Map": self.map_page,
            "SQLite Database": self.db_page,
            "Resources": self.resources_page[0],
            "Transport": self.transport_page[0],
            "Geography": self.geography_page[0],
            "Downloads": self.downloads_page[0],
            "Coverage": self.coverage_page[0],
            "Activity": self.activity_page
        }[name]
        page.grid(row=0, column=0, sticky="nsew")
        if name == "SQLite Database":
            self._refresh_db_preview()
        for k, b in self.nav.items():
            active = (k == name)
            b.configure(fg_color="#182744" if active else "transparent", text_color=self.fg if active else self.muted)
            self.nav_indicators[k].configure(fg_color=self.orange if active else "transparent")

    def choose_output(self):
        x = filedialog.askdirectory(initialdir=str(self.output_dir))
        if x:
            self.output_dir = Path(x)
            self.path_label.configure(text=str(x))

    def _launch(self, mode, source=None):
        if self.worker and self.worker.is_alive(): return
        self.stop_event.clear()
        self.progress_target = 0.0; self.progress_current = 0.0; self.progress.set(0)
        for k in self.metric_targets:
            self.metric_targets[k] = 0
            self.metric_display[k] = 0.0
        self.is_running = True
        self.telemetry_canvas.set_active(True)
        self.status.configure(text="RUNNING · ACTIVE", text_color=self.green)
        for b in [self.start_btn, self.reanalyse_btn, self.local_btn]: b.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.engine = RecoveryEngine(self.output_dir, self.events, self.stop_event)
        self.worker = threading.Thread(target=self.engine.run, args=(mode, source), daemon=True)
        self.worker.start()
        self.show_page("Overview")

    def start_recovery(self): self._launch("recover")
    def reanalyse(self):
        folder = filedialog.askdirectory(title="Select MASARI export folder (contains resources.json)")
        if folder: self._launch("reanalyse", folder)
    def inspect_local(self):
        folder = filedialog.askdirectory(title="Select folder containing files to inspect & extract to SQLite")
        if folder: self._launch("local", folder)
    def stop(self):
        self.stop_event.set()
        self.status.configure(text="STOPPING…", text_color=self.amber)
        self.stage.configure(text="Halting pipeline safely…")

    def log(self, level, msg):
        self.logbox.insert("end", f"[{datetime.now():%H:%M:%S}] [{level}] {msg}\n")
        self.logbox.see("end")

    def _animate_ui(self):
        self.pulse_phase = (self.pulse_phase + 0.12) % math.tau
        if self.is_running:
            dot_col = self.green if math.sin(self.pulse_phase) > 0 else "#1D6F53"
            self.status_dot.configure(text_color=dot_col)
        if abs(self.progress_target - self.progress_current) > 0.001:
            self.progress_current += (self.progress_target - self.progress_current) * 0.22
            self.progress.set(self.progress_current)
        for key, target in self.metric_targets.items():
            curr = self.metric_display[key]
            if abs(target - curr) > 0.2:
                curr += (target - curr) * 0.25
                self.metric_display[key] = curr
                self.metrics[key].configure(text=f"{int(round(curr)):,}")
            elif curr != target:
                self.metric_display[key] = float(target)
                self.metrics[key].configure(text=f"{target:,}")
        self.after(33, self._animate_ui)

    def _poll(self):
        try:
            while True:
                e = self.events.get_nowait()
                k = e.get("kind")
                if k == "log":
                    self.log(e.get("level", "INFO"), e.get("message", ""))
                elif k == "stage":
                    self.stage.configure(text=e.get("name", "Working"))
                    self.detail.configure(text=e.get("detail", ""))
                elif k == "progress":
                    v = max(0.0, min(100.0, float(e.get("value", 0))))
                    self.progress_target = v / 100.0
                    self.progress_label.configure(text=f"{v:.0f}% · {e.get('detail', '')}")
                elif k == "metrics":
                    counts = e.get("counts", {})
                    self.metric_targets["datasets"] = int(e.get("datasets", 0))
                    self.metric_targets["resources"] = int(e.get("resources", 0))
                    self.metric_targets["transport"] = int(counts.get("Transport", 0))
                elif k == "metric":
                    if self.engine:
                        self.metric_targets["downloaded"] = int(self.engine.stats.get("downloaded", 0))
                        self.metric_targets["validated"] = int(self.engine.stats.get("validated", 0))
                elif k == "db_metrics":
                    c = e.get("counts", {})
                    self.metric_targets["db_stops"] = int(c.get("stops", 0))
                    self.metric_targets["db_routes"] = int(c.get("routes", 0))
                    self.metric_targets["db_trips"] = int(c.get("trips", 0))
                    self.metric_targets["db_stop_times"] = int(c.get("stop_times", 0))
                elif k == "done":
                    self.finish(e)
                elif k == "fatal":
                    self.is_running = False
                    self.telemetry_canvas.set_active(False)
                    self.log("ERROR", e.get("message", "Unknown error"))
                    self.status.configure(text="ERROR · HALTED", text_color=self.red)
                    self.status_dot.configure(text_color=self.red)
                    self._unlock()
        except queue.Empty:
            pass
        self.after(120, self._poll)

    def _unlock(self):
        for b in [self.start_btn, self.reanalyse_btn, self.local_btn]: b.configure(state="normal")
        self.stop_btn.configure(state="disabled")

    def finish(self, e):
        self.is_running = False
        self.telemetry_canvas.set_active(False)
        stopped = e.get("stopped", False)
        self.status.configure(text="STOPPED · SAVED" if stopped else "COMPLETE · SAVED", text_color=self.amber if stopped else self.green)
        self.status_dot.configure(text_color=self.amber if stopped else self.green)
        self.stage.configure(text="Export & SQLite Database Complete")
        self.detail.configure(text=f"Saved SQLite DB, React Native fixtures & reports to: {e.get('out_dir')}")
        self.progress_target = 1.0
        self.progress_label.configure(text="100% · Saved")
        if self.engine:
            self.metric_targets["datasets"] = len(self.engine.datasets)
            self.metric_targets["resources"] = len(self.engine.resources)
            self.metric_targets["downloaded"] = int(self.engine.stats.get("downloaded", 0))
            self.metric_targets["validated"] = int(self.engine.stats.get("validated", 0))
            dbc = self.engine.deep_db.get_counts()
            self.metric_targets["db_stops"] = dbc["stops"]
            self.metric_targets["db_routes"] = dbc["routes"]
            self.metric_targets["db_trips"] = dbc["trips"]
            self.metric_targets["db_stop_times"] = dbc["stop_times"]
        self.log("SUCCESS", f"{e.get('datasets')} datasets · {e.get('resources')} resources · SQLite DB & Fixtures ready at {e.get('out_dir')}")
        self.refresh()
        self._refresh_db_preview()
        self._unlock()

    def refresh(self):
        if not self.engine: return
        needle = norm(self.search_var.get())
        rs = list(self.engine.resources.values())
        for _, tree in [self.resources_page, self.transport_page, self.geography_page, self.downloads_page, self.coverage_page]:
            for item in tree.get_children(): tree.delete(item)
        idx_map = Counter()
        for r in rs:
            searchable = norm(" ".join(str(r.get(k, "")) for k in ["dataset_title", "name", "description", "host", "mode", "category", "relative_path"]))
            if needle and needle not in searchable: continue
            cat = r.get("category", "Other")
            gov = ", ".join(r.get("governorates") or [])
            fmt = r.get("detected_format") or r.get("format", "")
            status = r.get("validation_status") or r.get("download_status", "")

            if self.category_var.get() in {"All", cat}:
                tag = "even" if idx_map["res"] % 2 == 0 else "odd"
                self.resources_page[1].insert("", "end", tags=(tag,), values=(cat, r.get("dataset_title"), r.get("name"), fmt, r.get("relevance_score"), r.get("host"), status))
                idx_map["res"] += 1
            if cat == "Transport":
                tag = "even" if idx_map["tr"] % 2 == 0 else "odd"
                self.transport_page[1].insert("", "end", tags=(tag,), values=(r.get("mode"), r.get("dataset_title"), r.get("name"), fmt, r.get("relevance_score"), gov, status))
                idx_map["tr"] += 1
            if cat in {"Administrative geography", "Useful geography"}:
                tag = "even" if idx_map["geo"] % 2 == 0 else "odd"
                self.geography_page[1].insert("", "end", tags=(tag,), values=(cat, r.get("dataset_title"), r.get("name"), fmt, gov, status))
                idx_map["geo"] += 1
            if r.get("download_status") not in {None, "Not attempted"}:
                tag = "even" if idx_map["dl"] % 2 == 0 else "odd"
                self.downloads_page[1].insert("", "end", tags=(tag,), values=(cat, r.get("name"), r.get("download_status"), fmt, f"{r.get('bytes_downloaded', 0)/1024:.1f} KB" if r.get("bytes_downloaded") else "—", r.get("local_path", "")))
                idx_map["dl"] += 1

        cov_data = self.engine.coverage_report()["governorates"]
        for i, (gov, row) in enumerate(cov_data.items()):
            tag = "even" if i % 2 == 0 else "odd"
            self.coverage_page[1].insert("", "end", tags=(tag,), values=(gov, row["metadata_matches"], row["transport_metadata_matches"], row["administrative_geography_resources"], row["db_extracted_stops"], row["evidence"]))
        self.tunisia_map.update_data(cov_data, self.engine.map_features)
        self._on_map_gov_select(self.tunisia_map.selected_gov)


if __name__ == "__main__":
    App().mainloop()
