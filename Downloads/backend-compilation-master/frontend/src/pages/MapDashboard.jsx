import { useEffect, useState } from 'react';
import { api } from '../services/api';
import { MapContainer, TileLayer, CircleMarker, Popup, GeoJSON } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import GlassCard from '../components/ui/GlassCard';
import { Map as MapIcon, Filter, Layers, Activity } from 'lucide-react';
import sousseGeoJSON from '../assets/sousse.json';

// Fix for default marker icons
import L from 'leaflet';
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});
L.Marker.prototype.options.icon = DefaultIcon;

const MapDashboard = ({ wsMessages }) => {
  const soussePosition = [35.8256, 10.6369];
  const [zones, setZones] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchZones();
  }, []);

  const fetchZones = async () => {
    try {
      const response = await api.get('/zones');
      // Append random pollution to zones for the demo if not provided by API directly
      const zonesWithData = response.data.map(z => ({
        ...z,
        pollution: z.pollution || Math.floor(Math.random() * 100),
        temperature: z.temperature || (25 + Math.random() * 10),
        humidite: z.humidite || (40 + Math.random() * 30)
      }));
      setZones(zonesWithData);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching zones:", error);
      setLoading(false);
    }
  };

  // Listen to WebSockets to update specific zones dynamically
  useEffect(() => {
    if (wsMessages && wsMessages.length > 0 && zones.length > 0) {
      const latest = wsMessages[0].data;
      if (latest && latest.id_zone) {
        setZones(prev => prev.map(z => 
          z.id_zone === latest.id_zone 
            ? { ...z, pollution: latest.pollution, temperature: latest.temperature, humidite: latest.humidite } 
            : z
        ));
      }
    }
  }, [wsMessages]);

  const getColor = (pollution) => {
    if (pollution > 80) return '#ef4444'; // neo-danger
    if (pollution > 50) return '#f59e0b'; // neo-warning
    return '#10b981'; // neo-success
  };

  // Style function for GeoJSON polygons
  const getGeoJsonStyle = (feature) => {
    const zoneName = feature.properties.del_fr || "";
    // On essaie de correspondre avec nom_zone en ignorant la casse
    const matchedZone = zones.find(z => z.nom_zone.toLowerCase().includes(zoneName.toLowerCase()) || zoneName.toLowerCase().includes(z.nom_zone.toLowerCase()));
    
    if (!matchedZone) {
      return {
        fillColor: '#333333',
        weight: 1,
        opacity: 0.8,
        color: '#555555',
        fillOpacity: 0.2
      };
    }

    return {
        fillColor: getColor(matchedZone.pollution),
        weight: 2,
        opacity: 1,
        color: '#ffffff',
        fillOpacity: 0.5
    };
  };

  // Ajout de Popups et Tooltips sur les polygones de la carte
  const onEachFeature = (feature, layer) => {
    const zoneName = feature.properties.del_fr || "Zone Inconnue";
    const matchedZone = zones.find(z => z.nom_zone.toLowerCase().includes(zoneName.toLowerCase()) || zoneName.toLowerCase().includes(z.nom_zone.toLowerCase()));
    
    if (matchedZone) {
      const content = `
        <div class="neo-popup-content text-left" style="min-width: 140px;">
          <strong style="font-size: 14px; display: block; margin-bottom: 6px; border-bottom: 1px solid #ccc; padding-bottom: 4px;">${matchedZone.nom_zone}</strong>
          <div style="font-size: 13px; color: #444; margin-bottom: 3px;">Pollution: <span style="color: ${getColor(matchedZone.pollution)}; font-weight: bold;">${Math.round(matchedZone.pollution)} µg</span></div>
          <div style="font-size: 13px; color: #444; margin-bottom: 3px;">Température: <span style="color: #f97316; font-weight: bold;">${matchedZone.temperature?.toFixed(1)} °C</span></div>
          <div style="font-size: 13px; color: #444;">Humidité: <span style="color: #3b82f6; font-weight: bold;">${matchedZone.humidite?.toFixed(1)} %</span></div>
        </div>
      `;
      // Afficher l'infobulle au survol (hover)
      layer.bindTooltip(content, { sticky: true, opacity: 0.95 });
      // L'afficher aussi au clic
      layer.bindPopup(content);
    } else {
      layer.bindTooltip(`<strong>${zoneName}</strong><br><span style="color:#888; font-size:12px;">Aucune donnée capteur</span>`, { sticky: true });
    }
  };

  return (
    <div className="flex flex-col gap-6 h-full">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3 text-white">
            <MapIcon className="text-blue-500 w-8 h-8" />
            City Map Overview
          </h1>
          <p className="text-gray-400 mt-2 text-sm">Visualisation géographique des délégations de Sousse (GeoJSON)</p>
        </div>
        
        <div className="flex gap-2">
          <button className="flex items-center gap-2 px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-sm text-gray-300 hover:bg-gray-800 transition-colors">
            <Filter className="w-4 h-4" /> Filters
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-sm text-gray-300 hover:bg-gray-800 transition-colors">
            <Layers className="w-4 h-4" /> Layers
          </button>
        </div>
      </div>

      <div className="flex-1 grid grid-cols-1 lg:grid-cols-4 gap-6 overflow-hidden">
        
        {/* Sidebar */}
        <div className="lg:col-span-1 flex flex-col gap-4 overflow-y-auto custom-scrollbar pr-2">
          <GlassCard className="p-4">
            <h3 className="font-bold text-lg mb-4 text-white flex items-center gap-2">
              <Activity className="w-5 h-5 text-blue-500" />
              Live Status
            </h3>
            <div className="flex flex-col gap-3">
              <div className="flex justify-between items-center bg-gray-900/50 p-3 rounded-lg border border-gray-800">
                <span className="text-gray-400 text-sm">Active Zones</span>
                <span className="font-bold text-white">{zones.length}</span>
              </div>
              <div className="flex justify-between items-center bg-gray-900/50 p-3 rounded-lg border border-gray-800">
                <span className="text-gray-400 text-sm">Critical Alerts</span>
                <span className="font-bold text-neo-danger">{zones.filter(z => z.pollution > 80).length}</span>
              </div>
            </div>
            
            <div className="mt-6">
              <h4 className="text-sm font-semibold text-gray-400 mb-3 uppercase tracking-wider">Legend</h4>
              <div className="flex flex-col gap-2 text-sm bg-gray-900/80 p-4 rounded-xl border border-gray-700">
                <div className="flex items-center gap-3">
                  <span className="w-4 h-4 rounded-md bg-neo-success/50 border-2 border-neo-success shadow-[0_0_10px_rgba(16,185,129,0.5)]"></span> 
                  <span className="text-gray-200 font-medium">Optimal (AQI &lt; 50)</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="w-4 h-4 rounded-md bg-neo-warning/50 border-2 border-neo-warning shadow-[0_0_10px_rgba(245,158,11,0.5)]"></span> 
                  <span className="text-gray-200 font-medium">Moderate (AQI 50-80)</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="w-4 h-4 rounded-md bg-neo-danger/50 border-2 border-neo-danger shadow-[0_0_10px_rgba(239,68,68,0.5)]"></span> 
                  <span className="text-gray-200 font-medium">Hazardous (AQI &gt; 80)</span>
                </div>
                <div className="flex items-center gap-3 mt-2 border-t border-gray-700 pt-2">
                  <span className="w-4 h-4 rounded-md bg-[#333333]/20 border border-[#555555]"></span> 
                  <span className="text-gray-500 italic">No Data / Hors Limite</span>
                </div>
              </div>
            </div>
          </GlassCard>
        </div>

        {/* Map */}
        <div className="lg:col-span-3 rounded-2xl overflow-hidden shadow-[0_0_30px_rgba(0,0,0,0.5)] border border-gray-700/50 relative">
          {loading ? (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-900 z-[1000]">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            </div>
          ) : (
            <MapContainer 
              center={soussePosition} 
              zoom={10} 
              style={{ height: '100%', width: '100%', background: '#0a0b10' }}
              zoomControl={true}
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
              />
              
              {/* Dynamic GeoJSON layer mapped to live zone data */}
              <GeoJSON 
                key={JSON.stringify(zones.map(z => z.pollution))} 
                data={sousseGeoJSON} 
                style={getGeoJsonStyle}
                onEachFeature={onEachFeature}
              />
            </MapContainer>
          )}
        </div>
      </div>
    </div>
  );
};

export default MapDashboard;
