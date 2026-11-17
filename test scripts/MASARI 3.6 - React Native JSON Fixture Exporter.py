"""
MASARI 3.6 - React Native JSON Fixture Exporter
Exports SQLite stops and route geometries into mobile-ready JSON files.
"""
import sqlite3
import json
from pathlib import Path

DB_PATH = Path(r"C:\Users\awich\OneDrive\Bureau\working folder\MASARI_Recovery_3_6\run_20261115_023158\tunisia_mobility.db")
OUTPUT_DIR = DB_PATH.parent

def export_fixtures():
    if not DB_PATH.exists():
        print(f"[ERREUR] Base de données introuvable : {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # 1. Exportation des arrêts (Stops Registry)
    cur.execute("SELECT stop_id, name_fr, lat, lon, governorate, verification_status FROM stops_registry")
    stops = [dict(row) for row in cur.fetchall()]
    
    stops_file = OUTPUT_DIR / "stops_fixture.json"
    with open(stops_file, "w", encoding="utf-8") as f:
        json.dump(stops, f, ensure_ascii=False, indent=2)
    print(f"[SUCCÈS] {len(stops)} arrêts exportés vers '{stops_file.name}'")

    # 2. Exportation des lignes et de leurs géométries LineString
    cur.execute("SELECT route_id, route_name, route_type, operator, geometry_json, verification_status FROM routes_registry")
    routes = []
    for row in cur.fetchall():
        r = dict(row)
        # Parse le JSON de géométrie stocké pour l'inclure proprement dans le GeoJSON final
        if r["geometry_json"]:
            r["geometry"] = json.loads(r["geometry_json"])
        del r["geometry_json"]
        routes.append(r)

    routes_file = OUTPUT_DIR / "routes_fixture.json"
    with open(routes_file, "w", encoding="utf-8") as f:
        json.dump(routes, f, ensure_ascii=False, indent=2)
    print(f"[SUCCÈS] {len(routes)} lignes de transport exportées vers '{routes_file.name}'")

    conn.close()
    print("\n[TERMINÉ] Toutes les fixtures JSON sont prêtes pour React Native !")

if __name__ == "__main__":
    export_fixtures()