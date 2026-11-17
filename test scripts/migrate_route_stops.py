"""
MASARI 3.6 - Migration des relations route_stops depuis SQLite vers MySQL
Associe chaque arrêt à sa ligne correspondante avec le bon mot de passe.
"""
import sqlite3
import pymysql
from pathlib import Path

# Chemin vers votre base SQLite existante
DB_SQLITE = Path(r"C:\Users\awich\OneDrive\Bureau\working folder\MASARI_Recovery_3_6\run_20261115_023158\tunisia_mobility.db")

# Configuration de connexion à MySQL 8.0 avec votre mot de passe
MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Awichi@33",
    "database": "masari_mobility",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor
}

def migrate_route_stops():
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
        # Récupération des relations depuis SQLite
        print("[INFO] Lecture des relations route_stops dans SQLite...")
        s_cur.execute("SELECT route_id, stop_id, sequence_order FROM route_stops")
        relations = s_cur.fetchall()
        
        print(f"[INFO] {len(relations)} relations trouvées. Insertion dans MySQL...")

        inserted_count = 0
        for row in relations:
            m_cur.execute("""
                INSERT IGNORE INTO route_stops (route_id, stop_id, sequence_order)
                VALUES (%s, %s, %s)
            """, (row["route_id"], row["stop_id"], row["sequence_order"]))
            inserted_count += m_cur.rowcount

        mysql_conn.commit()
        print(f"\n[SUCCÈS] Migration des relations terminée avec succès !")
        print(f" - Relations insérées : {inserted_count}")

    except Exception as e:
        mysql_conn.rollback()
        print(f"[ERREUR] Une erreur est survenue lors de la migration : {e}")
    finally:
        s_cur.close()
        sqlite_conn.close()
        m_cur.close()
        mysql_conn.close()
        print("[INFO] Connexions fermées.")

if __name__ == "__main__":
    migrate_route_stops()