"""
MASARI 3.6 - GTFS Schedule Tables Setup
Ajoute les tables de gestion des horaires, fréquences et calendriers dans SQLite.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(r"C:\Users\awich\OneDrive\Bureau\working folder\MASARI_Recovery_3_6\run_20261115_023158\tunisia_mobility.db")

def create_schedule_tables():
    if not DB_PATH.exists():
        print(f"[ERREUR] Base de données introuvable : {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("[INFO] Création des tables GTFS d'horaires dans SQLite...")

    # 1. Table des calendriers (Jours de service : jours de la semaine, vacances, etc.)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS calendar (
            service_id TEXT PRIMARY KEY,
            monday INTEGER,
            tuesday INTEGER,
            wednesday INTEGER,
            thursday INTEGER,
            friday INTEGER,
            saturday INTEGER,
            sunday INTEGER,
            start_date TEXT,
            end_date TEXT
        )
    """)

    # 2. Table des voyages (Relie une ligne à un calendrier de service)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS trips (
            trip_id TEXT PRIMARY KEY,
            route_id TEXT,
            service_id TEXT,
            trip_headsign TEXT,
            direction_id INTEGER,
            FOREIGN KEY(route_id) REFERENCES routes_registry(route_id),
            FOREIGN KEY(service_id) REFERENCES calendar(service_id)
        )
    """)

    # 3. Table des horaires de passage (L'heure exacte d'arrivée/départ à chaque arrêt pour chaque voyage)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS stop_times (
            trip_id TEXT,
            stop_id TEXT,
            arrival_time TEXT,
            departure_time TEXT,
            stop_sequence INTEGER,
            FOREIGN KEY(trip_id) REFERENCES trips(trip_id),
            FOREIGN KEY(stop_id) REFERENCES stops_registry(stop_id)
        )
    """)

    conn.commit()
    conn.close()
    print("[SUCCÈS] Les tables d'horaires et de fréquences GTFS ont été intégrées avec succès !")

if __name__ == "__main__":
    create_schedule_tables()