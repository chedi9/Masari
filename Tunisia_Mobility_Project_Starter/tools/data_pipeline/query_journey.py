"""
Journey Query Engine — Tunisia Mobility Platform
Queries real scheduled journeys between stations from data/processed/tunisia_mobility.db.
Provides exact stops, timetables, duration, and millimes fares.
"""

import sqlite3
import os
import sys

def parse_time_minutes(t_str: str) -> int:
    parts = t_str.split(':')
    return int(parts[0]) * 60 + int(parts[1])

def format_minutes(mins: int) -> str:
    h = mins // 60
    m = mins % 60
    if h > 0:
        return f"{h}h {m:02d}min"
    return f"{m} min"

def find_journeys(origin_query: str, dest_query: str, db_path: str = None, limit: int = 5):
    if db_path is None:
        db_path = os.path.join("data", "processed", "tunisia_mobility.db")
        
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}. Run sncft_importer.py first.")
        return []

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # 1. Resolve Origin Stop
    cur.execute("SELECT stop_id, stop_name, stop_lat, stop_lon FROM stops WHERE stop_name LIKE ? LIMIT 1", (f"%{origin_query}%",))
    origin = cur.fetchone()
    if not origin:
        print(f"Origin stop matching '{origin_query}' not found.")
        conn.close()
        return []

    # 2. Resolve Destination Stop
    cur.execute("SELECT stop_id, stop_name, stop_lat, stop_lon FROM stops WHERE stop_name LIKE ? LIMIT 1", (f"%{dest_query}%",))
    dest = cur.fetchone()
    if not dest:
        print(f"Destination stop matching '{dest_query}' not found.")
        conn.close()
        return []

    print(f"\n=======================================================")
    print(f"🔍 ITINÉRAIRE RECHERCHÉ : {origin['stop_name']} ➔ {dest['stop_name']}")
    print(f"   Origine : {origin['stop_name']} (GPS: {origin['stop_lat']:.4f}, {origin['stop_lon']:.4f})")
    print(f"   Destination : {dest['stop_name']} (GPS: {dest['stop_lat']:.4f}, {dest['stop_lon']:.4f})")
    print(f"=======================================================\n")

    # 3. Find trips serving both origin and destination where origin sequence < destination sequence
    query = """
    SELECT 
        r.route_id,
        r.route_short_name,
        r.route_long_name,
        a.agency_name,
        t.trip_id,
        st_orig.departure_time AS dep_time,
        st_dest.arrival_time AS arr_time,
        st_orig.stop_sequence AS orig_seq,
        st_dest.stop_sequence AS dest_seq
    FROM stop_times st_orig
    JOIN stop_times st_dest ON st_orig.trip_id = st_dest.trip_id
    JOIN trips t ON t.trip_id = st_orig.trip_id
    JOIN routes r ON r.route_id = t.route_id
    JOIN agencies a ON a.agency_id = r.agency_id
    WHERE st_orig.stop_id = ? 
      AND st_dest.stop_id = ?
      AND st_orig.stop_sequence < st_dest.stop_sequence
    ORDER BY st_orig.departure_time ASC
    LIMIT ?
    """

    cur.execute(query, (origin['stop_id'], dest['stop_id'], limit))
    trips = cur.fetchall()

    if not trips:
        print(f"Aucun trajet direct trouvé entre {origin['stop_name']} et {dest['stop_name']}.")
        conn.close()
        return []

    # 4. Lookup Fare if available
    fare_info = None
    cur.execute("""
        SELECT fa.price_tnd, fa.price_millimes
        FROM fare_rules fr
        JOIN fare_attributes fa ON fa.fare_id = fr.fare_id
        WHERE fr.route_id = ?
        LIMIT 1
    """, (trips[0]['route_id'],))
    fare_row = cur.fetchone()
    if fare_row:
        fare_info = f"{fare_row['price_millimes']} millimes ({fare_row['price_tnd']:.3f} TND)"
    else:
        fare_info = "Tarif indicatif par zone (SNCFT)"

    results = []
    print(f"Trouvé {len(trips)} départs directs :\n")

    for idx, trip in enumerate(trips, 1):
        dep_m = parse_time_minutes(trip['dep_time'])
        arr_m = parse_time_minutes(trip['arr_time'])
        duration = arr_m - dep_m
        if duration < 0:
            duration += 24 * 60 # midnight rollover

        # Fetch intermediate stops
        cur.execute("""
            SELECT s.stop_name, st.arrival_time
            FROM stop_times st
            JOIN stops s ON s.stop_id = st.stop_id
            WHERE st.trip_id = ? AND st.stop_sequence BETWEEN ? AND ?
            ORDER BY st.stop_sequence ASC
        """, (trip['trip_id'], trip['orig_seq'], trip['dest_seq']))
        intermediate = cur.fetchall()
        stop_count = len(intermediate) - 1

        print(f"Option #{idx} [{trip['agency_name']}]")
        print(f"  Ligne       : {trip['route_short_name']} ({trip['route_long_name']})")
        print(f"  Départ      : {trip['dep_time'][:5]} ➔ Arrivée : {trip['arr_time'][:5]} (Durée : {format_minutes(duration)})")
        print(f"  Arrêts      : {stop_count} arrêts")
        print(f"  Tarif       : {fare_info}")
        print(f"  Itinéraire  : {' ➔ '.join([s['stop_name'] for s in intermediate])}")
        print("-" * 55)

        results.append({
            "trip_id": trip['trip_id'],
            "agency": trip['agency_name'],
            "route": f"{trip['route_short_name']} - {trip['route_long_name']}",
            "departure": trip['dep_time'][:5],
            "arrival": trip['arr_time'][:5],
            "duration_minutes": duration,
            "stops": [s['stop_name'] for s in intermediate],
            "fare": fare_info
        })

    conn.close()
    return results

if __name__ == '__main__':
    orig = sys.argv[1] if len(sys.argv) > 1 else "Tunis Ville"
    dest = sys.argv[2] if len(sys.argv) > 2 else "Borj Cedria"
    database = sys.argv[3] if len(sys.argv) > 3 else None
    find_journeys(orig, dest, db_path=database)
