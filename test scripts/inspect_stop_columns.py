"""
MASARI 3.6 - Inspect Stops Registry Columns and Data Structure
"""
import sqlite3
from pathlib import Path

DB_SQLITE = Path(r"C:\Users\awich\OneDrive\Bureau\working folder\MASARI_Recovery_3_6\run_20261115_023158\tunisia_mobility.db")

def inspect_columns():
    if not DB_SQLITE.exists():
        print(f"[ERROR] SQLite database not found at: {DB_SQLITE}")
        return

    conn = sqlite3.connect(DB_SQLITE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("--- 1. Table schema for stops_registry ---")
    cursor.execute("PRAGMA table_info(stops_registry);")
    for col in cursor.fetchall():
        print(f"Column: {col['name']} | Type: {col['type']}")

    print("\n--- 2. Sample full row from stops_registry ---")
    cursor.execute("SELECT * FROM stops_registry LIMIT 1;")
    row = cursor.fetchone()
    if row:
        for key in row.keys():
            print(f"  {key}: {row[key]}")

    conn.close()

if __name__ == "__main__":
    inspect_columns()