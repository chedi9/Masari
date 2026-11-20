"""
GTFS Folder Importer — Tunisia Mobility Platform
Imports an uncompressed GTFS directory (e.g. RFR Tunis) directly into SQLite.
"""

import os
import sys
import csv
import sqlite3

def import_gtfs_folder(folder_path: str, db_path: str):
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder not found: {folder_path}")
        
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.executescript("""
    PRAGMA foreign_keys = ON;
    DROP TABLE IF EXISTS fare_rules;
    DROP TABLE IF EXISTS fare_attributes;
    DROP TABLE IF EXISTS stop_times;
    DROP TABLE IF EXISTS trips;
    DROP TABLE IF EXISTS stops;
    DROP TABLE IF EXISTS routes;
    DROP TABLE IF EXISTS agencies;

    CREATE TABLE agencies (
        agency_id TEXT PRIMARY KEY,
        agency_name TEXT NOT NULL,
        agency_url TEXT,
        agency_timezone TEXT,
        agency_lang TEXT
    );

    CREATE TABLE routes (
        route_id TEXT PRIMARY KEY,
        agency_id TEXT,
        route_short_name TEXT,
        route_long_name TEXT,
        route_type INTEGER,
        FOREIGN KEY (agency_id) REFERENCES agencies(agency_id)
    );

    CREATE TABLE stops (
        stop_id TEXT PRIMARY KEY,
        stop_name TEXT NOT NULL,
        stop_lat REAL NOT NULL,
        stop_lon REAL NOT NULL
    );

    CREATE TABLE trips (
        trip_id TEXT PRIMARY KEY,
        route_id TEXT NOT NULL,
        service_id TEXT,
        trip_headsign TEXT,
        FOREIGN KEY (route_id) REFERENCES routes(route_id)
    );

    CREATE TABLE stop_times (
        trip_id TEXT NOT NULL,
        arrival_time TEXT NOT NULL,
        departure_time TEXT NOT NULL,
        stop_id TEXT NOT NULL,
        stop_sequence INTEGER NOT NULL,
        PRIMARY KEY (trip_id, stop_sequence),
        FOREIGN KEY (trip_id) REFERENCES trips(trip_id),
        FOREIGN KEY (stop_id) REFERENCES stops(stop_id)
    );

    CREATE TABLE fare_attributes (
        fare_id TEXT PRIMARY KEY,
        price_tnd REAL NOT NULL,
        price_millimes INTEGER NOT NULL,
        payment_method INTEGER,
        transfers INTEGER,
        agency_id TEXT
    );

    CREATE TABLE fare_rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fare_id TEXT NOT NULL,
        route_id TEXT,
        origin_id TEXT,
        destination_id TEXT,
        FOREIGN KEY (fare_id) REFERENCES fare_attributes(fare_id)
    );

    CREATE INDEX idx_stop_times_trip ON stop_times(trip_id);
    CREATE INDEX idx_stop_times_stop ON stop_times(stop_id);
    CREATE INDEX idx_stops_name ON stops(stop_name COLLATE NOCASE);
    CREATE INDEX idx_trips_route ON trips(route_id);
    """)

    def read_csv(filename):
        p = os.path.join(folder_path, filename)
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8-sig') as f:
                return list(csv.DictReader(f))
        return []

    # 1. agencies
    agencies = read_csv('agency.txt')
    for r in agencies:
        cur.execute("INSERT OR REPLACE INTO agencies VALUES (?, ?, ?, ?, ?)",
                    (r.get('agency_id'), r.get('agency_name'), r.get('agency_url'), r.get('agency_timezone'), r.get('agency_lang')))
    print(f"  Imported {len(agencies)} agencies")

    # 2. routes
    routes = read_csv('routes.txt')
    for r in routes:
        cur.execute("INSERT OR REPLACE INTO routes VALUES (?, ?, ?, ?, ?)",
                    (r.get('route_id'), r.get('agency_id', agencies[0]['agency_id'] if agencies else None),
                     r.get('route_short_name'), r.get('route_long_name'), r.get('route_type', 2)))
    print(f"  Imported {len(routes)} routes")

    # 3. stops
    stops = read_csv('stops.txt')
    for r in stops:
        cur.execute("INSERT OR REPLACE INTO stops VALUES (?, ?, ?, ?)",
                    (r.get('stop_id'), r.get('stop_name'), float(r.get('stop_lat', 0)), float(r.get('stop_lon', 0))))
    print(f"  Imported {len(stops)} stops")

    # 4. trips
    trips = read_csv('trips.txt')
    for r in trips:
        cur.execute("INSERT OR REPLACE INTO trips VALUES (?, ?, ?, ?)",
                    (r.get('trip_id'), r.get('route_id'), r.get('service_id'), r.get('trip_headsign')))
    print(f"  Imported {len(trips)} trips")

    # 5. stop_times
    stop_times = read_csv('stop_times.txt')
    batch = []
    for r in stop_times:
        batch.append((r.get('trip_id'), r.get('arrival_time'), r.get('departure_time'), r.get('stop_id'), int(r.get('stop_sequence', 0))))
    cur.executemany("INSERT OR REPLACE INTO stop_times VALUES (?, ?, ?, ?, ?)", batch)
    print(f"  Imported {len(stop_times)} stop_times")

    conn.commit()
    conn.close()
    print(f"RFR GTFS successfully imported to {db_path}!")

if __name__ == '__main__':
    # Determine base directory dynamically based on current working directory
    if os.path.exists(os.path.join("tunisia_transport_data", "rfr_tunis", "gtfs")):
        default_src = os.path.join("tunisia_transport_data", "rfr_tunis", "gtfs")
        default_dst = os.path.join("..", "..", "..", "data", "processed", "rfr_tunis.db")
    else:
        default_src = os.path.join("tools", "data_pipeline", "sources", "tunisia_transport_data", "rfr_tunis", "gtfs")
        default_dst = os.path.join("data", "processed", "rfr_tunis.db")

    src = sys.argv[1] if len(sys.argv) > 1 else default_src
    dst = sys.argv[2] if len(sys.argv) > 2 else default_dst
    import_gtfs_folder(src, dst)
