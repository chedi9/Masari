"""
MASARI 3.6 - CKAN Transport Scraper
Pulls extra transport datasets & route files directly from catalog.data.gov.tn
"""
import requests
import json

CKAN_API = "https://catalog.data.gov.tn/api/3/action/package_search"

def fetch_tunisia_transit_datasets():
    # Search terms focusing on Tunisian transport networks, bus lines, and stops
    queries = ["transport", "transtu", "bus", "itineraire", "stops", "lignes", "gare"]
    
    all_found_resources = []
    
    for q in queries:
        print(f"[RECHERCHE] Interrogation du portail open data pour : '{q}'...")
        url = f"{CKAN_API}?q={q}&rows=20"
        try:
            resp = requests.get(url, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("success"):
                    results = data["result"]["results"]
                    for dataset in results:
                        title = dataset.get("title", "")
                        for res in dataset.get("resources", []):
                            format_type = res.get("format", "").upper()
                            download_url = res.get("url", "")
                            if format_type in ["CSV", "GEOJSON", "ZIP", "JSON"] and download_url:
                                all_found_resources.append({
                                    "dataset_title": title,
                                    "resource_name": res.get("name", "Unnamed"),
                                    "format": format_type,
                                    "url": download_url
                                })
        except Exception as e:
            print(f"[ERREUR] Échec de la recherche pour {q} : {e}")

    print(f"\n[SUCCÈS] {len(all_found_resources)} ressources de transport supplémentaires identifiées !")
    
    # Sauvegarde de la liste pour téléchargement par votre moteur MASARI
    with open("extra_transport_resources.json", "w", encoding="utf-8") as f:
        json.dump(all_found_resources, f, indent=2, ensure_ascii=False)
    print("Liste sauvegardée dans 'extra_transport_resources.json'.")

if __name__ == "__main__":
    fetch_tunisia_transit_datasets()
