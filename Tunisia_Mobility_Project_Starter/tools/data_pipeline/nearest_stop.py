import math

def haversine_distance_meters(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi/2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2.0)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def walking_time_minutes(distance_meters, speed_kmh=4.5):
    speed_mps = (speed_kmh * 1000) / 3600
    return int(round((distance_meters / speed_mps) / 60))

def find_nearest_stops(passenger_lat, passenger_lon, limit=3):
    import sqlite3, os
    db_path = os.path.join("data", "processed", "unified_stops_fts.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT stop_name, agency_name, mode, lat, lon FROM stops_master")
    stops = cur.fetchall()
    conn.close()

    ranked = []
    for s in stops:
        dist_m = haversine_distance_meters(passenger_lat, passenger_lon, s[3], s[4])
        mins = walking_time_minutes(dist_m)
        ranked.append({
            "stop_name": s[0],
            "agency": s[1],
            "mode": s[2],
            "distance_m": int(dist_m),
            "walk_min": mins,
            "coords": (s[3], s[4])
        })

    ranked.sort(key=lambda x: x["distance_m"])
    return ranked[:limit]

if __name__ == '__main__':
    # Test passenger location: Avenue Habib Bourguiba, Tunis (36.8000, 10.1860)
    print("\n📍 PASSENGER GPS : 36.8000, 10.1860 (Av. Habib Bourguiba, Tunis)")
    print("=" * 60)
    nearest = find_nearest_stops(36.8000, 10.1860, limit=3)
    for i, n in enumerate(nearest, 1):
        print(f"#{i} Closest Station: {n['stop_name']}")
        print(f"   Network : {n['agency']} ({n['mode']})")
        print(f"   Walk    : {n['walk_min']} min walk ({n['distance_m']} meters)")
        print("-" * 60)
