"""
MASARI 3.6 - Deep OpenStreetMap Transport & Stations Extractor
Extrait toutes les gares ferroviaires, arrêts de bus additionnels et correspondances de transport.
"""
import sqlite3
import requests
import json
from pathlib import Path

DB_PATH = Path(r"C:\Users\awich\OneDrive\Bureau\working folder\MASARI_Recovery_3_6\run_20261115_023158\tunisia_mobility.db")
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
TUNISIA_BBOX = "30.2,7.5,37.5,11.6"

# Requête élargie pour cibler les gares, arrêts de bus isolés et plateformes multimodales
OVERPASS_QUERY = f"""
[out:json][timeout:150];
(
  node["public_transport"~"platform|stop_position"]({TUNISIA_BBOX});
  node["railway"="station"]({TUNISIA_BBOX});
  node["amenity"="bus_station"]({TUNISIA_BBOX});
  way["route"="bus"]({TUNISIA_BBOX});
);
out body;
"""

def fetch_additional_infrastructure():
    if not DB_PATH.exists():
        print(f"[ERREUR] Base de données introuvable : {DB_PATH}")
        return

    headers = {
        "User-Agent": "MasariMobilityStudio/3.6 (Tunisian Transit Research Project; contact@masari.tn)"
    }

    print("[INFO] Interrogation approfondie d'OpenStreetMap pour les gares et arrêts supplémentaires...")
    try:
        response = requests.post(OVERPASS_URL, data={"data": OVERPASS_QUERY}, headers=headers, timeout=180)
        if response.status_code != 200:
            print(f"[ERREUR] Échec de la requête Overpass (Code {response.status_code})")
            return
        
        data = response.json()
        elements = data.get("elements", [])
        print(f"[SUCCÈS] {len(elements)} éléments de transport supplémentaires trouvés !")
    except Exception as e:
        print(f"[ERREUR] Connexion impossible : {e}")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    added_stops = 0
    for el in elements:
        if el["type"] == "node":
            node_id = f"osm_extra_stop_{el['id']}"
            lat = el.get("lat")
            lon = el.get("lon")
            tags = el.get("tags", {})
            name = tags.get("name") or tags.get("name:fr") or tags.get("ref") or f"Station {el['id']}"
            
            if lat and lon:
                try:
                    cur.execute(
                        """INSERT OR IGNORE INTO stops_registry 
                           (stop_id, name_fr, lat, lon, governorate, verification_status)
                           VALUES (?, ?, ?, ?, 'Tunisie (OSM)', 'OSM_VERIFIED')""",
                        (node_id, name, lat, lon)
                    )
                    if cur.rowcount > 0:
                        added_stops += 1
                except Exception:
                    pass

    conn.commit()
    conn.close()
    print(f"\n[SUCCÈS] {added_stops} nouveaux arrêts/gares intégrés dans SQLite !")

if __name__ == "__main__":
    fetch_additional_infrastructure()