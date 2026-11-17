import React, { useState, useMemo } from 'react';
import { 
  MapPin, Bus, Train, Search, Filter, Layers, Navigation, 
  BarChart2, ShieldCheck, Database, RefreshCw, ChevronRight, 
  Globe, Compass, AlertCircle, CheckCircle2 
} from 'lucide-react';

// Sample dataset reflecting the 287 recovered stops and governorates in Tunisia
const INITIAL_STOPS = [
  { id: "stop_001", name_ar: "محطة تونس البحرية", name_fr: "Gare Marine de Tunis", type: "GTFS_STOP", governorate: "Tunis", lon: 10.1815, lat: 36.8065, status: "OFFICIAL_GTFS" },
  { id: "stop_002", name_ar: "محطة الحبيب ثامر", name_fr: "Station Habib Thameur", type: "METRO_STATION", governorate: "Tunis", lon: 10.1850, lat: 36.8010, status: "VERIFIED_GEO" },
  { id: "stop_003", name_ar: "ساحة برشلونة", name_fr: "Place de Barcelone", type: "INTERCHANGE", governorate: "Tunis", lon: 10.1790, lat: 36.7985, status: "OFFICIAL_GTFS" },
  { id: "stop_004", name_ar: "باب سعدون", name_fr: "Bab Saadoun", type: "BUS_TERMINAL", governorate: "Tunis", lon: 10.1650, lat: 36.8120, status: "VERIFIED_GEO" },
  { id: "stop_005", name_ar: "أريانة المدينة", name_fr: "Ariana Ville", type: "METRO_STATION", governorate: "Ariana", lon: 10.1934, lat: 36.8625, status: "VERIFIED_GEO" },
  { id: "stop_006", name_ar: "النحلي", name_fr: "Ennahli", type: "BUS_STOP", governorate: "Ariana", lon: 10.1500, lat: 36.8850, status: "VERIFIED_GEO" },
  { id: "stop_007", name_ar: "بن عروس المركز", name_fr: "Ben Arous Centre", type: "TRAIN_STATION", governorate: "Ben Arous", lon: 10.2189, lat: 36.7531, status: "VERIFIED_GEO" },
  { id: "stop_008", name_ar: "رادس التدريب", name_fr: "Rades Plage", type: "TRAIN_STATION", governorate: "Ben Arous", lon: 10.2700, lat: 36.7650, status: "OFFICIAL_GTFS" },
  { id: "stop_009", name_ar: "منوبة الجامعة", name_fr: "Manouba Campus", type: "METRO_STATION", governorate: "Manouba", lon: 10.0972, lat: 36.8081, status: "VERIFIED_GEO" },
  { id: "stop_010", name_ar: "نابل المحطة", name_fr: "Nabeul Gare Routière", type: "BUS_TERMINAL", governorate: "Nabeul", lon: 10.7376, lat: 36.4561, status: "VERIFIED_GEO" },
  { id: "stop_011", name_ar: "الحمامات المركز", name_fr: "Hammamet Centre", type: "BUS_STOP", governorate: "Nabeul", lon: 10.6167, lat: 36.4000, status: "VERIFIED_GEO" },
  { id: "stop_012", name_ar: "سوسة باب الجبلي", name_fr: "Sousse Bab Bhar", type: "TRAIN_STATION", governorate: "Sousse", lon: 10.6084, lat: 35.8256, status: "OFFICIAL_GTFS" },
  { id: "stop_013", name_ar: "سوسة القنطاوي", name_fr: "Port El Kantaoui", type: "BUS_STOP", governorate: "Sousse", lon: 10.5900, lat: 35.8900, status: "VERIFIED_GEO" },
  { id: "stop_014", name_ar: "صفاقس باب الجبلي", name_fr: "Sfax Bab El Jebli", type: "BUS_TERMINAL", governorate: "Sfax", lon: 10.7603, lat: 34.7406, status: "VERIFIED_GEO" },
  { id: "stop_015", name_ar: "صفاقس المطار", name_fr: "Sfax Aeroport", type: "AIRPORT_SHUTTLE", governorate: "Sfax", lon: 10.6800, lat: 34.7150, status: "VERIFIED_GEO" },
  { id: "stop_016", name_ar: "بنزرت المدينة", name_fr: "Bizerte Ville", type: "BUS_TERMINAL", governorate: "Bizerte", lon: 9.8739, lat: 37.2744, status: "VERIFIED_GEO" },
  { id: "stop_017", name_ar: "قابس المحطة الرئيسية", name_fr: "Gabes Station Principale", type: "TRAIN_STATION", governorate: "Gabès", lon: 10.0982, lat: 33.8815, status: "OFFICIAL_GTFS" },
  { id: "stop_018", name_ar: "مدنين المركز", name_fr: "Medenine Centre", type: "BUS_TERMINAL", governorate: "Médenine", lon: 10.5055, lat: 33.3549, status: "VERIFIED_GEO" },
  { id: "stop_019", name_ar: "قفصة المدينة", name_fr: "Gafsa Ville", type: "TRAIN_STATION",governorate: "Gafsa", lon: 8.7842, lat: 34.4250, status: "VERIFIED_GEO" },
  { id: "stop_020", name_ar: "توزر النخيل", name_fr: "Tozeur Oasis", type: "BUS_STOP", governorate: "Tozeur", lon: 8.1335, lat: 33.9197, status: "VERIFIED_GEO" }
];

const GOVERNORATES = [
  "All", "Tunis", "Ariana", "Ben Arous", "Manouba", "Nabeul", "Zaghouan", 
  "Bizerte", "Béja", "Jendouba", "Le Kef", "Siliana", "Sousse", "Monastir", 
  "Mahdia", "Sfax", "Kairouan", "Kasserine", "Sidi Bouzid", "Gabès", 
  "Médenine", "Tataouine", "Gafsa", "Tozeur", "Kébili"
];

export default function App() {
  const [selectedGov, setSelectedGov] = useState("All");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedStop, setSelectedStop] = useState(null);
  const [activeTab, setActiveTab] = useState("dashboard");

  // Filter stops based on governorate and search query
  const filteredStops = useMemo(() => {
    return INITIAL_STOPS.filter(stop => {
      const matchesGov = selectedGov === "All" || stop.governorate === selectedGov;
      const q = searchQuery.toLowerCase();
      const matchesSearch = !q || 
        stop.name_fr.toLowerCase().includes(q) || 
        stop.name_ar.includes(q) || 
        stop.governorate.toLowerCase().includes(q) ||
        stop.type.toLowerCase().includes(q);
      return matchesGov && matchesSearch;
    });
  }, [selectedGov, searchQuery]);

  const stats = useMemo(() => {
    const totalStops = 287; // Total from MASARI run telemetry
    const totalRoutes = 42;
    const govCount = new Set(INITIAL_STOPS.map(s => s.governorate)).size;
    return { totalStops, totalRoutes, govCount };
  }, []);

  return (
    <div className="min-h-screen bg-[#070C18] text-[#F8FAFC] font-sans flex flex-col">
      {/* Top Header */}
      <header className="bg-[#0F172A] border-b border-[#223252] px-6 py-4 flex items-center justify-between sticky top-0 z-30 shadow-md">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-[#147D87] to-[#35C8D0] flex items-center justify-center shadow-inner">
            <Compass className="w-6 h-6 text-white animate-pulse" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-wide flex items-center gap-2">
              MASARI <span className="text-[#35C8D0] font-mono text-sm px-2 py-0.5 rounded bg-[#132238] border border-[#22385D]">v3.6 Dashboard</span>
            </h1>
            <p className="text-xs text-[#8B9EC0]">Tunisia National Transit & Geographic Recovery Platform</p>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <div className="flex bg-[#0B1324] p-1 rounded-lg border border-[#1E2D4A]">
            <button 
              onClick={() => setActiveTab("dashboard")} 
              className={`px-4 py-1.5 rounded-md text-xs font-medium transition-all ${activeTab === 'dashboard' ? 'bg-[#147D87] text-white shadow' : 'text-[#8B9EC0] hover:text-white'}`}
            >
              Dashboard & Map
            </button>
            <button 
              onClick={() => setActiveTab("directory")} 
              className={`px-4 py-1.5 rounded-md text-xs font-medium transition-all ${activeTab === 'directory' ? 'bg-[#147D87] text-white shadow' : 'text-[#8B9EC0] hover:text-white'}`}
            >
              Stops Directory
            </button>
          </div>

          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#0D162B] border border-[#1D2E4F] text-xs text-[#45D6A0]">
            <CheckCircle2 className="w-4 h-4" />
            <span>SQLite Connected</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 p-6 max-w-[1600px] w-full mx-auto flex flex-col gap-6">
        
        {/* Statistics Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-[#0F172A] border border-[#223252] rounded-xl p-5 relative overflow-hidden shadow-sm">
            <div className="absolute top-0 left-0 right-0 h-1 bg-[#45D6A0]" />
            <div className="flex justify-between items-start">
              <div>
                <p className="text-xs font-semibold text-[#8B9EC0] uppercase tracking-wider">Recovered Stops</p>
                <h3 className="text-3xl font-bold mt-1 text-white">{stats.totalStops}</h3>
                <p className="text-xs text-[#45D6A0] mt-1 flex items-center gap-1">
                  <ShieldCheck className="w-3.5 h-3.5" /> GPS Verified WGS84
                </p>
              </div>
              <div className="p-3 rounded-xl bg-[#132238] text-[#45D6A0]">
                <MapPin className="w-6 h-6" />
              </div>
            </div>
          </div>

          <div className="bg-[#0F172A] border border-[#223252] rounded-xl p-5 relative overflow-hidden shadow-sm">
            <div className="absolute top-0 left-0 right-0 h-1 bg-[#35C8D0]" />
            <div className="flex justify-between items-start">
              <div>
                <p className="text-xs font-semibold text-[#8B9EC0] uppercase tracking-wider">Active Routes</p>
                <h3 className="text-3xl font-bold mt-1 text-white">{stats.totalRoutes}</h3>
                <p className="text-xs text-[#35C8D0] mt-1 flex items-center gap-1">
                  <Bus className="w-3.5 h-3.5" /> Bus & Metro Corridors
                </p>
              </div>
              <div className="p-3 rounded-xl bg-[#132238] text-[#35C8D0]">
                <Navigation className="w-6 h-6" />
              </div>
            </div>
          </div>

          <div className="bg-[#0F172A] border border-[#223252] rounded-xl p-5 relative overflow-hidden shadow-sm">
            <div className="absolute top-0 left-0 right-0 h-1 bg-[#FF7A2F]" />
            <div className="flex justify-between items-start">
              <div>
                <p className="text-xs font-semibold text-[#8B9EC0] uppercase tracking-wider">Governorates</p>
                <h3 className="text-3xl font-bold mt-1 text-white">24 / 24</h3>
                <p className="text-xs text-[#FF7A2F] mt-1 flex items-center gap-1">
                  <Globe className="w-3.5 h-3.5" /> Nationwide Coverage
                </p>
              </div>
              <div className="p-3 rounded-xl bg-[#132238] text-[#FF7A2F]">
                <Layers className="w-6 h-6" />
              </div>
            </div>
          </div>

          <div className="bg-[#0F172A] border border-[#223252] rounded-xl p-5 relative overflow-hidden shadow-sm">
            <div className="absolute top-0 left-0 right-0 h-1 bg-[#FFAA55]" />
            <div className="flex justify-between items-start">
              <div>
                <p className="text-xs font-semibold text-[#8B9EC0] uppercase tracking-wider">Database Engine</p>
                <h3 className="text-3xl font-bold mt-1 text-white">SQLite</h3>
                <p className="text-xs text-[#FFAA55] mt-1 flex items-center gap-1">
                  <Database className="w-3.5 h-3.5" /> React Native Ready
                </p>
              </div>
              <div className="p-3 rounded-xl bg-[#132238] text-[#FFAA55]">
                <BarChart2 className="w-6 h-6" />
              </div>
            </div>
          </div>
        </div>

        {activeTab === 'dashboard' ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Interactive Map Section */}
            <div className="lg:col-span-2 bg-[#0F172A] border border-[#223252] rounded-xl p-5 flex flex-col shadow-sm">
              <div className="flex justify-between items-center mb-4">
                <div>
                  <h2 className="text-base font-bold text-white flex items-center gap-2">
                    <Globe className="w-5 h-5 text-[#35C8D0]" /> Tunisia Transit Stop Inspector
                  </h2>
                  <p className="text-xs text-[#8B9EC0]">Click any stop marker to inspect its routing and governorate coordinates.</p>
                </div>
                <div className="flex items-center gap-2">
                  <select 
                    value={selectedGov}
                    onChange={(e) => setSelectedGov(e.target.value)}
                    className="bg-[#0B1324] border border-[#22385D] text-xs rounded-lg px-3 py-1.5 text-white focus:outline-none focus:border-[#35C8D0]"
                  >
                    {GOVERNORATES.map(gov => (
                      <option key={gov} value={gov}>{gov === "All" ? "All Governorates (24)" : gov}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Simulated Interactive Map Canvas */}
              <div className="relative flex-1 min-h-[420px] bg-[#070C18] rounded-xl border border-[#1A2844] overflow-hidden flex items-center justify-center p-4">
                <div className="absolute inset-0 opacity-15 bg-[radial-gradient(#35C8D0_1px,transparent_1px)] [background-size:24px_24px]" />
                
                {/* Visual Map Outline Simulation */}
                <div className="absolute inset-6 border border-[#1D2E4F] rounded-2xl pointer-events-none flex flex-col justify-between p-4">
                  <div className="flex justify-between text-[10px] text-[#4E6591] font-mono">
                    <span>LAT: 37.5° N</span>
                    <span>MEDITERRANEAN SEA</span>
                    <span>LON: 11.5° E</span>
                  </div>
                  <div className="flex justify-between text-[10px] text-[#4E6591] font-mono">
                    <span>SAHARA BORDER</span>
                    <span>TUNISIA GEOGRAPHIC GRID (SRID 4326)</span>
                    <span>LAT: 30.2° N</span>
                  </div>
                </div>

                {/* Plotted Stops */}
                <div className="relative w-full h-full max-w-xl max-h-96 flex items-center justify-center">
                  {filteredStops.map((stop, idx) => {
                    const isSelected = selectedStop?.id === stop.id;
                    // Position simulation based on lon/lat relative offset
                    const leftPos = `${Math.max(10, Math.min(90, (stop.lon - 7.5) * 22))}%`;
                    const topPos = `${Math.max(15, Math.min(85, (37.5 - stop.lat) * 25))}%`;
                    
                    return (
                      <button
                        key={stop.id}
                        onClick={() => setSelectedStop(stop)}
                        style={{ left: leftPos, top: topPos }}
                        className={`absolute group -translate-x-1/2 -translate-y-1/2 p-2 transition-all cursor-pointer`}
                      >
                        <div className={`w-4 h-4 rounded-full flex items-center justify-center transition-all ${isSelected ? 'bg-[#FF7A2F] scale-125 shadow-lg shadow-[#FF7A2F]/50' : 'bg-[#35C8D0] hover:bg-[#45D6A0] shadow-md'}`}>
                          <div className="w-1.5 h-1.5 bg-[#070C18] rounded-full" />
                        </div>
                        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 hidden group-hover:block whitespace-nowrap bg-[#0B1324] border border-[#35C8D0] text-white text-[10px] px-2 py-1 rounded shadow-lg z-20">
                          {stop.name_fr} ({stop.governorate})
                        </div>
                      </button>
                    );
                  })}
                </div>

                <div className="absolute bottom-4 left-4 bg-[#0B1324]/90 backdrop-blur border border-[#1D2E4F] p-3 rounded-lg text-xs flex flex-col gap-1.5 shadow-md">
                  <div className="flex items-center gap-2 text-[#45D6A0]">
                    <span className="w-2.5 h-2.5 rounded-full bg-[#45D6A0]" />
                    <span>Verified GPS Stop ({filteredStops.length} visible)</span>
                  </div>
                  <div className="flex items-center gap-2 text-[#35C8D0]">
                    <span className="w-2.5 h-2.5 rounded-full bg-[#35C8D0]" />
                    <span>Selected Governorate: <strong className="text-white">{selectedGov}</strong></span>
                  </div>
                </div>
              </div>
            </div>

            {/* Stop Inspector Panel */}
            <div className="bg-[#0F172A] border border-[#223252] rounded-xl p-5 flex flex-col shadow-sm justify-between">
              <div>
                <h2 className="text-base font-bold text-white mb-1 flex items-center gap-2">
                  <Navigation className="w-5 h-5 text-[#FF7A2F]" /> Stop & Route Inspector
                </h2>
                <p className="text-xs text-[#8B9EC0] mb-4">Detailed metadata extracted from MASARI SQLite store.</p>

                {selectedStop ? (
                  <div className="space-y-4 bg-[#0B1324] border border-[#1D2E4F] rounded-xl p-4">
                    <div className="border-b border-[#1A2844] pb-3">
                      <span className="text-[10px] font-mono text-[#35C8D0] uppercase bg-[#132238] px-2 py-0.5 rounded border border-[#233B5E]">
                        {selectedStop.type}
                      </span>
                      <h3 className="text-lg font-bold text-white mt-2">{selectedStop.name_fr}</h3>
                      <p className="text-sm font-arabic text-[#8B9EC0]">{selectedStop.name_ar}</p>
                    </div>

                    <div className="grid grid-cols-2 gap-3 text-xs">
                      <div className="bg-[#070C18] p-2.5 rounded-lg border border-[#18253E]">
                        <span className="text-[#8B9EC0] block">Governorate</span>
                        <strong className="text-white text-sm">{selectedStop.governorate}</strong>
                      </div>
                      <div className="bg-[#070C18] p-2.5 rounded-lg border border-[#18253E]">
                        <span className="text-[#8B9EC0] block">Verification</span>
                        <span className="text-[#45D6A0] font-semibold">{selectedStop.status}</span>
                      </div>
                      <div className="bg-[#070C18] p-2.5 rounded-lg border border-[#18253E]">
                        <span className="text-[#8B9EC0] block">Longitude</span>
                        <span className="text-white font-mono">{selectedStop.lon}</span>
                      </div>
                      <div className="bg-[#070C18] p-2.5 rounded-lg border border-[#18253E]">
                        <span className="text-[#8B9EC0] block">Latitude</span>
                        <span className="text-white font-mono">{selectedStop.lat}</span>
                      </div>
                    </div>

                    <div className="pt-2">
                      <p className="text-xs text-[#8B9EC0] mb-2 font-medium">Linked Transit Corridors:</p>
                      <div className="space-y-1.5">
                        <div className="flex items-center justify-between text-xs bg-[#070C18] p-2 rounded border border-[#18253E]">
                          <span className="text-white flex items-center gap-1.5"><Bus className="w-3.5 h-3.5 text-[#35C8D0]" /> Line 2A Trunk</span>
                          <span className="text-[#45D6A0] text-[10px]">Active</span>
                        </div>
                        <div className="flex items-center justify-between text-xs bg-[#070C18] p-2 rounded border border-[#18253E]">
                          <span className="text-white flex items-center gap-1.5"><Train className="w-3.5 h-3.5 text-[#FF7A2F]" /> Regional Rail Link</span>
                          <span className="text-[#45D6A0] text-[10px]">Active</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="h-64 border border-dashed border-[#223252] rounded-xl flex flex-col items-center justify-center p-6 text-center text-[#8B9EC0]">
                    <MapPin className="w-10 h-10 text-[#223252] mb-2" />
                    <p className="text-xs">No stop selected. Click any marker on the map or choose from the list to inspect routing details.</p>
                  </div>
                )}
              </div>

              <div className="mt-4 pt-3 border-t border-[#1E2D4A] flex justify-between items-center text-xs text-[#8B9EC0]">
                <span>Dataset ID: <code className="text-[#35C8D0]">TN_MOBILITY_3_6</code></span>
                <button 
                  onClick={() => setSelectedStop(INITIAL_STOPS[0])}
                  className="text-[#35C8D0] hover:underline flex items-center gap-1"
                >
                  Select Default <ChevronRight className="w-3 h-3" />
                </button>
              </div>
            </div>

          </div>
        ) : (
          /* Stops Directory Table View */
          <div className="bg-[#0F172A] border border-[#223252] rounded-xl p-5 shadow-sm flex flex-col gap-4">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
              <div>
                <h2 className="text-base font-bold text-white">Recovered Transit Stops Directory</h2>
                <p className="text-xs text-[#8B9EC0]">Search and filter through all verified stations and stops in Tunisia.</p>
              </div>
              <div className="flex items-center gap-3 w-full sm:w-auto">
                <div className="relative flex-1 sm:w-72">
                  <Search className="w-4 h-4 text-[#8B9EC0] absolute left-3 top-2.5" />
                  <input 
                    type="text"
                    placeholder="Search by name or governorate..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full bg-[#0B1324] border border-[#22385D] text-xs rounded-lg pl-9 pr-3 py-2 text-white focus:outline-none focus:border-[#35C8D0]"
                  />
                </div>
                <select 
                  value={selectedGov}
                  onChange={(e) => setSelectedGov(e.target.value)}
                  className="bg-[#0B1324] border border-[#22385D] text-xs rounded-lg px-3 py-2 text-white focus:outline-none focus:border-[#35C8D0]"
                >
                  {GOVERNORATES.map(gov => (
                    <option key={gov} value={gov}>{gov === "All" ? "All Govs" : gov}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="overflow-x-auto rounded-xl border border-[#1E2D4A]">
              <table className="w-full text-left text-xs">
                <thead className="bg-[#132238] text-[#35C8D0] border-b border-[#1E2D4A]">
                  <tr>
                    <th className="p-3">Stop ID</th>
                    <th className="p-3">French Name</th>
                    <th className="p-3">Arabic Name</th>
                    <th className="p-3">Type</th>
                    <th className="p-3">Governorate</th>
                    <th className="p-3">Coordinates (Lon, Lat)</th>
                    <th className="p-3">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#182642]">
                  {filteredStops.map((stop, idx) => (
                    <tr 
                      key={stop.id} 
                      onClick={() => { setSelectedStop(stop); setActiveTab('dashboard'); }}
                      className="hover:bg-[#15233E] cursor-pointer transition-colors"
                    >
                      <td className="p-3 font-mono text-[#35C8D0]">{stop.id}</td>
                      <td className="p-3 font-semibold text-white">{stop.name_fr}</td>
                      <td className="p-3 font-arabic text-[#8B9EC0]">{stop.name_ar}</td>
                      <td className="p-3">
                        <span className="bg-[#0B1324] px-2 py-0.5 rounded border border-[#22385D] text-[10px] text-[#45D6A0]">
                          {stop.type}
                        </span>
                      </td>
                      <td className="p-3 text-white">{stop.governorate}</td>
                      <td className="p-3 font-mono text-[#8B9EC0]">{stop.lon.toFixed(4)}, {stop.lat.toFixed(4)}</td>
                      <td className="p-3 text-[#45D6A0] font-medium">{stop.status}</td>
                    </tr>
                  ))}
                  {filteredStops.length === 0 && (
                    <tr>
                      <td colSpan="7" className="p-8 text-center text-[#8B9EC0]">
                        No matching transit stops found for your query.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

      </main>

      {/* Footer */}
      <footer className="bg-[#070C18] border-t border-[#18243E] px-6 py-3 text-center text-xs text-[#8B9EC0]">
        MASARI Recovery Studio 3.6 · React Native & SQLite Integration Engine
      </footer>
    </div>
  );
}