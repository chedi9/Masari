#!/usr/bin/env python3
# MASARI Local Geographic Data Diagnostic
# Read-only: scans local files and writes reports to a separate output folder.
# Python standard library only.

from __future__ import annotations
import csv
import datetime as dt
import hashlib
import json
import math
import os
import re
import struct
import sys
import zipfile
from collections import Counter
from pathlib import Path
from tkinter import Tk, filedialog, messagebox

TARGET_HINTS = [
    "779dae17", "TN-Découpage_de_la_Tunisie_par_Gouvernorats",
    "01b6fc4a", "TN-Découpage_de_la_Tunisie_par_Délégations",
    "fd1d28bb", "TN-Découpage_de_la_Tunisie_par_circonsciptions",
    "cbe6f9ee", "Découpage_administratif_de_la_Tunisie_par_Délégation",
    "5c677281", "Découpage_administratif_de_la_Tunisie_par_Gouvernorat",
    "9e445b0b", "TN-Carte_de_la_Tunisie",
]
NAME_KEYS = {"name", "nom", "label", "libelle", "libellé", "gouvernorat",
             "governorate", "delegation", "délégation", "circonscription",
             "municipality", "municipalite", "commune", "ville", "localite",
             "localité", "ar_name", "fr_name", "name_ar", "name_fr"}
COORD_KEYS = {"coordinates", "coords", "geometry", "geom", "latitude",
              "longitude", "lat", "lon", "lng", "x", "y"}

def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def safe_text(raw):
    for enc in ("utf-8-sig", "utf-8", "cp1256", "latin-1"):
        try:
            return raw.decode(enc), enc
        except UnicodeDecodeError:
            pass
    return raw.decode("utf-8", errors="replace"), "utf-8-replacement"

def walk_json(obj, stats, depth=0):
    if depth > 40:
        return
    if isinstance(obj, dict):
        stats["dict_count"] += 1
        for k, v in obj.items():
            key = str(k).strip().lower()
            if key in NAME_KEYS and isinstance(v, (str, int, float)):
                s = str(v).strip()
                if s and len(s) < 180:
                    stats["names"].add(s)
            if key in {"type"} and isinstance(v, str):
                if v in {"Feature", "FeatureCollection", "Point", "MultiPoint",
                         "LineString", "MultiLineString", "Polygon",
                         "MultiPolygon", "GeometryCollection"}:
                    stats["geo_types"][v] += 1
            if key in {"coordinates", "geometry"}:
                collect_coords(v, stats)
            walk_json(v, stats, depth + 1)
    elif isinstance(obj, list):
        stats["list_count"] += 1
        for v in obj:
            walk_json(v, stats, depth + 1)

def collect_coords(obj, stats):
    # Collect coordinate pairs conservatively; ignore non-numeric / malformed values.
    if isinstance(obj, (list, tuple)):
        if len(obj) >= 2 and all(isinstance(x, (int, float)) and math.isfinite(x) for x in obj[:2]):
            x, y = float(obj[0]), float(obj[1])
            if -180 <= x <= 180 and -90 <= y <= 90:
                stats["coord_count"] += 1
                stats["min_lon"] = x if stats["min_lon"] is None else min(stats["min_lon"], x)
                stats["max_lon"] = x if stats["max_lon"] is None else max(stats["max_lon"], x)
                stats["min_lat"] = y if stats["min_lat"] is None else min(stats["min_lat"], y)
                stats["max_lat"] = y if stats["max_lat"] is None else max(stats["max_lat"], y)
                if 7.0 <= x <= 12.5 and 30.0 <= y <= 38.0:
                    stats["tunisia_coord_count"] += 1
                return
        for child in obj:
            collect_coords(child, stats)

def new_stats():
    return {"dict_count": 0, "list_count": 0, "names": set(),
            "geo_types": Counter(), "coord_count": 0, "tunisia_coord_count": 0,
            "min_lon": None, "max_lon": None, "min_lat": None, "max_lat": None}

def inspect_json(raw):
    text, enc = safe_text(raw)
    try:
        obj = json.loads(text)
    except Exception as e:
        return {"parse_ok": False, "encoding": enc, "error": str(e)[:300],
                "text_preview": text[:500]}
    s = new_stats()
    walk_json(obj, s)
    feature_count = None
    if isinstance(obj, dict):
        if obj.get("type") == "FeatureCollection" and isinstance(obj.get("features"), list):
            feature_count = len(obj["features"])
        elif isinstance(obj.get("features"), list):
            feature_count = len(obj["features"])
    return {
        "parse_ok": True, "encoding": enc,
        "root_type": type(obj).__name__,
        "root_keys": list(obj.keys())[:100] if isinstance(obj, dict) else None,
        "feature_count": feature_count,
        "object_count": s["dict_count"], "array_count": s["list_count"],
        "geometry_types": dict(s["geo_types"]),
        "coordinate_pairs": s["coord_count"],
        "coordinates_in_tunisia_bbox": s["tunisia_coord_count"],
        "coordinate_bounds_lon_lat": [s["min_lon"], s["min_lat"], s["max_lon"], s["max_lat"]],
        "sample_names": sorted(s["names"])[:80],
    }

def inspect_csv(raw):
    text, enc = safe_text(raw[:8 * 1024 * 1024])
    sample = text[:65536]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\\t|")
        delim = dialect.delimiter
    except Exception:
        delim = max([",", ";", "\t", "|"], key=lambda d: sample.count(d))
    rows = []
    try:
        reader = csv.reader(text.splitlines(), delimiter=delim)
        for row in reader:
            if row and any(str(c).strip() for c in row):
                rows.append(row)
            if len(rows) >= 10001:
                break
    except Exception as e:
        return {"parse_ok": False, "encoding": enc, "delimiter": repr(delim), "error": str(e)[:300]}
    header = rows[0] if rows else []
    return {
        "parse_ok": bool(rows), "encoding": enc, "delimiter": "\t" if delim == "\t" else delim,
        "rows_sampled_including_header": len(rows), "columns": len(header),
        "headers": header[:150],
        "sample_rows": rows[1:6],
        "warning": "Only first 10,000 non-empty rows inspected" if len(rows) >= 10001 else None,
        "json_like_first_character": text.lstrip()[:1] in ("{", "["),
    }

def inspect_zip(path):
    result = {"zip_valid": False, "members": [], "shapefile_components": [],
              "gtfs_text_files": [], "xlsx_detected": False}
    try:
        with zipfile.ZipFile(path) as z:
            bad = z.testzip()
            names = z.namelist()
            result.update({"zip_valid": bad is None, "first_corrupt_member": bad,
                           "member_count": len(names), "members": names[:300]})
            lower = [n.lower() for n in names]
            result["shapefile_components"] = [n for n in names if Path(n).suffix.lower() in
                                              {".shp", ".shx", ".dbf", ".prj", ".cpg"}]
            result["gtfs_text_files"] = [n for n in names if Path(n).name.lower() in
                                         {"agency.txt", "stops.txt", "routes.txt", "trips.txt",
                                          "stop_times.txt", "calendar.txt", "calendar_dates.txt"}]
            result["xlsx_detected"] = "[content_types].xml" in lower and any(n.startswith("xl/") for n in lower)
            result["likely_shapefile_archive"] = any(n.lower().endswith(".shp") for n in names) and any(n.lower().endswith(".dbf") for n in names)
            result["likely_gtfs_archive"] = len(result["gtfs_text_files"]) >= 3
    except Exception as e:
        result["error"] = str(e)[:300]
    return result

def inspect_file(path):
    st = path.stat()
    raw_head = path.read_bytes()[:2 * 1024 * 1024]
    full_hash = sha256_file(path)
    result = {"file": str(path), "name": path.name, "size_bytes": st.st_size,
              "sha256": full_hash, "extension": path.suffix.lower(),
              "magic_hex": raw_head[:32].hex(" "), "detected_format": "UNKNOWN"}
    if raw_head.startswith(b"PK\x03\x04") or raw_head.startswith(b"PK\x05\x06"):
        result["detected_format"] = "ZIP"
        result["zip"] = inspect_zip(path)
        if result["zip"].get("xlsx_detected"):
            result["detected_format"] = "XLSX"
        elif result["zip"].get("likely_gtfs_archive"):
            result["detected_format"] = "GTFS-ZIP"
        elif result["zip"].get("likely_shapefile_archive"):
            result["detected_format"] = "SHAPEFILE-ZIP"
    elif raw_head.startswith(b"%PDF-"):
        result["detected_format"] = "PDF"
    elif raw_head.startswith(b"\x89PNG\r\n\x1a\n"):
        result["detected_format"] = "PNG"
    elif raw_head.startswith((b"\xff\xfe", b"\xfe\xff")):
        result["detected_format"] = "TEXT-UTF16"
    else:
        txt, enc = safe_text(raw_head)
        stripped = txt.lstrip("\ufeff \t\r\n")
        if stripped.startswith(("{", "[")):
            j = inspect_json(path.read_bytes())
            result["json"] = j
            if j.get("parse_ok"):
                root = j.get("root_keys") or []
                result["detected_format"] = "GEOJSON" if ("type" in root and j.get("geometry_types")) else "JSON"
            else:
                result["detected_format"] = "JSON-LIKE-INVALID"
        elif "\x00" not in txt[:1000] and ("," in txt[:4096] or ";" in txt[:4096]):
            c = inspect_csv(path.read_bytes())
            result["csv"] = c
            result["detected_format"] = "CSV" if c.get("parse_ok") else "TEXT"
            if c.get("json_like_first_character"):
                result["detected_format"] = "JSON-LIKE-MISLABELLED"
        elif txt.strip():
            result["detected_format"] = "TEXT"
            result["text_encoding"] = enc
            result["text_preview"] = txt[:500]
        else:
            result["detected_format"] = "BINARY"
    # Parse JSON independently even if file extension suggests CSV.
    if result["detected_format"] in {"JSON", "GEOJSON", "JSON-LIKE-INVALID"}:
        pass
    elif raw_head.lstrip().startswith((b"{", b"[")):
        result["json"] = inspect_json(path.read_bytes())
        result["detected_format"] = "JSON" if result["json"].get("parse_ok") else "JSON-LIKE-INVALID"
    return result

def choose_folder():
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    folder = filedialog.askdirectory(title="Select MASARI Recovery Studio run folder (or its downloaded/raw folder)")
    root.destroy()
    return Path(folder) if folder else None

def discover_files(folder):
    found = []
    for p in folder.rglob("*"):
        if p.is_file() and not any(part.lower() in {"diagnostic_output", "__pycache__"} for part in p.parts):
            found.append(p)
    # Prioritize named target resources but also inspect all files in selected folder.
    return found

def main():
    print("=" * 72)
    print("MASARI LOCAL GEOGRAPHIC DATA DIAGNOSTIC")
    print("Read-only scan. Original files will not be modified.")
    print("=" * 72)
    folder = choose_folder()
    if not folder:
        print("No folder selected. Exiting.")
        return 2
    files = discover_files(folder)
    if not files:
        print("No files found in selected folder.")
        return 2
    out = folder / "MASARI_DIAGNOSTIC_OUTPUT"
    out.mkdir(exist_ok=True)
    records, errors = [], []
    print(f"Selected: {folder}")
    print(f"Files found: {len(files)}")
    for i, path in enumerate(files, 1):
        try:
            rec = inspect_file(path)
            records.append(rec)
            print(f"[{i}/{len(files)}] {path.name[:58]} -> {rec['detected_format']}")
        except Exception as e:
            errors.append({"file": str(path), "error": str(e)[:500]})
            print(f"[{i}/{len(files)}] ERROR {path.name}: {e}")
    report = {
        "tool": "MASARI Local Geographic Data Diagnostic",
        "version": "1.0",
        "generated_at": dt.datetime.now().astimezone().isoformat(),
        "selected_folder": str(folder),
        "files_scanned": len(files),
        "files_inspected": len(records),
        "errors": errors,
        "format_counts": dict(Counter(r["detected_format"] for r in records)),
        "files": records,
    }
    json_path = out / "masari_geographic_diagnostic.json"
    txt_path = out / "masari_geographic_diagnostic_summary.txt"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "MASARI LOCAL GEOGRAPHIC DATA DIAGNOSTIC",
        f"Generated: {report['generated_at']}",
        f"Folder: {folder}",
        f"Files inspected: {len(records)}",
        f"Format counts: {json.dumps(report['format_counts'], ensure_ascii=False)}",
        "",
        "FILE RESULTS",
        "-" * 72,
    ]
    for r in records:
        lines += [f"\n{r['name']}", f"  Format: {r['detected_format']}",
                  f"  Size: {r['size_bytes']:,} bytes", f"  SHA256: {r['sha256']}"]
        if "json" in r:
            j = r["json"]
            lines += [f"  JSON valid: {j.get('parse_ok')}",
                      f"  Root keys: {j.get('root_keys')}",
                      f"  Features: {j.get('feature_count')}",
                      f"  Geometry types: {j.get('geometry_types')}",
                      f"  Coordinate pairs: {j.get('coordinate_pairs')}",
                      f"  Tunisia bbox coordinate pairs: {j.get('coordinates_in_tunisia_bbox')}",
                      f"  Bounds lon/lat: {j.get('coordinate_bounds_lon_lat')}",
                      f"  Sample names: {j.get('sample_names')}"]
        if "csv" in r:
            c = r["csv"]
            lines += [f"  CSV headers: {c.get('headers')}",
                      f"  CSV sample rows: {c.get('sample_rows')}",
                      f"  CSV warning: {c.get('warning')}"]
        if "zip" in r:
            z = r["zip"]
            lines += [f"  ZIP valid: {z.get('zip_valid')}",
                      f"  Members: {z.get('member_count')}",
                      f"  Shapefile components: {z.get('shapefile_components')}",
                      f"  GTFS files: {z.get('gtfs_text_files')}",
                      f"  XLSX: {z.get('xlsx_detected')}"]
    lines += ["", "Errors:", json.dumps(errors, ensure_ascii=False, indent=2)]
    txt_path.write_text("\n".join(lines), encoding="utf-8")
    print("\\n" + "=" * 72)
    print("DIAGNOSTIC COMPLETE")
    print(f"JSON report: {json_path}")
    print(f"Text summary: {txt_path}")
    print("Open the TEXT summary first. Paste its contents here.")
    print("If it is too long, paste format counts and the entries for the six target files.")
    print("=" * 72)
    try:
        os.startfile(txt_path)
    except Exception:
        pass
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
