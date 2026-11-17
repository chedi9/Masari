"""
Tunisia Mobility Platform — Data Ingestion Sprint 2026-11-13
Task: TUM-P0-003 — Download and profile 4 datasets from catalog.data.gov.tn
Rules: Zero spend, free/open data only (OTL), no invented data.
"""

import subprocess
import json
import os
import hashlib
import csv
import zipfile
import sys
import re
import datetime
from pathlib import Path

BASE = Path(r"c:\Users\awich\OneDrive\Bureau\transport\Tunisia_Mobility_Project_Starter")
RAW = BASE / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

results = {}  # dataset_id -> dict of profiling info

def run_curl(args, capture=True):
    """Run curl.exe with given args. Returns (returncode, stdout, stderr)."""
    cmd = ["curl.exe"] + args
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, r.stdout, r.stderr

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def file_size(path):
    return os.path.getsize(path)

def count_csv_rows(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.reader(f)
            headers = next(reader, [])
            count = sum(1 for _ in reader)
        return headers, count
    except Exception as e:
        return [], f"ERROR: {e}"

def sample_lat_lon(path, lat_col=None, lon_col=None):
    """Try to find lat/lon columns and return first 3 samples."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            # auto-detect lat/lon column names
            lat_candidates = [h for h in headers if re.search(r'lat|latitude|coord_y|y_wgs', h, re.I)]
            lon_candidates = [h for h in headers if re.search(r'lon|lng|longitude|coord_x|x_wgs', h, re.I)]
            if not lat_candidates or not lon_candidates:
                return None, headers
            lat_col = lat_candidates[0]
            lon_col = lon_candidates[0]
            samples = []
            for i, row in enumerate(reader):
                if i >= 3:
                    break
                samples.append((row.get(lat_col, ""), row.get(lon_col, "")))
            return samples, headers
    except Exception as e:
        return f"ERROR: {e}", []

# ─────────────────────────────────────────────────────────────
# STEP 1A — National Stop Registry (UUID 628f26a4-...)
# ─────────────────────────────────────────────────────────────
print("\n=== A) National Stop Registry ===")
UUID_A = "628f26a4-3ee0-4e9d-b8a1-9bb2c2f5b2ff"
rc, out, err = run_curl(["-k", "-s", "-m", "15",
    f"https://catalog.data.gov.tn/api/3/action/package_show?id={UUID_A}"])
print(f"  CKAN API rc={rc}, response len={len(out)}, stderr={err[:200] if err else ''}")

result_a = {"id": UUID_A, "name": "National Stop Registry", "ckan_rc": rc, "resources": [], "files": []}
if rc == 0 and out:
    try:
        data = json.loads(out)
        if data.get("success"):
            pkg = data["result"]
            result_a["title"] = pkg.get("title", "")
            result_a["license"] = pkg.get("license_id", "")
            result_a["notes"] = pkg.get("notes", "")[:200]
            resources = pkg.get("resources", [])
            print(f"  Found {len(resources)} resource(s)")
            for i, res in enumerate(resources):
                url = res.get("url", "")
                fmt = res.get("format", "").upper()
                name = res.get("name", f"resource_{i}")
                result_a["resources"].append({"name": name, "url": url, "format": fmt})
                print(f"  Resource {i}: {fmt} — {name} — {url[:80]}")
            # Try to download first CSV or XLSX
            for res in resources:
                url = res.get("url", "")
                fmt = res.get("format", "").upper()
                if not url:
                    continue
                ext = fmt.lower() if fmt else "csv"
                if ext not in ("csv", "xlsx", "xls", "json", "geojson", "zip"):
                    ext = url.rsplit(".", 1)[-1].lower() if "." in url else "csv"
                dest = RAW / f"national_stop_registry.{ext}"
                print(f"  Downloading {url[:80]} -> {dest.name}")
                rc2, _, err2 = run_curl(["-k", "-s", "-L", "-m", "30", "-o", str(dest), url])
                print(f"  Download rc={rc2} stderr={err2[:100] if err2 else ''}")
                if rc2 == 0 and dest.exists() and dest.stat().st_size > 100:
                    result_a["files"].append(str(dest))
                    print(f"  Saved {dest.stat().st_size} bytes")
                    break  # got one file — profile it
                else:
                    if dest.exists():
                        dest.unlink()
        else:
            result_a["error"] = data.get("error", "unknown")
            print(f"  CKAN error: {result_a['error']}")
    except Exception as e:
        result_a["error"] = str(e)
        print(f"  Parse error: {e}")
else:
    result_a["error"] = f"curl rc={rc} err={err[:200]}"
    print(f"  Failed: {result_a['error']}")

results["A"] = result_a

# ─────────────────────────────────────────────────────────────
# STEP 1B — Taxi Collectif Routes (UUID c07055ec-...)
# ─────────────────────────────────────────────────────────────
print("\n=== B) Taxi Collectif Routes ===")
UUID_B = "c07055ec-6049-4c02-a713-3174bd1da096"
rc, out, err = run_curl(["-k", "-s", "-m", "15",
    f"https://catalog.data.gov.tn/api/3/action/package_show?id={UUID_B}"])
print(f"  CKAN API rc={rc}, response len={len(out)}, stderr={err[:200] if err else ''}")

result_b = {"id": UUID_B, "name": "Taxi Collectif Routes", "ckan_rc": rc, "resources": [], "files": []}
if rc == 0 and out:
    try:
        data = json.loads(out)
        if data.get("success"):
            pkg = data["result"]
            result_b["title"] = pkg.get("title", "")
            result_b["license"] = pkg.get("license_id", "")
            resources = pkg.get("resources", [])
            print(f"  Found {len(resources)} resource(s)")
            for i, res in enumerate(resources):
                url = res.get("url", "")
                fmt = res.get("format", "").upper()
                name = res.get("name", f"resource_{i}")
                result_b["resources"].append({"name": name, "url": url, "format": fmt})
                print(f"  Resource {i}: {fmt} — {name[:50]} — {url[:80]}")
            # Download all CSVs
            for i, res in enumerate(resources):
                url = res.get("url", "")
                fmt = res.get("format", "").upper()
                if not url:
                    continue
                ext = "csv" if "csv" in fmt.lower() else (url.rsplit(".", 1)[-1].lower() if "." in url else "csv")
                safe_name = re.sub(r"[^\w\-]", "_", res.get("name", f"resource_{i}"))[:40]
                dest = RAW / f"taxi_collectif_{safe_name}.{ext}"
                print(f"  Downloading resource {i} -> {dest.name}")
                rc2, _, err2 = run_curl(["-k", "-s", "-L", "-m", "30", "-o", str(dest), url])
                print(f"  rc={rc2} stderr={err2[:100] if err2 else ''}")
                if rc2 == 0 and dest.exists() and dest.stat().st_size > 50:
                    result_b["files"].append(str(dest))
                    print(f"  Saved {dest.stat().st_size} bytes")
                else:
                    if dest.exists():
                        dest.unlink()
        else:
            result_b["error"] = data.get("error", "unknown")
            print(f"  CKAN error: {result_b['error']}")
    except Exception as e:
        result_b["error"] = str(e)
        print(f"  Parse error: {e}")
else:
    result_b["error"] = f"curl rc={rc} err={err[:200]}"
    print(f"  Failed: {result_b['error']}")

results["B"] = result_b

# ─────────────────────────────────────────────────────────────
# STEP 1C — TRANSTU GTFS (direct URL check)
# ─────────────────────────────────────────────────────────────
print("\n=== C) TRANSTU GTFS ===")
TRANSTU_URL = "http://data.transport.tn/dataset/8c42c45a-137c-444d-ab01-53ab50c5e583/resource/41e5bb3e-3ef6-4d1e-ba29-e504601ab17b/download/transtu_gtfs1.zip"
rc, out, err = run_curl(["-k", "-I", "-m", "10", TRANSTU_URL])
print(f"  HEAD rc={rc}")
print(f"  Headers: {out[:300]}")

result_c = {"name": "TRANSTU GTFS", "url": TRANSTU_URL, "files": []}
if rc == 0 and "200" in out:
    dest_c = RAW / "transtu_gtfs.zip"
    print("  HEAD 200 — downloading...")
    rc2, _, err2 = run_curl(["-k", "-s", "-L", "-m", "120", "-o", str(dest_c), TRANSTU_URL])
    print(f"  Download rc={rc2}")
    if rc2 == 0 and dest_c.exists() and dest_c.stat().st_size > 1000:
        result_c["files"].append(str(dest_c))
        result_c["status"] = "downloaded"
        print(f"  Saved {dest_c.stat().st_size} bytes")
    else:
        result_c["status"] = "download_failed"
        result_c["error"] = f"rc={rc2}"
        if dest_c.exists():
            dest_c.unlink()
else:
    result_c["status"] = "unreachable"
    result_c["head_rc"] = rc
    result_c["head_response"] = out[:200]
    print("  TRANSTU host still unreachable")

results["C"] = result_c

# ─────────────────────────────────────────────────────────────
# STEP 1D — RFR Station Mapping CSV (direct known URL)
# ─────────────────────────────────────────────────────────────
print("\n=== D) RFR Station Mapping ===")
RFR_URL = "https://catalogue-data.transport.tn/dataset/245e848e-2829-4548-b563-2e8c3bc52e97/resource/4c512d3f-bf5b-41ca-8e50-6d71a932b6fa/download/245e848e-2829-4548-b563-2e8c3bc52e97_43dbb48c-4576-4520-8d93-59c4b6585e01.csv"
dest_d = RAW / "rfr_stations.csv"
print(f"  Downloading {RFR_URL[:80]}")
rc, _, err = run_curl(["-k", "-s", "-L", "-m", "30", "-o", str(dest_d), RFR_URL])
print(f"  rc={rc} stderr={err[:200] if err else ''}")

result_d = {"name": "RFR Station Mapping", "url": RFR_URL, "files": []}
if rc == 0 and dest_d.exists() and dest_d.stat().st_size > 50:
    result_d["files"].append(str(dest_d))
    result_d["status"] = "downloaded"
    print(f"  Saved {dest_d.stat().st_size} bytes")
else:
    result_d["status"] = "failed"
    result_d["error"] = f"rc={rc}"
    if dest_d.exists():
        dest_d.unlink()

results["D"] = result_d

# ─────────────────────────────────────────────────────────────
# STEP 2 — Profile everything downloaded
# ─────────────────────────────────────────────────────────────
print("\n=== STEP 2: Profiling ===")

profiles = {}

def profile_csv(path):
    p = Path(path)
    if not p.exists():
        return {"error": "file not found"}
    headers, row_count = count_csv_rows(p)
    lat_lon_samples, _ = sample_lat_lon(p)
    return {
        "path": str(p),
        "size_bytes": file_size(p),
        "sha256": sha256_file(p),
        "format": "CSV",
        "row_count": row_count,
        "columns": headers,
        "geo_samples": lat_lon_samples,
    }

def profile_zip(path):
    p = Path(path)
    if not p.exists():
        return {"error": "file not found"}
    info = {
        "path": str(p),
        "size_bytes": file_size(p),
        "sha256": sha256_file(p),
        "format": "ZIP",
        "members": [],
    }
    try:
        with zipfile.ZipFile(p) as z:
            for member in z.infolist():
                info["members"].append({
                    "name": member.filename,
                    "size": member.file_size,
                    "compressed": member.compress_size,
                })
    except Exception as e:
        info["zip_error"] = str(e)
    return info

# Profile A
for f in results["A"].get("files", []):
    ext = f.rsplit(".", 1)[-1].lower()
    if ext == "csv":
        profiles["A"] = profile_csv(f)
    elif ext == "zip":
        profiles["A"] = profile_zip(f)
    else:
        p = Path(f)
        profiles["A"] = {"path": f, "size_bytes": p.stat().st_size if p.exists() else 0,
                         "sha256": sha256_file(f) if p.exists() else "", "format": ext.upper()}
    print(f"  A profiled: {profiles['A']}")

if "A" not in profiles:
    profiles["A"] = {"status": "no_file_downloaded", "resources": results["A"].get("resources", []),
                     "error": results["A"].get("error", "")}

# Profile B — multiple CSVs
profiles["B"] = []
for f in results["B"].get("files", []):
    ext = f.rsplit(".", 1)[-1].lower()
    p = profile_csv(f) if ext == "csv" else profile_zip(f)
    profiles["B"].append(p)
    print(f"  B profiled: {p}")
if not profiles["B"]:
    profiles["B"] = [{"status": "no_file_downloaded", "resources": results["B"].get("resources", []),
                      "error": results["B"].get("error", "")}]

# Profile C
if results["C"].get("files"):
    profiles["C"] = profile_zip(results["C"]["files"][0])
else:
    profiles["C"] = {"status": results["C"].get("status"), "error": results["C"].get("error", ""),
                     "head_response": results["C"].get("head_response", "")}
print(f"  C profiled: {profiles['C']}")

# Profile D
if results["D"].get("files"):
    profiles["D"] = profile_csv(results["D"]["files"][0])
else:
    profiles["D"] = {"status": results["D"].get("status"), "error": results["D"].get("error", "")}
print(f"  D profiled: {profiles['D']}")

# ─────────────────────────────────────────────────────────────
# STEP 3 — Generate report section for TUM-P0-003
# ─────────────────────────────────────────────────────────────

now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

def fmt_list(lst, limit=8):
    if isinstance(lst, list):
        s = ", ".join(str(x) for x in lst[:limit])
        if len(lst) > limit:
            s += f", ... ({len(lst)} total)"
        return s
    return str(lst)

def fmt_geo(samples):
    if not samples or isinstance(samples, str):
        return "N/A"
    return "; ".join(f"({lat}, {lon})" for lat, lon in samples)

# Section for A
def section_a():
    p = profiles.get("A", {})
    if p.get("status") == "no_file_downloaded":
        lines = [f"**Status:** No file downloaded — CKAN API accessible but download failed or no suitable resource URL."]
        for res in p.get("resources", []):
            lines.append(f"  - Resource: `{res.get('name')}` | Format: `{res.get('format')}` | URL: `{res.get('url', '')[:100]}`")
        if p.get("error"):
            lines.append(f"  - Error: {p['error'][:200]}")
        return "\n".join(lines)
    elif p.get("error"):
        return f"**Status:** CKAN API error — {p.get('error', '')[:200]}"
    else:
        cols = fmt_list(p.get("columns", []))
        geo = fmt_geo(p.get("geo_samples"))
        return f"""**Status:** Downloaded ✓
- **Path:** `{p.get('path','')}`
- **Size:** {p.get('size_bytes',0):,} bytes
- **SHA-256:** `{p.get('sha256','')}`
- **Format:** {p.get('format','')}
- **Row count:** {p.get('row_count','')}
- **Columns:** {cols}
- **Geographic samples (lat, lon):** {geo}"""

def section_b():
    items = profiles.get("B", [])
    if not items or (len(items) == 1 and items[0].get("status") == "no_file_downloaded"):
        p = items[0] if items else {}
        lines = [f"**Status:** No files downloaded — CKAN API accessible but download failed or no CSVs."]
        for res in results["B"].get("resources", []):
            lines.append(f"  - Resource: `{res.get('name')}` | Format: `{res.get('format')}` | URL: `{res.get('url','')[:100]}`")
        if p.get("error"):
            lines.append(f"  - Error: {p['error'][:200]}")
        return "\n".join(lines)
    out = [f"**Status:** {len(items)} file(s) downloaded ✓\n"]
    for p in items:
        fname = Path(p.get("path", "unknown")).name
        cols = fmt_list(p.get("columns", []))
        geo = fmt_geo(p.get("geo_samples"))
        out.append(f"##### `{fname}`")
        out.append(f"- **Size:** {p.get('size_bytes',0):,} bytes")
        out.append(f"- **SHA-256:** `{p.get('sha256','')}`")
        out.append(f"- **Format:** {p.get('format','')}")
        out.append(f"- **Rows:** {p.get('row_count','')}")
        out.append(f"- **Columns:** {cols}")
        out.append(f"- **Geographic samples:** {geo}")
        out.append("")
    return "\n".join(out)

def section_c():
    p = profiles.get("C", {})
    if p.get("status") in ("unreachable", None) and "members" not in p:
        return f"**Status:** Host still unreachable (HEAD rc={results['C'].get('head_rc','')}) — same failure mode as 2026-11-03. CKAN metadata previously verified.\n- **Head response:** `{p.get('head_response','')[:150]}`"
    elif p.get("status") == "download_failed":
        return f"**Status:** HEAD returned 200 but download failed — {p.get('error','')}"
    else:
        members = p.get("members", [])
        member_lines = "\n".join(f"  - `{m['name']}`: {m['size']:,} bytes" for m in members[:20])
        return f"""**Status:** Downloaded ✓
- **Path:** `{p.get('path','')}`
- **Size:** {p.get('size_bytes',0):,} bytes
- **SHA-256:** `{p.get('sha256','')}`
- **Format:** ZIP (GTFS)
- **Members ({len(members)}):**
{member_lines}"""

def section_d():
    p = profiles.get("D", {})
    if p.get("status") in ("failed", None) and "sha256" not in p:
        return f"**Status:** Download failed — {p.get('error','')[:200]}"
    cols = fmt_list(p.get("columns", []))
    geo = fmt_geo(p.get("geo_samples"))
    return f"""**Status:** Downloaded ✓
- **Path:** `{p.get('path','')}`
- **Size:** {p.get('size_bytes',0):,} bytes
- **SHA-256:** `{p.get('sha256','')}`
- **Format:** CSV
- **Row count:** {p.get('row_count','')}
- **Columns:** {cols}
- **Geographic samples (lat, lon):** {geo}"""

report_section = f"""
---

## 2026-11-13 Additional Downloads

**Sprint date:** {now}
**Agent:** Antigravity data-ingestor (Python 3 + curl.exe)
**Method:** CKAN API `package_show` for A and B; direct URL for C and D.

### A — National Stop Registry (UUID `628f26a4-3ee0-4e9d-b8a1-9bb2c2f5b2ff`)

{section_a()}

---

### B — Taxi Collectif Routes (UUID `c07055ec-6049-4c02-a713-3174bd1da096`)

{section_b()}

---

### C — TRANSTU GTFS Zip

{section_c()}

---

### D — RFR Station Mapping CSV

{section_d()}

---

### Sprint Summary

| Dataset | Download | File(s) |
|---|---|---|
| A — National Stop Registry | {"✓" if results["A"].get("files") else "✗ CKAN accessible, no download"} | {", ".join(Path(f).name for f in results["A"].get("files", [])) or "—"} |
| B — Taxi Collectif Routes | {"✓ " + str(len(results["B"].get("files",[]))) + " file(s)" if results["B"].get("files") else "✗ CKAN accessible, no download"} | {", ".join(Path(f).name for f in results["B"].get("files", [])) or "—"} |
| C — TRANSTU GTFS | {"✓" if results["C"].get("files") else "✗ unreachable"} | {Path(results["C"]["files"][0]).name if results["C"].get("files") else "—"} |
| D — RFR Stations | {"✓" if results["D"].get("files") else "✗ failed"} | {Path(results["D"]["files"][0]).name if results["D"].get("files") else "—"} |
"""

print("\n=== REPORT SECTION GENERATED ===")
print(report_section[:500])

# Save report to a temp file for the caller to read
out_path = BASE / "scripts" / "ingest_report_2026_11_13.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump({"profiles": {k: (v if not isinstance(v, list) else v) for k, v in profiles.items()},
               "results": {k: {kk: vv for kk, vv in v.items() if kk != "resources" or True}
                           for k, v in results.items()}}, f, indent=2, default=str)
print(f"\nJSON report saved to: {out_path}")

# Also print the full text section
print("\n===SECTION_START===")
print(report_section)
print("===SECTION_END===")
