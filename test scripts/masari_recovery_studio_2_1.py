"""
MASARI Data Recovery Studio 2.1
Nationwide Tunisia transport + useful geographic data recovery from CKAN.

Install:
    py -m pip install customtkinter requests truststore matplotlib
Run:
    py masari_recovery_studio_2_1.py

The catalogue search is nationwide. The four initial MASARI launch areas are NOT
used as extraction filters. Metadata is retained for all discovered datasets;
only relevant resources are downloaded.
"""
from __future__ import annotations
import csv, hashlib, json, mimetypes, os, queue, re, threading, time, zipfile
from collections import Counter
from datetime import datetime
from email.message import Message
from pathlib import Path
from urllib.parse import urlparse, unquote

import customtkinter as ctk
import requests
import truststore
from tkinter import ttk, filedialog, messagebox

APP_TITLE = "MASARI | Data Recovery Studio 2.1"
CKAN_BASE = "https://catalog.data.gov.tn/api/3/action"
BLOCKED_HOSTS = {"data.transport.tn"}
USER_AGENT = "MASARI-Data-Recovery-Studio/2.1"

# Search terms are discovery queries, not geographic restrictions.
OPERATORS = ["TRANSTU", "SNCFT", "RFR", "SNTRI", "SORETRAS", "SORETRAK", "STS",
             "SRTJ", "SRT KEF", "SRTB", "SRTGN", "SRTM", "SRTG", "SRT Kairouan",
             "SRT Sousse", "SRT Monastir", "SRT Mahdia", "SRT Nabeul", "SRT Bizerte"]
MODES = ["bus", "autobus", "transport urbain", "transport interurbain", "transport rural",
         "métro", "metro léger", "train", "chemin de fer", "ferroviaire", "RFR",
         "taxi collectif", "taxi louage", "louage", "transport collectif", "transport public",
         "transport scolaire", "transport universitaire", "gare routière", "gare ferroviaire",
         "station", "arrêt bus", "arret bus", "ligne bus", "itinéraire transport",
         "horaire bus", "horaires transport", "horaire train", "tarif transport", "GTFS",
         "arrêts", "stops", "timetable", "schedule", "fare", "route network"]
GEO_TERMS = ["découpage administratif Tunisie", "gouvernorats Tunisie", "délégations Tunisie",
             "municipalités Tunisie", "communes Tunisie", "limites administratives",
             "frontières administratives", "localités Tunisie", "villes Tunisie",
             "codes géographiques Tunisie", "référentiel géographique", "GeoJSON Tunisie",
             "shapefile Tunisie", "carte administrative Tunisie", "coordonnées stations transport"]
GOVERNORATES = ["Tunis", "Ariana", "Ben Arous", "Manouba", "Nabeul", "Zaghouan", "Bizerte",
                "Béja", "Jendouba", "Le Kef", "Siliana", "Sousse", "Monastir", "Mahdia",
                "Sfax", "Kairouan", "Kasserine", "Sidi Bouzid", "Gabès", "Médenine",
                "Tataouine", "Gafsa", "Tozeur", "Kébili"]
# Alternate spellings improve catalogue discovery; these are not assumed to be official names.
GOV_ALIASES = {"Tunis": ["Tunis"], "Ariana": ["Ariana"], "Ben Arous": ["Ben Arous", "Ben Arous"],
 "Manouba": ["Manouba", "La Manouba"], "Nabeul": ["Nabeul", "Nabeul"], "Zaghouan": ["Zaghouan"],
 "Bizerte": ["Bizerte"], "Béja": ["Beja", "Béja"], "Jendouba": ["Jendouba"],
 "Le Kef": ["Kef", "Le Kef", "El Kef"], "Siliana": ["Siliana"], "Sousse": ["Sousse"],
 "Monastir": ["Monastir"], "Mahdia": ["Mahdia"], "Sfax": ["Sfax"], "Kairouan": ["Kairouan"],
 "Kasserine": ["Kasserine"], "Sidi Bouzid": ["Sidi Bouzid"], "Gabès": ["Gabes", "Gabès"],
 "Médenine": ["Medenine", "Médenine"], "Tataouine": ["Tataouine"], "Gafsa": ["Gafsa"],
 "Tozeur": ["Tozeur"], "Kébili": ["Kebili", "Kébili"]}

GTFS_REQUIRED = {"agency.txt", "stops.txt", "routes.txt", "trips.txt", "stop_times.txt"}
GTFS_RECOMMENDED = {"calendar.txt", "calendar_dates.txt"}
TRANSPORT_HINTS = {
 "gtfs": 35, "stop_times": 35, "agency.txt": 24, "routes.txt": 25, "trips.txt": 25,
 "stops.txt": 25, "transport": 9, "transport public": 18, "transport collectif": 18,
 "transtu": 22, "sncft": 22, "sntri": 20, "soretras": 20, "soretrak": 20,
 "horaire": 16, "horaires": 16, "timetable": 16, "schedule": 14, "bus": 12,
 "autobus": 14, "métro": 14, "metro": 14, "train": 14, "ferroviaire": 14,
 "gare": 10, "station": 9, "arrêt": 13, "arret": 13, "taxi collectif": 18,
 "louage": 18, "itinéraire": 12, "itineraire": 12, "ligne": 8, "tarif": 9,
 "fare": 9, "rfr": 15, "srt": 10, "transport rural": 16
}
ADMIN_HINTS = {
 "gouvernorat": 18, "gouvernorats": 18, "délégation": 18, "delegation": 18,
 "municipalité": 18, "municipalite": 18, "commune": 14, "découpage administratif": 24,
 "decoupage administratif": 24, "limites administratives": 24, "frontière administrative": 18,
 "frontiere administrative": 18, "localité": 12, "localite": 12, "code géographique": 16,
 "code geographique": 16, "geojson": 12, "shapefile": 12, "geopackage": 12,
 "gpkg": 12, "administratif": 10, "carte administrative": 18
}
GEO_USEFUL_HINTS = {"latitude": 5, "longitude": 5, "coordonnée": 7, "coordonnees": 7,
                    "géographique": 5, "geographique": 5, "cartographie": 5, "localité": 8,
                    "localite": 8, "ville": 3, "station": 4, "arrêt": 5, "arret": 5,
                    "route": 3, "réseau": 3, "reseau": 3}

FIELDS = ["id", "category", "subcategories", "mode", "governorates", "coverage_confidence",
 "dataset_title", "organization", "name", "format", "detected_format", "url", "final_url",
 "host", "relevance", "relevance_score", "validation_status", "download_status", "local_path",
 "bytes_downloaded", "sha256", "duplicate_of", "description", "dataset_id", "retrieved_at"]


def norm(s):
    s = str(s or "").lower()
    return re.sub(r"\s+", " ", s.replace("’", "'")).strip()

def safe_name(value):
    value = unquote(str(value or "resource"))
    value = re.sub(r"[^\w.\-]+", "_", value, flags=re.UNICODE).strip("._")
    return value[:130] or "resource"

def classify_resource(dataset_title, description, resource_name, url=""):
    text = norm(f"{dataset_title} {description} {resource_name} {url}")
    ts = sum(w for term, w in TRANSPORT_HINTS.items() if term in text)
    admin = sum(w for term, w in ADMIN_HINTS.items() if term in text)
    geo = admin + sum(w for term, w in GEO_USEFUL_HINTS.items() if term in text)
    ext = Path(urlparse(url).path).suffix.lower()
    if ext in {".geojson", ".shp", ".shx", ".dbf", ".prj", ".gpkg", ".kml", ".gpx"}:
        geo += 10
    if any(x in text for x in ("stop_times.txt", "agency.txt", "routes.txt", "gtfs")):
        ts += 25
    # Avoid treating generic coordinate-rich datasets as administrative geography.
    if ts >= 12 and ts >= admin * 0.75:
        category = "Transport"
        sub = ["transport_network"]
        if any(x in text for x in ("horaire", "schedule", "timetable")): sub.append("timetables")
        if any(x in text for x in ("tarif", "fare", "prix")): sub.append("fares")
        if any(x in text for x in ("arrêt", "arret", "stop", "station", "gare")): sub.append("stops_stations")
        if any(x in text for x in ("ligne", "route", "itinéraire", "itineraire")): sub.append("routes_lines")
        score = ts
    elif admin >= 14:
        category, sub, score = "Administrative geography", ["administrative_reference"], admin
        if any(x in text for x in ("gouvernorat", "delegation", "délégation")): sub.append("governorates_delegations")
        if any(x in text for x in ("municipalité", "municipalite", "commune")): sub.append("municipalities")
        if any(x in text for x in ("limite", "frontière", "frontiere", "geojson", "shapefile")): sub.append("boundaries")
    elif geo >= 12 and (any(x in text for x in ("station", "arrêt", "arret", "localité", "localite", "ville", "coordonnée", "coordonnees", "cartographie"))):
        category, sub, score = "Useful geography", ["geographic_reference"], geo
    else:
        category, sub, score = "Other", [], max(ts, geo)
    mode = "General transport"
    if category == "Transport":
        matches = []
        for label, terms in [("Bus", ["bus", "autobus", "soretras", "soretrak", "transtu", "srt"]),
          ("Metro / Light rail", ["métro", "metro", "light rail"]),
          ("Train / RFR", ["sncft", "train", "ferroviaire", "rfr", "sntri"]),
          ("Taxi collectif", ["taxi collectif"]), ("Louage", ["louage"]),
          ("Stops / Stations", ["arrêt", "arret", "station", "gare", "stop"]),
          ("Fares / Timetables", ["tarif", "fare", "horaire", "schedule", "timetable"])]:
            if any(t in text for t in terms): matches.append(label)
        mode = "; ".join(matches) if matches else "General transport"
    elif category in {"Administrative geography", "Useful geography"}:
        mode = "Administrative / geographic reference"
    level = "Very high" if score >= 45 else "High" if score >= 25 else "Medium" if score >= 12 else "Low"
    govs = []
    for official, aliases in GOV_ALIASES.items():
        if any(norm(a) in text for a in aliases): govs.append(official)
    return category, sub, mode, min(score, 300), level, govs


def sniff_format(path: Path, content_type=""):
    try:
        with path.open("rb") as f: head = f.read(8192)
    except OSError:
        return "UNKNOWN"
    h = head.lstrip(b"\xef\xbb\xbf\x00\t\r\n ")
    if head.startswith(b"PK\x03\x04"):
        try:
            with zipfile.ZipFile(path) as z:
                names = {Path(n.replace("\\", "/")).name.lower() for n in z.namelist()}
                if "stops.txt" in names and "routes.txt" in names: return "GTFS-ZIP"
                if any(n.endswith(".shp") for n in names): return "SHAPEFILE-ZIP"
                if any(n.endswith(".geojson") for n in names): return "GEOJSON-ZIP"
        except Exception: pass
        return "ZIP"
    if head.startswith(b"%PDF-"): return "PDF"
    if head.startswith(bytes.fromhex("D0CF11E0A1B11AE1")): return "XLS"
    if head.startswith(b"SQLite format 3\x00"): return "SQLITE/GPKG"
    if h.startswith((b"{", b"[")):
        try:
            obj = json.loads(h.decode("utf-8-sig"))
            if isinstance(obj, dict) and obj.get("type") in {"FeatureCollection", "Feature", "GeometryCollection"}: return "GEOJSON"
            return "JSON"
        except Exception: pass
    if b"," in head or b";" in head or b"\t" in head:
        try:
            sample = h.decode("utf-8-sig", errors="strict")
            if len(sample.splitlines()) >= 2: return "CSV/TEXT"
        except Exception: pass
    ct = norm(content_type)
    if "json" in ct: return "JSON"
    if "csv" in ct: return "CSV"
    if "excel" in ct or "spreadsheet" in ct: return "XLSX"
    if "html" in ct: return "HTML"
    if "xml" in ct: return "XML"
    return "UNKNOWN"


class RecoveryEngine:
    def __init__(self, out_dir, events, stop_event, max_file_mb=250, max_pages_per_term=20):
        self.out_dir, self.events, self.stop_event = out_dir, events, stop_event
        self.max_file_bytes = max_file_mb * 1024 * 1024
        self.max_pages_per_term = max_pages_per_term
        self.session = requests.Session(); self.session.headers.update({"User-Agent": USER_AGENT})
        self.datasets, self.resources = {}, {}
        self.stats = Counter(); self.started = time.time()
        self.retrieved_at = datetime.now().astimezone().isoformat(timespec="seconds")
        self.gtfs_reports, self.quality_issues = [], []
        self.seen_hashes = {}; self.seen_urls = set()

    def emit(self, kind, **data): self.events.put({"kind": kind, **data})
    def api(self, action, params=None, timeout=25):
        if self.stop_event.is_set(): return None
        try:
            r = self.session.get(f"{CKAN_BASE}/{action}", params=params or {}, timeout=(8, timeout))
            r.raise_for_status(); payload = r.json()
            if payload.get("success"): return payload.get("result")
            self.stats["api_errors"] += 1
            self.emit("log", level="WARN", message=f"{action}: CKAN success=false")
        except Exception as e:
            self.stats["api_errors"] += 1
            self.emit("log", level="WARN", message=f"{action}: {str(e)[:160]}")
        return None

    def search_terms(self):
        terms = [("Transport", x) for x in dict.fromkeys(OPERATORS + MODES)]
        terms += [("Geography", x) for x in GEO_TERMS]
        # Explicit governorate queries improve geographic discovery without restricting results.
        for gov in GOVERNORATES: terms.append(("Governorate coverage", f"transport {gov} Tunisie"))
        for gov in GOVERNORATES: terms.append(("Governorate geography", f"données géographiques {gov}"))
        return terms

    def search_datasets(self):
        terms = self.search_terms(); found = {}
        self.emit("stage", name="Nationwide discovery", detail=f"Searching {len(terms)} nationwide CKAN queries · all 24 governorates")
        for idx, (group, term) in enumerate(terms, 1):
            if self.stop_event.is_set(): break
            start = 0; count = None
            for _ in range(self.max_pages_per_term):
                if self.stop_event.is_set(): break
                result = self.api("package_search", {"q": term, "rows": 100, "start": start, "include_private": False})
                if not result: break
                items = result.get("results", []) or []; count = int(result.get("count") or 0)
                for item in items:
                    if item.get("id"):
                        old = found.get(item["id"])
                        if old is None or len(item) > len(old): found[item["id"]] = item
                self.stats["search_pages"] += 1
                if not items or start + len(items) >= count: break
                start += len(items)
            self.stats["searches"] += 1
            self.emit("progress", value=18 * idx / max(1, len(terms)), detail=f"{group}: {term} ({count if count is not None else 'no result'})")
        self.datasets.update(found); self.stats["datasets_found"] = len(found)
        self.emit("metric", name="datasets", value=len(found))
        self.emit("log", level="SUCCESS", message=f"Nationwide discovery: {len(found)} unique datasets")
        return list(found)

    def fetch_dataset_details(self, ids):
        self.emit("stage", name="Indexing dataset metadata", detail="Collecting publisher, tags, notes, dates, resources and source identifiers")
        total = max(1, len(ids))
        for i, did in enumerate(ids, 1):
            if self.stop_event.is_set(): break
            detail = self.api("package_show", {"id": did})
            if detail:
                self.datasets[did] = detail; self.stats["dataset_details_ok"] += 1
                org = (detail.get("organization") or {}).get("title", "")
                for raw in detail.get("resources", []) or []:
                    rid = str(raw.get("id") or raw.get("url") or "")
                    if not rid: continue
                    row = dict(raw); row.update({"dataset_id": did, "dataset_title": detail.get("title", ""),
                      "dataset_notes": detail.get("notes", ""), "organization": org,
                      "retrieved_at": self.retrieved_at})
                    if rid not in self.resources: self.resources[rid] = row
                    else:
                        for k, v in row.items():
                            if self.resources[rid].get(k) in (None, "", []): self.resources[rid][k] = v
            else: self.stats["dataset_details_failed"] += 1
            self.emit("progress", value=18 + 30 * i / total, detail=f"Dataset metadata {i}/{total}")
            if i % 10 == 0 or i == total: self.emit("metric", name="resources", value=len(self.resources))
        self.stats["resources_found"] = len(self.resources)
        self.emit("log", level="SUCCESS", message=f"Indexed {len(self.resources)} unique resource records")

    def enrich_resources(self):
        self.emit("stage", name="Classifying nationwide resources", detail="Transport · administrative geography · useful geography · other")
        rows = list(self.resources.values()); total = max(1, len(rows))
        for i, r in enumerate(rows, 1):
            if self.stop_event.is_set(): break
            url = r.get("url") or ""; host = urlparse(url).hostname or ""
            category, sub, mode, score, level, govs = classify_resource(
                r.get("dataset_title", ""), r.get("description", "") or r.get("dataset_notes", ""), r.get("name", "") or url, url)
            r.update({"category": category, "subcategories": ";".join(sub), "mode": mode,
              "relevance_score": score, "relevance": level, "host": host,
              "format": str(r.get("format") or Path(urlparse(url).path).suffix.lstrip(".") or "UNKNOWN").upper(),
              "governorates": govs, "coverage_confidence": "Name/metadata match" if govs else "Not identified",
              "download_status": "Not attempted", "validation_status": "Not validated"})
            self.stats[f"category_{category.lower().replace(' ', '_')}"] += 1
            self.emit("progress", value=48 + 10 * i / total, detail=f"Classifying {i}/{total}")
        for metric, cat in [("transport", "Transport"), ("admin_geo", "Administrative geography"), ("useful_geo", "Useful geography"), ("other", "Other")]:
            self.emit("metric", name=metric, value=sum(r.get("category") == cat for r in rows))

    def _filename(self, resource, response, index):
        filename = ""
        disp = response.headers.get("content-disposition", "")
        if disp:
            msg = Message(); msg["content-disposition"] = disp; filename = msg.get_filename() or ""
        if not filename: filename = resource.get("name") or Path(urlparse(response.url).path).name
        filename = safe_name(filename or f"resource_{index}")
        return filename

    def validate_file(self, path, resource, content_type):
        detected = sniff_format(path, content_type); issues = []; status = "Valid / inspected"
        if path.stat().st_size == 0: return detected, "Invalid · empty file", ["zero_byte_file"]
        if detected == "ZIP":
            try:
                with zipfile.ZipFile(path) as z: bad = z.testzip()
                if bad: status = "Invalid · corrupt ZIP"; issues.append(f"corrupt_member:{bad}")
                else: status = "Valid ZIP · contents not identified"
            except Exception as e: status = "Invalid · ZIP error"; issues.append(str(e)[:120])
        elif detected == "GTFS-ZIP": self.inspect_gtfs(path, resource)
        elif detected == "GEOJSON":
            try:
                obj = json.loads(path.read_text(encoding="utf-8-sig"))
                if obj.get("type") not in {"FeatureCollection", "Feature", "GeometryCollection"}: raise ValueError("Not a GeoJSON geometry object")
                if obj.get("type") == "FeatureCollection" and not isinstance(obj.get("features"), list): raise ValueError("features must be an array")
                status = "Valid GeoJSON structure"
            except Exception as e: status = "Invalid · GeoJSON"; issues.append(str(e)[:140])
        elif detected == "JSON":
            try: json.loads(path.read_text(encoding="utf-8-sig")); status = "Valid JSON"
            except Exception as e: status = "Invalid · JSON"; issues.append(str(e)[:140])
        elif detected in {"CSV/TEXT", "CSV"}:
            try:
                with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as f:
                    sample = f.read(8192); f.seek(0); dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
                    reader = csv.reader(f, dialect); header = next(reader, [])
                resource["detected_columns"] = header[:100]
                if len(header) < 2: status = "Review · weak CSV structure"
                else: status = "CSV readable · schema requires review"
            except Exception as e: status = "Review · text/CSV"; issues.append(str(e)[:120])
        elif detected == "PDF": status = "PDF signature valid · text/content not extracted"
        elif detected in {"XLS", "XLSX", "SQLITE/GPKG", "HTML", "XML"}: status = f"Detected {detected} · deeper parser not installed"
        else: status = "Unknown format · preserved original bytes"
        return detected, status, issues

    def inspect_gtfs(self, path, resource):
        report = {"resource_id": resource.get("id"), "dataset_title": resource.get("dataset_title"),
          "file": str(path), "valid_zip": False, "files": [], "missing_required": sorted(GTFS_REQUIRED),
          "missing_recommended": sorted(GTFS_RECOMMENDED), "status": "Not a readable GTFS ZIP"}
        try:
            with zipfile.ZipFile(path) as z:
                names = {Path(n.replace("\\", "/")).name.lower() for n in z.namelist() if not n.endswith("/")}
                required = GTFS_REQUIRED <= names
                report.update({"valid_zip": z.testzip() is None, "files": sorted(names),
                  "missing_required": sorted(GTFS_REQUIRED - names), "missing_recommended": sorted(GTFS_RECOMMENDED - names),
                  "status": "Core GTFS files present" if required else "Incomplete / non-standard GTFS"})
                # Check required text files have readable headers.
                header_checks = {}
                for fname in GTFS_REQUIRED & names:
                    member = next(n for n in z.namelist() if Path(n.replace("\\", "/")).name.lower() == fname)
                    try:
                        line = z.read(member).decode("utf-8-sig", errors="replace").splitlines()[0]
                        header_checks[fname] = [x.strip().lower() for x in next(csv.reader([line]))]
                    except Exception: header_checks[fname] = []
                report["header_checks"] = header_checks
                if required and all(header_checks.values()): report["status"] = "Core GTFS present · headers readable"
                self.stats["gtfs_archives"] += 1
                if required: self.stats["gtfs_core_complete"] += 1
        except Exception as e: report["status"] = f"ZIP inspection failed: {str(e)[:120]}"
        self.gtfs_reports.append(report)
        self.emit("log", level="INFO", message=f"GTFS inspection · {report['status']} · {path.name}")

    def download_resources(self):
        eligible = [r for r in self.resources.values() if r.get("category") in {"Transport", "Administrative geography", "Useful geography"} and r.get("relevance_score", 0) >= 12 and r.get("url")]
        eligible.sort(key=lambda r: (r.get("category") == "Transport", r.get("relevance_score", 0)), reverse=True)
        self.emit("stage", name="Recovering relevant resources", detail=f"{len(eligible)} candidates · max {self.max_file_bytes // (1024*1024)} MB each · all Tunisia")
        base = self.out_dir / "downloaded"; base.mkdir(parents=True, exist_ok=True)
        # Reuse previous manifest hashes so reruns do not save identical payloads again.
        manifest = self.out_dir / "download_manifest.json"
        if manifest.exists():
            try:
                for x in json.loads(manifest.read_text(encoding="utf-8")):
                    if x.get("sha256") and x.get("local_path"): self.seen_hashes[x["sha256"]] = x["local_path"]
            except Exception: pass
        total = max(1, len(eligible))
        for i, r in enumerate(eligible, 1):
            if self.stop_event.is_set(): break
            url = str(r.get("url") or ""); host = urlparse(url).hostname or ""
            if not url.startswith(("http://", "https://")):
                r["download_status"] = "Skipped · invalid URL"; self.stats["skipped"] += 1
            elif host in BLOCKED_HOSTS:
                r["download_status"] = "Skipped · known unreachable host"; self.stats["skipped"] += 1
            elif url in self.seen_urls:
                r["download_status"] = "Skipped · duplicate URL"; self.stats["duplicates"] += 1
            else:
                self.seen_urls.add(url); tmp = None
                try:
                    with self.session.get(url, timeout=(10, 40), stream=True, allow_redirects=True) as resp:
                        resp.raise_for_status(); final_host = urlparse(resp.url).hostname or ""
                        if final_host in BLOCKED_HOSTS: raise ValueError("Redirected to known unreachable host")
                        length = int(resp.headers.get("content-length") or 0)
                        if length and length > self.max_file_bytes: raise ValueError("File exceeds configured size limit")
                        folder = base / ("transport" if r["category"] == "Transport" else "geography")
                        folder.mkdir(parents=True, exist_ok=True)
                        stem = safe_name(r.get("id") or str(i))[:30]
                        suggested = self._filename(r, resp, i)
                        tmp = folder / f"{stem}_{suggested}.part"
                        digest = hashlib.sha256(); size = 0
                        with tmp.open("wb") as f:
                            for chunk in resp.iter_content(128 * 1024):
                                if self.stop_event.is_set(): break
                                if not chunk: continue
                                size += len(chunk)
                                if size > self.max_file_bytes: raise ValueError("File exceeded configured size limit while streaming")
                                digest.update(chunk); f.write(chunk)
                        if self.stop_event.is_set():
                            tmp.unlink(missing_ok=True); r["download_status"] = "Stopped"
                        else:
                            sha = digest.hexdigest(); detected = sniff_format(tmp, resp.headers.get("content-type", ""))
                            if sha in self.seen_hashes:
                                tmp.unlink(missing_ok=True); r.update({"sha256": sha, "duplicate_of": self.seen_hashes[sha], "download_status": "Duplicate content"}); self.stats["duplicates"] += 1
                            else:
                                extmap = {"GTFS-ZIP": ".zip", "SHAPEFILE-ZIP": ".zip", "GEOJSON-ZIP": ".zip", "ZIP": ".zip", "GEOJSON": ".geojson", "JSON": ".json", "CSV/TEXT": ".csv", "CSV": ".csv", "PDF": ".pdf", "XLS": ".xls", "XLSX": ".xlsx", "SQLITE/GPKG": ".gpkg", "HTML": ".html", "XML": ".xml"}
                                original_ext = Path(suggested).suffix
                                ext = extmap.get(detected, original_ext or ".bin")
                                clean_stem = Path(suggested).stem or "resource"
                                final = folder / f"{stem}_{safe_name(clean_stem)}{ext}"
                                n = 2
                                while final.exists(): final = folder / f"{stem}_{safe_name(clean_stem)}_{n}{ext}"; n += 1
                                tmp.replace(final)
                                detected, validation, issues = self.validate_file(final, r, resp.headers.get("content-type", ""))
                                r.update({"sha256": sha, "detected_format": detected, "validation_status": validation,
                                  "download_status": "Downloaded", "local_path": str(final), "bytes_downloaded": size,
                                  "final_url": resp.url, "host": final_host})
                                if issues: self.quality_issues.append({"resource_id": r.get("id"), "file": str(final), "issues": issues})
                                self.seen_hashes[sha] = str(final); self.stats["downloaded"] += 1; self.stats["bytes_downloaded"] += size
                                self.emit("log", level="SUCCESS", message=f"Downloaded [{r['category']}] {final.name} · {size/1024:.1f} KB · {detected}")
                except Exception as e:
                    if tmp and tmp.exists(): tmp.unlink(missing_ok=True)
                    r["download_status"] = f"Failed · {str(e)[:130]}"; self.stats["failed"] += 1
                    self.emit("log", level="WARN", message=f"Download failed · {r.get('name') or url} · {str(e)[:150]}")
            self.emit("progress", value=58 + 37 * i / total, detail=f"Download/validation {i}/{total}")
            if i % 5 == 0 or i == total:
                self.emit("metric", name="downloaded", value=self.stats["downloaded"])
        for r in self.resources.values():
            if r.get("download_status") == "Not attempted":
                if r.get("category") == "Other": r["download_status"] = "Not selected · other"
                elif r.get("relevance_score", 0) < 12: r["download_status"] = "Not selected · low confidence"
                else: r["download_status"] = "Not selected · no URL"

    def coverage_report(self):
        rows = list(self.resources.values()); coverage = {}
        for gov in GOVERNORATES:
            matched = [r for r in rows if gov in (r.get("governorates") or [])]
            coverage[gov] = {"matched_resources": len(matched), "transport_resources": sum(r.get("category") == "Transport" for r in matched),
              "geographic_resources": sum(r.get("category") in {"Administrative geography", "Useful geography"} for r in matched),
              "evidence": "Dataset/resource title or description match" if matched else "No explicit match found"}
        operator_coverage = {}
        for op in OPERATORS:
            hits = [r for r in rows if op.lower() in norm(f"{r.get('dataset_title')} {r.get('organization')} {r.get('name')} {r.get('description')}")]
            operator_coverage[op] = len(hits)
        return {"scope": "Nationwide Tunisia · all 24 governorates; not restricted to launch cities", "governorates": coverage,
          "operator_name_matches": operator_coverage,
          "warning": "Coverage is inferred from catalogue metadata text. A match does not prove service coverage; absence of a match does not prove no service exists."}

    def write_outputs(self):
        self.out_dir.mkdir(parents=True, exist_ok=True)
        ds, rs = list(self.datasets.values()), list(self.resources.values())
        def wjson(name, obj): (self.out_dir / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        def wcsv(name, rows):
            with (self.out_dir / name).open("w", newline="", encoding="utf-8-sig") as f:
                wr = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore"); wr.writeheader(); wr.writerows(rows)
        wjson("datasets.json", ds); wjson("resources.json", rs); wcsv("resources_index.csv", rs)
        wcsv("transport_resources.csv", [r for r in rs if r.get("category") == "Transport"])
        wcsv("administrative_geography.csv", [r for r in rs if r.get("category") == "Administrative geography"])
        wcsv("useful_geography.csv", [r for r in rs if r.get("category") == "Useful geography"])
        wcsv("failed_resources.csv", [r for r in rs if str(r.get("download_status", "")).startswith("Failed")])
        wcsv("priority_resources.csv", [r for r in rs if r.get("category") != "Other" and r.get("relevance") in {"Very high", "High"}])
        wjson("gtfs_inspection.json", self.gtfs_reports); wjson("quality_issues.json", self.quality_issues)
        wjson("coverage_by_governorate.json", self.coverage_report())
        manifest = [{"sha256": r.get("sha256"), "local_path": r.get("local_path"), "resource_id": r.get("id"), "url": r.get("url")} for r in rs if r.get("sha256") and r.get("local_path")]
        # Preserve older manifest entries as well.
        old = self.out_dir / "download_manifest.json"
        try:
            prior = json.loads(old.read_text(encoding="utf-8")) if old.exists() else []
            by_hash = {x.get("sha256"): x for x in prior if x.get("sha256")}
            by_hash.update({x.get("sha256"): x for x in manifest if x.get("sha256")})
            manifest = list(by_hash.values())
        except Exception: pass
        wjson("download_manifest.json", manifest)
        cats = Counter(r.get("category", "Other") for r in rs); fmts = Counter(r.get("detected_format") or r.get("format", "UNKNOWN") for r in rs)
        report = {"application": APP_TITLE, "generated_at": self.retrieved_at, "catalogue": CKAN_BASE,
          "collection_scope": "Nationwide Tunisia; all 24 governorates; no launch-city restriction",
          "launch_cities_are_not_extraction_filters": True, "governorates": GOVERNORATES,
          "datasets_found": len(ds), "dataset_details_ok": self.stats["dataset_details_ok"],
          "dataset_details_failed": self.stats["dataset_details_failed"], "resources_found": len(rs),
          "category_counts": dict(cats), "format_counts": dict(fmts), "downloaded": self.stats["downloaded"],
          "failed": self.stats["failed"], "skipped": self.stats["skipped"], "duplicates": self.stats["duplicates"],
          "bytes_downloaded": self.stats["bytes_downloaded"], "api_errors": self.stats["api_errors"],
          "searches": self.stats["searches"], "search_pages": self.stats["search_pages"],
          "gtfs_archives": self.stats["gtfs_archives"], "gtfs_core_complete": self.stats["gtfs_core_complete"],
          "coverage_summary": self.coverage_report(), "stopped_by_user": self.stop_event.is_set(),
          "notes": ["All 24 governorates are included in discovery queries; results are not geographically filtered.",
            "Coverage is inferred from metadata text and is not proof of actual service coverage.",
            "All discovered dataset/resource metadata is exported, including resources not downloaded.",
            "Classification is heuristic; inspect source metadata and validation status before production use.",
            "GTFS core filenames and readable headers are checked; full GTFS semantic validation is not performed.",
            "XLS/XLSX/PDF content extraction is not performed; original files are preserved.",
            "Static catalogue data does not imply live vehicle positions or real-time service guarantees."]}
        wjson("extraction_report.json", report)
        self.emit("log", level="SUCCESS", message="Exported nationwide metadata, category indexes, coverage, GTFS and quality reports")

    def run(self):
        try:
            truststore.inject_into_ssl()
            self.emit("stage", name="Connecting to National Catalogue", detail="CKAN API · HTTPS · Windows trust store")
            status = self.api("status_show", timeout=20)
            if not status: raise RuntimeError("National catalogue API did not respond successfully.")
            self.emit("log", level="SUCCESS", message=f"Connected · CKAN {status.get('ckan_version', 'version unknown')}")
            ids = self.search_datasets()
            if not ids: raise RuntimeError("No datasets discovered. Check connection and try again.")
            self.fetch_dataset_details(ids); self.enrich_resources()
            if not self.stop_event.is_set(): self.download_resources()
            else: self.emit("log", level="WARN", message="Stop requested; download phase skipped")
            self.write_outputs(); elapsed = time.time() - self.started; stopped = self.stop_event.is_set()
            self.emit("progress", value=100, detail="Partial recovery saved" if stopped else "Recovery complete")
            self.emit("done", stats=dict(self.stats), elapsed=elapsed, stopped=stopped,
              datasets=len(self.datasets), resources=len(self.resources), out_dir=str(self.out_dir))
        except Exception as e:
            try: self.write_outputs()
            except Exception: pass
            self.emit("fatal", message=str(e))


class App(ctk.CTk):
    def __init__(self):
        super().__init__(); self.title(APP_TITLE); self.geometry("1500x920"); self.minsize(1150, 720)
        ctk.set_appearance_mode("dark"); ctk.set_default_color_theme("blue")
        self.bg="#0B1020"; self.panel="#121A2D"; self.line="#26344D"; self.text="#F2F5FA"; self.muted="#8FA0B8"; self.cyan="#35C8D0"; self.green="#42D39A"; self.orange="#FF9F43"; self.red="#FF647C"
        self.events=queue.Queue(); self.stop_event=threading.Event(); self.worker=None; self.engine=None
        self.output_dir=Path.home()/"Documents"/"MASARI_Recovery_2_1"; self.status_var=ctk.StringVar(value="READY"); self.search_var=ctk.StringVar(value=""); self.category_var=ctk.StringVar(value="All")
        self._style(); self._build(); self.after(150,self._poll)
    def _style(self):
        s=ttk.Style(); s.theme_use("clam"); s.configure("Treeview",background=self.panel,foreground="#E8EEF8",fieldbackground=self.panel,rowheight=27,borderwidth=0,font=("Segoe UI",9)); s.configure("Treeview.Heading",background="#1B2941",foreground="#AFC0D8",relief="flat",font=("Segoe UI Semibold",9)); s.map("Treeview",background=[("selected","#244A65")],foreground=[("selected","#FFFFFF")])
    def _build(self):
        self.grid_columnconfigure(1,weight=1); self.grid_rowconfigure(0,weight=1)
        side=ctk.CTkFrame(self,width=235,corner_radius=0,fg_color="#0E1628"); side.grid(row=0,column=0,sticky="nsew"); side.grid_propagate(False)
        ctk.CTkLabel(side,text="MASARI",font=("Segoe UI Black",22),text_color=self.cyan).pack(anchor="w",padx=22,pady=(25,3)); ctk.CTkLabel(side,text="DATA RECOVERY STUDIO 2.1",font=("Segoe UI",8),text_color=self.muted).pack(anchor="w",padx=23,pady=(0,25))
        self.nav={};
        for name in ["Overview","Datasets","Transport","Geography","Resources","Downloads","Coverage","Activity"]:
            b=ctk.CTkButton(side,text="  "+name,anchor="w",height=37,fg_color="#1B2A43" if name=="Overview" else "transparent",hover_color="#1B2A43",command=lambda n=name:self.show_page(n)); b.pack(fill="x",padx=13,pady=2); self.nav[name]=b
        ctk.CTkLabel(side,text="OUTPUT DIRECTORY",font=("Segoe UI Semibold",9),text_color="#60728F").pack(anchor="w",padx=20,pady=(22,5)); self.path_label=ctk.CTkLabel(side,text=str(self.output_dir),wraplength=190,justify="left",text_color=self.muted,font=("Segoe UI",9)); self.path_label.pack(anchor="w",padx=20,pady=5)
        ctk.CTkButton(side,text="Choose folder",height=31,fg_color="#1B2A43",command=self.choose_folder).pack(fill="x",padx=16,pady=5)
        ctk.CTkLabel(side,text="NATIONWIDE COLLECTION\nALL 24 GOVERNORATES",font=("Segoe UI",8),text_color="#60728F",justify="left").pack(side="bottom",anchor="w",padx=20,pady=20)
        main=ctk.CTkFrame(self,fg_color=self.bg,corner_radius=0); main.grid(row=0,column=1,sticky="nsew"); main.grid_columnconfigure(0,weight=1); main.grid_rowconfigure(1,weight=1)
        head=ctk.CTkFrame(main,fg_color="transparent"); head.grid(row=0,column=0,sticky="ew",padx=25,pady=(18,10)); self.title_label=ctk.CTkLabel(head,text="Recovery overview",font=("Segoe UI Semibold",22),text_color=self.text); self.title_label.pack(side="left")
        self.status=ctk.CTkLabel(head,textvariable=self.status_var,fg_color="#183D3A",text_color=self.green,corner_radius=18,padx=12,pady=6); self.status.pack(side="right",padx=10)
        self.start_btn=ctk.CTkButton(head,text="▶ Start nationwide recovery",width=205,fg_color=self.cyan,text_color="#07131D",hover_color="#22AAB4",command=self.start); self.start_btn.pack(side="right")
        self.stop_btn=ctk.CTkButton(head,text="■ Stop",width=80,fg_color="#482436",state="disabled",command=self.stop); self.stop_btn.pack(side="right",padx=7)
        self.pages=ctk.CTkFrame(main,fg_color="transparent"); self.pages.grid(row=1,column=0,sticky="nsew",padx=25,pady=(0,18)); self.pages.grid_rowconfigure(0,weight=1); self.pages.grid_columnconfigure(0,weight=1)
        self._overview(); self._table_page("Datasets",("title","organization","resources","id"),(370,200,90,300)); self._table_page("Transport",("mode","dataset","resource","format","score","governorates","status"),(160,250,220,85,65,150,180)); self._table_page("Geography",("category","dataset","resource","format","governorates","status"),(170,260,230,90,160,180)); self._table_page("Resources",("category","mode","dataset","resource","format","score","host","status"),(150,150,240,210,85,65,160,180)); self._table_page("Downloads",("category","resource","status","format","size","path"),(150,230,220,100,90,390)); self._table_page("Coverage",("governorate","resources","transport","geography","evidence"),(180,110,110,110,450)); self._activity(); self.show_page("Overview")
    def _overview(self):
        p=ctk.CTkFrame(self.pages,fg_color="transparent"); p.grid_columnconfigure((0,1,2,3),weight=1); p.grid_rowconfigure(1,weight=1); self.overview=p
        self.metrics={}
        for i,(name,color) in enumerate([("Datasets",self.cyan),("Resources", "#A78BFA"),("Transport",self.orange),("Geography",self.green)]):
            card=ctk.CTkFrame(p,fg_color=self.panel,corner_radius=12,border_width=1,border_color=self.line); card.grid(row=0,column=i,sticky="ew",padx=5,pady=(0,12)); ctk.CTkLabel(card,text=name.upper(),text_color=self.muted,font=("Segoe UI Semibold",9)).pack(anchor="w",padx=14,pady=(12,0)); v=ctk.CTkLabel(card,text="0",text_color=color,font=("Segoe UI Semibold",27)); v.pack(anchor="w",padx=14); ctk.CTkLabel(card,text="Nationwide catalogue records",text_color=self.muted,font=("Segoe UI",8)).pack(anchor="w",padx=14,pady=(0,12)); self.metrics[name]=v
        panel=ctk.CTkFrame(p,fg_color=self.panel,corner_radius=12,border_width=1,border_color=self.line); panel.grid(row=1,column=0,columnspan=4,sticky="nsew",pady=4); ctk.CTkLabel(panel,text="NATIONWIDE RECOVERY PIPELINE",font=("Segoe UI Semibold",11),text_color=self.text).pack(anchor="w",padx=16,pady=(15,3)); self.stage=ctk.CTkLabel(panel,text="Waiting to start",font=("Segoe UI Semibold",15),text_color=self.cyan); self.stage.pack(anchor="w",padx=16,pady=(20,2)); self.detail=ctk.CTkLabel(panel,text="All 24 governorates · no launch-city restriction",text_color=self.muted); self.detail.pack(anchor="w",padx=16); self.progress=ctk.CTkProgressBar(panel,progress_color=self.cyan); self.progress.pack(fill="x",padx=16,pady=(20,5)); self.progress.set(0); self.progress_text=ctk.CTkLabel(panel,text="0%",text_color=self.muted); self.progress_text.pack(anchor="e",padx=16)
        ctk.CTkLabel(panel,text="Discovery → metadata indexing → classification → download → file validation → nationwide coverage report",text_color=self.muted,font=("Segoe UI",10)).pack(anchor="w",padx=16,pady=18)
    def _table_page(self,name,cols,widths):
        p=ctk.CTkFrame(self.pages,fg_color=self.panel,corner_radius=12,border_width=1,border_color=self.line); p.grid_columnconfigure(0,weight=1); p.grid_rowconfigure(1,weight=1); setattr(self,name.lower()+"_page",p)
        bar=ctk.CTkFrame(p,fg_color="transparent"); bar.grid(row=0,column=0,sticky="ew",padx=10,pady=10)
        if name in {"Datasets","Resources"}:
            ctk.CTkEntry(bar,placeholder_text="Filter rows…",textvariable=self.search_var,width=260).pack(side="left")
        if name=="Resources": ctk.CTkOptionMenu(bar,variable=self.category_var,values=["All","Transport","Administrative geography","Useful geography","Other"],command=lambda _:self.refresh()).pack(side="left",padx=8)
        tree=ttk.Treeview(p,columns=cols,show="headings")
        for c,w in zip(cols,widths): tree.heading(c,text=c.replace("_"," ").title()); tree.column(c,width=w,minwidth=60,anchor="w")
        tree.grid(row=1,column=0,sticky="nsew",padx=(10,0),pady=(0,10)); sc=ttk.Scrollbar(p,orient="vertical",command=tree.yview); sc.grid(row=1,column=1,sticky="ns",padx=(0,10),pady=(0,10)); tree.configure(yscrollcommand=sc.set); setattr(self,name.lower()+"_tree",tree)
    def _activity(self):
        p=ctk.CTkFrame(self.pages,fg_color=self.panel,corner_radius=12); p.grid_rowconfigure(0,weight=1); p.grid_columnconfigure(0,weight=1); self.activity_page=p; self.activity_log=ctk.CTkTextbox(p,fg_color="#0E1628",text_color="#C8D4E5",font=("Cascadia Code",10)); self.activity_log.grid(row=0,column=0,sticky="nsew",padx=10,pady=10)
    def show_page(self,name):
        for w in self.pages.winfo_children(): w.grid_forget()
        p={"Overview":self.overview,"Datasets":self.datasets_page,"Transport":self.transport_page,"Geography":self.geography_page,"Resources":self.resources_page,"Downloads":self.downloads_page,"Coverage":self.coverage_page,"Activity":self.activity_page}[name]; p.grid(row=0,column=0,sticky="nsew"); self.title_label.configure(text="Recovery overview" if name=="Overview" else name)
        for k,b in self.nav.items(): b.configure(fg_color="#1B2A43" if k==name else "transparent")
    def choose_folder(self):
        x=filedialog.askdirectory(initialdir=str(self.output_dir))
        if x: self.output_dir=Path(x); self.path_label.configure(text=x)
    def start(self):
        if self.worker and self.worker.is_alive(): return
        self.stop_event.clear(); self.progress.set(0); self.status_var.set("RUNNING"); self.start_btn.configure(state="disabled"); self.stop_btn.configure(state="normal"); self.clear_tables(); self.engine=RecoveryEngine(self.output_dir,self.events,self.stop_event); self.worker=threading.Thread(target=self.engine.run,daemon=True); self.worker.start(); self.log("INFO","MASARI Recovery Studio 2.1 started · nationwide discovery enabled")
    def stop(self): self.stop_event.set(); self.status_var.set("STOPPING"); self.stage.configure(text="Stopping safely…"); self.log("WARN","Stop requested · partial results will be exported")
    def clear_tables(self):
        for t in [self.datasets_tree,self.transport_tree,self.geography_tree,self.resources_tree,self.downloads_tree,self.coverage_tree]:
            for x in t.get_children(): t.delete(x)
    def log(self,level,msg):
        line=f"[{datetime.now():%H:%M:%S}] [{level:<7}] {msg}\n"; self.activity_log.insert("end",line); self.activity_log.see("end")
    def _poll(self):
        try:
            while True:
                e=self.events.get_nowait(); k=e.get("kind")
                if k=="log": self.log(e.get("level","INFO"),e.get("message",""))
                elif k=="stage": self.stage.configure(text=e["name"]); self.detail.configure(text=e.get("detail",""))
                elif k=="progress":
                    v=max(0,min(100,float(e.get("value",0)))); self.progress.set(v/100); self.progress_text.configure(text=f"{v:.0f}% · {e.get('detail','')}")
                elif k=="metric":
                    m={"datasets":"Datasets","resources":"Resources","transport":"Transport","admin_geo":"Geography","useful_geo":"Geography"}
                    if e["name"] in m: self.metrics[m[e["name"]]].configure(text=str(e["value"]))
                elif k=="done": self.finish(e)
                elif k=="fatal": self.log("ERROR",e["message"]); self.status_var.set("ERROR"); self.stage.configure(text="Recovery failed"); self.detail.configure(text=e["message"]); self.start_btn.configure(state="normal"); self.stop_btn.configure(state="disabled")
        except queue.Empty: pass
        self.after(150,self._poll)
    def finish(self,e):
        stopped=e.get("stopped",False); self.status_var.set("STOPPED · SAVED" if stopped else "COMPLETE"); self.stage.configure(text="Partial recovery saved" if stopped else "Recovery complete"); self.detail.configure(text=f"Output: {e['out_dir']}"); self.progress.set(1); self.progress_text.configure(text="100% · Export complete"); self.log("SUCCESS",f"{'Stopped' if stopped else 'Finished'} · {e['datasets']} datasets · {e['resources']} resources"); self.refresh(); self.start_btn.configure(state="normal"); self.stop_btn.configure(state="disabled")
    def refresh(self):
        if not self.engine:return
        needle=self.search_var.get().lower().strip(); rs=list(self.engine.resources.values())
        for t in [self.datasets_tree,self.transport_tree,self.geography_tree,self.resources_tree,self.downloads_tree,self.coverage_tree]:
            for x in t.get_children():t.delete(x)
        for d in self.engine.datasets.values():
            org=(d.get("organization") or {}).get("title",""); s=f"{d.get('title','')} {org} {d.get('id','')}".lower()
            if not needle or needle in s:self.datasets_tree.insert("","end",values=(d.get("title",""),org,len(d.get("resources",[]) or []),d.get("id","")))
        catfilter=self.category_var.get()
        for r in rs:
            s=norm(f"{r.get('dataset_title')} {r.get('name')} {r.get('description')} {r.get('host')} {r.get('mode')}")
            if needle and needle not in s:continue
            cat=r.get("category","Other"); gov=", ".join(r.get("governorates") or []); status=r.get("download_status","")
            if cat=="Transport":self.transport_tree.insert("","end",values=(r.get("mode"),r.get("dataset_title"),r.get("name"),r.get("detected_format") or r.get("format"),r.get("relevance_score"),gov,status))
            if cat in {"Administrative geography","Useful geography"}:self.geography_tree.insert("","end",values=(cat,r.get("dataset_title"),r.get("name"),r.get("detected_format") or r.get("format"),gov,status))
            if catfilter=="All" or catfilter==cat:self.resources_tree.insert("","end",values=(cat,r.get("mode"),r.get("dataset_title"),r.get("name"),r.get("detected_format") or r.get("format"),r.get("relevance_score"),r.get("host"),status))
            if status and status!="Not attempted":self.downloads_tree.insert("","end",values=(cat,r.get("name"),status,r.get("detected_format") or r.get("format"),f"{r.get('bytes_downloaded',0)/1024:.1f} KB" if r.get("bytes_downloaded") else "—",r.get("local_path","—")))
        cov=self.engine.coverage_report()["governorates"]
        for gov,x in cov.items():self.coverage_tree.insert("","end",values=(gov,x["matched_resources"],x["transport_resources"],x["geographic_resources"],x["evidence"]))

if __name__ == "__main__":
    app=App(); app.mainloop()
