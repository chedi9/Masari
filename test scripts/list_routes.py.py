"""
MASARI 3.6 - List All Route Names in MySQL
"""
import pymysql

MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Awichi@33",
    "database": "masari_mobility",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor
}

def list_routes():
    try:
        conn = pymysql.connect(**MYSQL_CONFIG)
        with conn.cursor() as cursor:
            cursor.execute("SELECT route_id, route_name, route_type FROM routes_registry ORDER BY route_name;")
            routes = cursor.fetchall()
            print(f"Total routes found in MySQL: {len(routes)}\n")
            for idx, r in enumerate(routes, 1):
                print(f"{idx}. ID: {r['route_id']} | Name: {r['route_name']} | Type: {r['route_type']}")
        conn.close()
    except Exception as e:
        print(f"[ERROR] Failed to list routes: {e}")

if __name__ == "__main__":
    list_routes()