import { useEffect, useState } from 'react';
import { ShieldAlert, Zap, Thermometer, Wind, Activity, Users, Wifi, Trees, Truck, Map, Wrench } from 'lucide-react';
import { motion } from 'framer-motion';
import KpiCard from '../components/dashboard/KpiCard';
import LiveFeed from '../components/dashboard/LiveFeed';
import AdvancedChart from '../components/dashboard/AdvancedChart';
import CityMap from '../components/map/CityMap';
import AlertPanel from '../components/dashboard/AlertPanel';
import ZoneStats from '../components/dashboard/ZoneStats';
import { getDashboardKPIs } from '../services/api';

const Dashboard = ({ wsMessages, isConnected }) => {
  const [kpis, setKpis] = useState({
    zones: 0,
    capteurs: { actifs: 0 },
    interventions: { en_cours: 0 },
    mesures: { moyennes: { pollution_µg_m3: 0 } },
    environnement: { co2_economise_kg_total: 0 }
  });

  useEffect(() => {
    const fetchKPIs = async () => {
      try {
        const res = await getDashboardKPIs();
        setKpis(res.data);
      } catch (err) {
        console.error("Error fetching KPIs:", err);
      }
    };
    fetchKPIs();
    const interval = setInterval(fetchKPIs, 30000);
    return () => clearInterval(interval);
  }, []);

  // Extract latest pollution from wsMessages or use default
  const latestData = wsMessages && wsMessages.length > 0 ? wsMessages[0].data : null;
  const currentTemp = latestData ? latestData.temperature : 24;

  return (
    <div className="flex flex-col gap-6 pb-6 h-[calc(100vh-120px)] overflow-y-auto">
      {/* Header with live status */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between sticky top-0 z-10 backdrop-blur-sm"
      >
        <div>
          <h1 className="text-3xl font-bold text-white">Smart City Dashboard</h1>
          <p className="text-gray-400 text-sm mt-1">Real-time environmental monitoring</p>
        </div>
        <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-800/50 border border-gray-700/50">
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`}></div>
          <span className="text-sm text-gray-300">{isConnected ? 'Live' : 'Offline'}</span>
        </div>
      </motion.div>

      {/* Premium KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        <KpiCard 
          title="Active Sensors" 
          value={(kpis?.capteurs?.actifs || 0).toString()} 
          icon={Zap} 
          colorClass="from-blue-500 to-blue-600"
          delay={0}
          change={8}
          isPositive={true}
        />
        <KpiCard 
          title="Avg Pollution (AQI)" 
          value={(kpis?.mesures?.moyennes?.pollution_µg_m3 || 0).toFixed(1)} 
          unit="µg/m³"
          icon={Wind} 
          colorClass="from-emerald-500 to-emerald-600"
          delay={0.1}
          change={12}
          isPositive={false}
        />
        <KpiCard 
          title="CO2 Saved" 
          value={((kpis?.environnement?.co2_economise_kg_total || 0) / 1000).toFixed(2)} 
          unit="Tons"
          icon={Trees} 
          colorClass="from-green-500 to-green-600"
          delay={0.2}
          change={5}
          isPositive={true}
        />
        <KpiCard 
          title="Total Zones" 
          value={(kpis?.zones || 0).toString()} 
          icon={Map} 
          colorClass="from-purple-500 to-purple-600"
          delay={0.3}
          change={0}
          isPositive={true}
        />
        <KpiCard 
          title="Active Interventions" 
          value={(kpis?.interventions?.en_cours || 0).toString()} 
          icon={Wrench} 
          colorClass="from-orange-500 to-orange-600"
          delay={0.4}
          change={2}
          isPositive={false}
        />
      </div>

      {/* Main Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Advanced Chart - Takes up 2 columns */}
        <div className="lg:col-span-2">
          <AdvancedChart data={wsMessages} chartType="composed" />
        </div>

        {/* Live Feed - Right Column */}
        <div className="flex flex-col gap-6">
          <LiveFeed messages={wsMessages} />
        </div>
      </div>
      
      {/* Zone Stats */}
      <ZoneStats />

      {/* Bottom Grid: Alerts & Map */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Alerts - Left */}
        <AlertPanel />

        {/* Map - Right (spans 2 columns) */}
        <div className="lg:col-span-2 rounded-2xl overflow-hidden shadow-2xl border border-gray-700/50 relative h-96 group">
          {/* Decorative frame overlay */}
          <div className="absolute inset-0 pointer-events-none border border-neo-primary/30 rounded-2xl z-[500]"></div>
          <div className="absolute top-0 left-0 w-6 h-6 border-t-2 border-l-2 border-neo-primary z-[500] group-hover:border-neo-primary transition-all"></div>
          <div className="absolute top-0 right-0 w-6 h-6 border-t-2 border-r-2 border-neo-primary z-[500]"></div>
          <div className="absolute bottom-0 left-0 w-6 h-6 border-b-2 border-l-2 border-neo-primary z-[500]"></div>
          <div className="absolute bottom-0 right-0 w-6 h-6 border-b-2 border-r-2 border-neo-primary z-[500]"></div>
          
          <CityMap wsMessages={wsMessages} />
        </div>
      </div>

      {/* Footer Stats */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.8 }}
        className="grid grid-cols-3 gap-4 mt-6"
      >
        <div className="p-4 rounded-xl bg-gradient-to-br from-gray-800/40 to-gray-900/40 border border-gray-700/50 text-center">
          <p className="text-gray-400 text-xs uppercase tracking-wider mb-2">System Uptime</p>
          <p className="text-2xl font-bold text-white">99.8%</p>
        </div>
        <div className="p-4 rounded-xl bg-gradient-to-br from-gray-800/40 to-gray-900/40 border border-gray-700/50 text-center">
          <p className="text-gray-400 text-xs uppercase tracking-wider mb-2">Data Points</p>
          <p className="text-2xl font-bold text-neo-primary">2.4M</p>
        </div>
        <div className="p-4 rounded-xl bg-gradient-to-br from-gray-800/40 to-gray-900/40 border border-gray-700/50 text-center">
          <p className="text-gray-400 text-xs uppercase tracking-wider mb-2">Response Time</p>
          <p className="text-2xl font-bold text-green-400">145ms</p>
        </div>
      </motion.div>
    </div>
  );
};

export default Dashboard;
