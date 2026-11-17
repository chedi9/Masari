"""
MASARI Data Recovery Studio 2.0
Dual-pipeline extractor for Tunisia's National Open Data Catalogue.

Install:
    py -m pip install customtkinter requests truststore matplotlib

Run:
    py masari_recovery_studio.py

Outputs:
    datasets.json
    resources.json
    transport_resources.csv
    geographic_resources.csv
    resources_index.csv
    gtfs_inspection.json
    extraction_report.json
    downloaded/  (only relevant transport/geographic resources)
"""

from __future__ import annotations

import csv
import hashlib
import json
import mimetypes
import os
import queue
import re
import threading
import time
import zipfile
from collections import Counter
from datetime import datetime
from email.message import Message
from pathlib import Path
from urllib.parse import urlparse, unquote, unquote_to_bytes

import customtkinter as ctk
import requests
import truststore
from tkinter import ttk, filedialog, messagebox

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


APP_TITLE = "MASARI | Data Recovery Studio 2.0"
CKAN_BASE = "https://catalog.data.gov.tn/api/3/action"
BLOCKED_HOSTS = {"data.transport.tn"}
USER_AGENT = "MASARI-Data-Recovery-Studio/2.0"

# Search terms are intentionally split by data purpose. Broad terms are retained
# for discovery, but classification controls which resources may be downloaded.
SEARCH_GROUPS = {
    "Transport": [
        "TRANSTU", "SNCFT", "RFR", "SNTRI", "SORETRAS", "STS", "SORETRAK",
        "SRTJ", "SRT KEF", "SRTB", "SRTGN", "SRTM", "transport terrestre",
        "transport public", "horaires transport", "horaires bus",
        "horaires trains", "GTFS", "stations transport",
        "positions geographiques stations", "taxis collectifs", "louage",
        "transport rural", "référentiel national arrêt", "arrêts bus",
        "lignes bus", "réseau ferroviaire", "transport urbain",
    ],
    "Geography": [
        "découpage administratif Tunisie", "gouvernorats Tunisie",
        "délégations Tunisie", "municipalités Tunisie", "communes Tunisie",
        "limites administratives", "frontières administratives",
        "carte Tunisie", "cartographie Tunisie", "coordonnées géographiques",
        "référentiel géographique", "localités Tunisie", "villes Tunisie",
        "codes géographiques", "GeoJSON Tunisie", "shapefile Tunisie",
    ],
}

GTFS_REQUIRED = {"agency.txt", "stops.txt", "routes.txt", "trips.txt", "stop_times.txt"}
GTFS_RECOMMENDED = {"calendar.txt", "calendar_dates.txt"}
GTFS_OPTIONAL = {"shapes.txt", "frequencies.txt", "transfers.txt", "feed_info.txt"}

TRANSPORT_TERMS = {
    "gtfs": 30, "stop_times": 30, "routes.txt": 25, "trips.txt": 25,
    "stops.txt": 25, "agency.txt": 20, "horaire": 16, "horaires": 16,
    "timetable": 16, "schedule": 14, "transport": 10, "transtu": 18,
    "sncft": 18, "sntri": 18, "soretras": 18, "soretrak": 18, "sts": 8,
    "rfr": 12, "srt": 8, "bus": 12, "metro": 12, "métro": 12,
    "train": 12, "ferroviaire": 12, "ligne": 9, "lignes": 9,
    "arrêt": 12, "arret": 12, "station": 10, "gare": 10,
    "taxi collectif": 15, "louage": 15, "transport rural": 15,
    "itinéraire": 10, "itineraire": 10, "trajet": 9, "tarif": 8,
    "fare": 8, "frequence": 8, "fréquence": 8, "depart": 7, "départ": 7,
}
GEOGRAPHY_TERMS = {
    "geojson": 25, "shapefile": 25, "geopackage": 25, "gpkg": 20,
    "administratif": 15, "gouvernorat": 15, "gouvernorats": 15,
    "délégation": 15, "delegation": 15, "municipalité": 15,
    "municipalite": 15, "commune": 12, "limite": 10, "frontière": 10,
    "frontiere": 10, "coordonnée": 12, "coordonnees": 12,
    "géographique": 12, "geographique": 12, "cartographie": 12,
    "cartographique": 12, "localité": 10, "localite": 10,
    "ville": 8, "villes": 8, "tunisie": 2, "découpage": 12,
    "decoupage": 12, "latitude": 8, "longitude": 8,
}
MODE_TERMS = {
    "Bus": ["bus", "transtu", "soretras", "soretrak", "sts", "srt"],
    "Metro / Light rail": ["metro", "métro", "transtu", "léger", "light rail"],
    "Train / RFR": ["sncft", "sntri", "rfr", "train", "ferroviaire", "gare"],
    "Taxi collectif": ["taxi collectif", "taxi collectif"],
    "Louage": ["louage"],
    "Stops / Stations": ["arrêt", "arret", "station", "stops", "gare"],
    "Fares / Timetables": ["tarif", "fare", "horaire", "schedule", "timetable"],
}
FIELDS = [
    "id", "category", "mode", "dataset_title", "organization", "name",
    "format", "url", "host", "relevance", "relevance_score",
    "download_status", "local_path", "bytes_downloaded", "sha256",
    "description", "dataset_id", "retrieved_at",
]


def safe_name(value: str) -> str:
    value = unquote(str(value or "resource"))
    value = re.sub(r"[^\w.\-]+", "_", value, flags=re.UNICODE).strip("._")
    return value[:150] or "resource"


def infer_format(resource: dict) -> str:
    declared = str(resource.get("format") or "").strip().lower()
    if declared and declared not in {"unknown", "none", "n/a"}:
        return declared.lstrip(".").upper()
    url = str(resource.get("url") or "")
    suffix = Path(urlparse(url).path).suffix.lstrip(".")
    if suffix:
        return suffix.upper()
    name_suffix = Path(str(resource.get("name") or "")).suffix.lstrip(".")
    return name_suffix.upper() if name_suffix else "UNKNOWN"


def classify_resource(dataset_title: str, description: str, resource_name: str,
                      url: str = "") -> tuple[str, str, int, str]:
    text = f"{dataset_title} {description} {resource_name} {url}".lower()
    t_score = sum(weight for term, weight in TRANSPORT_TERMS.items() if term in text)
    g_score = sum(weight for term, weight in GEOGRAPHY_TERMS.items() if term in text)

    # Strong file-format evidence for geographic data.
    fmt = Path(urlparse(url).path).suffix.lower()
    if fmt in {".geojson", ".shp", ".shx", ".dbf", ".prj", ".gpkg", ".kml"}:
        g_score += 20
    if "gtfs" in text or any(x in text for x in ("stop_times.txt", "agency.txt", "routes.txt")):
        t_score += 25

    if t_score >= 12 and t_score >= g_score * 0.85:
        category = "Transport"
        score = t_score
    elif g_score >= 12:
        category = "Geography"
        score = g_score
    else:
        category = "Other"
        score = max(t_score, g_score)

    mode = "General transport"
    if category == "Transport":
        for candidate, terms in MODE_TERMS.items():
            if any(term in text for term in terms):
                mode = candidate
                break
    elif category == "Geography":
        mode = "Administrative / reference geography"

    if score >= 45:
        level = "Very high"
    elif score >= 25:
        level = "High"
    elif score >= 12:
        level = "Medium"
    else:
        level = "Low"
    return category, mode, min(score, 250), level


class RecoveryEngine:
    def __init__(self, out_dir: Path, events: queue.Queue, stop_event: threading.Event,
                 max_file_mb: int = 250, max_pages_per_term: int = 10):
        self.out_dir = out_dir
        self.events = events
        self.stop_event = stop_event
        self.max_file_bytes = max_file_mb * 1024 * 1024
        self.max_pages_per_term = max_pages_per_term
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self.datasets: dict[str, dict] = {}
        self.resources: dict[str, dict] = {}
        self.host_status: dict[str, bool] = {}
        self.stats = Counter()
        self.started = time.time()
        self.retrieved_at = datetime.now().astimezone().isoformat(timespec="seconds")
        self.gtfs_reports = []

    def emit(self, kind: str, **data):
        self.events.put({"kind": kind, **data})

    def api(self, action: str, params: dict | None = None, timeout: int = 20):
        if self.stop_event.is_set():
            return None
        try:
            response = self.session.get(
                f"{CKAN_BASE}/{action}", params=params or {}, timeout=(7, timeout)
            )
            response.raise_for_status()
            payload = response.json()
            if payload.get("success"):
                return payload.get("result")
            self.stats["api_errors"] += 1
            self.emit("log", level="WARN", message=f"{action}: CKAN returned success=false")
        except Exception as exc:
            self.stats["api_errors"] += 1
            self.emit("log", level="WARN", message=f"{action}: {str(exc)[:180]}")
        return None

    def search_datasets(self):
        terms = [(group, term) for group, values in SEARCH_GROUPS.items() for term in values]
        found = {}
        self.emit("stage", name="Discovering transport + geography",
                  detail=f"Searching {len(terms)} terms with CKAN pagination")
        for index, (group, term) in enumerate(terms, 1):
            if self.stop_event.is_set():
                break
            start = 0
            total_count = None
            for page in range(self.max_pages_per_term):
                if self.stop_event.is_set():
                    break
                result = self.api("package_search", {
                    "q": term, "rows": 100, "start": start,
                    "include_private": False,
                })
                if not result:
                    break
                items = result.get("results", []) or []
                total_count = int(result.get("count") or 0)
                for item in items:
                    if item.get("id"):
                        existing = found.get(item["id"], {})
                        # Keep the richer search result if the same package appears again.
                        found[item["id"]] = item if len(item) >= len(existing) else existing
                self.stats["search_pages"] += 1
                if not items or start + len(items) >= total_count:
                    break
                start += len(items)
            self.stats["searches"] += 1
            self.emit("progress", value=(index / max(len(terms), 1)) * 18,
                      detail=f"{group} search {index}/{len(terms)} · {term}")
            self.emit("log", level="INFO",
                      message=f"[{group}] '{term}' · {total_count if total_count is not None else 'no result'} matches")
        self.datasets.update(found)
        self.stats["datasets_found"] = len(found)
        self.emit("metric", name="datasets", value=len(found))
        self.emit("log", level="SUCCESS", message=f"Discovered {len(found)} unique datasets")
        return list(found)

    def fetch_dataset_details(self, ids):
        self.emit("stage", name="Indexing dataset metadata",
                  detail="Collecting publisher, tags, dates, notes and resource records")
        total = max(len(ids), 1)
        for i, dataset_id in enumerate(ids, 1):
            if self.stop_event.is_set():
                break
            detail = self.api("package_show", {"id": dataset_id})
            if detail:
                self.datasets[dataset_id] = detail
                self.stats["dataset_details_ok"] += 1
                organization = (detail.get("organization") or {}).get("title", "")
                for resource in detail.get("resources", []) or []:
                    rid = str(resource.get("id") or resource.get("url") or "")
                    if not rid:
                        continue
                    row = dict(resource)
                    row.update({
                        "dataset_id": dataset_id,
                        "dataset_title": detail.get("title", ""),
                        "organization": organization,
                        "category": "",
                        "mode": "",
                        "retrieved_at": self.retrieved_at,
                    })
                    previous = self.resources.get(rid)
                    if previous:
                        # Preserve the first source record but fill missing metadata.
                        for key, value in row.items():
                            if previous.get(key) in (None, "", []):
                                previous[key] = value
                    else:
                        self.resources[rid] = row
            else:
                self.stats["dataset_details_failed"] += 1
            self.emit("progress", value=18 + (i / total) * 32,
                      detail=f"Dataset metadata {i}/{total}")
            if i % 10 == 0 or i == total:
                self.emit("metric", name="resources", value=len(self.resources))
        self.stats["resources_found"] = len(self.resources)
        self.emit("log", level="SUCCESS",
                  message=f"Indexed {len(self.resources)} unique resource records")

    def probe_host(self, host: str) -> bool:
        if not host:
            return False
        if host in self.host_status:
            return self.host_status[host]
        if host in BLOCKED_HOSTS:
            self.host_status[host] = False
            return False
        try:
            response = self.session.head(
                f"https://{host}", timeout=(5, 8), allow_redirects=True
            )
            ok = response.status_code < 500
            response.close()
        except Exception:
            ok = False
        self.host_status[host] = ok
        self.emit("log", level="INFO" if ok else "WARN",
                  message=f"Host check · {host} · {'reachable' if ok else 'unreachable'}")
        return ok

    def enrich_resources(self):
        self.emit("stage", name="Classifying transport and geography",
                  detail="Separating mobility datasets from administrative reference data")
        rows = list(self.resources.values())
        total = max(len(rows), 1)
        for i, resource in enumerate(rows, 1):
            if self.stop_event.is_set():
                break
            url = resource.get("url") or ""
            host = urlparse(url).hostname or ""
            category, mode, score, level = classify_resource(
                resource.get("dataset_title", ""),
                resource.get("description", ""),
                resource.get("name", "") or url,
                url,
            )
            resource["category"] = category
            resource["mode"] = mode
            resource["relevance_score"] = score
            resource["relevance"] = level
            resource["host"] = host
            resource["format"] = infer_format(resource)
            resource["download_status"] = "Not attempted"
            self.stats[f"category_{category.lower()}"] += 1
            self.emit("progress", value=50 + (i / total) * 12,
                      detail=f"Classifying resources {i}/{total}")
        self.emit("metric", name="resources", value=len(rows))
        self.emit("metric", name="transport", value=sum(r.get("category") == "Transport" for r in rows))
        self.emit("metric", name="geography", value=sum(r.get("category") == "Geography" for r in rows))

    def _filename(self, resource: dict, response: requests.Response, index: int) -> str:
        # Prefer Content-Disposition, then resource name, then URL.
        disposition = response.headers.get("content-disposition", "")
        filename = ""
        if disposition:
            msg = Message()
            msg["content-disposition"] = disposition
            filename = msg.get_filename() or ""
        if not filename:
            filename = resource.get("name") or Path(urlparse(resource.get("url", "")).path).name
        filename = safe_name(filename or f"resource_{index}")
        suffix = Path(filename).suffix
        if not suffix:
            content_type = response.headers.get("content-type", "").split(";")[0].strip()
            guessed = mimetypes.guess_extension(content_type or "")
            fmt = str(resource.get("format") or "").lower()
            ext = guessed or (("." + fmt) if fmt and fmt != "unknown" else ".bin")
            filename += ext
        return filename

    def inspect_gtfs(self, target: Path, resource: dict):
        if target.suffix.lower() != ".zip":
            return
        report = {
            "resource_id": resource.get("id"),
            "dataset_title": resource.get("dataset_title"),
            "file": str(target),
            "valid_zip": False,
            "files": [],
            "missing_required": sorted(GTFS_REQUIRED),
            "missing_recommended": sorted(GTFS_RECOMMENDED),
            "status": "Not a readable ZIP",
        }
        try:
            with zipfile.ZipFile(target) as archive:
                names = {
                    Path(name.replace("\\", "/")).name.lower()
                    for name in archive.namelist()
                    if not name.endswith("/")
                }
                required = GTFS_REQUIRED & names
                recommended = GTFS_RECOMMENDED & names
                report.update({
                    "valid_zip": True,
                    "files": sorted(names),
                    "missing_required": sorted(GTFS_REQUIRED - required),
                    "missing_recommended": sorted(GTFS_RECOMMENDED - recommended),
                    "status": "Complete core GTFS" if GTFS_REQUIRED <= names
                              else "Incomplete / non-standard GTFS archive",
                })
                self.stats["gtfs_archives"] += 1
                if GTFS_REQUIRED <= names:
                    self.stats["gtfs_core_complete"] += 1
        except Exception as exc:
            report["status"] = f"ZIP inspection failed: {str(exc)[:120]}"
        self.gtfs_reports.append(report)
        self.emit("log", level="INFO",
                  message=f"GTFS inspection · {report['status']} · {target.name}")

    def download_resources(self):
        # Do not download broad-search noise. Preserve metadata for all resources.
        rows = [
            r for r in self.resources.values()
            if r.get("category") in {"Transport", "Geography"}
            and r.get("relevance_score", 0) >= 12
            and r.get("url")
        ]
        rows.sort(key=lambda r: (
            r.get("category") == "Transport",
            r.get("relevance_score", 0),
            bool(r.get("url")),
        ), reverse=True)
        total = max(len(rows), 1)
        self.emit("stage", name="Recovering relevant files",
                  detail=f"Downloading {len(rows)} classified transport/geographic resources")
        downloaded_dir = self.out_dir / "downloaded"
        downloaded_dir.mkdir(parents=True, exist_ok=True)
        seen_hashes = {}

        for i, resource in enumerate(rows, 1):
            if self.stop_event.is_set():
                break
            url = str(resource.get("url") or "")
            host = resource.get("host") or urlparse(url).hostname or ""
            if not url.startswith(("http://", "https://")):
                resource["download_status"] = "Skipped · invalid URL"
                self.stats["skipped"] += 1
            elif host in BLOCKED_HOSTS:
                resource["download_status"] = "Skipped · known unreachable host"
                self.stats["skipped"] += 1
            elif not self.probe_host(host):
                resource["download_status"] = "Skipped · host unreachable"
                self.stats["skipped"] += 1
            else:
                target = None
                try:
                    with self.session.get(url, timeout=(8, 25), stream=True,
                                          allow_redirects=True) as response:
                        response.raise_for_status()
                        length = int(response.headers.get("content-length") or 0)
                        if length and length > self.max_file_bytes:
                            resource["download_status"] = "Skipped · exceeds size limit"
                            self.stats["skipped"] += 1
                        else:
                            filename = self._filename(resource, response, i)
                            prefix = safe_name(resource.get("id") or str(i))[:32]
                            category_dir = "transport" if resource["category"] == "Transport" else "geography"
                            folder = downloaded_dir / category_dir
                            folder.mkdir(parents=True, exist_ok=True)
                            target = folder / f"{prefix}_{filename}"
                            digest = hashlib.sha256()
                            bytes_written = 0
                            with target.open("wb") as output:
                                for chunk in response.iter_content(128 * 1024):
                                    if self.stop_event.is_set():
                                        break
                                    if not chunk:
                                        continue
                                    bytes_written += len(chunk)
                                    if bytes_written > self.max_file_bytes:
                                        raise ValueError("File exceeded configured size limit")
                                    digest.update(chunk)
                                    output.write(chunk)
                            if self.stop_event.is_set():
                                target.unlink(missing_ok=True)
                                resource["download_status"] = "Stopped"
                            else:
                                sha = digest.hexdigest()
                                resource["sha256"] = sha
                                if sha in seen_hashes:
                                    target.unlink(missing_ok=True)
                                    resource["download_status"] = "Duplicate content"
                                    resource["duplicate_of"] = seen_hashes[sha]
                                    self.stats["duplicates"] += 1
                                else:
                                    seen_hashes[sha] = str(target)
                                    resource["download_status"] = "Downloaded"
                                    resource["local_path"] = str(target)
                                    resource["bytes_downloaded"] = bytes_written
                                    self.stats["downloaded"] += 1
                                    self.stats["bytes_downloaded"] += bytes_written
                                    self.emit("log", level="SUCCESS",
                                              message=f"Downloaded [{category_dir}] {filename} · {bytes_written / 1024:.1f} KB")
                                    self.inspect_gtfs(target, resource)
                except Exception as exc:
                    if target and target.exists():
                        target.unlink(missing_ok=True)
                    resource["download_status"] = f"Failed · {str(exc)[:120]}"
                    self.stats["failed"] += 1
                    self.emit("log", level="WARN",
                              message=f"Download failed · {resource.get('name') or url} · {str(exc)[:160]}")
            self.emit("progress", value=62 + (i / total) * 35,
                      detail=f"Relevant file pass {i}/{total}")
            if i % 5 == 0 or i == total:
                self.emit("metric", name="downloaded", value=self.stats["downloaded"])
                self.emit("metric", name="failed", value=self.stats["failed"])
                self.emit("metric", name="skipped", value=self.stats["skipped"])

        # Record why potentially useful records were not downloaded.
        for resource in self.resources.values():
            if resource.get("download_status") == "Not attempted":
                if resource.get("category") == "Other":
                    resource["download_status"] = "Not selected · other category"
                    self.stats["not_selected"] += 1
                elif resource.get("relevance_score", 0) < 12:
                    resource["download_status"] = "Not selected · low confidence"
                    self.stats["not_selected"] += 1

    def write_outputs(self):
        self.emit("stage", name="Exporting recovery catalogue",
                  detail="Writing full metadata, split indexes, provenance and quality reports")
        self.out_dir.mkdir(parents=True, exist_ok=True)
        datasets = list(self.datasets.values())
        resources = list(self.resources.values())

        def write_json(filename, value):
            (self.out_dir / filename).write_text(
                json.dumps(value, ensure_ascii=False, indent=2, default=str),
                encoding="utf-8"
            )

        def write_csv(filename, rows):
            with (self.out_dir / filename).open("w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
                writer.writeheader()
                writer.writerows(rows)

        write_json("datasets.json", datasets)
        write_json("resources.json", resources)
        write_csv("resources_index.csv", resources)
        write_csv("transport_resources.csv", [r for r in resources if r.get("category") == "Transport"])
        write_csv("geographic_resources.csv", [r for r in resources if r.get("category") == "Geography"])
        write_csv("failed_resources.csv", [r for r in resources if str(r.get("download_status", "")).startswith("Failed")])
        write_csv("priority_resources.csv", [
            r for r in resources if r.get("category") in {"Transport", "Geography"}
            and r.get("relevance") in {"Very high", "High"}
        ])
        write_json("gtfs_inspection.json", self.gtfs_reports)

        category_counts = Counter(r.get("category", "Other") for r in resources)
        format_counts = Counter(r.get("format", "UNKNOWN") for r in resources)
        report = {
            "application": APP_TITLE,
            "generated_at": self.retrieved_at,
            "catalogue": CKAN_BASE,
            "search_groups": SEARCH_GROUPS,
            "datasets_found": len(datasets),
            "dataset_details_ok": self.stats["dataset_details_ok"],
            "dataset_details_failed": self.stats["dataset_details_failed"],
            "resources_found": len(resources),
            "category_counts": dict(category_counts),
            "format_counts": dict(format_counts),
            "downloaded": self.stats["downloaded"],
            "failed": self.stats["failed"],
            "skipped": self.stats["skipped"],
            "duplicates": self.stats["duplicates"],
            "not_selected": self.stats["not_selected"],
            "bytes_downloaded": self.stats["bytes_downloaded"],
            "api_errors": self.stats["api_errors"],
            "search_pages": self.stats["search_pages"],
            "gtfs_archives": self.stats["gtfs_archives"],
            "gtfs_core_complete": self.stats["gtfs_core_complete"],
            "host_checks": self.host_status,
            "stopped_by_user": self.stop_event.is_set(),
            "notes": [
                "Transport and geography are classified separately; 'Other' resources are indexed but not auto-downloaded.",
                "Classification is heuristic. Review resource metadata and source provenance before production use.",
                "GTFS ZIP files are inspected for core and recommended files; archive contents are not modified.",
                "Resources on data.transport.tn are skipped because this host was previously unreachable from the user's network.",
                "Static catalogue data does not imply live vehicle positions or real-time service guarantees.",
            ],
        }
        write_json("extraction_report.json", report)
        self.emit("log", level="SUCCESS",
                  message="Exported datasets, resources, transport/geography indexes, GTFS and extraction reports")

    def run(self):
        try:
            truststore.inject_into_ssl()
            self.emit("stage", name="Connecting to National Catalogue", detail="CKAN API · HTTPS · Windows trust store")
            status = self.api("status_show", timeout=18)
            if not status:
                raise RuntimeError("National catalogue API did not respond successfully.")
            self.emit("log", level="SUCCESS",
                      message=f"Connected · CKAN {status.get('ckan_version', 'version unknown')}")
            ids = self.search_datasets()
            if not ids:
                raise RuntimeError("No datasets discovered. Check the connection and try again.")
            self.fetch_dataset_details(ids)
            self.enrich_resources()
            if not self.stop_event.is_set():
                self.download_resources()
            else:
                self.emit("log", level="WARN", message="Stop requested; download phase skipped.")
            # Always save partial results after a user stop.
            self.write_outputs()
            elapsed = time.time() - self.started
            stopped = self.stop_event.is_set()
            self.emit("progress", value=100, detail="Partial recovery saved" if stopped else "Recovery run complete")
            self.emit("done", stats=dict(self.stats), elapsed=elapsed,
                      stopped=stopped, datasets=len(self.datasets),
                      resources=len(self.resources), out_dir=str(self.out_dir))
        except Exception as exc:
            # Preserve any partial discoveries on fatal errors too.
            try:
                self.write_outputs()
            except Exception:
                pass
            self.emit("fatal", message=str(exc))


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1500x940")
        self.minsize(1180, 740)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.bg = "#0B1020"
        self.panel = "#121A2D"
        self.line = "#26344D"
        self.text = "#F2F5FA"
        self.muted = "#8FA0B8"
        self.cyan = "#35C8D0"
        self.orange = "#FF9F43"
        self.green = "#42D39A"
        self.red = "#FF647C"
        self.purple = "#A78BFA"

        self.events = queue.Queue()
        self.stop_event = threading.Event()
        self.worker = None
        self.engine = None
        self.output_dir = Path.home() / "Documents" / "MASARI_Recovery"
        self.status_var = ctk.StringVar(value="READY")
        self.search_var = ctk.StringVar(value="")
        self.category_var = ctk.StringVar(value="All categories")
        self._style_tree()
        self._build_ui()
        self.after(150, self._poll_events)

    def _style_tree(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#121A2D", foreground="#E8EEF8",
                        fieldbackground="#121A2D", rowheight=29, borderwidth=0,
                        font=("Segoe UI", 9))
        style.configure("Treeview.Heading", background="#1B2941", foreground="#AFC0D8",
                        relief="flat", font=("Segoe UI Semibold", 9))
        style.map("Treeview", background=[("selected", "#244A65")],
                  foreground=[("selected", "#FFFFFF")])

    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.sidebar = ctk.CTkFrame(self, width=235, corner_radius=0, fg_color="#0E1628")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        brand = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand.pack(fill="x", padx=22, pady=(25, 28))
        ctk.CTkLabel(brand, text="M", font=("Segoe UI Black", 35),
                     text_color=self.cyan).pack(side="left")
        box = ctk.CTkFrame(brand, fg_color="transparent")
        box.pack(side="left", padx=9)
        ctk.CTkLabel(box, text="MASARI", font=("Segoe UI Semibold", 17),
                     text_color=self.text).pack(anchor="w")
        ctk.CTkLabel(box, text="DATA RECOVERY STUDIO 2.0",
                     font=("Segoe UI", 8), text_color=self.muted).pack(anchor="w")

        ctk.CTkLabel(self.sidebar, text="WORKSPACE", font=("Segoe UI Semibold", 9),
                     text_color="#60728F").pack(anchor="w", padx=24, pady=(0, 10))
        self.nav_buttons = {}
        nav = [
            ("Overview", "◈"), ("Datasets", "▦"), ("Transport", "⇄"),
            ("Geography", "⌖"), ("Resources", "▤"), ("Downloads", "↓"),
            ("Activity", "≋"),
        ]
        for name, icon in nav:
            btn = ctk.CTkButton(
                self.sidebar, text=f"  {icon}    {name}", anchor="w", height=39,
                corner_radius=9,
                fg_color="#1B2A43" if name == "Overview" else "transparent",
                hover_color="#1B2A43", text_color=self.text,
                font=("Segoe UI", 11),
                command=lambda n=name: self.show_page(n)
            )
            btn.pack(fill="x", padx=14, pady=2)
            self.nav_buttons[name] = btn

        ctk.CTkFrame(self.sidebar, height=1, fg_color=self.line).pack(fill="x", padx=18, pady=20)
        ctk.CTkLabel(self.sidebar, text="OUTPUT DIRECTORY", font=("Segoe UI Semibold", 9),
                     text_color="#60728F").pack(anchor="w", padx=24)
        self.path_label = ctk.CTkLabel(
            self.sidebar, text=str(self.output_dir), wraplength=185,
            justify="left", text_color=self.muted, font=("Segoe UI", 9)
        )
        self.path_label.pack(anchor="w", padx=24, pady=(8, 8))
        ctk.CTkButton(self.sidebar, text="Choose folder", height=32,
                      fg_color="#1B2A43", hover_color="#263B59",
                      command=self.choose_folder).pack(fill="x", padx=18)
        ctk.CTkLabel(
            self.sidebar, text="NATIONAL OPEN DATA CATALOGUE\nCKAN · HTTPS · TRUSTSTORE",
            font=("Segoe UI", 8), text_color="#60728F", justify="left"
        ).pack(side="bottom", anchor="w", padx=22, pady=22)

        self.main = ctk.CTkFrame(self, fg_color=self.bg, corner_radius=0)
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(1, weight=1)
        header = ctk.CTkFrame(self.main, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=28, pady=(20, 12))
        self.page_title = ctk.CTkLabel(header, text="Recovery overview",
                                       font=("Segoe UI Semibold", 23), text_color=self.text)
        self.page_title.pack(side="left")
        self.status_pill = ctk.CTkLabel(header, textvariable=self.status_var,
                                        fg_color="#183D3A", text_color=self.green,
                                        corner_radius=20, padx=13, pady=6,
                                        font=("Segoe UI Semibold", 9))
        self.status_pill.pack(side="right", padx=(12, 0))
        self.start_btn = ctk.CTkButton(
            header, text="▶  Start recovery", width=155, height=38,
            fg_color=self.cyan, hover_color="#22AAB4", text_color="#07131D",
            font=("Segoe UI Semibold", 11), command=self.start_recovery
        )
        self.start_btn.pack(side="right")
        self.stop_btn = ctk.CTkButton(
            header, text="■  Stop", width=86, height=38,
            fg_color="#482436", hover_color="#633047", text_color="#FFDCE3",
            state="disabled", command=self.stop_recovery
        )
        self.stop_btn.pack(side="right", padx=8)

        self.pages = ctk.CTkFrame(self.main, fg_color="transparent")
        self.pages.grid(row=1, column=0, sticky="nsew", padx=28, pady=(0, 20))
        self.pages.grid_rowconfigure(0, weight=1)
        self.pages.grid_columnconfigure(0, weight=1)
        self._build_overview()
        self._build_datasets()
        self._build_category_page("Transport")
        self._build_category_page("Geography")
        self._build_resources()
        self._build_downloads()
        self._build_activity()
        self.show_page("Overview")

    def _card(self, parent, title, value, sub, accent):
        card = ctk.CTkFrame(parent, fg_color=self.panel, corner_radius=13,
                            border_width=1, border_color=self.line)
        ctk.CTkLabel(card, text=title.upper(), font=("Segoe UI Semibold", 9),
                     text_color=self.muted).pack(anchor="w", padx=16, pady=(13, 2))
        val = ctk.CTkLabel(card, text=value, font=("Segoe UI Semibold", 26),
                           text_color=accent)
        val.pack(anchor="w", padx=16)
        ctk.CTkLabel(card, text=sub, font=("Segoe UI", 9),
                     text_color=self.muted).pack(anchor="w", padx=16, pady=(1, 12))
        return card, val

    def _build_overview(self):
        self.overview = ctk.CTkFrame(self.pages, fg_color="transparent")
        self.overview.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.overview.grid_rowconfigure(1, weight=1)
        metric_specs = [
            ("Datasets discovered", "0", "Unique catalogue records", self.cyan),
            ("Resources indexed", "0", "All resource metadata", self.purple),
            ("Transport resources", "0", "Mobility-related files", self.orange),
            ("Geographic resources", "0", "Reference / boundary data", self.green),
        ]
        self.metric_labels = {}
        for col, (name, value, sub, accent) in enumerate(metric_specs):
            card, label = self._card(self.overview, name, value, sub, accent)
            card.grid(row=0, column=col, sticky="ew",
                      padx=(0 if col == 0 else 7, 0), pady=(0, 12))
            self.metric_labels[name] = label

        pipeline = ctk.CTkFrame(self.overview, fg_color=self.panel, corner_radius=13,
                                border_width=1, border_color=self.line)
        pipeline.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=(0, 7), pady=(0, 12))
        ctk.CTkLabel(pipeline, text="DUAL EXTRACTION PIPELINE",
                     font=("Segoe UI Semibold", 11), text_color=self.text
                     ).pack(anchor="w", padx=17, pady=(15, 3))
        ctk.CTkLabel(pipeline, text="Transport network data + geographic reference data",
                     font=("Segoe UI", 9), text_color=self.muted
                     ).pack(anchor="w", padx=17)
        self.stage_label = ctk.CTkLabel(pipeline, text="Waiting to start",
                                        font=("Segoe UI Semibold", 14), text_color=self.cyan)
        self.stage_label.pack(anchor="w", padx=17, pady=(23, 2))
        self.stage_detail = ctk.CTkLabel(
            pipeline, text="Metadata is retained even when source files are unreachable.",
            font=("Segoe UI", 9), text_color=self.muted
        )
        self.stage_detail.pack(anchor="w", padx=17)
        self.progress = ctk.CTkProgressBar(pipeline, height=11,
                                           progress_color=self.cyan, fg_color="#26344D")
        self.progress.pack(fill="x", padx=17, pady=(19, 7))
        self.progress.set(0)
        self.progress_text = ctk.CTkLabel(pipeline, text="0%", text_color=self.muted,
                                          font=("Segoe UI Semibold", 10))
        self.progress_text.pack(anchor="e", padx=17)
        self.pipeline_steps = ctk.CTkFrame(pipeline, fg_color="transparent")
        self.pipeline_steps.pack(fill="x", padx=13, pady=(16, 15))
        for i, label in enumerate(["CONNECT", "DISCOVER", "INDEX", "CLASSIFY", "RECOVER", "EXPORT"]):
            step = ctk.CTkFrame(self.pipeline_steps, fg_color="#1A2940", corner_radius=7)
            step.pack(side="left", fill="x", expand=True, padx=3)
            ctk.CTkLabel(step, text=f"{i+1:02d}", text_color=self.cyan,
                         font=("Segoe UI Semibold", 9)).pack(pady=(7, 0))
            ctk.CTkLabel(step, text=label, text_color=self.muted,
                         font=("Segoe UI", 7)).pack(pady=(0, 7))

        chart_panel = ctk.CTkFrame(self.overview, fg_color=self.panel, corner_radius=13,
                                   border_width=1, border_color=self.line)
        chart_panel.grid(row=1, column=2, columnspan=2, sticky="nsew", padx=(7, 0), pady=(0, 12))
        ctk.CTkLabel(chart_panel, text="DATA CLASSIFICATION",
                     font=("Segoe UI Semibold", 11), text_color=self.text
                     ).pack(anchor="w", padx=17, pady=(15, 0))
        ctk.CTkLabel(chart_panel, text="Transport / Geography / Other",
                     font=("Segoe UI", 9), text_color=self.muted
                     ).pack(anchor="w", padx=17)
        self.figure = Figure(figsize=(5.1, 3.15), dpi=100, facecolor=self.panel)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor(self.panel)
        self.ax.text(.5, .5, "Run recovery to populate chart", color=self.muted,
                     ha="center", va="center", transform=self.ax.transAxes)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        for spine in self.ax.spines.values():
            spine.set_visible(False)
        self.chart_canvas = FigureCanvasTkAgg(self.figure, master=chart_panel)
        self.chart_canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=4)

        recent = ctk.CTkFrame(self.overview, fg_color=self.panel, corner_radius=13,
                              border_width=1, border_color=self.line)
        recent.grid(row=2, column=0, columnspan=4, sticky="ew")
        ctk.CTkLabel(recent, text="LATEST ACTIVITY", font=("Segoe UI Semibold", 10),
                     text_color=self.text).pack(anchor="w", padx=16, pady=(11, 4))
        self.recent_log = ctk.CTkTextbox(recent, height=88, fg_color="#0E1628",
                                         text_color="#C8D4E5", corner_radius=8,
                                         font=("Cascadia Code", 9))
        self.recent_log.pack(fill="x", padx=12, pady=(0, 11))
        self.recent_log.configure(state="disabled")

    def _make_table(self, parent, columns, widths):
        tree = ttk.Treeview(parent, columns=columns, show="headings")
        for col, width in zip(columns, widths):
            tree.heading(col, text=col.replace("_", " ").title())
            tree.column(col, width=width, minwidth=65, anchor="w")
        tree.grid(row=1, column=0, sticky="nsew", padx=(12, 0), pady=(0, 12))
        scroll = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        scroll.grid(row=1, column=1, sticky="ns", padx=(0, 12), pady=(0, 12))
        tree.configure(yscrollcommand=scroll.set)
        return tree

    def _build_datasets(self):
        page = ctk.CTkFrame(self.pages, fg_color=self.panel, corner_radius=13,
                            border_width=1, border_color=self.line)
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(1, weight=1)
        bar = ctk.CTkFrame(page, fg_color="transparent")
        bar.grid(row=0, column=0, sticky="ew", padx=12, pady=12)
        ctk.CTkEntry(bar, placeholder_text="Search datasets...",
                     textvariable=self.search_var, width=280).pack(side="left")
        self.datasets_page = page
        self.dataset_tree = self._make_table(
            page, ("title", "organization", "name", "resources", "id"),
            (350, 190, 180, 80, 250)
        )

    def _build_category_page(self, category):
        page = ctk.CTkFrame(self.pages, fg_color=self.panel, corner_radius=13,
                            border_width=1, border_color=self.line)
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(1, weight=1)
        bar = ctk.CTkFrame(page, fg_color="transparent")
        bar.grid(row=0, column=0, sticky="ew", padx=12, pady=12)
        ctk.CTkLabel(bar, text=f"{category.upper()} DATA",
                     text_color=self.text, font=("Segoe UI Semibold", 11)).pack(side="left", padx=(2, 15))
        tree = self._make_table(
            page, ("mode", "dataset", "resource", "format", "relevance", "host", "status"),
            (170, 260, 220, 80, 95, 180, 190)
        )
        setattr(self, category.lower() + "_page", page)
        setattr(self, category.lower() + "_tree", tree)

    def _build_resources(self):
        page = ctk.CTkFrame(self.pages, fg_color=self.panel, corner_radius=13,
                            border_width=1, border_color=self.line)
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(1, weight=1)
        bar = ctk.CTkFrame(page, fg_color="transparent")
        bar.grid(row=0, column=0, sticky="ew", padx=12, pady=12)
        ctk.CTkEntry(bar, placeholder_text="Filter by text...",
                     textvariable=self.search_var, width=250).pack(side="left")
        ctk.CTkOptionMenu(
            bar, variable=self.category_var,
            values=["All categories", "Transport", "Geography", "Other"],
            command=lambda _value: self.refresh_data_views()
        ).pack(side="left", padx=10)
        self.resources_page = page
        self.resource_tree = self._make_table(
            page, ("category", "mode", "dataset", "resource", "format", "relevance", "host", "status"),
            (100, 160, 250, 210, 75, 95, 160, 190)
        )

    def _build_downloads(self):
        page = ctk.CTkFrame(self.pages, fg_color="transparent")
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(1, weight=1)
        summary = ctk.CTkFrame(page, fg_color=self.panel, corner_radius=13,
                               border_width=1, border_color=self.line)
        summary.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.download_summary = ctk.CTkLabel(summary, text="No recovery run yet",
                                             text_color=self.muted, font=("Segoe UI", 12))
        self.download_summary.pack(anchor="w", padx=16, pady=14)
        self.downloads_page = page
        self.download_tree = self._make_table(
            page, ("category", "resource", "host", "status", "size", "local_path"),
            (100, 240, 180, 230, 90, 420)
        )

    def _build_activity(self):
        self.activity_page = ctk.CTkFrame(self.pages, fg_color=self.panel, corner_radius=13,
                                          border_width=1, border_color=self.line)
        self.activity_page.grid_columnconfigure(0, weight=1)
        self.activity_page.grid_rowconfigure(0, weight=1)
        self.activity_log = ctk.CTkTextbox(
            self.activity_page, fg_color="#0E1628", text_color="#C8D4E5",
            font=("Cascadia Code", 10)
        )
        self.activity_log.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)

    def show_page(self, name):
        for child in self.pages.winfo_children():
            child.grid_forget()
        page = {
            "Overview": self.overview, "Datasets": self.datasets_page,
            "Transport": self.transport_page, "Geography": self.geography_page,
            "Resources": self.resources_page, "Downloads": self.downloads_page,
            "Activity": self.activity_page,
        }[name]
        page.grid(row=0, column=0, sticky="nsew")
        self.page_title.configure(text="Recovery overview" if name == "Overview" else name)
        for key, button in self.nav_buttons.items():
            button.configure(fg_color="#1B2A43" if key == name else "transparent")

    def choose_folder(self):
        path = filedialog.askdirectory(initialdir=str(self.output_dir))
        if path:
            self.output_dir = Path(path)
            self.path_label.configure(text=str(path))

    def start_recovery(self):
        if self.worker and self.worker.is_alive():
            return
        self.stop_event.clear()
        self.progress.set(0)
        self.status_var.set("RUNNING")
        self.status_pill.configure(fg_color="#183D3A", text_color=self.green)
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.clear_tables()
        self.engine = RecoveryEngine(self.output_dir, self.events, self.stop_event)
        self.worker = threading.Thread(target=self.engine.run, daemon=True)
        self.worker.start()
        self.log("INFO", "MASARI Recovery Studio 2.0 started · dual pipeline enabled")

    def stop_recovery(self):
        self.stop_event.set()
        self.status_var.set("STOPPING")
        self.stage_label.configure(text="Stopping safely…")
        self.stage_detail.configure(text="The current request will finish; partial metadata will be exported.")
        self.log("WARN", "Stop requested. Saving partial recovery data after current operation.")

    def clear_tables(self):
        trees = [
            self.dataset_tree, self.transport_tree, self.geography_tree,
            self.resource_tree, self.download_tree,
        ]
        for tree in trees:
            for item in tree.get_children():
                tree.delete(item)

    def log(self, level, message):
        stamp = datetime.now().strftime("%H:%M:%S")
        line = f"[{stamp}] [{level:<7}] {message}\n"
        for widget in (self.activity_log, self.recent_log):
            widget.configure(state="normal")
            widget.insert("end", line)
            widget.see("end")
            if widget is self.recent_log:
                try:
                    if int(widget.index("end-1c").split(".")[0]) > 7:
                        widget.delete("1.0", "2.0")
                except Exception:
                    pass
            widget.configure(state="disabled")

    def _poll_events(self):
        try:
            while True:
                event = self.events.get_nowait()
                kind = event.get("kind")
                if kind == "log":
                    self.log(event.get("level", "INFO"), event.get("message", ""))
                elif kind == "stage":
                    self.stage_label.configure(text=event["name"])
                    self.stage_detail.configure(text=event.get("detail", ""))
                elif kind == "progress":
                    value = max(0, min(100, float(event.get("value", 0))))
                    self.progress.set(value / 100)
                    self.progress_text.configure(text=f"{value:.0f}%  ·  {event.get('detail', '')}")
                elif kind == "metric":
                    self.update_metric(event["name"], event["value"])
                elif kind == "done":
                    self.finish_run(event)
                elif kind == "fatal":
                    self.log("ERROR", event["message"])
                    self.status_var.set("ERROR")
                    self.status_pill.configure(fg_color="#482436", text_color=self.red)
                    self.stage_label.configure(text="Recovery failed")
                    self.stage_detail.configure(text=event["message"])
                    self.start_btn.configure(state="normal")
                    self.stop_btn.configure(state="disabled")
        except queue.Empty:
            pass
        self.after(150, self._poll_events)

    def update_metric(self, name, value):
        mapping = {
            "datasets": "Datasets discovered",
            "resources": "Resources indexed",
            "transport": "Transport resources",
            "geography": "Geographic resources",
        }
        if name in mapping:
            self.metric_labels[mapping[name]].configure(text=str(value))

    def finish_run(self, event):
        stopped = bool(event.get("stopped"))
        self.status_var.set("STOPPED · SAVED" if stopped else "COMPLETE")
        self.status_pill.configure(
            fg_color="#4A3820" if stopped else "#183D3A",
            text_color=self.orange if stopped else self.green
        )
        self.stage_label.configure(text="Partial recovery saved" if stopped else "Recovery complete")
        self.stage_detail.configure(text=f"Output saved to {event['out_dir']}")
        self.progress.set(1)
        self.progress_text.configure(text="100%  ·  Export complete")
        self.log("WARN" if stopped else "SUCCESS",
                 f"{'Stopped' if stopped else 'Finished'} · {event['datasets']} datasets · {event['resources']} resources")
        self.log("INFO", f"Output folder: {event['out_dir']}")
        self.refresh_data_views()
        self.update_chart()
        stats = event.get("stats", {})
        self.download_summary.configure(
            text=f"{stats.get('downloaded', 0)} downloaded · "
                 f"{stats.get('failed', 0)} failed · {stats.get('skipped', 0)} skipped · "
                 f"{stats.get('duplicates', 0)} duplicates · "
                 f"{'Partial data saved' if stopped else 'Complete'} · {event['out_dir']}"
        )
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")

    def refresh_data_views(self):
        if not self.engine:
            return
        needle = self.search_var.get().strip().lower()
        datasets = list(self.engine.datasets.values())
        resources = list(self.engine.resources.values())
        for tree in (self.dataset_tree, self.transport_tree, self.geography_tree,
                     self.resource_tree, self.download_tree):
            for item in tree.get_children():
                tree.delete(item)

        for d in datasets:
            searchable = f"{d.get('title','')} {d.get('name','')} {d.get('id','')} {(d.get('organization') or {}).get('title','')}".lower()
            if needle and needle not in searchable:
                continue
            self.dataset_tree.insert("", "end", values=(
                d.get("title", ""), (d.get("organization") or {}).get("title", ""),
                d.get("name", ""), len(d.get("resources", []) or []), d.get("id", "")
            ))

        category_filter = self.category_var.get()
        for r in resources:
            searchable = f"{r.get('dataset_title','')} {r.get('name','')} {r.get('description','')} {r.get('host','')} {r.get('mode','')}".lower()
            if needle and needle not in searchable:
                continue
            category = r.get("category", "Other")
            if category == "Transport":
                self.transport_tree.insert("", "end", values=(
                    r.get("mode", ""), r.get("dataset_title", ""), r.get("name", ""),
                    r.get("format", ""), r.get("relevance", ""), r.get("host", ""),
                    r.get("download_status", "")
                ))
            elif category == "Geography":
                self.geography_tree.insert("", "end", values=(
                    r.get("mode", ""), r.get("dataset_title", ""), r.get("name", ""),
                    r.get("format", ""), r.get("relevance", ""), r.get("host", ""),
                    r.get("download_status", "")
                ))
            if category_filter in ("All categories", category):
                self.resource_tree.insert("", "end", values=(
                    category, r.get("mode", ""), r.get("dataset_title", ""),
                    r.get("name", ""), r.get("format", ""), r.get("relevance", ""),
                    r.get("host", ""), r.get("download_status", "")
                ))
            status = r.get("download_status", "Not attempted")
            if status != "Not attempted":
                size = r.get("bytes_downloaded", 0)
                self.download_tree.insert("", "end", values=(
                    category, r.get("name", ""), r.get("host", ""), status,
                    f"{size / 1024:.1f} KB" if size else "—",
                    r.get("local_path", "—")
                ))

    def update_chart(self):
        if not self.engine:
            return
        counts = Counter(r.get("category", "Other") for r in self.engine.resources.values())
        labels = ["Transport", "Geography", "Other"]
        values = [counts.get(label, 0) for label in labels]
        self.ax.clear()
        self.ax.set_facecolor(self.panel)
        if sum(values):
            colors = [self.cyan, self.green, "#596A83"]
            wedges, _ = self.ax.pie(
                values, startangle=90, counterclock=False, colors=colors,
                wedgeprops={"width": .34, "edgecolor": self.panel}
            )
            legend = [f"{label}   {value}" for label, value in zip(labels, values)]
            self.ax.legend(wedges, legend, loc="center left", bbox_to_anchor=(.82, .5),
                           frameon=False, labelcolor="#C8D4E5", fontsize=8)
            self.ax.text(0, 0, str(sum(values)), ha="center", va="center",
                         color=self.text, fontsize=20, fontweight="bold")
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        for spine in self.ax.spines.values():
            spine.set_visible(False)
        self.figure.tight_layout()
        self.chart_canvas.draw_idle()


if __name__ == "__main__":
    app = App()
    app.mainloop()
