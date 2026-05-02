import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, GeoJSON, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { motion } from 'framer-motion';
import { getZonesStatus } from '../../services/api';
import sousseGeoJSON from '../../data/sousse.json';

// Fix for default marker icons in React Leaflet
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

const MapResizer = () => {
  const map = useMap();
  useEffect(() => {
    const timer = setTimeout(() => {
      map.invalidateSize();
    }, 1200); // Wait for framer-motion animation to finish
    return () => clearTimeout(timer);
  }, [map]);
  return null;
};

const CityMap = ({ wsMessages }) => {
  const soussePosition = [35.8256, 10.6369]; // Center of Sousse
  const [zones, setZones] = useState([]);

  useEffect(() => {
    const fetchMapZones = async () => {
      try {
        const res = await getZonesStatus();
        const apiZones = res.data.map(z => ({
          id: z.id,
          name: z.name,
          pos: z.pos,
          pollution: z.aqi
        }));
        setZones(apiZones);
      } catch (err) {
        console.error("Error fetching map zones:", err);
      }
    };
    fetchMapZones();
    // Optional: add interval if needed, or rely on WS
  }, []);

  // Update map markers based on WS live data
  useEffect(() => {
    if (wsMessages && wsMessages.length > 0) {
      const latest = wsMessages[0];
      if (latest && latest.data && latest.data.id_zone) {
        setZones(prev => prev.map(z => {
          if (z.id === latest.data.id_zone) { 
            return { ...z, pollution: latest.data.pollution };
          }
          return z;
        }));
      }
    }
  }, [wsMessages]);

  const getColor = (pollution) => {
    if (pollution > 80) return '#ef4444'; // neo-danger
    if (pollution > 50) return '#f59e0b'; // neo-warning
    return '#10b981'; // neo-success
  };

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className="h-full w-full relative overflow-hidden bg-[#0a0b10] rounded-2xl"
    >
      <div className="absolute top-4 left-4 z-[400] bg-neo-panel/90 backdrop-blur-md p-3 rounded-lg border border-gray-700/50">
        <h3 className="font-semibold text-white mb-2 text-sm">Zone Status</h3>
        <div className="flex flex-col gap-1 text-xs">
          <div className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-neo-success"></span> Good (0-50)</div>
          <div className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-neo-warning"></span> Moderate (51-80)</div>
          <div className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-neo-danger"></span> Hazardous (&gt;80)</div>
        </div>
      </div>

      <MapContainer 
        center={soussePosition} 
        zoom={12} 
        style={{ height: '100%', width: '100%', background: '#0a0b10' }}
        zoomControl={false}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />
        
        <MapResizer />
        
        <GeoJSON
          key={zones.length > 0 ? zones.map(z => `${z.id}-${z.pollution}`).join('-') : 'empty-zones'}
          data={sousseGeoJSON}
          style={(feature) => {
            const featName = feature.properties.del_fr.toLowerCase().replace(/sousse\s+/g, '').trim();
            const zone = zones.find(z => {
              const zName = z.name.toLowerCase().replace(/sousse\s+/g, '').trim();
              return zName === featName || zName.includes(featName) || featName.includes(zName);
            });
            
            const pollution = zone ? zone.pollution : 0;
            const color = zone ? getColor(pollution) : '#4b5563';
            return {
              fillColor: color,
              weight: 2,
              opacity: 1,
              color: '#1f2937',
              fillOpacity: zone ? 0.6 : 0.15
            };
          }}
          onEachFeature={(feature, layer) => {
            const featName = feature.properties.del_fr.toLowerCase().replace(/sousse\s+/g, '').trim();
            const zone = zones.find(z => {
              const zName = z.name.toLowerCase().replace(/sousse\s+/g, '').trim();
              return zName === featName || zName.includes(featName) || featName.includes(zName);
            });

            if (zone) {
              layer.bindPopup(
                `<div class="text-gray-800 font-sans">
                  <h4 class="font-bold text-base mb-1">${zone.name}</h4>
                  <p class="text-sm m-0">AQI: <span class="font-mono font-bold" style="color: ${getColor(zone.pollution)}">${zone.pollution}</span></p>
                </div>`,
                { className: 'neo-popup' }
              );
              layer.on({
                mouseover: (e) => {
                  const l = e.target;
                  l.setStyle({ fillOpacity: 0.8, weight: 3, color: '#fff' });
                },
                mouseout: (e) => {
                  const l = e.target;
                  l.setStyle({ fillOpacity: 0.6, weight: 2, color: '#1f2937' });
                }
              });
            } else {
              layer.bindPopup(
                `<div class="text-gray-800 font-sans">
                  <h4 class="font-bold text-base mb-1">${feature.properties.del_fr || 'Zone Inconnue'}</h4>
                  <p class="text-sm m-0">Pas de capteurs actifs</p>
                </div>`,
                { className: 'neo-popup' }
              );
            }
          }}
        />
      </MapContainer>
    </motion.div>
  );
};

export default CityMap;
