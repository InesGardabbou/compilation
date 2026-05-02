import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { MapPin, AlertTriangle, CheckCircle } from 'lucide-react';
import { getZonesStatus } from '../../services/api';

const ZoneStats = () => {
  const [zones, setZones] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchZones = async () => {
      try {
        const res = await getZonesStatus();
        setZones(res.data || []);
      } catch (err) {
        console.error("Error fetching zone stats:", err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchZones();
    const interval = setInterval(fetchZones, 30000);
    return () => clearInterval(interval);
  }, []);

  const stats = {
    critical: zones.filter(z => z.status === 'critical').length,
    moderate: zones.filter(z => z.status === 'moderate').length,
    good: zones.filter(z => z.status === 'good').length,
    excellent: zones.filter(z => z.status === 'excellent').length,
    avgAqi: zones.length > 0 ? Math.round(zones.reduce((acc, z) => acc + z.aqi, 0) / zones.length) : 0,
    totalSensors: zones.reduce((acc, z) => acc + z.sensors, 0)
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.5 }}
      className="rounded-2xl backdrop-blur-xl bg-gradient-to-br from-gray-800/40 to-gray-900/40 border border-gray-700/50 p-6"
    >
      <div className="mb-6 flex justify-between items-end">
        <div>
          <h3 className="text-xl font-bold text-white flex items-center gap-2">
            <MapPin className="w-5 h-5 text-neo-primary" />
            Zone Status Aggregation
          </h3>
          <p className="text-gray-400 text-sm mt-1">High-level overview of the {zones.length} monitored zones</p>
        </div>
        {!loading && (
          <div className="text-right hidden sm:block">
            <div className="text-2xl font-bold text-white">{stats.avgAqi} <span className="text-sm text-gray-400 font-normal">AQI Moyen</span></div>
            <div className="text-sm text-neo-primary">{stats.totalSensors} capteurs en ligne</div>
          </div>
        )}
      </div>

      {loading ? (
        <div className="text-gray-400 text-center py-8">Chargement des statistiques...</div>
      ) : (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-4 rounded-xl bg-gradient-to-br from-red-500/20 to-red-600/10 border border-red-500/30 flex flex-col items-center justify-center hover:bg-red-500/20 transition-colors">
            <AlertTriangle className="w-8 h-8 text-red-400 mb-2" />
            <span className="text-4xl font-bold text-red-400">{stats.critical}</span>
            <span className="text-sm text-gray-300 mt-1 uppercase tracking-wider font-semibold">Critiques</span>
          </div>
          
          <div className="p-4 rounded-xl bg-gradient-to-br from-yellow-500/20 to-yellow-600/10 border border-yellow-500/30 flex flex-col items-center justify-center hover:bg-yellow-500/20 transition-colors">
            <AlertTriangle className="w-8 h-8 text-yellow-400 mb-2" />
            <span className="text-4xl font-bold text-yellow-400">{stats.moderate}</span>
            <span className="text-sm text-gray-300 mt-1 uppercase tracking-wider font-semibold">Modérées</span>
          </div>

          <div className="p-4 rounded-xl bg-gradient-to-br from-blue-500/20 to-blue-600/10 border border-blue-500/30 flex flex-col items-center justify-center hover:bg-blue-500/20 transition-colors">
            <CheckCircle className="w-8 h-8 text-blue-400 mb-2" />
            <span className="text-4xl font-bold text-blue-400">{stats.good}</span>
            <span className="text-sm text-gray-300 mt-1 uppercase tracking-wider font-semibold">Bonnes</span>
          </div>

          <div className="p-4 rounded-xl bg-gradient-to-br from-green-500/20 to-green-600/10 border border-green-500/30 flex flex-col items-center justify-center hover:bg-green-500/20 transition-colors">
            <CheckCircle className="w-8 h-8 text-green-400 mb-2" />
            <span className="text-4xl font-bold text-green-400">{stats.excellent}</span>
            <span className="text-sm text-gray-300 mt-1 uppercase tracking-wider font-semibold">Excellentes</span>
          </div>
        </div>
      )}
    </motion.div>
  );
};

export default ZoneStats;
