"""
MASARI 3.6 - Transit Data Control Center (MySQL 8.0)
Complete Self-Healing GUI with Live SQLite Fallback for Route Exploration.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import pymysql
import sqlite3
from pathlib import Path

# MySQL Configuration
MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Awichi@33",
    "database": "masari_mobility",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor
}

# Path to original SQLite database for live fallback lookup
SQLITE_DB_PATH = Path(r"C:\Users\awich\OneDrive\Bureau\working folder\MASARI_Recovery_3_6\run_20261115_023158\tunisia_mobility.db")

class MasariControlCenter(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MASARI 3.6 - Transit Data Control Center (MySQL 8.0)")
        self.geometry("950x650")
        self.minsize(800, 550)

        # Apply Modern Styling
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Create Notebook (Tabs)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Initialize Tabs
        self.init_connection_tab()
        self.init_explorer_tab()

        # Initial Connection Check
        self.check_db_connection()

    def get_db_connection(self):
        return pymysql.connect(**MYSQL_CONFIG)

    # ==========================================
    # TAB 1: CONNECTION & STATS
    # ==========================================
    def init_connection_tab(self):
        self.tab_conn = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_conn, text=" Connexion & Stats ")

        lbl_title = ttk.Label(self.tab_conn, text="État de la Base de Données MySQL 8.0", font=("Arial", 14, "bold"))
        lbl_title.pack(pady=15)

        self.lbl_status = ttk.Label(self.tab_conn, text="Vérification de la connexion...", font=("Arial", 11))
        self.lbl_status.pack(pady=5)

        # Stats Frame
        self.frame_stats = ttk.LabelFrame(self.tab_conn, text=" Statistiques des Tables ")
        self.frame_stats.pack(fill="both", expand=True, padx=20, pady=15)

        self.txt_stats = tk.Text(self.frame_stats, font=("Consolas", 10), bg="#f8f9fa", fg="#333333")
        self.txt_stats.pack(fill="both", expand=True, padx=10, pady=10)

        btn_refresh = ttk.Button(self.tab_conn, text="Actualiser les Statistiques", command=self.check_db_connection)
        btn_refresh.pack(pady=10)

    def check_db_connection(self):
        try:
            conn = self.get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT VERSION() AS version;")
                ver = cursor.fetchone()["version"]
                
                tables = ["stops_registry", "routes_registry", "route_stops", "trips", "stop_times", "calendar"]
                stats_text = f"Connecté avec succès à MySQL {ver}\nBase de données : masari_mobility\n\n"
                for t in tables:
                    cursor.execute(f"SELECT COUNT(*) AS cnt FROM `{t}`;")
                    cnt = cursor.fetchone()["cnt"]
                    stats_text += f" - Table `{t}` : {cnt} enregistrements\n"

            self.lbl_status.config(text="[OK] Connexion active et stable", foreground="green")
            self.txt_stats.delete("1.0", tk.END)
            self.txt_stats.insert(tk.END, stats_text)
            conn.close()
        except Exception as e:
            self.lbl_status.config(text=f"[ERREUR] Échec de connexion : {e}", foreground="red")
            self.txt_stats.delete("1.0", tk.END)
            self.txt_stats.insert(tk.END, f"Impossible de se connecter à MySQL :\n{e}")

    # ==========================================
    # TAB 2: ROUTE & STOP EXPLORER
    # ==========================================
    def init_explorer_tab(self):
        self.tab_explorer = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_explorer, text=" Explorateur de Lignes ")

        # Search Frame
        frame_search = ttk.LabelFrame(self.tab_explorer, text=" Recherche et Exploration des Lignes et Arrêts ")
        frame_search.pack(fill="x", padx=15, pady=10)

        lbl_search = ttk.Label(frame_search, text="Rechercher une ligne (ex: 1, 4, خط):")
        lbl_search.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.ent_search = ttk.Entry(frame_search, width=30, font=("Arial", 11))
        self.ent_search.grid(row=0, column=1, padx=5, pady=10)
        self.ent_search.insert(0, "1")
        self.ent_search.bind("<Return>", lambda event: self.search_route_stops())

        btn_search = ttk.Button(frame_search, text="Rechercher les Arrêts", command=self.search_route_stops)
        btn_search.grid(row=0, column=2, padx=10, pady=10)

        # Results Treeview Table
        frame_table = ttk.Frame(self.tab_explorer)
        frame_table.pack(fill="both", expand=True, padx=15, pady=5)

        columns = ("sequence", "stop_id", "name_fr", "governorate", "lat", "lon")
        self.tree = ttk.Treeview(frame_table, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("sequence", text="Ordre")
        self.tree.heading("stop_id", text="ID Arrêt / OSM")
        self.tree.heading("name_fr", text="Nom de l'Arrêt")
        self.tree.heading("governorate", text="Gouvernorat")
        self.tree.heading("lat", text="Latitude")
        self.tree.heading("lon", text="Longitude")

        self.tree.column("sequence", width=60, anchor="center")
        self.tree.column("stop_id", width=140, anchor="w")
        self.tree.column("name_fr", width=260, anchor="w")
        self.tree.column("governorate", width=110, anchor="center")
        self.tree.column("lat", width=100, anchor="center")
        self.tree.column("lon", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Status Bar Info for Route
        self.lbl_route_info = ttk.Label(self.tab_explorer, text="Prêt pour la recherche.", font=("Arial", 10, "italic"))
        self.lbl_route_info.pack(fill="x", padx=15, pady=10)

    def fetch_sqlite_stop_details(self, stop_id):
        """Live fallback: query SQLite database directly if MySQL lacks stop details."""
        if not SQLITE_DB_PATH.exists():
            return None, None, None, None
        try:
            s_conn = sqlite3.connect(SQLITE_DB_PATH)
            s_conn.row_factory = sqlite3.Row
            s_cur = s_conn.cursor()
            
            # Check stops_registry in SQLite
            s_cur.execute("SELECT name_fr, governorate, lat, lon FROM stops_registry WHERE stop_id = ?", (stop_id,))
            row = s_cur.fetchone()
            s_conn.close()
            
            if row:
                return row["name_fr"], row["governorate"], row["lat"], row["lon"]
        except Exception:
            pass
        return None, None, None, None

    def search_route_stops(self):
        query_term = self.ent_search.get().strip()
        if not query_term:
            messagebox.showwarning("Attention", "Veuillez entrer un terme de recherche.")
            return

        # Clear previous results
        for row in self.tree.get_children():
            self.tree.delete(row)

        try:
            conn = self.get_db_connection()
            with conn.cursor() as cursor:
                # 1. Find matching route
                sql_route = """
                    SELECT r.route_id, r.route_name, r.route_type, r.operator
                    FROM routes_registry r
                    WHERE r.route_name LIKE %s OR r.route_id LIKE %s
                    LIMIT 1;
                """
                cursor.execute(sql_route, (f"%{query_term}%", f"%{query_term}%"))
                route = cursor.fetchone()

                if not route:
                    self.lbl_route_info.config(text=f"Aucune ligne trouvée pour : '{query_term}'")
                    conn.close()
                    return

                r_id = route["route_id"]
                r_name = route["route_name"]
                r_type = route["route_type"]
                r_op = route.get("operator", "Inconnu")

                self.lbl_route_info.config(text=f"Ligne : {r_name} | Type : {r_type} | Opérateur : {r_op}")

                # 2. Fetch ordered stops from MySQL
                sql_stops = """
                    SELECT rs.sequence_order, rs.stop_id, s.name_fr, s.governorate, s.lat, s.lon
                    FROM route_stops rs
                    LEFT JOIN stops_registry s ON rs.stop_id = s.stop_id
                    WHERE rs.route_id = %s
                    ORDER BY rs.sequence_order ASC;
                """
                cursor.execute(sql_stops, (r_id,))
                stops = cursor.fetchall()

                for s in stops:
                    stop_name = s["name_fr"]
                    governorate = s["governorate"]
                    lat = s["lat"]
                    lon = s["lon"]

                    # Self-healing fallback: if missing in MySQL, query SQLite live
                    if not stop_name or lat is None or lon is None or float(lat or 0) == 0.0:
                        sq_name, sq_gov, sq_lat, sq_lon = self.fetch_sqlite_stop_details(s["stop_id"])
                        if sq_name:
                            stop_name = sq_name
                        if sq_gov:
                            governorate = sq_gov
                        if sq_lat is not None:
                            lat = sq_lat
                        if sq_lon is not None:
                            lon = sq_lon

                    # Final display formatting
                    final_name = stop_name if stop_name else f"OSM Stop {s['stop_id']}"
                    final_gov = governorate if governorate else "Tunis"
                    lat_val = f"{lat:.6f}" if lat is not None and float(lat) != 0.0 else "N/A"
                    lon_val = f"{lon:.6f}" if lon is not None and float(lon) != 0.0 else "N/A"

                    self.tree.insert("", "end", values=(
                        s["sequence_order"],
                        s["stop_id"],
                        final_name,
                        final_gov,
                        lat_val,
                        lon_val
                    ))

                if not stops:
                    messagebox.showinfo("Information", f"La ligne '{r_name}' n'a aucun arrêt enregistré.")

            conn.close()
        except Exception as e:
            messagebox.showerror("Erreur de Base de Données", f"Une erreur est survenue :\n{e}")

if __name__ == "__main__":
    app = MasariControlCenter()
    app.mainloop()