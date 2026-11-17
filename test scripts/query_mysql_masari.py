"""
MASARI 3.6 - Script de consultation des données MySQL
Vérifie et affiche les arrêts et lignes migrés depuis la base masari_mobility.
"""
import pymysql

# Configuration de connexion à MySQL 8.0
MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Awichi@33",  # Mettez votre mot de passe root si nécessaire
    "database": "masari_mobility",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor
}

def query_masari_data():
    print("[INFO] Connexion à la base de données MySQL 8.0...")
    connection = pymysql.connect(**MYSQL_CONFIG)

    try:
        with connection.cursor() as cursor:
            # 1. Compter le nombre total d'arrêts et de lignes
            cursor.execute("SELECT COUNT(*) AS total_stops FROM stops_registry;")
            stops_count = cursor.fetchone()["total_stops"]

            cursor.execute("SELECT COUNT(*) AS total_routes FROM routes_registry;")
            routes_count = cursor.fetchone()["total_routes"]

            print(f"\n[STATISTIQUES] Base 'masari_mobility' :")
            print(f" - Total des arrêts : {stops_count}")
            print(f" - Total des lignes : {routes_count}")

            # 2. Afficher 5 exemples d'arrêts enregistrés
            print("\n[APERÇU] Exemples d'arrêts de transport :")
            cursor.execute("SELECT stop_id, name_fr, governorate, lat, lon FROM stops_registry LIMIT 5;")
            for row in cursor.fetchall():
                print(f" * Arrêt : {row['name_fr']} | Gouvernorat : {row['governorate'] or 'N/A'} (Lat: {row['lat']}, Lon: {row['lon']})")

            # 3. Afficher un aperçu des lignes de transport
            print("\n[APERÇU] Exemples de lignes de transport :")
            cursor.execute("SELECT route_id, route_name, route_type, operator FROM routes_registry LIMIT 5;")
            for row in cursor.fetchall():
                print(f" * Ligne : {row['route_name']} | Type : {row['route_type']} | Opérateur : {row['operator']}")

    except Exception as e:
        print(f"[ERREUR] Échec de la requête : {e}")
    finally:
        connection.close()
        print("\n[INFO] Connexion MySQL fermée.")

if __name__ == "__main__":
    query_masari_data()