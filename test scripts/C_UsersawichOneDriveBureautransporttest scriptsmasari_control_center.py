"""
MASARI 3.6 - All-in-One Interactive GUI & Migration Control Center
Integrates SQLite-to-MySQL 8.0 migration, database connection manager,
and real-time transit route/stop explorer with full GUI experience.
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sqlite3
import pymysql
from pathlib import Path
import threading

DEFAULT_SQLITE_PATH = r"C:\Users\awich\OneDrive\Bureau\working folder\MASARI_Recovery_3_6\run_20261115_023158\tunisia_mobility.db"

class MasariApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MASARI 3.6 - Transit Data Control Center (MySQL 8.0)")
        self.root.geometry("950x700")
        self.root.minsize(800, 600)

        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Main Layout Notebook (Tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tab 1: Connection & Overview
        self.tab_conn = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_conn, text="🗄️ Connexion & Stats")
        self.build_connection_tab()

        # Tab 2: Migration Wizard
        self.tab_mig = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_mig, text="⚡ Assistant de Migration")
        self.build_migration_tab()

        # Tab 3: Route & Stop Explorer
        self.tab_exp = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_exp, text="🗺️ Explorateur de Lignes")
        self.build_explorer_tab()

    def get_mysql_config(self):
        return {
            "host": self.host_entry.get().strip(),
            "user": self.user_entry.get().strip(),
            "password": self.pass_entry.get().strip(),
            "database": self.db_entry.get().strip(),
            "charset": "utf8mb4",
            "cursorclass": pymysql.cursors.DictCursor
        }

    def build_connection_tab(self):
        # Configuration Frame
        cfg_frame = ttk.LabelFrame(self.tab_conn, text=" Paramètres de Connexion MySQL 8.0 ", padding=15)
        cfg_frame.pack(fill=tk.X, padx=10, pady=10)

        fields = [
            ("Hôte (Host):", "localhost", 0, 0),
            ("Utilisateur (User):", "root", 0, 2),
            ("Mot de passe:", "Awichi@33", 1, 0),
            ("Base de données:", "masari_mobility", 1, 2)
        ]

        self.host_entry = ttk.Entry(cfg_frame, width=20)
        self.host_entry.insert(0, "localhost")
        self.user_entry = ttk.Entry(cfg_frame, width=20)
        self.user_entry.insert(0, "root")
        self.pass_entry = ttk.Entry(cfg_frame, width=20, show="*")
        self.pass_entry.insert(0, "Awichi@33")
        self.db_entry = ttk.Entry(cfg_frame, width=20)
        self.db_entry.insert(0, "masari_mobility")

        widgets = [self.host_entry, self.user_entry, self.pass_entry, self.db_entry]
        positions = [(0, 1), (0, 3), (1, 1), (1, 3)]

        for idx, (label_text, _, _) in enumerate(fields):
            r, c = positions[idx]
            ttk.Label(cfg_frame, text=label_text).grid(row=r, column=c, sticky=tk.W, padx=5, pady=5)
            widgets[idx].grid(row=r, column=c+1, sticky=tk.W, padx=5, pady=5)

        btn_test = ttk.Button(cfg_frame, text="Tester la Connexion & Charger Stats", command=self.test_connection)
        btn_test.grid(row=2, column=0, columnspan=4, pady=15, sticky=tk.EW)

        # Stats Display Frame
        stats_frame = ttk.LabelFrame(self.tab_conn, text=" Statistiques de la Base MySQL ", padding=15)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.lbl_stops = ttk.Label(stats_frame, text="Arrêts enregistrés : -", font=("Segoe UI", 11, "bold"))
        self.lbl_stops.pack(anchor=tk.W, pady=5)

        self.lbl_routes = ttk.Label(stats_frame, text="Lignes de transport : -", font=("Segoe UI", 11, "bold"))
        self.lbl_routes.pack(anchor=tk.W, pady=5)

        self.lbl_relations = ttk.Label(stats_frame, text="Relations route_stops : -", font=("Segoe UI", 11, "bold"))
        self.lbl_relations.pack(anchor=tk.W, pady=5)

    def test_connection(self):
        try:
            config = self.get_mysql_config()
            conn = pymysql.connect(**config)
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) AS cnt FROM stops_registry;")
                stops = cursor.fetchone()["cnt"]
                cursor.execute("SELECT COUNT(*) AS cnt FROM routes_registry;")
                routes = cursor.fetchone()["cnt"]
                cursor.execute("SELECT COUNT(*) AS cnt FROM route_stops;")
                relations = cursor.fetchone()["cnt"]
            conn.close()

            self.lbl_stops.config(text=f"Arrêts enregistrés : {stops}")
            self.lbl_routes.config(text=f"Lignes de transport : {routes}")
            self.lbl_relations.config(text=f"Relations route_stops : {relations}")
            messagebox.showinfo("Succès", "Connexion à MySQL réussie et statistiques mises à jour !")
        except Exception as e:
            messagebox.showerror("Erreur de Connexion", f"Impossible de se connecter à MySQL :
{e}")

    def build_migration_tab(self):
        mig_frame = ttk.LabelFrame(self.tab_mig, text=" Migration Automatisée SQLite -> MySQL ", padding=15)
        mig_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(mig_frame, text="Chemin de la base SQLite source :").pack(anchor=tk.W, pady=2)
        
        path_frame = ttk.Frame(mig_frame)
        path_frame.pack(fill=tk.X, pady=5)
        
        self.sqlite_path_entry = ttk.Entry(path_frame, width=70)
        self.sqlite_path_entry.insert(0, DEFAULT_SQLITE_PATH)
        self.sqlite_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        btn_run_mig = ttk.Button(mig_frame, text="Lancer la Migration Complète (Arrêts + Lignes + Relations)", command=self.run_full_migration)
        btn_run_mig.pack(fill=tk.X, pady=15)

        ttk.Label(mig_frame, text="Journal d'exécution en direct :").pack(anchor=tk.W, pady=2)
        
        self.log_text = scrolledtext.ScrolledText(mig_frame, height=15, font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=5)

    def log_message(self, msg):
        self.log_text.insert(tk.END, msg + "
")
        self.log_text.see(tk.END)

    def run_full_migration(self):
        sqlite_file = Path(self.sqlite_path_entry.get().strip())
        if not sqlite_file.exists():
            messagebox.showerror("Erreur", f"Fichier SQLite introuvable :
{sqlite_file}")
            return

        self.log_text.delete("1.0", tk.END)
        self.log_message("[INFO] Démarrage de la migration globale...")

        # Run in thread to keep GUI responsive
        threading.Thread(target=self._execute_migration_thread, args=(sqlite_file,), daemon=True).start()

    def _execute_migration_thread(self, sqlite_file):
        try:
            config = self.get_mysql_config()
            s_conn = sqlite3.connect(sqlite_file)
            s_conn.row_factory = sqlite3.Row
            s_cur = s_conn.cursor()

            m_conn = pymysql.connect(**config)
            m_cur = m_conn.cursor()

            # 1. Stops
            self.log_message("[INFO] Migration des arrêts (stops_registry)...")
            s_cur.execute("SELECT stop_id, name_fr, governorate, lat, lon FROM stops_registry")
            stops = s_cur.fetchall()
            stops_count = 0
            for row in stops:
                m_cur.execute("""
                    INSERT IGNORE INTO stops_registry (stop_id, name_fr, governorate, lat, lon)
                    VALUES (%s, %s, %s, %s, %s)
                """, (row["stop_id"], row["name_fr"], row["governorate"], row["lat"], row["lon"]))
                stops_count += m_cur.rowcount
            m_conn.commit()
            self.log_message(f" -> Arrêts insérés : {stops_count}")

            # 2. Routes
            self.log_message("[INFO] Migration des lignes (routes_registry)...")
            s_cur.execute("SELECT route_id, route_name, route_type, operator FROM routes_registry")
            routes = s_cur.fetchall()
            routes_count = 0
            for row in routes:
                m_cur.execute("""
                    INSERT IGNORE INTO routes_registry (route_id, route_name, route_type, operator)
                    VALUES (%s, %s, %s, %s)
                """, (row["route_id"], row["route_name"], row["route_type"], row["operator"]))
                routes_count += m_cur.rowcount
            m_conn.commit()
            self.log_message(f" -> Lignes insérées : {routes_count}")

            # 3. Route Stops
            self.log_message("[INFO] Migration des relations (route_stops)...")
            s_cur.execute("SELECT route_id, stop_id, sequence_order FROM route_stops")
            relations = s_cur.fetchall()
            rel_count = 0
            for row in relations:
                m_cur.execute("""
                    INSERT IGNORE INTO route_stops (route_id, stop_id, sequence_order)
                    VALUES (%s, %s, %s)
                """, (row["route_id"], row["stop_id"], row["sequence_order"]))
                rel_count += m_cur.rowcount
            m_conn.commit()
            self.log_message(f" -> Relations insérées : {rel_count}")

            s_cur.close()
            s_conn.close()
            m_cur.close()
            m_conn.close()

            self.log_message("
[SUCCÈS] Migration globale terminée avec succès !")
            messagebox.showinfo("Succès", "La migration complète a été exécutée avec succès !")
        except Exception as e:
            self.log_message(f"[ERREUR] {e}")
            messagebox.showerror("Erreur de Migration", str(e))

    def build_explorer_tab(self):
        exp_frame = ttk.LabelFrame(self.tab_exp, text=" Recherche et Exploration des Lignes et Arrêts ", padding=15)
        exp_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        search_frame = ttk.Frame(exp_frame)
        search_frame.pack(fill=tk.X, pady=5)

        ttk.Label(search_frame, text="Rechercher une ligne (ex: خط 1, Métro):").pack(side=tk.LEFT, padx=(0, 10))
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.insert(0, "خط 1")
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))

        btn_search = ttk.Button(search_frame, text="Rechercher les Arrêts", command=self.search_route_stops)
        btn_search.pack(side=tk.LEFT)

        # Treeview for Stops
        tree_frame = ttk.Frame(exp_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        columns = ("seq", "stop_id", "name_fr", "governorate", "lat", "lon")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("seq", text="Ordre")
        self.tree.heading("stop_id", text="ID Arrêt")
        self.tree.heading("name_fr", text="Nom de l'Arrêt")
        self.tree.heading("governorate", text="Gouvernorat")
        self.tree.heading("lat", text="Latitude")
        self.tree.heading("lon", text="Longitude")

        self.tree.column("seq", width=60, anchor=tk.CENTER)
        self.tree.column("stop_id", width=120, anchor=tk.W)
        self.tree.column("name_fr", width=250, anchor=tk.W)
        self.tree.column("governorate", width=120, anchor=tk.W)
        self.tree.column("lat", width=100, anchor=tk.CENTER)
        self.tree.column("lon", width=100, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.lbl_route_info = ttk.Label(exp_frame, text="Sélectionnez une ligne pour afficher ses arrêts ordonnés.", font=("Segoe UI", 10, "italic"))
        self.lbl_route_info.pack(anchor=tk.W, pady=5)

    def search_route_stops(self):
        term = self.search_entry.get().strip()
        if not term:
            messagebox.showwarning("Attention", "Veuillez entrer un terme de recherche.")
            return

        for row in self.tree.get_children():
            self.tree.delete(row)

        try:
            config = self.get_mysql_config()
            conn = pymysql.connect(**config)
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT route_id, route_name, route_type, operator 
                    FROM routes_registry 
                    WHERE route_name LIKE %s LIMIT 1;
                """, (f"%{term}%",))
                route = cursor.fetchone()

                if not route:
                    self.lbl_route_info.config(text=f"Aucune ligne trouvée pour : '{term}'")
                    conn.close()
                    return

                self.lbl_route_info.config(text=f"Ligne : {route['route_name']} | Type : {route['route_type']} | Opérateur : {route['operator']}")

                cursor.execute("""
                    SELECT rs.sequence_order, s.stop_id, s.name_fr, s.governorate, s.lat, s.lon
                    FROM route_stops rs
                    JOIN stops_registry s ON rs.stop_id = s.stop_id
                    WHERE rs.route_id = %s
                    ORDER BY rs.sequence_order ASC;
                """, (route['route_id'],))
                stops = cursor.fetchall()

                for s in stops:
                    self.tree.insert("", tk.END, values=(
                        s["sequence_order"],
                        s["stop_id"],
                        s["name_fr"] or "N/A",
                        s["governorate"] or "N/A",
                        f"{s['lat']:.6f}" if s['lat'] else "N/A",
                        f"{s['lon']:.6f}" if s['lon'] else "N/A"
                    ))
            conn.close()
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec de la recherche :
{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MasariApp(root)
    root.mainloop()
