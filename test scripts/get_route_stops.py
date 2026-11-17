"""
MASARI 3.6 - Requête des arrêts par ligne de transport
Interroge MySQL pour lister les arrêts associés à une route spécifique.
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

def get_stops_for_route(route_search_term):
    print(f"[INFO] Recherche des arrêts pour la ligne contenant : '{route_search_term}'...")
    connection = pymysql.connect(**MYSQL_CONFIG)

    try:
        with connection.cursor() as cursor:
            # 1. Trouver la ligne correspondante dans routes_registry
            cursor.execute("""
                SELECT route_id, route_name, route_type, operator 
                FROM routes_registry 
                WHERE route_name LIKE %s LIMIT 1;
            """, (f"%{route_search_term}%",))
            
            route = cursor.fetchone()
            if not route:
                print(f"[AVERTISSEMENT] Aucune ligne trouvée pour le terme '{route_search_term}'.")
                return

            print(f"\n[LIGNE TROUVÉE]")
            print(f" - ID : {route['route_id']}")
            print(f" - Nom : {route['route_name']}")
            print(f" - Type : {route['route_type']}")
            print(f" - Opérateur : {route['operator']}\n")

            # 2. Récupérer les arrêts associés via la table de liaison route_stops
            query = """
                SELECT rs.sequence_order, s.stop_id, s.name_fr, s.governorate, s.lat, s.lon
                FROM route_stops rs
                JOIN stops_registry s ON rs.stop_id = s.stop_id
                WHERE rs.route_id = %s
                ORDER BY rs.sequence_order ASC;
            """
            cursor.execute(query, (route['route_id'],))
            stops = cursor.fetchall()

            if not stops:
                print("[INFO] Aucun arrêt n'est encore lié à cette route dans la table 'route_stops'. (Pensez à peupler les relations si ce n'est pas fait).")
            else:
                print(f"[ARRÊTS] Liste ordonnée des arrêts ({len(stops)} arrêts) :")
                for stop in stops:
                    print(f" [{stop['sequence_order']}] {stop['name_fr']} ({stop['governorate'] or 'N/A'}) - Lat: {stop['lat']}, Lon: {stop['lon']}")

    except Exception as e:
        print(f"[ERREUR] Échec de la requête : {e}")
    finally:
        connection.close()
        print("\n[INFO] Connexion MySQL fermée.")

if __name__ == "__main__":
    # Test avec l'une de vos lignes (ex: "خط 1" ou "المرسى")
    get_stops_for_route("خط 1")