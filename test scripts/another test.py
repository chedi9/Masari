
import json
from pathlib import Path

ROOT = Path(r"C:\Users\awich\OneDrive\Bureau\transport\data")
OUTPUT = ROOT / "MASARI_FINAL_DIAGNOSTIC.txt"

TRANSPORT_TERMS = [
    "transtu", "sncft", "rfr", "sntri", "soretras",
    "soretrak", "srtb", "srtgn", "srtj", "srtm",
    "sonotrak", "bus", "metro", "train", "railway",
    "transport", "horaire", "gtfs", "station",
    "arrêt", "ligne", "louage", "taxi", "ferroviaire"
]

GEO_TERMS = [
    "geojson", "shapefile", "gouvernorat", "délégation",
    "delegation", "municipalité", "commune", "frontière",
    "limite administrative", "localité", "localite",
    "carte", "découpage administratif"
]

def read_json(name):
    path = ROOT / name
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as e:
        return {"error": str(e)}

def matches(record, terms):
    text = json.dumps(record, ensure_ascii=False, default=str).lower()
    return any(term in text for term in terms)

def write_json(out, title, data):
    out.write(f"\n{'='*65}\n{title}\n{'='*65}\n")
    out.write(json.dumps(data, ensure_ascii=False, indent=2, default=str))
    out.write("\n")

with OUTPUT.open("w", encoding="utf-8") as out:

    for name in [
        "diagnostic_report.json",
        "extraction_report.json",
        "coverage_by_governorate.json",
        "quality_issues.json",
        "gtfs_inspection.json"
    ]:
        data = read_json(name)
        if data is not None:
            write_json(out, name, data)

    resources = read_json("resources.json")
    if isinstance(resources, list):
        transport = [r for r in resources if matches(r, TRANSPORT_TERMS)]
        geography = [r for r in resources if matches(r, GEO_TERMS)]

        write_json(out, "RESOURCE SUMMARY", {
            "total": len(resources),
            "transport_matches": len(transport),
            "geography_matches": len(geography)
        })

        write_json(out, "TRANSPORT RESOURCES (maximum 150)", transport[:150])
        write_json(out, "GEOGRAPHY RESOURCES (maximum 100)", geography[:100])

    datasets = read_json("datasets.json")
    if isinstance(datasets, list):
        relevant = [
            d for d in datasets
            if matches(d, TRANSPORT_TERMS + GEO_TERMS)
        ]
        write_json(out, "RELEVANT DATASETS (maximum 100)", relevant[:100])

print("Created:", OUTPUT)
print("Size:", round(OUTPUT.stat().st_size / 1024), "KB")
