"""
TRANSTU GTFS Downloader & Importer – Tunisia Mobility Platform

This helper script downloads the public TRANSTU GTFS archive from the
Ministry catalogue and imports it into a SQLite database using the same
schema as the existing SNCFT importer.

Features:
  • Simple progress indicator while downloading (percentage and size).
  • Handles network errors and retries (max 3 attempts).
  • After successful download it calls the generic `import_gtfs` function
    (re‑implemented locally to avoid external imports) to build
    `data/processed/transtu.db`.
  • Prints a concise summary of row counts for each table – useful to
    verify that the import completed without getting stuck.

Usage (from the repository root):
    python tools/data_pipeline/sources/download_and_import_transtu.py

Optional arguments:
  --url <gtfs_url>        Override the default catalogue URL.
  --zip <path>            Destination path for the downloaded zip.
  --db  <path>            Destination SQLite DB (default: data/processed/transtu.db).

The script relies only on the Python standard library (urllib, zipfile,
csv, sqlite3, sys, os, argparse, time) – no extra packages, keeping the
zero‑spend policy.
"""

import argparse
import os
import sys
import time
import urllib.request
import zipfile
import csv
import io
import sqlite3
from pathlib import Path

DEFAULT_GTFS_URL = (
    "https://catalogue-data.transport.tn/dataset/horaires-des-voyages-de-la-transtu-gtfs/"
    "resource/fe6c29b8-86c8-44cd-b36d-d41b70fab3f2/download/horaires-des-voyages-de-la-transtu-gtfs.zip"
)

def download_gtfs(url: str, dest_path: str, retries: int = 3) -> None:
    """Download a GTFS zip with a basic progress bar.
    Parameters
    ----------
    url: str – HTTP URL of the GTFS archive.
    dest_path: str – Local file path where the zip will be saved.
    retries: int – Number of retry attempts on failure.
    """
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(url) as resp:
                total = int(resp.getheader('Content-Length', '0'))
                print(f"Downloading GTFS ({total // 1024:,} KB) – attempt {attempt}/{retries}")
                chunk_size = 8192
                downloaded = 0
                with open(dest_path, "wb") as out_file:
                    while True:
                        chunk = resp.read(chunk_size)
                        if not chunk:
                            break
                        out_file.write(chunk)
                        downloaded += len(chunk)
                        if total:
                            pct = downloaded * 100 // total
                            print(f"\r  {pct:3d}% ({downloaded // 1024:,} KB)", end="")
                        else:
                            print(f"\r  {downloaded // 1024:,} KB downloaded", end="")
                print("\nDownload completed.")
            return
        except Exception as exc:
            print(f"\nError during download: {exc}")
            if attempt == retries:
                raise
            wait = 2 ** attempt
            print(f"Retrying in {wait}s…")
            time.sleep(wait)

def import_gtfs(zip_path: str, db_path: str) -> None:
    """Import a GTFS zip into a SQLite database using the shared schema."""
    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"GTFS archive not found at: {zip_path}")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # Schema (same as SNCFT importer)
    cur.executescript("""
    PRAGMA foreign_keys = ON;
    DROP TABLE IF EXISTS fare_rules;
    DROP TABLE IF EXISTS fare_attributes;
    DROP TABLE IF EXISTS stop_times;
    DROP TABLE IF EXISTS trips;
    DROP TABLE IF EXISTS stops;
    DROP TABLE IF EXISTS routes;
    DROP TABLE IF EXISTS agencies;
    CREATE TABLE agencies (agency_id TEXT PRIMARY KEY, agency_name TEXT NOT NULL, agency_url TEXT, agency_timezone TEXT, agency_lang TEXT);
    CREATE TABLE routes (route_id TEXT PRIMARY KEY, agency_id TEXT, route_short_name TEXT, route_long_name TEXT, route_type INTEGER, FOREIGN KEY (agency_id) REFERENCES agencies(agency_id));
    CREATE TABLE stops (stop_id TEXT PRIMARY KEY, stop_name TEXT NOT NULL, stop_lat REAL NOT NULL, stop_lon REAL NOT NULL);
    CREATE TABLE trips (trip_id TEXT PRIMARY KEY, route_id TEXT NOT NULL, service_id TEXT, trip_headsign TEXT, FOREIGN KEY (route_id) REFERENCES routes(route_id));
    CREATE TABLE stop_times (trip_id TEXT NOT NULL, arrival_time TEXT NOT NULL, departure_time TEXT NOT NULL, stop_id TEXT NOT NULL, stop_sequence INTEGER NOT NULL, PRIMARY KEY (trip_id, stop_sequence), FOREIGN KEY (trip_id) REFERENCES trips(trip_id), FOREIGN KEY (stop_id) REFERENCES stops(stop_id));
    CREATE TABLE fare_attributes (fare_id TEXT PRIMARY KEY, price_tnd REAL NOT NULL, price_millimes INTEGER NOT NULL, payment_method INTEGER, transfers INTEGER, agency_id TEXT);
    CREATE TABLE fare_rules (id INTEGER PRIMARY KEY AUTOINCREMENT, fare_id TEXT NOT NULL, route_id TEXT, origin_id TEXT, destination_id TEXT, FOREIGN KEY (fare_id) REFERENCES fare_attributes(fare_id));
    CREATE INDEX idx_stop_times_trip ON stop_times(trip_id);
    CREATE INDEX idx_stop_times_stop ON stop_times(stop_id);
    CREATE INDEX idx_stops_name ON stops(stop_name COLLATE NOCASE);
    CREATE INDEX idx_trips_route ON trips(route_id);
    """)
    print(f"Opening GTFS archive: {zip_path}")
    with zipfile.ZipFile(zip_path, 'r') as z:
        # agencies
        if 'agency.txt' in z.namelist():
            with z.open('agency.txt') as f:
                reader = csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig'))
                for r in reader:
                    cur.execute(
                        "INSERT OR REPLACE INTO agencies (agency_id, agency_name, agency_url, agency_timezone, agency_lang) VALUES (?,?,?,?,?)",
                        (r.get('agency_id'), r.get('agency_name'), r.get('agency_url'), r.get('agency_timezone'), r.get('agency_lang')))
            print("  Imported agencies")
        # routes
        if 'routes.txt' in z.namelist():
            with z.open('routes.txt') as f:
                reader = csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig'))
                for r in reader:
                    cur.execute(
                        "INSERT OR REPLACE INTO routes (route_id, agency_id, route_short_name, route_long_name, route_type) VALUES (?,?,?,?,?)",
                        (r.get('route_id'), r.get('agency_id'), r.get('route_short_name'), r.get('route_long_name'), r.get('route_type')))
            print("  Imported routes")
        # stops
        if 'stops.txt' in z.namelist():
            with z.open('stops.txt') as f:
                reader = csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig'))
                for r in reader:
                    cur.execute(
                        "INSERT OR REPLACE INTO stops (stop_id, stop_name, stop_lat, stop_lon) VALUES (?,?,?,?)",
                        (r.get('stop_id'), r.get('stop_name'), float(r.get('stop_lat',0)), float(r.get('stop_lon',0))))
            print("  Imported stops")
        # trips
        if 'trips.txt' in z.namelist():
            with z.open('trips.txt') as f:
                reader = csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig'))
                for r in reader:
                    cur.execute(
                        "INSERT OR REPLACE INTO trips (trip_id, route_id, service_id, trip_headsign) VALUES (?,?,?,?)",
                        (r.get('trip_id'), r.get('route_id'), r.get('service_id'), r.get('trip_headsign')))
            print("  Imported trips")
        # stop_times
        if 'stop_times.txt' in z.namelist():
            with z.open('stop_times.txt') as f:
                reader = csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig'))
                batch = []
                for r in reader:
                    batch.append((r.get('trip_id'), r.get('arrival_time'), r.get('departure_time'), r.get('stop_id'), int(r.get('stop_sequence',0))))
                    if len(batch) >= 1000:
                        cur.executemany(
                            "INSERT OR REPLACE INTO stop_times (trip_id, arrival_time, departure_time, stop_id, stop_sequence) VALUES (?,?,?,?,?)",
                            batch)
                        batch.clear()
                if batch:
                    cur.executemany(
                        "INSERT OR REPLACE INTO stop_times (trip_id, arrival_time, departure_time, stop_id, stop_sequence) VALUES (?,?,?,?,?)",
                        batch)
            print("  Imported stop_times")
        # optional fare tables
        if 'fare_attributes.txt' in z.namelist():
            with z.open('fare_attributes.txt') as f:
                reader = csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig'))
                for r in reader:
                    price_tnd = float(r.get('price',0))
                    price_mill = int(round(price_tnd*1000))
                    cur.execute(
                        "INSERT OR REPLACE INTO fare_attributes (fare_id, price_tnd, price_millimes, payment_method, transfers, agency_id) VALUES (?,?,?,?,?,?)",
                        (r.get('fare_id'), price_tnd, price_mill, r.get('payment_method'), r.get('transfers'), r.get('agency_id')))
            print("  Imported fare_attributes")
        if 'fare_rules.txt' in z.namelist():
            with z.open('fare_rules.txt') as f:
                reader = csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig'))
                batch = []
                for r in reader:
                    batch.append((r.get('fare_id'), r.get('route_id'), r.get('origin_id'), r.get('destination_id')))
                    if len(batch) >= 1000:
                        cur.executemany(
                            "INSERT INTO fare_rules (fare_id, route_id, origin_id, destination_id) VALUES (?,?,?,?)",
                            batch)
                        batch.clear()
                if batch:
                    cur.executemany(
                        "INSERT INTO fare_rules (fare_id, route_id, origin_id, destination_id) VALUES (?,?,?,?)",
                        batch)
            print("  Imported fare_rules")
    conn.commit()
    print("\n--- DATABASE SUMMARY ---")
    for table in ['agencies','routes','stops','trips','stop_times','fare_attributes','fare_rules']:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        cnt = cur.fetchone()[0]
        print(f"  {table:16}: {cnt:,} records")
    conn.close()
    print(f"\nDatabase successfully built at: {db_path}")

def main():
    parser = argparse.ArgumentParser(description='Download TRANSTU GTFS and import to SQLite')
    parser.add_argument('--url', default=DEFAULT_GTFS_URL, help='GTFS download URL')
    parser.add_argument('--zip', default=os.path.join('data','raw','transtu_gtfs.zip'), help='Destination zip file')
    parser.add_argument('--db', default=os.path.join('data','processed','transtu.db'), help='SQLite DB output')
    args = parser.parse_args()
    zip_path = Path(args.zip)
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        download_gtfs(args.url, str(zip_path))
    except Exception as e:
        print(f'Failed to download GTFS: {e}')
        sys.exit(1)
    try:
        import_gtfs(str(zip_path), args.db)
    except Exception as e:
        print(f'Import failed: {e}')
        sys.exit(2)

if __name__ == '__main__':
    main()
