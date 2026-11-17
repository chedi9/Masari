"""
MASARI 3.6 - Inspect Stops Registry for OSM IDs
"""
import sqlite3
from pathlib import Path

DB_SQLITE = Path(r"C:\Users\awich\OneDrive\Bureau\working folder\MASARI_Recovery_3_6\run_20261115_023158\tunisia_mobility.db")

def inspect_stops():
    if not DB_SQLITE.exists():
        print(f"[ERROR] SQLite database not found at: {DB_SQLITE}")
        return

    conn = sqlite3.connect(DB_SQLITE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("--- Checking stop_id formats in stops_registry ---")
    cursor.execute("SELECT stop_id, source_id, name_fr FROM stops_registry LIMIT 10;")
    for row in cursor.fetchall():
        print(f"stop_id: {row['stop_id']} | source_id: {row['source_id']} | name: {row['name_fr']}")

    print("\n--- Checking if any stop_id in route_stops matches stop_id in stops_registry ---")
    cursor.execute("""
        SELECT COUNT(*) FROM route_stops rs
        JOIN stops_registry s ON rs.stop_id = s.stop_id;
    """)
    match_count = cursor.fetchone()[0]
    print(f"Direct matching rows between route_stops and stops_registry: {match_count}")

    conn.close()

if __name__ == "__main__":
    inspect_stops()