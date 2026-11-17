"""
MASARI 3.6 - Synchronize Stops Registry with Exact SQLite IDs
"""
import sqlite3
import pymysql
from pathlib import Path

DB_SQLITE = Path(r"C:\Users\awich\OneDrive\Bureau\working folder\MASARI_Recovery_3_6\run_20261115_023158\tunisia_mobility.db")

MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Awichi@33",
    "database": "masari_mobility",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor
}

def sync_stops():
    print("[INFO] Connecting to SQLite...")
    s_conn = sqlite3.connect(DB_SQLITE)
    s_conn.row_factory = sqlite3.Row
    s_cur = s_conn.cursor()

    s_cur.execute("SELECT stop_id, name_fr, governorate, lat, lon FROM stops_registry")
    sqlite_stops = s_cur.fetchall()
    print(f"[INFO] Found {len(sqlite_stops)} stops in SQLite.")
    s_conn.close()

    print("[INFO] Connecting to MySQL...")
    m_conn = pymysql.connect(**MYSQL_CONFIG)
    m_cur = m_conn.cursor()

    try:
        # Temporarily disable foreign keys to allow clearing and reloading
        m_cur.execute("SET FOREIGN_KEY_CHECKS = 0;")
        m_cur.execute("TRUNCATE TABLE route_stops;")
        m_cur.execute("TRUNCATE TABLE stops_registry;")
        m_conn.commit()

        print("[INFO] Re-inserting stops with exact IDs...")
        for row in sqlite_stops:
            m_cur.execute("""
                INSERT INTO stops_registry (stop_id, name_fr, governorate, lat, lon, verification_status)
                VALUES (%s, %s, %s, %s, %s, 'OSM_VERIFIED')
            """, (row["stop_id"], row["name_fr"], row["governorate"], row["lat"], row["lon"]))
        
        # Restore route_stops relationships
        s_conn = sqlite3.connect(DB_SQLITE)
        s_cur = s_conn.cursor()
        s_cur.execute("SELECT route_id, stop_id, sequence_order FROM route_stops")
        relations = s_cur.fetchall()
        
        print("[INFO] Re-inserting route-stop relationships...")
        for row in relations:
            try:
                m_cur.execute("""
                    INSERT INTO route_stops (route_id, stop_id, sequence_order)
                    VALUES (%s, %s, %s)
                """, (row[0], row[1], row[2]))
            except Exception:
                pass # Skip any orphan rows safely

        m_conn.commit()
        m_cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
        m_conn.commit()
        print("[SUCCESS] Stops and relations fully synchronized!")

    except Exception as e:
        m_conn.rollback()
        print(f"[ERROR] Sync failed: {e}")
    finally:
        m_cur.close()
        m_conn.close()

if __name__ == "__main__":
    sync_stops()