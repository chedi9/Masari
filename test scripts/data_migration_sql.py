"""
MASARI 3.6 - Migration SQLite vers MySQL 8.0
Transfère les arrêts et les routes depuis SQLite vers MySQL.
"""
import sqlite3
import pymysql
from pathlib import Path

# Chemin vers votre base SQLite existante
DB_SQLITE = Path(r"C:\Users\awich\OneDrive\Bureau\working folder\MASARI_Recovery_3_6\run_20261115_023158\tunisia_mobility.db")

# Paramètres de connexion MySQL 8.0 (Modifiez le mot de passe si nécessaire)
MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Awichi@33",  # Mettez votre mot de passe root MySQL ici si vous en avez un
    "database": "masari_mobility",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor
}

def migrate():
    if not DB_SQLITE.exists():
        print(f"[ERREUR] Fichier SQLite introuvable : {DB_SQLITE}")
        return

    print("[INFO] Connexion à SQLite et MySQL...")
    sqlite_conn = sqlite3.connect(DB_SQLITE)
    sqlite_conn.row_factory = sqlite3.Row
    s_cur = sqlite_conn.cursor()

    mysql_conn = pymysql.connect(**MYSQL_CONFIG)
    m_cur = mysql_conn.cursor()

    try:
        # 1. Migration des Arrêts (stops_registry)
        print("[INFO] Migration des arrêts en cours...")
        s_cur.execute("SELECT stop_id, name_fr, lat, lon, governorate, verification_status FROM stops_registry")
        stops = s_cur.fetchall()
        
        stops_inserted = 0
        for row in stops:
            m_cur.execute("""
                INSERT IGNORE INTO stops_registry (stop_id, name_fr, lat, lon, governorate, verification_status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (row["stop_id"], row["name_fr"], row["lat"], row["lon"], row["governorate"], row["verification_status"]))
            stops_inserted += m_cur.rowcount

        # 2. Migration des Lignes (routes_registry)
        print("[INFO] Migration des lignes de transport en cours...")
        s_cur.execute("SELECT route_id, route_name, route_type, operator, geometry_json, verification_status FROM routes_registry")
        routes = s_cur.fetchall()

        routes_inserted = 0
        for row in routes:
            m_cur.execute("""
                INSERT IGNORE INTO routes_registry (route_id, route_name, route_type, operator, geometry_json, verification_status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (row["route_id"], row["route_name"], row["route_type"], row["operator"], row["geometry_json"], row["verification_status"]))
            routes_inserted += m_cur.rowcount

        mysql_conn.commit()
        print(f"\n[SUCCÈS] Migration terminée avec succès !")
        print(f" - Arrêts insérés : {stops_inserted}")
        print(f" - Lignes insérées : {routes_inserted}")

    except Exception as e:
        mysql_conn.rollback()
        print(f"[ERREUR] Une erreur est survenue lors de la migration : {e}")
    finally:
        s_cur.close()
        sqlite_conn.close()
        m_cur.close()
        mysql_conn.close()

if __name__ == "__main__":
    migrate()