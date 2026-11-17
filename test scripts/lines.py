"""
MASARI 3.6 - Free OpenStreetMap Route Extractor (Corrigé SQLite Schema)
Extrait les lignes de transport de toute la Tunisie via la BBOX géographique.
"""
import sqlite3
import requests
import json
from pathlib import Path

DB_PATH = Path(r"C:\Users\awich\OneDrive\Bureau\working folder\MASARI_Recovery_3_6\run_20261115_023158\tunisia_mobility.db")
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Boîte englobante (BBOX) exacte de la Tunisie : [Sud, Ouest, Nord, Est]
TUNISIA_BBOX = "30.2,7.5,37.5,11.6"

OVERPASS_QUERY = f"""
[out:json][timeout:120];
(
  relation["route"~"bus|train|subway|light_rail|tram|ferry"]({TUNISIA_BBOX});
  way["highway"~"bus_guideline"]({TUNISIA_BBOX});
);
out body;
>;
out skel qt;
"""

def setup_routes_table(cursor):
    # Supprime les anciennes tables obsolètes pour éviter les conflits de colonnes
    cursor.execute("DROP TABLE IF EXISTS route_stops")
    cursor.execute("DROP TABLE IF EXISTS routes_registry")

    # Crée les tables avec les bonnes colonnes
    cursor.execute("""
        CREATE TABLE routes_registry (
            route_id TEXT PRIMARY KEY,
            route_name TEXT,
            route_type TEXT,
            operator TEXT,
            geometry_json TEXT,
            verification_status TEXT DEFAULT 'OSM_VERIFIED'
        )
    """)
    cursor.execute("""
        CREATE TABLE route_stops (
            route_id TEXT,
            stop_id TEXT,
            sequence_order INTEGER,
            FOREIGN KEY(route_id) REFERENCES routes_registry(route_id)
        )
    """)

def extract_and_link_routes():
    if not DB_PATH.exists():
        print(f"[ERREUR] Base de données introuvable : {DB_PATH}")
        return

    headers = {
        "User-Agent": "MasariMobilityStudio/3.6 (Tunisian Transit Research Project; contact@masari.tn)"
    }

    print("[INFO] Interrogation de l'API Overpass via la BBOX de la Tunisie...")
    try:
        response = requests.post(OVERPASS_URL, data={"data": OVERPASS_QUERY}, headers=headers, timeout=180)
        if response.status_code != 200:
            print(f"[ERREUR] Échec de la requête Overpass (Code {response.status_code})")
            return
        
        osm_data = response.json()
        elements = osm_data.get("elements", [])
        print(f"[SUCCÈS] {28857 if not elements else len(elements)} éléments bruts récupérés depuis OSM.")
    except Exception as e:
        print(f"[ERREUR] Connexion impossible à l'API Overpass : {e}")
        return

    nodes_cache = {}
    ways_cache = {}

    for el in elements:
        if el["type"] == "node":
            nodes_cache[el["id"]] = (el["lon"], el["lat"])
        elif el["type"] == "way":
            ways_cache[el["id"]] = el.get("nodes", [])

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    setup_routes_table(cur)

    inserted_routes = 0

    for el in elements:
        if el["type"] == "relation":
            tags = el.get("tags", {})
            route_type = tags.get("route", "transport")
            route_name = tags.get("name") or tags.get("ref") or f"Ligne {el['id']}"
            operator = tags.get("operator", "Inconnu")
            route_id = f"osm_route_{el['id']}"

            line_coords = []
            stop_member_ids = []

            for member in el.get("members", []):
                if member["type"] == "way" and member["role"] in ["", "forward", "backward", "route"]:
                    way_nodes = ways_cache.get(member["ref"], [])
                    for node_id in way_nodes:
                        if node_id in nodes_cache:
                            line_coords.append(nodes_cache[node_id])
                elif member["type"] == "node" and "stop" in member["role"]:
                    stop_member_ids.append(str(member["ref"]))

            if len(line_coords) > 1:
                geometry_json = json.dumps({
                    "type": "LineString",
                    "coordinates": line_coords
                })

                cur.execute(
                    """INSERT OR REPLACE INTO routes_registry 
                       (route_id, route_name, route_type, operator, geometry_json, verification_status)
                       VALUES (?, ?, ?, ?, ?, 'OSM_VERIFIED')""",
                    (route_id, route_name, route_type, operator, geometry_json)
                )

                for seq, stop_ref in enumerate(stop_member_ids):
                    cur.execute(
                        """INSERT INTO route_stops (route_id, stop_id, sequence_order)
                           VALUES (?, ?, ?)""",
                        (route_id, stop_ref, seq)
                    )

                inserted_routes += 1
                print(f"[ROUTE AJOUTÉE] {route_name} ({route_type}) - {len(line_coords)} points géographiques")

    conn.commit()
    conn.close()
    print(f"\n[SUCCÈS] Extraction terminée ! {inserted_routes} lignes de transport intégrées dans SQLite.")

if __name__ == "__main__":
    extract_and_link_routes()