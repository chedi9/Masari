"""
MASARI 3.6 - Diagnostic des clés étrangères route_stops
"""
import sqlite3
import pymysql
from pathlib import Path

DB_SQLITE = Path(r"C:\Users\awich\OneDrive\Bureau\working folder\MASARI_Recovery_3_6\run_20261115_023158\tunisia_mobility.db")
MYSQL_CONFIG = {
    "host": "localhost", "user": "root", "password": "", "database": "masari_mobility", "charset": "utf8mb4", "cursorclass": pymysql.cursors.DictCursor
}

def check_keys():
    sqlite_conn = sqlite3.connect(DB_SQLITE)
    s_cur = sqlite_conn.cursor()
    
    mysql_conn = pymysql.connect(**MYSQL_CONFIG)
    m_cur = mysql_conn.cursor()

    # Prendre une relation au hasard dans SQLite
    s_cur.execute("SELECT route_id, stop_id FROM route_stops LIMIT 1;")
    sample = s_cur.fetchone()
    
    if sample:
        r_id, s_id = sample[0], sample[1]
        print(f"[TEST] Relation test - route_id: {r_id} | stop_id: {s_id}")

        # Vérifier si la route existe dans MySQL
        m_cur.execute("SELECT COUNT(*) as cnt FROM routes_registry WHERE route_id = %s;", (r_id,))
        route_exists = m_cur.fetchone()['cnt']
        print(f" -> La route existe dans MySQL ? {'OUI' if route_exists else 'NON'}")

        # Vérifier si l'arrêt existe dans MySQL
        m_cur.execute("SELECT COUNT(*) as cnt FROM stops_registry WHERE stop_id = %s;", (s_id,))
        stop_exists = m_cur.fetchone()['cnt']
        print(f" -> L'arrêt existe dans MySQL ? {'OUI' if stop_exists else 'NON'}")

    sqlite_conn.close()
    mysql_conn.close()

if __name__ == "__main__":
    check_keys()