#!/usr/bin/env python3
"""Tunisia Mobility open-map harvester (Python 3.10+, standard library only).

Downloads:
- Geofabrik's latest Tunisia OSM PBF (national roads, railways, paths, POIs, etc.)
- Map Tunisia GitHub reference files (cities and administrative boundaries)
- OSM transport stops/platforms/stations and route relations via Overpass,
  separately for Greater Tunis, Sousse, Monastir and Sfax.

Usage:
  python harvest_tunisia_maps.py
  python harvest_tunisia_maps.py --skip-pbf
  python harvest_tunisia_maps.py --overpass-only
  python harvest_tunisia_maps.py --cities tunis,sousse
  python harvest_tunisia_maps.py --include-gpkg

Outputs: raw/, geojson/, csv/, reports/ under the output directory.

OSM data is ODbL 1.0. Include attribution and review share-alike obligations
before redistributing a derived database. OSM routes are not timetables.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, os, sys, time, urllib.parse, urllib.request, zipfile
from datetime import datetime, timezone
from pathlib import Path

APP = "TUNISIA MOBILITY | OPEN MAP DATA HARVESTER"
UA = "TunisiaMobilityDataHarvester/1.0 (open-data research project)"

# (south, west, north, east), WGS84. Collection extents, not official boundaries.
AREAS = {
    "tunis": ("Greater Tunis", (36.55, 9.55, 37.10, 10.45)),
    "sousse": ("Sousse", (35.70, 10.45, 36.00, 10.80)),
    "monastir": ("Monastir", (35.60, 10.70, 35.90, 11.05)),
    "sfax": ("Sfax", (34.60, 10.50, 34.95, 10.95)),
}
PBF_URL = "https://download.geofabrik.de/africa/tunisia-latest.osm.pbf"
GPKG_URL = "https://download.geofabrik.de/africa/tunisia-latest-free.gpkg.zip"
MAP_BASE = "https://raw.githubusercontent.com/Alaa-Taieb/map-tunisia/main/dist/"
MAP_FILES = [
    "data/cities.json", "data/governorates.json", "data/delegations.json",
    "data/municipalities.json", "data/sectors.json",
    "geojson/tunisia-governorates-medium.geojson",
    "geojson/tunisia-delegations-medium.geojson",
    "geojson/tunisia-municipalities-medium.geojson",
    "geojson/tunisia-cities-medium.geojson",
]
OVERPASS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]

class Dashboard:
    def __init__(self):
        self.ansi = sys.stdout.isatty() and not os.getenv("NO_COLOR")
    def c(self, s, code):
        return f"\033[{code}m{s}\033[0m" if self.ansi else s
    def header(self):
        print("\n" + self.c("╔" + "═"*68 + "╗", "36;1"))
        print(self.c("║" + APP.center(68) + "║", "36;1"))
        print(self.c("║" + "OpenStreetMap • Overpass • Geofabrik • GitHub".center(68) + "║", "36"))
        print(self.c("╚" + "═"*68 + "╝", "36;1"))
    def section(self, title):
        print("\n" + self.c("━━ " + title + " " + "━"*max(2, 54-len(title)), "35;1"))
    def status(self, name, message, state="info"):
        icon, color = {
            "ok": ("✓", "32;1"), "fail": ("✗", "31;1"),
            "warn": ("!", "33;1"), "info": ("›", "36")
        }[state]
        print(f"  {self.c(icon, color)} {name:<26} {message}")
    def progress(self, name, got, total):
        if total:
            ratio = min(got / total, 1)
            width = 25
            bar = "█"*int(width*ratio) + "░"*(width-int(width*ratio))
            line = f"\r  {name:<19} [{bar}] {ratio*100:5.1f}%"
        else:
            line = f"\r  {name:<19} {got/1048576:7.1f} MB"
        print(line, end="", flush=True)
    def done(self):
        print()
UI = Dashboard()

def fetch(url, timeout=180, retries=2, label=None, data=None, headers=None):
    last = None
    for attempt in range(1, retries+1):
        try:
            h = {"User-Agent": UA, "Accept": "*/*"}
            if headers: h.update(headers)
            req = urllib.request.Request(url, data=data, headers=h)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                total_h = r.headers.get("Content-Length")
                total = int(total_h) if total_h and total_h.isdigit() else None
                chunks, got = [], 0
                while True:
                    chunk = r.read(256*1024)
                    if not chunk: break
                    chunks.append(chunk); got += len(chunk)
                    if label: UI.progress(label, got, total)
            if label: UI.done()
            result = b"".join(chunks)
            if not result: raise ValueError("Empty response")
            return result
        except Exception as e:
            last = e
            if label: UI.done()
            if attempt < retries:
                delay = min(2**attempt, 8)
                UI.status("Retry", f"{attempt}/{retries}: {e}; wait {delay}s", "warn")
                time.sleep(delay)
    raise RuntimeError(f"Failed after {retries} attempts: {last}")

def save_url(url, dest, timeout, retries):
    dest.parent.mkdir(parents=True, exist_ok=True)
    data = fetch(url, timeout, retries, dest.name)
    tmp = dest.with_suffix(dest.suffix + ".part")
    tmp.write_bytes(data); tmp.replace(dest)
    return {"url": url, "path": str(dest), "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(), "status": "downloaded"}

def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

def overpass_query(bbox):
    s,w,n,e = bbox
    b = f"{s},{w},{n},{e}"
    return f"""[out:json][timeout:180];
(
 node["highway"="bus_stop"]({b});
 node["public_transport"~"^(platform|stop_position|station)$"]({b});
 node["railway"~"^(station|halt|tram_stop|stop)$"]({b});
 node["station"~"^(subway|light_rail|train)$"]({b});
 way["public_transport"="platform"]({b});
 way["railway"~"^(platform|station|halt|tram_stop)$"]({b});
 relation["type"="route"]["route"~"^(bus|trolleybus|tram|subway|train|light_rail|monorail|ferry)$"]({b});
 relation["type"="route_master"]["route_master"~"^(bus|trolleybus|tram|subway|train|light_rail|monorail|ferry)$"]({b});
);
out body center geom;"""

def overpass(query, timeout, retries):
    payload = urllib.parse.urlencode({"data": query}).encode()
    last = None
    for endpoint in OVERPASS:
        for attempt in range(retries):
            try:
                body = fetch(endpoint, timeout, 1, data=payload, headers={
                    "Content-Type": "application/x-www-form-urlencoded"})
                obj = json.loads(body.decode("utf-8"))
                if "elements" not in obj: raise ValueError("No elements in Overpass response")
                return obj
            except Exception as e:
                last = e
                if attempt+1 < retries: time.sleep(3*(attempt+1))
        UI.status("Overpass endpoint", f"Unavailable: {endpoint}", "warn")
    raise RuntimeError(f"All Overpass endpoints failed: {last}")

def props(el, city):
    t = el.get("tags", {})
    typ, oid = el.get("type"), el.get("id")
    return {
        "osm_type": typ, "osm_id": oid,
        "osm_url": f"https://www.openstreetmap.org/{typ}/{oid}",
        "city_area": AREAS[city][0],
        "name": t.get("name"), "name_ar": t.get("name:ar"),
        "name_fr": t.get("name:fr"), "name_en": t.get("name:en"),
        "ref": t.get("ref"), "operator": t.get("operator"),
        "network": t.get("network"), "route": t.get("route"),
        "public_transport": t.get("public_transport"),
        "highway": t.get("highway"), "railway": t.get("railway"),
        "station": t.get("station"), "wheelchair": t.get("wheelchair"),
        "shelter": t.get("shelter"), "bench": t.get("bench"),
        "source": "OpenStreetMap",
    }

def make_geojson(elements, city, kind):
    features = []
    for el in elements:
        if kind == "stops":
            if el["type"] == "node" and "lon" in el:
                xy = [el["lon"], el["lat"]]
            elif el.get("center"):
                xy = [el["center"]["lon"], el["center"]["lat"]]
            else: continue
            features.append({"type":"Feature","geometry":{"type":"Point","coordinates":xy},
                             "properties":props(el, city)})
        elif el["type"] == "relation":
            base = props(el, city)
            base["relation_type"] = el.get("tags", {}).get("type")
            base["route_master"] = el.get("tags", {}).get("route_master")
            for member in el.get("members", []):
                geom = member.get("geometry")
                if member.get("type") != "way" or not geom or len(geom) < 2: continue
                p = dict(base); p["member_role"] = member.get("role")
                p["member_way_id"] = member.get("ref")
                features.append({"type":"Feature",
                    "geometry":{"type":"LineString","coordinates":[[x["lon"],x["lat"]] for x in geom]},
                    "properties":p})
    return {"type":"FeatureCollection","name":f"{city}_{kind}","features":features}

def harvest_city(city, root, timeout, retries, results):
    label, bbox = AREAS[city]
    UI.section(f"OPENSTREETMAP / OVERPASS — {label}")
    query = overpass_query(bbox)
    qpath = root/"raw"/"overpass"/f"{city}_query.overpassql"
    qpath.parent.mkdir(parents=True, exist_ok=True); qpath.write_text(query, encoding="utf-8")
    try:
        data = overpass(query, timeout, retries)
        raw = root/"raw"/"overpass"/f"{city}_response.json"
        write_json(raw, data)
        els = data["elements"]
        def is_stop(e):
            t=e.get("tags",{})
            return (t.get("highway")=="bus_stop" or
                t.get("public_transport") in {"platform","stop_position","station"} or
                t.get("railway") in {"station","halt","tram_stop","stop","platform"} or
                t.get("station") in {"subway","light_rail","train"})
        stop_els=[e for e in els if e["type"] in {"node","way"} and is_stop(e)]
        route_els=[e for e in els if e["type"]=="relation" and e.get("tags",{}).get("type")=="route"]
        master_els=[e for e in els if e["type"]=="relation" and e.get("tags",{}).get("type")=="route_master"]
        stops=make_geojson(stop_els,city,"stops")
        routes=make_geojson(route_els,city,"routes")
        sp=root/"geojson"/city/"transport_stops.geojson"
        rp=root/"geojson"/city/"route_segments.geojson"
        write_json(sp,stops); write_json(rp,routes)
        cp=root/"csv"/city/"transport_stops.csv"; cp.parent.mkdir(parents=True,exist_ok=True)
        fields=["osm_type","osm_id","name","name_ar","name_fr","name_en","ref","operator",
          "network","public_transport","highway","railway","station","wheelchair",
          "shelter","bench","longitude","latitude","city_area","osm_url"]
        with cp.open("w",newline="",encoding="utf-8-sig") as f:
            w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
            for feat in stops["features"]:
                p=feat["properties"]; lon,lat=feat["geometry"]["coordinates"]
                w.writerow({**{k:p.get(k) for k in fields},"longitude":lon,"latitude":lat})
        summaries=[]
        for el in route_els+master_els:
            t=el.get("tags",{})
            summaries.append({"osm_id":el["id"],"relation_type":t.get("type"),
              "route":t.get("route") or t.get("route_master"),"ref":t.get("ref"),
              "name":t.get("name"),"operator":t.get("operator"),"network":t.get("network"),
              "from":t.get("from"),"to":t.get("to"),
              "osm_url":f"https://www.openstreetmap.org/relation/{el['id']}"})
        write_json(root/"csv"/city/"route_relations.json",summaries)
        result={"city":label,"bbox":bbox,"raw_elements":len(els),
          "stop_features":len(stops["features"]),"route_relations":len(route_els),
          "route_master_relations":len(master_els),"route_geometry_segments":len(routes["features"]),
          "status":"downloaded"}
        UI.status("Raw OSM elements",str(len(els)),"ok")
        UI.status("Stops/platforms",str(result["stop_features"]),"ok")
        UI.status("Route relations",str(len(route_els)),"ok")
        UI.status("Route geometry segments",str(len(routes["features"])),"ok")
        results.append({"source":f"Overpass / {label}",**result})
        return result
    except Exception as e:
        UI.status("City extraction",str(e),"fail")
        result={"city":label,"status":"failed","error":str(e)}
        results.append({"source":f"Overpass / {label}",**result})
        return result

def main():
    p=argparse.ArgumentParser(description="Harvest open map and transport data for Tunisia.")
    p.add_argument("--output",default="tunisia_map_harvest")
    p.add_argument("--cities",default="tunis,sousse,monastir,sfax")
    p.add_argument("--skip-pbf",action="store_true",help="Skip national ~80 MB PBF.")
    p.add_argument("--include-gpkg",action="store_true",help="Also download/extract ~170 MB GeoPackage.")
    p.add_argument("--overpass-only",action="store_true",help="Only collect city stops/routes.")
    p.add_argument("--timeout",type=int,default=180); p.add_argument("--retries",type=int,default=2)
    a=p.parse_args()
    cities=[x.strip().lower() for x in a.cities.split(",") if x.strip()]
    bad=[x for x in cities if x not in AREAS]
    if bad or not cities: p.error(f"Invalid/empty city selection: {bad}")
    root=Path(a.output).expanduser().resolve()
    for d in ("raw","geojson","csv","reports"): (root/d).mkdir(parents=True,exist_ok=True)
    UI.header()
    print(f"  Output: {root}\n  Areas:  {', '.join(AREAS[x][0] for x in cities)}")
    results=[]; city_results={}
    if not a.overpass_only:
        if not a.skip_pbf:
            UI.section("GEOFABRIK — NATIONAL OPENSTREETMAP EXTRACT")
            try:
                r=save_url(PBF_URL,root/"raw"/"geofabrik"/"tunisia-latest.osm.pbf",a.timeout,a.retries)
                results.append({"source":"Geofabrik Tunisia PBF",**r})
                UI.status("Tunisia OSM PBF",f"{r['bytes']/1048576:.1f} MB","ok")
            except Exception as e:
                results.append({"source":"Geofabrik Tunisia PBF","status":"failed","error":str(e)})
                UI.status("Tunisia OSM PBF",str(e),"fail")
        if a.include_gpkg:
            UI.section("GEOFABRIK — OPTIONAL GEOPACKAGE")
            dest=root/"raw"/"geofabrik"/"tunisia-latest-free.gpkg.zip"
            try:
                r=save_url(GPKG_URL,dest,a.timeout,a.retries)
                out=root/"raw"/"geofabrik"/"gpkg_extracted"; out.mkdir(parents=True,exist_ok=True)
                with zipfile.ZipFile(dest) as z:
                    badfile=z.testzip()
                    if badfile: raise ValueError(f"Corrupt ZIP member: {badfile}")
                    for m in z.infolist():
                        target=(out/m.filename).resolve()
                        if out.resolve() not in target.parents and target!=out.resolve():
                            raise ValueError("Unsafe ZIP path")
                    z.extractall(out)
                results.append({"source":"Geofabrik GeoPackage",**r})
                UI.status("GeoPackage",f"{r['bytes']/1048576:.1f} MB extracted","ok")
            except Exception as e:
                results.append({"source":"Geofabrik GeoPackage","status":"failed","error":str(e)})
                UI.status("GeoPackage",str(e),"fail")
        UI.section("GITHUB — MAP TUNISIA / ADMINISTRATIVE DATA")
        for rel in MAP_FILES:
            url=MAP_BASE+rel; dest=root/"raw"/"map_tunisia"/rel
            try:
                r=save_url(url,dest,a.timeout,a.retries)
                results.append({"source":"Map Tunisia",**r})
                if rel.endswith(".geojson"):
                    target=root/"geojson"/"administrative"/Path(rel).name
                    target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(dest.read_bytes())
                UI.status(rel,f"{r['bytes']:,} bytes","ok")
            except Exception as e:
                results.append({"source":"Map Tunisia","url":url,"status":"failed","error":str(e)})
                UI.status(rel,str(e),"fail")
    UI.section("CITY TRANSPORT STOPS / ROUTES")
    for city in cities:
        city_results[city]=harvest_city(city,root,a.timeout,a.retries,results)
        time.sleep(2)  # be polite to public Overpass servers
    manifest={
      "project":"Tunisia Mobility","generated_utc":datetime.now(timezone.utc).isoformat(),
      "areas":{k:{"label":AREAS[k][0],"bbox_south_west_north_east":AREAS[k][1]} for k in cities},
      "sources":[
        {"name":"OpenStreetMap / Overpass","url":"https://overpass-api.de/","license":"ODbL 1.0",
         "content":"Stops, platforms, stations, route and route_master relations."},
        {"name":"Geofabrik Tunisia extract","url":"https://download.geofabrik.de/africa/tunisia.html",
         "license":"ODbL 1.0","content":"National PBF: roads, railways, paths, POIs and other mapped features."},
        {"name":"Map Tunisia by Alaa Taieb","url":"https://github.com/Alaa-Taieb/map-tunisia",
         "license":"ODbL 1.0","content":"City points, multilingual place references and administrative boundaries.",
         "attribution":"Map data © OpenStreetMap contributors · Map Tunisia by Alaa Taieb"}
      ],
      "osm_attribution":"© OpenStreetMap contributors","city_results":city_results,"results":results,
      "limitations":[
        "Community mapping may be incomplete; absence from OSM does not mean no service exists.",
        "Bounding boxes are collection extents, not official city boundaries.",
        "Route relations are mapped alignments, not verified operator routes or schedules.",
        "These sources do not provide departure times, fares, headways or live vehicle locations.",
        "ODbL 1.0 attribution and share-alike obligations may apply to derivative databases."
      ]}
    report=root/"reports"/"harvest_manifest.json"; write_json(report,manifest)
    stops=sum(x.get("stop_features",0) for x in city_results.values())
    routes=sum(x.get("route_relations",0) for x in city_results.values())
    segments=sum(x.get("route_geometry_segments",0) for x in city_results.values())
    failures=sum(x.get("status")=="failed" for x in results)
    UI.section("HARVEST SUMMARY")
    UI.status("Transport stop features",str(stops),"ok")
    UI.status("Route relations",str(routes),"ok")
    UI.status("Route geometry segments",str(segments),"ok")
    UI.status("Failed steps",str(failures),"warn" if failures else "ok")
    UI.status("Manifest",str(report),"ok")
    print("\n  Open the GeoJSON files in QGIS or https://geojson.io/")
    print("  Attribution: © OpenStreetMap contributors (ODbL 1.0)")
    print("  Map Tunisia: https://github.com/Alaa-Taieb/map-tunisia\n")
    return 0 if stops or routes or any(x.get("status")=="downloaded" for x in results) else 1

if __name__=="__main__":
    raise SystemExit(main())
