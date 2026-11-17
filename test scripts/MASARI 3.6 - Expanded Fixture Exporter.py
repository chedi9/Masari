"""
MASARI 3.6 - Expanded Fixture Exporter
Refreshes stops_fixture.json and routes_fixture.json with the latest SQLite data.
"""
import sqlite3
import json
from pathlib import Path

DB_PATH = Path(r"C:\Users\awich\OneDrive\Bureau\working folder\MASARI_Recovery_3_6\run_20261115_023158\tunisia_mobility.db")
OUTPUT_DIR = DB_PATH.parent

def export_expanded():
    if not DB_PATH.exists():
        print(f"[ERREUR] Base de données introuvable : {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # 1. Exportation de tous les arrêts (mis à jour)
    cur.execute("SELECT stop_id, name_fr, lat, lon, governorate, verification_status FROM stops_registry")
    stops = [dict(row) for row in cur.fetchall()]
    
    stops_file = OUTPUT_DIR / "stops_fixture.json"
    with open(stops_file, "w", encoding="utf-8") as f:
        json.dump(stops, f, ensure_ascii=False, indent=2)
    print(f"[SUCCÈS] {len(stops)} arrêts totaux exportés vers '{stops_file.name}'")

    # 2. Exportation des lignes
    cur.execute("SELECT route_id, route_name, route_type, operator, geometry_json, verification_status FROM routes_registry")
    routes = []
    for row in cur.fetchall():
        r = dict(row)
        if r["geometry_json"]:
            r["geometry"] = json.loads(r["geometry_json"])
        del r["geometry_json"]
        routes.append(r)

    routes_file = OUTPUT_DIR / "routes_fixture.json"
    with open(routes_file, "w", encoding="utf-8") as f:
        json.dump(routes, f, ensure_ascii=False, indent=2)
    print(f"[SUCCÈS] {len(routes)} lignes de transport exportées vers '{routes_file.name}'")

    conn.close()
    print("\n[TERMINÉ] Votre plateforme MASARI dispose désormais d'un dataset national complet et 100% gratuit !")

if __name__ == "__main__":
    export_expanded()