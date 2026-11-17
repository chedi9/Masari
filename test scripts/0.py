from __future__ import annotations

import csv
import hashlib
import io
import json
import mimetypes
import os
import queue
import re
import shutil
import sqlite3
import threading
import time
import zipfile
from collections import Counter
from datetime import datetime
from email.message import Message
from pathlib import Path
from urllib.parse import urlparse, unquote

import truststore
truststore.inject_into_ssl()
import requests
import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox

APP_TITLE = "MASARI | Recovery Studio 3.4"
VERSION = "3.4.0"
CKAN_BASE = "https://catalog.data.gov.tn/api/3/action"
USER_AGENT = f"MASARI-Recovery-Studio/{VERSION}"
KNOWN_UNREACHABLE_HOSTS = {"data.transport.tn", "catalogue-data.transport.tn"}
MAX_FILE_MB = 300
MAX_PAGES_PER_QUERY = 12
CSV_ROW_LIMIT = 250000
ARCHIVE_MEMBER_LIMIT = 10000
MAX_TEXT_MB = 100

GOVERNORATES = ["Tunis", "Ariana", "Ben Arous", "Manouba", "Nabeul", "Zaghouan", "Bizerte", "Béja", "Jendouba", "Le Kef", "Siliana", "Sousse", "Monastir", "Mahdia", "Sfax", "Kairouan", "Kasserine", "Sidi Bouzid", "Gabès", "Médenine", "Tataouine", "Gafsa", "Tozeur", "Kébili"]
GOV_ALIASES = {
 "Tunis":["tunis"],"Ariana":["ariana"],"Ben Arous":["ben arous"],"Manouba":["manouba","la manouba"],"Nabeul":["nabeul","nabuel"],"Zaghouan":["zaghouan"],"Bizerte":["bizerte"],"Béja":["beja","béja"],"Jendouba":["jendouba"],"Le Kef":["le kef","el kef","kef"],"Siliana":["siliana"],"Sousse":["sousse"],"Monastir":["monastir"],"Mahdia":["mahdia"],"Sfax":["sfax"],"Kairouan":["kairouan"],"Kasserine":["kasserine"],"Sidi Bouzid":["sidi bouzid"],"Gabès":["gabes","gabès"],"Médenine":["medenine","médenine"],"Tataouine":["tataouine"],"Gafsa":["gafsa"],"Tozeur":["tozeur"],"Kébili":["kebili","kébili"]}
OPERATORS = ["TRANSTU","SNCFT","RFR","SNTRI","SORETRAS","SORETRAK","SONOTRAK","STS","SRTJ","SRT KEF","SRT Béja","SRTB","SRTGN","SRTM","SRTG"]
TRANSPORT_TERMS = ["transport public","transport collectif","transport terrestre","bus","autobus","métro","metro léger","train","ferroviaire","chemin de fer","taxi collectif","louage","gare routière","gare ferroviaire","arrêt bus","arret bus","ligne bus","horaires transport","horaire bus","horaire train","tarif transport","GTFS","timetable","stop_times","stops.txt","routes.txt"]
GEO_TERMS = ["découpage administratif Tunisie","gouvernorats Tunisie","délégations Tunisie","municipalités Tunisie","communes Tunisie","limites administratives","frontières administratives","localités Tunisie","villes Tunisie","codes géographiques Tunisie","référentiel géographique","GeoJSON Tunisie","shapefile Tunisie","carte administrative Tunisie"]
ADMIN_STRONG = ["découpage de la tunisie par gouvernorat","decoupage de la tunisie par gouvernorat","découpage géographique des gouvernorats","decoupage geographique des gouvernorats","liste des gouvernorats","liste des délégations","liste des delegations","limites des gouvernorats","limites des délégations","limites des delegations","codes des gouvernorats","découpage de la tunisie par délégation","decoupage de la tunisie par delegation","découpage de la tunisie par municipalité","decoupage de la tunisie par municipalite","découpage de la tunisie par circonscription","circonsciptions","administrative boundaries","découpage administratif","decoupage administratif","limites administratives","frontières administratives","frontieres administratives","gouvernorat boundary","limite de gouvernorat","délégations de tunisie","delegations de tunisie","municipalités de tunisie","communes de tunisie"]
ADMIN_TERMS = ["gouvernorat","gouvernorats","délégation","delegation","municipalité","municipalite","commune","administratif","administrative","limite administrative","frontière administrative","frontiere administrative"]
USEFUL_GEO_TERMS = ["localité","localite","ville","villes","poi","point of interest","lieu-dit","localisation","geolocalisation","geolocation","coordonnées des stations","coordonnees des stations","station de transport","arrêt de bus","arret de bus"]
EXCLUDE_TERMS = ["agriculture","agricole","agronomie","miel","apiculture","irrigation","barrage","barrages","eau potable","eaux usées","eaux usees","pluviométrie","pluviometrie","précipitation","precipitation","nappe phréatique","nappe phreatique","musée","musee","archéologie","archeologie","festival","école","ecole","scolaire","santé","sante","hôpital","hopital","incubateur","technopole","centre médical","centre medical","football","sport","pétrole","petrole","hydrocarbure","hydrocarbures","gaz naturel"]
GTFS_REQUIRED = {"agency.txt","stops.txt","routes.txt","trips.txt","stop_times.txt"}
GTFS_HEADERS = {
 "agency.txt":{"agency_name","agency_url","agency_timezone"},
 "stops.txt":{"stop_id","stop_name","stop_lat","stop_lon"},
 "routes.txt":{"route_id","route_type"},
 "trips.txt":{"route_id","service_id","trip_id"},
 "stop_times.txt":{"trip_id","arrival_time","departure_time","stop_id","stop_sequence"}}
GTFS_OPTIONAL = {"calendar.txt","calendar_dates.txt","shapes.txt","frequencies.txt","transfers.txt","fare_attributes.txt","fare_rules.txt","feed_info.txt","pathways.txt","levels.txt"}

def now_iso(): return datetime.now().astimezone().isoformat(timespec="seconds")
def norm(v): return re.sub(r"\s+"," ",str(v or "").lower().replace("’", "'")).strip()
def safe_name(v):
    s=unquote(str(v or "item"));s=re.sub(r"[^\w.\-]+","_",s,flags=re.UNICODE).strip("._")
    return s[:110] or "item"
def sha256_file(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
    return h.hexdigest()
def has_phrase(text, phrase):
    phrase=norm(phrase)
    if re.fullmatch(r"[a-z0-9]+",phrase):
        return re.search(r"(?<![a-z0-9])"+re.escape(phrase)+r"(?![a-z0-9])",text) is not None
    return phrase in text
def gov_matches(text):
    t=norm(text);found=[]
    for official,aliases in GOV_ALIASES.items():
        if any(re.search(r"(?<!\w)"+re.escape(norm(a))+r"(?!\w)",t) for a in aliases):found.append(official)
    return found

def classify_resource(row):
    title=norm(row.get("dataset_title") or row.get("title"));name=norm(row.get("name"));org=norm(row.get("organization"))
    tags=" ".join(norm(x.get("name") if isinstance(x,dict) else x) for x in (row.get("tags") or []))
    desc=norm(row.get("description") or row.get("dataset_notes") or row.get("notes"));url=norm(row.get("url"))
    primary=" ".join([title,name,org,tags]);alltext=" ".join([primary,desc,url])
    exclusions=[x for x in EXCLUDE_TERMS if has_phrase(primary,x)]
    operator_terms=["transtu","sncft","rfr","sntri","soretras","soretrak","sonotrak","sts","srtj","srt kef","srt béja","srtb","srtgn","srtm","srtg"]
    weighted=[
      ("gtfs",55),("stop_times",55),("agency.txt",45),("stops.txt",45),("routes.txt",45),("trips.txt",45),
      ("lignes des taxis collectifs",42),("taxis collectifs",36),("taxi collectif",30),("louage",30),
      ("sncft",32),("transtu",32),("sntri",30),("rfr",30),("soretras",30),("soretrak",30),("sonotrak",28),
      ("horaires",24),("horaire",24),("timetable",24),("schedule",20),("transport public",26),
      ("transport collectif",26),("transport terrestre",20),("transport rural",24),("métro léger",28),
      ("metro léger",28),("autobus",22),("chemin de fer",24),("réseau ferré",24),("reseau ferre",24)]
    score=0;evidence=[]
    for op in operator_terms:
        if has_phrase(primary,op):
            score+=28;evidence.append("operator:"+op);break
    for phrase,points in weighted:
        if has_phrase(primary,phrase):
            score+=points;evidence.append("strong:"+phrase)
    for phrase,points in [("itinéraire",10),("itineraire",10),("ligne",7),("gare",7),("arrêt",8),("arret",8),("station",5),("tarif",8),("fare",8),("position géographique",8),("position geographique",8)]:
        if has_phrase(primary,phrase):score+=points;evidence.append("title:"+phrase)
    desc_hits=[x for x in ["bus","train","transport","horaire","station"] if has_phrase(desc,x)]
    score+=min(8,len(desc_hits)*2)
    evidence += ["description:"+x for x in desc_hits]
    strong_transport=any(has_phrase(primary,x) for x in ["transport public","transport collectif","transport terrestre","lignes des taxis collectifs","taxis collectifs","sncft","transtu","sntri","rfr","soretras","soretrak","gtfs"])
    if exclusions and not strong_transport:score=0
    admin_hits=[x for x in ADMIN_STRONG if has_phrase(primary,x)]
    admin_score=len(admin_hits)*30
    geo_hits=[x for x in USEFUL_GEO_TERMS if has_phrase(primary,x)]
    geo_score=len(geo_hits)*9
    ext=Path(urlparse(str(row.get("url") or "")).path).suffix.lower()
    if ext in {".geojson",".gpkg",".kml",".gpx"}:geo_score+=5
    if score>=20 and score>=admin_score:
        category="Transport";sub=[]
        if any(x in alltext for x in ["horaire","horaires","timetable","schedule"]):sub.append("timetables")
        if any(x in alltext for x in ["tarif","fare","prix"]):sub.append("fares")
        if any(x in alltext for x in ["arrêt","arret","stop","station","gare"]):sub.append("stops_stations")
        if any(x in alltext for x in ["ligne","route","itinéraire","itineraire"]):sub.append("routes_lines")
        if not sub:sub=["transport_reference"]
        mode=[]
        for label,terms in [("Bus",["bus","autobus","transtu","soretras","soretrak","srtb","srtgn","srtj"]),("Metro / Light rail",["métro","metro","rfr","tgm"]),("Train",["sncft","train","ferroviaire","réseau ferré","reseau ferre"]),("Taxi collectif",["taxi collectif","taxis collectifs"]),("Louage",["louage"]),("Coach / Intercity",["sntri","interurbain"])]:
            if any(has_phrase(alltext,x) for x in terms):mode.append(label)
        mode="; ".join(mode) or "General transport";final=score
    elif admin_score>=30 and not exclusions:
        category="Administrative geography";sub=["administrative_reference"]
        if any("gouvernorat" in x for x in admin_hits):sub.append("governorates")
        if any("délégation" in x or "delegation" in x for x in admin_hits):sub.append("delegations")
        if any("municipalité" in x or "municipalite" in x for x in admin_hits):sub.append("municipalities")
        if any(any(y in x for y in ["limite","frontière","frontiere","boundary"]) for x in admin_hits):sub.append("boundary_candidate")
        mode="Administrative reference";final=admin_score
    elif geo_score>=12 and not exclusions:
        category="Useful geography";sub=["geographic_reference"];mode="Geographic reference";final=geo_score
    else:
        category="Other";sub=[];mode="Not classified";final=max(score,admin_score,geo_score)
    govs=gov_matches(alltext)
    return {"category":category,"subcategories":sub,"mode":mode,"relevance_score":final,
      "relevance":"Very high" if final>=55 else "High" if final>=32 else "Medium" if final>=20 else "Low",
      "governorates":govs,"coverage_confidence":"Metadata mention only" if govs else "Not identified",
      "excluded_topic_matches":exclusions,"classification_evidence":evidence+["admin:"+x for x in admin_hits]+["geo:"+x for x in geo_hits]}

def sniff_bytes(head,path=None,content_type=""):
    h=head.lstrip(b"\xef\xbb\xbf\x00\t\r\n ")
    if head.startswith(b"PK\x03\x04"):
        if path:
            try:
                with zipfile.ZipFile(path) as z:
                    names={n.replace("\\","/").lower() for n in z.namelist() if not n.endswith("/")}
                    bases={Path(n).name for n in names}
                    if "[content_types].xml" in bases and any(n.startswith("xl/") for n in names):return "XLSX"
                    if GTFS_REQUIRED.issubset(bases):return "GTFS-ZIP"
                    if any(n.endswith(".shp") for n in names):return "SHAPEFILE-ZIP"
                    if any(n.endswith((".geojson",".json")) for n in names):return "GEOJSON-ZIP"
            except Exception:return "CORRUPT-ZIP"
        return "ZIP"
    if head.startswith(b"Rar!\x1a\x07"):return "RAR"
    if head.startswith(b"%PDF-"):return "PDF"
    if head.startswith(bytes.fromhex("D0CF11E0A1B11AE1")):return "XLS"
    if head.startswith(b"SQLite format 3\x00"):return "SQLITE/GPKG"
    if h.startswith((b"{",b"[")):
        try:
            obj=json.loads(h.decode("utf-8-sig"))
            if isinstance(obj,dict) and obj.get("type") in {"FeatureCollection","Feature","GeometryCollection"}:return "GEOJSON"
            return "JSON"
        except Exception:pass
    try:
        sample=h.decode("utf-8-sig")
        if len(sample.splitlines())>=2 and any(d in sample for d in [",",";","\t","|"]):return "CSV"
    except Exception:pass
    ct=norm(content_type)
    if "json" in ct:return "JSON"
    if "csv" in ct:return "CSV"
    if "excel" in ct or "spreadsheet" in ct:return "XLSX"
    if "pdf" in ct:return "PDF"
    if "html" in ct:return "HTML"
    if "xml" in ct:return "XML"
    return "UNKNOWN"
def sniff_file(path,content_type=""):
    with open(path,"rb") as f:head=f.read(16384)
    return sniff_bytes(head,path,content_type)

def detect_encoding(sample):
    for enc in ("utf-8-sig","cp1252","cp1256","latin-1"):
        try:
            text=sample.decode(enc)
            if "\ufffd" not in text and text.count("\x00")<2:return enc
        except UnicodeDecodeError:continue
    return "utf-8"

def csv_info(path,limit=CSV_ROW_LIMIT):
    sample=Path(path).read_bytes()[:256000]
    enc=detect_encoding(sample)
    text=sample.decode(enc,errors="replace")
    try:delimiter=csv.Sniffer().sniff(text,delimiters=",;\t|").delimiter
    except Exception:
        counts={d:text.count(d) for d in [",",";","\t","|"]}
        delimiter=max(counts,key=counts.get) if max(counts.values()) else ","
    with open(path,"r",encoding=enc,errors="replace",newline="") as f:
        reader=csv.DictReader(f,delimiter=delimiter)
        headers=reader.fieldnames or []
        if not headers:raise ValueError("CSV has no header row")
        if len(set(headers))!=len(headers):raise ValueError("CSV contains duplicate column names")
        count=0
        def rows():
            nonlocal count
            for row in reader:
                count+=1
                yield row
        return headers,enc,delimiter,rows(),lambda:count

def inspect_geojson_obj(obj):
    typ=obj.get("type") if isinstance(obj,dict) else None
    if typ=="FeatureCollection":features=obj.get("features",[])
    elif typ=="Feature":features=[obj]
    else:features=[]
    geom=Counter();props=Counter();bounds=[float("inf"),float("inf"),float("-inf"),float("-inf")];points=0
    def walk(c):
        nonlocal points
        if isinstance(c,(list,tuple)) and len(c)>=2 and isinstance(c[0],(int,float)) and isinstance(c[1],(int,float)):
            x,y=float(c[0]),float(c[1]);bounds[0]=min(bounds[0],x);bounds[1]=min(bounds[1],y);bounds[2]=max(bounds[2],x);bounds[3]=max(bounds[3],y);points+=1
        elif isinstance(c,(list,tuple)):
            for x in c:walk(x)
    if typ=="GeometryCollection":
        geoms=obj.get("geometries",[])
        for g in geoms:geom[g.get("type","null")]+=1;walk(g.get("coordinates",[]))
        feature_count=len(geoms)
    else:
        for f in features:
            g=f.get("geometry") or {};geom[g.get("type","null")]+=1;walk(g.get("coordinates",[]));props.update((f.get("properties") or {}).keys())
        feature_count=len(features)
    bbox=bounds if points else None
    plausible=bool(bbox and 7.0<=bbox[0]<=12.5 and 30.0<=bbox[1]<=38.0 and 7.0<=bbox[2]<=12.5 and 30.0<=bbox[3]<=38.0)
    return {"geojson_type":typ,"feature_count":feature_count,"geometry_types":dict(geom),"property_names":sorted(props),"coordinate_count":points,"bbox_lonlat":bbox,"geographic_extent_verified":plausible,"governorates_identified_from_features":[],"service_coverage_verified":False,"administrative_boundary_verified":False}

class RecoveryEngine:
    def __init__(self,out_dir,events,stop_event):
        self.root=Path(out_dir);self.out=self.root/("run_"+datetime.now().strftime("%Y%m%d_%H%M%S"));self.events=events;self.stop=stop_event
        self.session=requests.Session();self.session.headers.update({"User-Agent":USER_AGENT})
        self.datasets={};self.resources={};self.stats=Counter();self.quality=[];self.gtfs=[];self.extractions=[];self.started=time.time();self.stamp=now_iso();self.host_status={};self.seen_hashes={}

    def emit(self,kind,**kw):self.events.put({"kind":kind,**kw})
    def log(self,level,msg):self.emit("log",level=level,message=msg)
    
    def api(self,action,params=None,timeout=25):
        if self.stop.is_set():return None
        try:
            r=self.session.get(f"{CKAN_BASE}/{action}",params=params or {},timeout=(8,timeout));r.raise_for_status();j=r.json()
            if j.get("success"):return j.get("result")
            self.stats["api_errors"]+=1
        except Exception as e:self.stats["api_errors"]+=1;self.log("WARN",f"CKAN {action}: {str(e)[:150]}")
        return None

    def load_21_exports(self,folder):
        folder=Path(folder);p=folder/"resources.json"
        if not p.exists():raise FileNotFoundError(f"resources.json not found in {folder}")
        rows=json.loads(p.read_text(encoding="utf-8-sig"))
        self.resources={str(r.get("id") or r.get("url") or i):r for i,r in enumerate(rows)}
        q=folder/"datasets.json"
        if q.exists():
            try:self.datasets={str(d.get("id") or i):d for i,d in enumerate(json.loads(q.read_text(encoding="utf-8-sig")))}
            except Exception:pass
        q=folder/"quality_issues.json"
        if q.exists():
            try:self.quality=json.loads(q.read_text(encoding="utf-8-sig"))
            except Exception:pass
        self.stats["imported_resources"]=len(self.resources);self.stats["imported_datasets"]=len(self.datasets)
        manifest=folder/"download_manifest.json"
        if manifest.exists():
            try:
                for item in json.loads(manifest.read_text(encoding="utf-8-sig")):
                    if item.get("sha256") and item.get("local_path"):self.seen_hashes[item["sha256"]]=item["local_path"]
            except Exception:pass
        self.log("SUCCESS",f"Imported {len(self.resources)} resource records; discovery not repeated")
        self.reanalyse_resources();self.inspect_existing_downloads()

    def discover(self):
        terms=list(dict.fromkeys(OPERATORS+TRANSPORT_TERMS+GEO_TERMS))
        for gov in GOVERNORATES:terms.extend([f"transport {gov} Tunisie",f"données géographiques {gov}"])
        terms=list(dict.fromkeys(terms));self.emit("stage",name="Nationwide catalogue discovery",detail=f"{len(terms)} queries · all 24 governorates")
        found={};total=len(terms)
        for i,term in enumerate(terms,1):
            if self.stop.is_set():break
            start=0
            for _ in range(MAX_PAGES_PER_QUERY):
                result=self.api("package_search",{"q":term,"rows":100,"start":start})
                if not result:break
                items=result.get("results",[]) or [];count=int(result.get("count") or 0)
                for d in items:
                    if d.get("id"):found[d["id"]]=d
                self.stats["search_pages"]+=1
                if not items or start+len(items)>=count:break
                start+=len(items)
            self.stats["searches"]+=1
            if i%5==0 or i==total:self.emit("progress",value=12*i/total,detail=f"Searching {i}/{total}: {term}")
        self.datasets.update(found);self.stats["datasets_found"]=len(found);self.log("SUCCESS",f"Found {len(found)} unique datasets")
        ids=list(found);self.stats["dataset_details_ok"]=0;self.stats["dataset_details_failed"]=0
        for i,did in enumerate(ids,1):
            if self.stop.is_set():break
            detail=self.api("package_show",{"id":did})
            if detail:
                self.stats["dataset_details_ok"]+=1;self.datasets[did]=detail;org=(detail.get("organization") or {}).get("title","")
                for raw in detail.get("resources",[]) or []:
                    rid=str(raw.get("id") or raw.get("url") or "")
                    if not rid:continue
                    row=dict(raw);row.update({"dataset_id":did,"dataset_title":detail.get("title",""),"dataset_notes":detail.get("notes",""),"organization":org,"retrieved_at":self.stamp})
                    if rid not in self.resources:self.resources[rid]=row
                    else:
                        for k,v in row.items():
                            if self.resources[rid].get(k) in (None,"",[]):self.resources[rid][k]=v
            else:self.stats["dataset_details_failed"]+=1
            if i%10==0 or i==len(ids):self.emit("progress",value=12+28*i/max(1,len(ids)),detail=f"Dataset details {i}/{len(ids)}")
        self.stats["dataset_details_attempted"]=self.stats["dataset_details_ok"]+self.stats["dataset_details_failed"]
        self.stats["resources_found"]=len(self.resources);self.log("SUCCESS",f"Indexed {len(self.resources)} resources")
        self.reanalyse_resources()

    def reanalyse_resources(self):
        self.emit("stage",name="Evidence-based classification",detail="Separating transport, administrative references, useful geography and unrelated resources")
        counts=Counter()
        for i,r in enumerate(self.resources.values(),1):
            r.setdefault("v2_original_category",r.get("category"));r.setdefault("v2_original_relevance_score",r.get("relevance_score"))
            result=classify_resource(r);r.update(result);r["host"]=urlparse(str(r.get("url") or "")).hostname or ""
            r.setdefault("download_status","Not attempted");r.setdefault("validation_status","Not inspected");counts[result["category"]]+=1
            if i%100==0:self.emit("progress",value=42+8*i/max(1,len(self.resources)),detail=f"Classifying {i}/{len(self.resources)}")
        self.stats.update({"category_"+k.lower().replace(" ","_"):v for k,v in counts.items()})
        self.emit("metrics",counts=dict(counts),datasets=len(self.datasets),resources=len(self.resources));self.log("INFO",f"Classification: {dict(counts)}")

    def inspect_existing_downloads(self):
        existing=[r for r in self.resources.values() if r.get("local_path") and Path(str(r["local_path"])).is_file()]
        self.emit("stage",name="Inspecting existing downloads",detail=f"{len(existing)} existing files")
        for i,r in enumerate(existing,1):
            if self.stop.is_set():break
            try:
                p=Path(str(r["local_path"]));digest=r.get("sha256") or sha256_file(p);r["sha256"]=digest;self.seen_hashes[digest]=str(p);r["detected_format"]=sniff_file(p);self.inspect_resource_file(p,r);self.stats["existing_files_inspected"]+=1
            except Exception as e:self.quality.append({"resource_id":r.get("id"),"local_path":r.get("local_path"),"error":str(e)})
            if i%10==0 or i==len(existing):self.emit("progress",value=50+10*i/max(1,len(existing)),detail=f"Existing files {i}/{len(existing)}")
        self.stats["missing_local_files"]=sum(1 for r in self.resources.values() if r.get("local_path") and not Path(str(r["local_path"])).is_file())

    def host_check(self,host,scheme="https"):
        if not host or host in KNOWN_UNREACHABLE_HOSTS:return False
        key=f"{scheme}://{host}"
        if key in self.host_status:return self.host_status[key]
        try:self.session.get(f"{scheme}://{host}/",timeout=(3,4),allow_redirects=True,stream=True).close();ok=True
        except Exception:ok=False
        self.host_status[key]=ok;return ok

    def _filename(self,r,response,idx):
        disp=response.headers.get("content-disposition","");name=""
        if disp:
            m=Message();m["content-disposition"]=disp;name=m.get_filename() or ""
        if not name:name=r.get("name") or Path(urlparse(response.url).path).name
        return safe_name(name or f"resource_{idx}")

    def recover(self,max_items=500):
        candidates=[r for r in self.resources.values() if r.get("category") in {"Transport","Administrative geography","Useful geography"} and r.get("relevance_score",0)>=18 and r.get("url") and not (r.get("local_path") and Path(str(r["local_path"])).is_file())]
        candidates.sort(key=lambda r:(r.get("category")=="Transport",r.get("relevance_score",0)),reverse=True)
        self.emit("stage",name="Resource recovery",detail=f"{len(candidates)} candidates · max {max_items}")
        base=self.out/"raw";base.mkdir(parents=True,exist_ok=True)
        for i,r in enumerate(candidates[:max_items],1):
            if self.stop.is_set():break
            urls=list(dict.fromkeys([str(r.get("url") or ""),str(r.get("cache_url") or "")]));urls=[u for u in urls if u.startswith(("http://","https://"))]
            if not urls:r["download_status"]="Skipped · no valid URL";continue
            url=urls[0];host=urlparse(url).hostname or ""
            if host in KNOWN_UNREACHABLE_HOSTS and len(urls)>1 and urlparse(urls[1]).hostname not in KNOWN_UNREACHABLE_HOSTS:url=urls[1];host=urlparse(url).hostname or "";r["recovery_url_source"]="CKAN cache_url"
            if host in KNOWN_UNREACHABLE_HOSTS:r["download_status"]="Blocked · known unreachable source host";self.stats["blocked_unreachable"]+=1;continue
            if not self.host_check(host,urlparse(url).scheme):
                if len(urls)>1 and url!=urls[1] and urlparse(urls[1]).hostname not in KNOWN_UNREACHABLE_HOSTS and self.host_check(urlparse(urls[1]).hostname or "",urlparse(urls[1]).scheme):url=urls[1];host=urlparse(url).hostname or "";r["recovery_url_source"]="CKAN cache_url"
                else:r["download_status"]="Host probe failed · not retried";self.stats["host_probe_failed"]+=1;continue
            tmp=None
            try:
                with self.session.get(url,timeout=(8,35),stream=True,allow_redirects=True) as resp:
                    resp.raise_for_status();finalhost=urlparse(resp.url).hostname or ""
                    if finalhost in KNOWN_UNREACHABLE_HOSTS:raise RuntimeError("Redirected to known unreachable host")
                    length=int(resp.headers.get("content-length") or 0)
                    if length>MAX_FILE_MB*1024*1024:raise RuntimeError("File exceeds size limit")
                    folder=base/{"Transport":"transport","Administrative geography":"admin_geography","Useful geography":"useful_geography"}[r["category"]];folder.mkdir(parents=True,exist_ok=True)
                    suggested=self._filename(r,resp,i);tmp=folder/(safe_name(r.get("id") or str(i))+".part");size=0;h=hashlib.sha256()
                    with tmp.open("wb") as f:
                        for chunk in resp.iter_content(128*1024):
                            if self.stop.is_set():break
                            if chunk:
                                size+=len(chunk)
                                if size>MAX_FILE_MB*1024*1024:raise RuntimeError("Streaming size limit exceeded")
                                f.write(chunk);h.update(chunk)
                    if self.stop.is_set():tmp.unlink(missing_ok=True);r["download_status"]="Stopped";continue
                    digest=h.hexdigest()
                    if digest in self.seen_hashes:
                        tmp.unlink(missing_ok=True);r.update({"sha256":digest,"duplicate_of":self.seen_hashes[digest],"download_status":"Duplicate content"});self.stats["duplicates"]+=1;continue
                    fmt=sniff_file(tmp,resp.headers.get("content-type",""))
                    ext={"GTFS-ZIP":".zip","SHAPEFILE-ZIP":".zip","GEOJSON-ZIP":".zip","ZIP":".zip","CORRUPT-ZIP":".zip","RAR":".rar","GEOJSON":".geojson","JSON":".json","CSV":".csv","PDF":".pdf","XLS":".xls","XLSX":".xlsx","SQLITE/GPKG":".gpkg","HTML":".html","XML":".xml"}.get(fmt,Path(suggested).suffix or ".bin")
                    final=folder/(safe_name(r.get("id") or str(i))+"_"+safe_name(Path(suggested).stem)+ext);n=2
                    while final.exists():final=folder/(safe_name(r.get("id") or str(i))+"_"+safe_name(Path(suggested).stem)+f"_{n}"+ext);n+=1
                    tmp.replace(final);tmp=None
                    r.update({"sha256":digest,"detected_format":fmt,"local_path":str(final),"bytes_downloaded":size,"final_url":resp.url,"download_status":"Downloaded"});self.seen_hashes[digest]=str(final);self.stats["downloaded"]+=1;self.stats["bytes_downloaded"]+=size
                    self.inspect_resource_file(final,r);self.log("SUCCESS",f"Downloaded {fmt}: {final.name}")
            except Exception as e:
                if tmp and tmp.exists():tmp.unlink(missing_ok=True)
                r["download_status"]="Failed · "+str(e)[:160];self.stats["failed"]+=1;self.log("WARN",f"Download failed {r.get('name')}: {str(e)[:120]}")
            if i%5==0 or i==min(max_items,len(candidates)):self.emit("progress",value=50+30*i/max(1,min(max_items,len(candidates))),detail=f"Recovery {i}/{min(max_items,len(candidates))}")

    def write_jsonl_many(self,rel,objects):
        p=self.out/rel;p.parent.mkdir(parents=True,exist_ok=True);count=0
        with p.open("a",encoding="utf-8") as f:
            for obj in objects:f.write(json.dumps(obj,ensure_ascii=False,default=str)+"\n");count+=1
        return count

    def write_jsonl(self,rel,obj):return self.write_jsonl_many(rel,[obj])

    def write_jsonl_stream(self,rel,prefix,rows):
        p=self.out/rel;p.parent.mkdir(parents=True,exist_ok=True);count=0
        with p.open("a",encoding="utf-8") as f:
            for row in rows:f.write(json.dumps({**prefix,**row},ensure_ascii=False,default=str)+"\n");count+=1
        return count

    def inspect_resource_file(self, path, r):
        path = Path(path)
        meta = {
            "resource_id": r.get("id"),
            "dataset_id": r.get("dataset_id"),
            "dataset_title": r.get("dataset_title"),
            "path": str(path),
            "format": "UNKNOWN",
            "validation_status": "Not inspected",
            "inspection_errors": [],
            "archive_members": [],
            "extracted_files": [],
            "extracted_rows": 0,
            "extracted_features": 0,
            "truncated": False,
        }

        def record_error(message):
            meta["inspection_errors"].append(str(message))

        def validate_geojson(obj):
            if not isinstance(obj, dict): return False
            geo_type = obj.get("type")
            if geo_type == "FeatureCollection":
                features = obj.get("features")
                return isinstance(features, list) and all(isinstance(f, dict) and f.get("type") == "Feature" for f in features)
            if geo_type == "Feature": return "geometry" in obj
            if geo_type == "GeometryCollection": return isinstance(obj.get("geometries"), list)
            return False

        def inspect_geojson_bytes(data, source_name):
            try:
                obj = json.loads(data.decode("utf-8-sig"))
                if not validate_geojson(obj): return False
                features = obj.get("features", []) if obj.get("type") == "FeatureCollection" else ([obj] if obj.get("type") == "Feature" else [])
                meta["extracted_features"] += len(features)
                meta.setdefault("geojson_files", []).append({"name": source_name, "type": obj.get("type"), "feature_count": len(features), "valid_structure": True})
                return True
            except Exception as exc:
                record_error(f"GeoJSON inspection failed for {source_name}: {exc}")
                return False

        def inspect_csv_bytes(data, source_name):
            try: text = data.decode("utf-8-sig")
            except UnicodeDecodeError:
                try: text = data.decode("cp1252")
                except Exception as exc:
                    record_error(f"CSV decoding failed for {source_name}: {exc}")
                    return False
            try:
                sample = text[:8192]
                try:
                    dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
                    delimiter = dialect.delimiter
                except csv.Error:
                    delimiter = next((d for d in [",", ";", "\t", "|"] if d in sample), ",")
                reader = csv.reader(io.StringIO(text), delimiter=delimiter)
                headers = next(reader, None)
                if not headers or len(headers) < 2:
                    record_error(f"CSV has no usable header: {source_name}")
                    return False
                rows = sum(1 for _ in reader)
                meta.setdefault("csv_files", []).append({"name": source_name, "delimiter": delimiter, "columns": len(headers), "headers": headers, "rows": rows})
                meta["extracted_rows"] += rows
                return True
            except Exception as exc:
                record_error(f"CSV inspection failed for {source_name}: {exc}")
                return False

        def inspect_zip_archive(archive_path):
            archive_results = {"valid_zip": False, "member_count": 0, "xlsx": False, "gtfs": False, "shapefile": False, "geojson": False, "csv": False, "members": []}
            try:
                with zipfile.ZipFile(archive_path, "r") as z:
                    bad_member = z.testzip()
                    if bad_member:
                        record_error(f"ZIP integrity check failed at {bad_member}")
                        return archive_results
                    files = [n for n in z.namelist() if not n.endswith("/")]
                    normalized = {n.replace("\\", "/").lower() for n in files}
                    basenames = {Path(n.replace("\\", "/")).name.lower() for n in files}
                    archive_results["valid_zip"] = True
                    archive_results["member_count"] = len(files)
                    archive_results["members"] = files[:200]
                    archive_results["xlsx"] = "[content_types].xml" in basenames and any(n.startswith("xl/") for n in normalized)
                    archive_results["gtfs"] = GTFS_REQUIRED.issubset(basenames)
                    archive_results["shapefile"] = any(n.endswith(".shp") for n in normalized)
                    archive_results["geojson"] = any(n.endswith((".geojson", ".json")) for n in normalized)
                    archive_results["csv"] = any(n.endswith(".csv") for n in normalized)
                    for member in files:
                        lower = member.lower()
                        if lower.endswith((".geojson", ".json")):
                            try:
                                info = z.getinfo(member)
                                if info.file_size <= 100 * 1024 * 1024:
                                    inspect_geojson_bytes(z.read(member), member)
                            except Exception: pass
                        elif lower.endswith(".csv"):
                            try:
                                info = z.getinfo(member)
                                if info.file_size <= 100 * 1024 * 1024:
                                    inspect_csv_bytes(z.read(member), member)
                            except Exception: pass
                    if archive_results["gtfs"]:
                        calendar_present = "calendar.txt" in basenames or "calendar_dates.txt" in basenames
                        meta["gtfs_calendar_present"] = calendar_present
                        meta["gtfs_basic_valid"] = calendar_present
                return archive_results
            except Exception as exc:
                record_error(f"ZIP inspection failed: {exc}")
                return archive_results

        try: fmt = sniff_file(path)
        except Exception as exc: fmt = "UNKNOWN"; record_error(f"Format detection failed: {exc}")

        meta["format"] = fmt
        r["detected_format"] = fmt

        if fmt in {"ZIP", "GTFS-ZIP", "SHAPEFILE-ZIP", "GEOJSON-ZIP"}:
            archive = inspect_zip_archive(path)
            meta["archive"] = archive
            meta["archive_members"] = archive.get("members", [])
            if not archive["valid_zip"]: meta["validation_status"] = "Invalid ZIP archive"
            elif archive["xlsx"]:
                meta["format"] = "XLSX"; r["detected_format"] = "XLSX"
                meta["validation_status"] = "Valid XLSX workbook"
            elif archive["gtfs"]:
                meta["format"] = "GTFS-ZIP"; r["detected_format"] = "GTFS-ZIP"
                meta["validation_status"] = "GTFS archive inspected"
            else: meta["validation_status"] = "Valid ZIP archive"
        elif fmt in {"GEOJSON", "JSON"}:
            meta["validation_status"] = "Valid JSON/GeoJSON structure"
        elif fmt == "CSV":
            meta["validation_status"] = "CSV readable"
        elif fmt == "XLSX":
            meta["validation_status"] = "Valid XLSX workbook"
        elif fmt == "XLS":
            meta["validation_status"] = "Valid XLS workbook"
        elif fmt == "PDF":
            meta["validation_status"] = "Valid PDF"
        elif fmt == "SQLITE/GPKG":
            meta["validation_status"] = "Valid SQLite/GeoPackage"
        elif fmt == "RAR":
            meta["validation_status"] = "RAR archive readable"
        else:
            meta["validation_status"] = f"Detected {fmt}"

        r["validation_status"] = meta["validation_status"]
        r["inspection_errors"] = meta["inspection_errors"]
        r["extracted_features"] = meta["extracted_features"]
        r["extracted_rows"] = meta["extracted_rows"]
        return meta

    def inspect_local_folder(self, folder):
        folder = Path(folder)
        files = [p for p in folder.rglob("*") if p.is_file() and p.suffix.lower() not in {".part", ".pyc"} and self.out not in p.parents]
        self.emit("stage", name="Local file ingestion", detail=f"Inspecting {len(files)} files; originals remain in place")
        for i, p in enumerate(files, 1):
            if self.stop.is_set(): break
            try:
                rel = p.relative_to(folder); parts = [x.lower() for x in rel.parts[:-1]]
                r = {"id": p.stem, "dataset_id": "local_import", "dataset_title": p.parent.name, "name": p.name, "category": "Other", "local_path": str(p), "url": "", "source_type": "local_import", "relative_path": str(rel), "original_filename": p.name, "directory_context": " ".join(parts + [p.stem.lower()])}
                r.update(classify_resource(r))
                r["sha256"] = sha256_file(p); r["download_status"] = "Existing local file"; self.resources["local:" + str(p)] = r; self.inspect_resource_file(p, r)
            except Exception as e: self.quality.append({"file": str(p), "error": str(e)})
            if i % 10 == 0 or i == len(files): self.emit("progress", value=90 * i / max(1, len(files)), detail=f"Inspecting local files {i}/{len(files)}")
        self.log("SUCCESS", f"Local inspection completed: {len(files)} files")

    def coverage_report(self):
        result = {}
        rows = list(self.resources.values())
        for gov in GOVERNORATES:
            matched = [r for r in rows if gov in (r.get("governorates") or [])]
            result[gov] = {
                "metadata_matches": len(matched),
                "transport_metadata_matches": sum(r.get("category") == "Transport" for r in matched),
                "administrative_geography_resources": sum(r.get("category") == "Administrative geography" for r in matched),
                "verified_boundary_assets": sum(bool(r.get("administrative_boundary_verified")) for r in matched),
                "evidence": "Metadata mention only; not verified service coverage" if matched else "No metadata match found"
            }
        return {
            "scope": "Nationwide Tunisia · all 24 governorates",
            "governorates": result,
            "warning": "Metadata mentions do not prove operational coverage. A Tunisia-plausible bounding box proves only approximate geographic extent, not governorate identity, administrative boundaries or service coverage."
        }

    def export(self):
        self.out.mkdir(parents=True, exist_ok=True)
        def dump(name, obj): (self.out / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        rows = list(self.resources.values()); datasets = list(self.datasets.values())
        dump("datasets.json", datasets); dump("resources.json", rows); dump("quality_issues.json", self.quality); dump("gtfs_validation.json", self.gtfs); dump("content_extraction_index.json", self.extractions); dump("coverage_by_governorate.json", self.coverage_report())
        for cat, filename in [("Transport", "transport_resources.json"), ("Administrative geography", "administrative_geography.json"), ("Useful geography", "useful_geography.json"), ("Other", "other_resources.json")]:
            dump(filename, [r for r in rows if r.get("category") == cat])
        cols = sorted({k for r in rows for k in r})
        with (self.out / "resources_index.csv").open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
        report = {
            "application": APP_TITLE, "version": VERSION, "generated_at": self.stamp, "output_run_directory": str(self.out), "catalogue": CKAN_BASE,
            "scope": "Nationwide Tunisia; all 24 governorates; launch-city-independent", "datasets": len(datasets), "resources": len(rows),
            "category_counts": dict(Counter(r.get("category", "Other") for r in rows)), "downloads": self.stats["downloaded"],
            "failed": self.stats["failed"], "blocked_unreachable": self.stats["blocked_unreachable"], "host_probe_failed": self.stats["host_probe_failed"],
            "duplicates": self.stats["duplicates"], "bytes_downloaded": self.stats["bytes_downloaded"], "quality_issues": len(self.quality), "host_checks": self.host_status, "stats": dict(self.stats),
            "stopped_by_user": self.stop.is_set()
        }
        dump("recovery_report.json", report)
        manifest = [{"resource_id": r.get("id"), "sha256": r.get("sha256"), "local_path": r.get("local_path"), "url": r.get("url"), "detected_format": r.get("detected_format")} for r in rows if r.get("sha256")]
        dump("download_manifest.json", manifest)
        self.log("SUCCESS", f"Exported {len(rows)} resources to {self.out}")

    def run(self, mode, source=None):
        try:
            self.root.mkdir(parents=True, exist_ok=True); self.out.mkdir(parents=True, exist_ok=True)
            if mode == "reanalyse": self.load_21_exports(source)
            elif mode == "recover":
                self.emit("stage", name="Connecting to National CKAN", detail="Windows certificate trust store · HTTPS")
                status = self.api("status_show", timeout=20)
                if not status: raise RuntimeError("National CKAN status_show failed")
                self.log("SUCCESS", f"Connected to CKAN {status.get('ckan_version', 'version unknown')}"); self.discover()
            elif mode == "local": self.inspect_local_folder(source)
            if mode in {"reanalyse", "recover"} and not self.stop.is_set(): self.recover()
            self.export(); self.emit("done", out_dir=str(self.out), datasets=len(self.datasets), resources=len(self.resources), stats=dict(self.stats), stopped=self.stop.is_set())
        except Exception as e:
            try: self.export()
            except Exception: pass
            self.emit("fatal", message=str(e))

def default_output_dir():
    home = Path.home()
    candidates = [home / "Desktop", home / "OneDrive" / "Desktop", home / "OneDrive" / "Bureau", home / "Bureau"]
    desktop = next((p for p in candidates if p.exists()), home / "Desktop")
    return desktop / "working folder" / "MASARI_Recovery_3_4"

class App(ctk.CTk):
    def __init__(self):
        super().__init__(); ctk.set_appearance_mode("dark"); ctk.set_default_color_theme("blue")
        self.title(APP_TITLE); self.geometry("1500x920"); self.minsize(1180, 740)
        self.bg = "#0A1020"; self.panel = "#121B2E"; self.line = "#273650"; self.fg = "#F1F5FA"; self.muted = "#91A1B8"; self.cyan = "#35C8D0"; self.green = "#45D6A0"; self.orange = "#FFAA55"; self.red = "#FF687E"
        self.events = queue.Queue(); self.stop_event = threading.Event(); self.worker = None; self.engine = None; self.output_dir = default_output_dir(); self.source_dir = None
        self.search_var = ctk.StringVar(); self.category_var = ctk.StringVar(value="All")
        self.configure(fg_color=self.bg); self.grid_columnconfigure(1, weight=1); self.grid_rowconfigure(0, weight=1)
        self._style(); self._build(); self.after(150, self._poll)

    def _style(self):
        style = ttk.Style(); style.theme_use("clam")
        style.configure("Treeview", background="#0E1729", foreground=self.fg, fieldbackground="#0E1729", rowheight=28, borderwidth=0, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", background="#1A2942", foreground=self.fg, relief="flat", font=("Segoe UI Semibold", 9))
        style.map("Treeview", background=[("selected", "#23415A")], foreground=[("selected", "white")])

    def _build(self):
        side = ctk.CTkFrame(self, width=230, fg_color=self.panel, corner_radius=0)
        side.grid(row=0, column=0, sticky="nsw"); side.grid_propagate(False)
        ctk.CTkLabel(side, text="MASARI", font=("Segoe UI Semibold", 25), text_color=self.fg).pack(anchor="w", padx=22, pady=(24, 0))
        ctk.CTkLabel(side, text="RECOVERY STUDIO 3.4", font=("Segoe UI Semibold", 10), text_color=self.cyan).pack(anchor="w", padx=23, pady=(0, 26))
        self.nav = {}; self.pages = ctk.CTkFrame(self, fg_color="transparent")
        self.pages.grid(row=0, column=1, sticky="nsew", padx=22, pady=18); self.pages.grid_columnconfigure(0, weight=1); self.pages.grid_rowconfigure(0, weight=1)
        for name in ["Overview", "Resources", "Transport", "Geography", "Downloads", "Coverage", "Activity"]:
            b = ctk.CTkButton(side, text=name, anchor="w", height=38, corner_radius=8, fg_color="transparent", hover_color="#1B2A43", command=lambda n=name: self.show_page(n))
            b.pack(fill="x", padx=12, pady=3); self.nav[name] = b
        ctk.CTkLabel(side, text="PIPELINE", text_color=self.muted, font=("Segoe UI Semibold", 9)).pack(anchor="w", padx=20, pady=(26, 6))
        self.status = ctk.CTkLabel(side, text="IDLE", text_color=self.orange, font=("Segoe UI Semibold", 11)); self.status.pack(anchor="w", padx=20)
        self.start_btn = ctk.CTkButton(side, text="Start nationwide recovery", height=40, fg_color="#167C86", hover_color="#12636B", command=self.start_recovery)
        self.start_btn.pack(fill="x", padx=12, pady=(18, 6))
        self.reanalyse_btn = ctk.CTkButton(side, text="Reanalyse v2.1 exports", height=36, fg_color="#263A57", hover_color="#314B70", command=self.reanalyse)
        self.reanalyse_btn.pack(fill="x", padx=12, pady=5)
        self.local_btn = ctk.CTkButton(side, text="Inspect local files", height=36, fg_color="#263A57", hover_color="#314B70", command=self.inspect_local)
        self.local_btn.pack(fill="x", padx=12, pady=5)
        self.stop_btn = ctk.CTkButton(side, text="Stop safely", height=34, fg_color="#692D3B", hover_color="#803648", command=self.stop, state="disabled")
        self.stop_btn.pack(fill="x", padx=12, pady=5)
        self.path_label = ctk.CTkLabel(side, text=str(self.output_dir), text_color=self.muted, wraplength=190, justify="left")
        self.path_label.pack(anchor="w", padx=14, pady=(18, 3))
        ctk.CTkButton(side, text="Change output folder", height=28, fg_color="transparent", border_width=1, border_color=self.line, command=self.choose_output).pack(fill="x", padx=12, pady=3)
        self.overview = self._overview()
        self.resources_page = self._table("Resources", ["category", "dataset_title", "name", "format", "score", "host", "status"], [145, 280, 230, 100, 65, 160, 240])
        self.transport_page = self._table("Transport", ["mode", "dataset_title", "name", "format", "score", "governorates", "status"], [150, 250, 220, 100, 65, 180, 230])
        self.geography_page = self._table("Geography", ["category", "dataset_title", "name", "format", "governorates", "status"], [150, 250, 220, 100, 180, 230])
        self.downloads_page = self._table("Downloads", ["category", "name", "status", "format", "size", "path"], [150, 220, 240, 100, 90, 350])
        self.coverage_page = self._table("Coverage", ["governorate", "metadata_matches", "transport_matches", "admin_geo_resources", "verified_boundaries", "evidence"], [130, 120, 130, 150, 130, 400])
        self.activity_page = self._activity()
        self.show_page("Overview")

    def _overview(self):
        p = ctk.CTkFrame(self.pages, fg_color="transparent")
        p.grid_columnconfigure((0, 1, 2, 3, 4), weight=1); p.grid_rowconfigure(2, weight=1)
        ctk.CTkLabel(p, text="Nationwide data recovery", font=("Segoe UI Semibold", 24), text_color=self.fg).grid(row=0, column=0, columnspan=5, sticky="w", pady=(0, 4))
        ctk.CTkLabel(p, text="Discovery → recovery → validation → extraction → MASARI-ready exports", text_color=self.muted).grid(row=1, column=0, columnspan=5, sticky="w", pady=(0, 18))
        self.metrics = {}
        for i, (key, label, color) in enumerate([("datasets", "DATASETS", self.cyan), ("resources", "RESOURCES", self.cyan), ("transport", "TRANSPORT", self.green), ("downloaded", "DOWNLOADED", self.orange), ("validated", "VALIDATED", self.green)]):
            card = ctk.CTkFrame(p, fg_color=self.panel, border_width=1, border_color=self.line, corner_radius=12)
            card.grid(row=2, column=i, sticky="new", padx=4)
            ctk.CTkLabel(card, text=label, text_color=self.muted, font=("Segoe UI Semibold", 9)).pack(anchor="w", padx=12, pady=(12, 0))
            v = ctk.CTkLabel(card, text="0", font=("Segoe UI Semibold", 25), text_color=color); v.pack(anchor="w", padx=12, pady=(0, 10))
            self.metrics[key] = v
        panel = ctk.CTkFrame(p, fg_color=self.panel, border_width=1, border_color=self.line, corner_radius=12)
        panel.grid(row=3, column=0, columnspan=5, sticky="nsew", pady=16); panel.grid_columnconfigure(0, weight=1)
        self.stage = ctk.CTkLabel(panel, text="Ready", font=("Segoe UI Semibold", 17), text_color=self.cyan); self.stage.pack(anchor="w", padx=18, pady=(18, 2))
        self.detail = ctk.CTkLabel(panel, text="All 24 governorates · launch cities do not restrict collection", text_color=self.muted); self.detail.pack(anchor="w", padx=18)
        self.progress = ctk.CTkProgressBar(panel, progress_color=self.cyan); self.progress.pack(fill="x", padx=18, pady=(22, 5)); self.progress.set(0)
        self.progress_label = ctk.CTkLabel(panel, text="0%", text_color=self.muted); self.progress_label.pack(anchor="e", padx=18)
        ctk.CTkLabel(panel, text="Modes: nationwide CKAN recovery, offline reanalysis of v2.1 exports, and local-file ingestion.", text_color=self.muted, wraplength=950).pack(anchor="w", padx=18, pady=18)
        return p

    def _table(self, name, cols, widths):
        p = ctk.CTkFrame(self.pages, fg_color=self.panel, corner_radius=12, border_width=1, border_color=self.line)
        p.grid_columnconfigure(0, weight=1); p.grid_rowconfigure(1, weight=1)
        bar = ctk.CTkFrame(p, fg_color="transparent"); bar.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        ctk.CTkEntry(bar, textvariable=self.search_var, placeholder_text="Filter visible records…", width=270).pack(side="left")
        if name == "Resources":
            ctk.CTkOptionMenu(bar, variable=self.category_var, values=["All", "Transport", "Administrative geography", "Useful geography", "Other"], command=lambda _: self.refresh()).pack(side="left", padx=8)
        tree = ttk.Treeview(p, columns=cols, show="headings")
        for col, w in zip(cols, widths):
            tree.heading(col, text=col.replace("_", " ").title())
            tree.column(col, width=w, minwidth=60, anchor="w")
        tree.grid(row=1, column=0, sticky="nsew", padx=(10, 0), pady=(0, 10))
        sc = ttk.Scrollbar(p, orient="vertical", command=tree.yview)
        sc.grid(row=1, column=1, sticky="ns", padx=(0, 10), pady=(0, 10))
        tree.configure(yscrollcommand=sc.set)
        return p, tree

    def _activity(self):
        p = ctk.CTkFrame(self.pages, fg_color=self.panel, corner_radius=12)
        p.grid_columnconfigure(0, weight=1); p.grid_rowconfigure(0, weight=1)
        self.logbox = ctk.CTkTextbox(p, fg_color="#0D1628", text_color="#D0D9E6", font=("Cascadia Code", 10))
        self.logbox.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        return p

    def show_page(self, name):
        for w in self.pages.winfo_children(): w.grid_forget()
        page = {"Overview": self.overview, "Resources": self.resources_page[0], "Transport": self.transport_page[0], "Geography": self.geography_page[0], "Downloads": self.downloads_page[0], "Coverage": self.coverage_page[0], "Activity": self.activity_page}[name]
        page.grid(row=0, column=0, sticky="nsew")
        for k, b in self.nav.items(): b.configure(fg_color="#1B2A43" if k == name else "transparent")

    def choose_output(self):
        x = filedialog.askdirectory(initialdir=str(self.output_dir))
        if x: self.output_dir = Path(x); self.path_label.configure(text=str(x))

    def _launch(self, mode, source=None):
        if self.worker and self.worker.is_alive(): return
        self.stop_event.clear(); self.progress.set(0); self.status.configure(text="RUNNING", text_color=self.green)
        for b in [self.start_btn, self.reanalyse_btn, self.local_btn]: b.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.engine = RecoveryEngine(self.output_dir, self.events, self.stop_event)
        self.worker = threading.Thread(target=self.engine.run, args=(mode, source), daemon=True)
        self.worker.start(); self.show_page("Overview")

    def start_recovery(self): self._launch("recover")
    def reanalyse(self):
        folder = filedialog.askdirectory(title="Select MASARI 2.1 export folder (contains resources.json)")
        if folder: self._launch("reanalyse", folder)
    def inspect_local(self):
        folder = filedialog.askdirectory(title="Select folder containing files to inspect")
        if folder: self._launch("local", folder)
    def stop(self):
        self.stop_event.set(); self.status.configure(text="STOPPING", text_color=self.orange); self.stage.configure(text="Stopping safely…")
    def log(self, level, msg):
        self.logbox.insert("end", f"[{datetime.now():%H:%M:%S}] [{level}] {msg}\n"); self.logbox.see("end")

    def _poll(self):
        try:
            while True:
                e = self.events.get_nowait(); k = e.get("kind")
                if k == "log": self.log(e.get("level", "INFO"), e.get("message", ""))
                elif k == "stage": self.stage.configure(text=e.get("name", "Working")); self.detail.configure(text=e.get("detail", ""))
                elif k == "progress":
                    v = max(0, min(100, float(e.get("value", 0))))
                    self.progress.set(v / 100); self.progress_label.configure(text=f"{v:.0f}% · {e.get('detail', '')}")
                elif k == "metrics":
                    counts = e.get("counts", {})
                    self.metrics["datasets"].configure(text=str(e.get("datasets", 0)))
                    self.metrics["resources"].configure(text=str(e.get("resources", 0)))
                    self.metrics["transport"].configure(text=str(counts.get("Transport", 0)))
                elif k == "done": self.finish(e)
                elif k == "fatal":
                    self.log("ERROR", e.get("message", "Unknown error"))
                    self.status.configure(text="ERROR", text_color=self.red)
                    self._unlock()
        except queue.Empty: pass
        self.after(150, self._poll)

    def _unlock(self):
        for b in [self.start_btn, self.reanalyse_btn, self.local_btn]: b.configure(state="normal")
        self.stop_btn.configure(state="disabled")

    def finish(self, e):
        self.status.configure(text="STOPPED · SAVED" if e.get("stopped") else "COMPLETE", text_color=self.orange if e.get("stopped") else self.green)
        self.stage.configure(text="Export complete"); self.detail.configure(text=f"Output: {e.get('out_dir')}")
        self.progress.set(1); self.progress_label.configure(text="100% · Saved")
        self.log("SUCCESS", f"{e.get('datasets')} datasets · {e.get('resources')} resources · {e.get('out_dir')}")
        self.refresh(); self._unlock()

    def refresh(self):
        if not self.engine: return
        needle = norm(self.search_var.get()); rs = list(self.engine.resources.values())
        for _, tree in [self.resources_page, self.transport_page, self.geography_page, self.downloads_page, self.coverage_page]:
            for item in tree.get_children(): tree.delete(item)
        for r in rs:
            searchable = norm(" ".join(str(r.get(k, "")) for k in ["dataset_title", "name", "description", "host", "mode", "category", "relative_path"]))
            if needle and needle not in searchable: continue
            cat = r.get("category", "Other"); gov = ", ".join(r.get("governorates") or []); fmt = r.get("detected_format") or r.get("format", ""); status = r.get("validation_status") or r.get("download_status", "")
            if self.category_var.get() in {"All", cat}: self.resources_page[1].insert("", "end", values=(cat, r.get("dataset_title"), r.get("name"), fmt, r.get("relevance_score"), r.get("host"), status))
            if cat == "Transport": self.transport_page[1].insert("", "end", values=(r.get("mode"), r.get("dataset_title"), r.get("name"), fmt, r.get("relevance_score"), gov, status))
            if cat in {"Administrative geography", "Useful geography"}: self.geography_page[1].insert("", "end", values=(cat, r.get("dataset_title"), r.get("name"), fmt, gov, status))
            if r.get("download_status") not in {None, "Not attempted"}:
                self.downloads_page[1].insert("", "end", values=(cat, r.get("name"), r.get("download_status"), fmt, f"{r.get('bytes_downloaded', 0)/1024:.1f} KB" if r.get("bytes_downloaded") else "—", r.get("local_path", "")))
        for gov, row in self.engine.coverage_report()["governorates"].items():
            self.coverage_page[1].insert("", "end", values=(gov, row["metadata_matches"], row["transport_metadata_matches"], row["administrative_geography_resources"], row["verified_boundary_assets"], row["evidence"]))
if __name__ == "__main__":
    App().mainloop()

