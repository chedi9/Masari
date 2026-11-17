
import json
from pathlib import Path

ROOT = Path(r"C:\Users\awich\OneDrive\Bureau\transport\data")
OUTPUT = ROOT / "MASARI_COMPACT_DIAGNOSTIC.txt"

FILES = [
    "diagnostic_report.json",
    "extraction_report.json",
    "resources.json",
    "quality_issues.json",
    "datasets.json",
    "gtfs_inspection.json",
    "coverage_by_governorate.json",
]

def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as e:
        return f"READ ERROR: {e}"

def compact(obj, limit=12000):
    text = json.dumps(obj, ensure_ascii=False, indent=2, default=str)
    return text[:limit] + ("\n... TRUNCATED ..." if len(text) > limit else "")

with OUTPUT.open("w", encoding="utf-8") as out:
    for filename in FILES:
        path = ROOT / filename
        if not path.exists():
            continue

        data = load_json(path)
        out.write(f"\n{'='*70}\n{filename}\n{'='*70}\n")

        if filename == "resources.json" and isinstance(data, list):
            out.write(f"Total resources: {len(data)}\n")
            for r in data:
                text = json.dumps(r, ensure_ascii=False, default=str).lower()
                keywords = [
                    "transtu", "sncft", "rfr", "sntri", "soretras",
                    "soretrak", "srtb", "srtgn", "bus", "metro",
                    "train", "rail", "transport", "horaire", "gtfs",
                    "station", "arrêt", "ligne", "louage", "taxi"
                ]
                if any(k in text for k in keywords):
                    out.write(json.dumps(r, ensure_ascii=False, default=str) + "\n")
        else:
            out.write(compact(data))

print(f"Report created: {OUTPUT}")
