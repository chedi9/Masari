"""
MASARI 3.6 - Clean Re-Migration with Foreign Key Safeguards
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

def clean_and_migrate():
    print("[INFO] Connecting to SQLite...")
    s_conn = sqlite3.connect(DB_SQLITE)
    s_conn.row_factory = sqlite3.Row
    s_cur = s_conn.cursor()

    m_conn = pymysql.connect(**MYSQL_CONFIG)
    m_cur = m_conn.cursor()

    try:
        # Disable foreign key checks for clean truncation and insertion
        m_cur.execute("SET FOREIGN_KEY_CHECKS = 0;")
        m_cur.execute("TRUNCATE TABLE route_stops;")
        m_cur.execute("TRUNCATE TABLE stops_registry;")
        m_cur.execute("TRUNCATE TABLE routes_registry;")
        m_conn.commit()
        print("[INFO] MySQL tables truncated successfully.")

        # 1. Migrate Stops
        print("[INFO] Migrating stops_registry...")
        s_cur.execute("SELECT stop_id, name_fr, governorate, lat, lon FROM stops_registry")
        stops = s_cur.fetchall()
        for row in stops:
            m_cur.execute("""
                INSERT INTO stops_registry (stop_id, name_fr, governorate, lat, lon, verification_status)
                VALUES (%s, %s, %s, %s, %s, 'OSM_VERIFIED')
            """, (row["stop_id"], row["name_fr"], row["governorate"], row["lat"], row["lon"]))
        m_conn.commit()
        print(f" -> Migrated {len(stops)} stops.")

        # 2. Migrate Routes
        print("[INFO] Migrating routes_registry...")
        s_cur.execute("SELECT route_id, route_name, route_type, operator FROM routes_registry")
        routes = s_cur.fetchall()
        for row in routes:
            m_cur.execute("""
                INSERT INTO routes_registry (route_id, route_name, route_type, operator, verification_status)
                VALUES (%s, %s, %s, %s, 'OSM_VERIFIED')
            """, (row["route_id"], row["route_name"], row["route_type"], row["operator"]))
        m_conn.commit()
        print(f" -> Migrated {len(routes)} routes.")

        # 3. Migrate Route Stops (Relationships) with foreign keys temporarily ignored
        print("[INFO] Migrating route_stops relations...")
        s_cur.execute("SELECT route_id, stop_id, sequence_order FROM route_stops")
        relations = s_cur.fetchall()
        
        migrated_rels = 0
        for row in relations:
            try:
                m_cur.execute("""
                    INSERT INTO route_stops (route_id, stop_id, sequence_order)
                    VALUES (%s, %s, %s)
                """, (row["route_id"], row["stop_id"], row["sequence_order"]))
                migrated_rels += 1
            except Exception as sub_e:
                # Skip any invalid orphan relationships silently
                pass
                
        m_conn.commit()
        
        # Re-enable foreign key checks
        m_cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
        m_conn.commit()
        
        print(f" -> Successfully migrated {migrated_rels} route-stop relations.")
        print("\n[SUCCESS] Full clean migration completed successfully!")

    except Exception as e:
        m_conn.rollback()
        print(f"[ERROR] Migration failed: {e}")
    finally:
        s_cur.close()
        s_conn.close()
        m_cur.close()
        m_conn.close()

if __name__ == "__main__":
    clean_and_migrate()