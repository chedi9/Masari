"""
MASARI 3.6 - Check Routes with Stops
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

def check_routes():
    conn = pymysql.connect(**MYSQL_CONFIG)
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT r.route_id, r.route_name, COUNT(rs.stop_id) AS stop_count
            FROM routes_registry r
            LEFT JOIN route_stops rs ON r.route_id = rs.route_id
            GROUP BY r.route_id, r.route_name
            HAVING stop_count > 0;
        """)
        results = cursor.fetchall()
        print(f"Found {len(results)} routes with active stop connections:\n")
        for r in results:
            print(f" - [{r['route_id']}] {r['route_name']} ({r['stop_count']} stops)")
    conn.close()

if __name__ == "__main__":
    check_routes()