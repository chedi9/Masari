"""
MASARI 3.6 - Inspect SQLite Stop IDs and Mappings
"""
import sqlite3
from pathlib import Path

DB_SQLITE = Path(r"C:\Users\awich\OneDrive\Bureau\working folder\MASARI_Recovery_3_6\run_20261115_023158\tunisia_mobility.db")

def inspect_ids():
    if not DB_SQLITE.exists():
        print(f"[ERROR] SQLite database not found at: {DB_SQLITE}")
        return

    conn = sqlite3.connect(DB_SQLITE)
    cursor = conn.cursor()

    print("--- 1. Sample rows from route_stops ---")
    try:
        cursor.execute("SELECT route_id, stop_id, sequence_order FROM route_stops LIMIT 5;")
        for row in cursor.fetchall():
            print(row)
    except Exception as e:
        print(f"Error querying route_stops: {e}")

    print("\n--- 2. Sample rows from stops_registry ---")
    try:
        cursor.execute("SELECT stop_id, name_fr FROM stops_registry LIMIT 5;")
        for row in cursor.fetchall():
            print(row)
    except Exception as e:
        print(f"Error querying stops_registry: {e}")

    conn.close()

if __name__ == "__main__":
    inspect_ids()