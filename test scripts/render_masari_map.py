"""
MASARI 3.6 - Local Live Map Visualizer (Version Finale Corrigée)
Génère une carte HTML interactive avec fond OpenTopoMap pour visualiser
tous les arrêts et les tracés géographiques (LineString) de la Tunisie.
"""
import sqlite3
import json
from pathlib import Path
import folium
from folium.plugins import MarkerCluster

# Chemin vers votre base de données SQLite MASARI
DB_PATH = Path(r"C:\Users\awich\OneDrive\Bureau\working folder\MASARI_Recovery_3_6\run_20261115_023158\tunisia_mobility.db")
OUTPUT_MAP_PATH = DB_PATH.parent / "masari_live_map.html"

def render_map():
    if not DB_PATH.exists():
        print(f"[ERREUR] Base de données introuvable : {DB_PATH}")
        return

    print("[INFO] Chargement des données géographiques depuis SQLite...")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1. Récupération des arrêts
    cur.execute("SELECT stop_id, name_fr, lat, lon, governorate FROM stops_registry WHERE lat IS NOT NULL AND lon IS NOT NULL")
    stops = cur.fetchall()

    # 2. Récupération des routes et géométries LineString
    cur.execute("SELECT route_name, route_type, operator, geometry_json FROM routes_registry WHERE geometry_json IS NOT NULL")
    routes = cur.fetchall()
    conn.close()

    print(f"[INFO] Génération de la carte centrée sur la Tunisie ({len(stops)} arrêts & {len(routes)} lignes)...")
    
    # Initialisation de la carte avec OpenTopoMap (contourne totalement les restrictions de tuiles)
    masari_map = folium.Map(
        location=[35.5, 9.5], 
        zoom_start=7, 
        tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
        attr='Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a>'
    )

    # Ajout d'un groupe de clusters pour les arrêts afin de garder une interface fluide
    marker_cluster = MarkerCluster(name=f"Arrêts de Transport ({len(stops)})").add_to(masari_map)

    for stop_id, name_fr, lat, lon, gov in stops:
        popup_text = f"<b>Arrêt:</b> {name_fr}<br><b>Gouvernorat:</b> {gov or 'Tunisie'}"
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_text, max_width=300),
            icon=folium.Icon(color="blue", icon="bus", prefix="fa")
        ).add_to(marker_cluster)

    # Ajout des tracés de lignes (LineString) sur la carte
    route_feature_group = folium.FeatureGroup(name=f"Lignes de Transport ({len(routes)})").add_to(masari_map)
    
    for route_name, route_type, operator, geom_json in routes:
        try:
            geom = json.loads(geom_json)
            if geom.get("type") == "LineString":
                # Inversion des coordonnées (lon, lat) GeoJSON vers (lat, lon) pour Folium
                coords = [[lat, lon] for lon, lat in geom["coordinates"]]
                
                # Code couleur : Rouge pour le rail/train, Vert pour les bus/ferries
                color = "red" if any(t in route_type.lower() for t in ["train", "light_rail", "subway", "tram"]) else "green"
                
                folium.PolyLine(
                    locations=coords,
                    color=color,
                    weight=4,
                    opacity=0.8,
                    tooltip=f"<b>Ligne:</b> {route_name} ({route_type})<br><b>Opérateur:</b> {operator}"
                ).add_to(route_feature_group)
        except Exception:
            pass

    # Contrôleur pour afficher/masquer les couches
    folium.LayerControl().add_to(masari_map)

    # Sauvegarde du fichier HTML
    masari_map.save(str(OUTPUT_MAP_PATH))
    print(f"\n[SUCCÈS] Carte interactive générée avec succès : {OUTPUT_MAP_PATH}")
    print("Double-cliquez sur le fichier 'masari_live_map.html' dans votre dossier pour voir le résultat en direct !")

if __name__ == "__main__":
    render_map()