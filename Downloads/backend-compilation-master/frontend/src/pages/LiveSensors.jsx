import { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Activity, Battery, BatteryCharging, BatteryWarning, Wifi, WifiOff, AlertTriangle, Wrench, Settings, MapPin, Power, CheckCircle } from 'lucide-react';
import GlassCard from '../components/ui/GlassCard';
import { motion, AnimatePresence } from 'framer-motion';

const LiveSensors = ({ wsMessages }) => {
  const [sensors, setSensors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // all, actif, en_maintenance, etc.
  const [selectedSensor, setSelectedSensor] = useState(null);

  useEffect(() => {
    fetchSensors();
  }, []);

  const fetchSensors = async () => {
    try {
      const response = await api.get('/capteurs');
      setSensors(response.data);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching sensors:", error);
      setLoading(false);
    }
  };

  const getStatusColor = (statut) => {
    switch(statut) {
      case 'actif': return 'text-neo-success border-neo-success shadow-[0_0_10px_rgba(16,185,129,0.3)]';
      case 'inactif': return 'text-gray-500 border-gray-600';
      case 'signale': return 'text-neo-warning border-neo-warning shadow-[0_0_10px_rgba(245,158,11,0.3)]';
      case 'en_maintenance': return 'text-neo-primary border-neo-primary shadow-[0_0_10px_rgba(59,130,246,0.3)]';
      case 'hors_service': return 'text-neo-danger border-neo-danger shadow-[0_0_10px_rgba(239,68,68,0.3)]';
      default: return 'text-gray-400 border-gray-600';
    }
  };

  const getStatusIcon = (statut) => {
    switch(statut) {
      case 'actif': return <Activity className="w-4 h-4" />;
      case 'inactif': return <Power className="w-4 h-4" />;
      case 'signale': return <AlertTriangle className="w-4 h-4" />;
      case 'en_maintenance': return <Wrench className="w-4 h-4" />;
      case 'hors_service': return <WifiOff className="w-4 h-4" />;
      default: return <Settings className="w-4 h-4" />;
    }
  };

  const getBatteryIcon = (pct) => {
    if (pct > 70) return <Battery className="w-4 h-4 text-neo-success" />;
    if (pct > 30) return <BatteryCharging className="w-4 h-4 text-neo-warning" />;
    return <BatteryWarning className="w-4 h-4 text-neo-danger animate-pulse" />;
  };

  // Automata states
  const FSM_STATES = ['inactif', 'actif', 'signale', 'en_maintenance', 'hors_service'];

  const filteredSensors = filter === 'all' ? sensors : sensors.filter(s => s.statut === filter);

  // Group by zone to avoid huge lists
  const topSensors = filteredSensors.slice(0, 50); // Just showing top 50 for performance

  return (
    <div className="flex flex-col gap-6 h-full">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Activity className="text-neo-primary w-8 h-8" />
            Live Sensors & FSM Tracker
          </h1>
          <p className="text-gray-400 mt-2">Manage IoT devices and monitor their Finite State Machines (Automates)</p>
        </div>
        
        <div className="flex gap-2 bg-gray-900/50 p-1 rounded-lg border border-gray-800">
          {['all', 'actif', 'signale', 'en_maintenance', 'hors_service'].map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                filter === f ? 'bg-neo-primary text-white shadow-[0_0_10px_rgba(59,130,246,0.3)]' : 'text-gray-400 hover:text-white hover:bg-gray-800'
              }`}
            >
              {f.toUpperCase().replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="flex-1 flex justify-center items-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-neo-primary"></div>
        </div>
      ) : (
        <div className="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-6 overflow-hidden">
          
          {/* Sensor Grid */}
          <div className="lg:col-span-2 overflow-y-auto custom-scrollbar pr-2 grid grid-cols-1 md:grid-cols-2 gap-4 content-start">
            {topSensors.map(sensor => (
              <motion.div 
                whileHover={{ scale: 1.02 }}
                key={sensor.id_capteur}
                onClick={() => setSelectedSensor(sensor)}
                className={`bg-gray-900/40 backdrop-blur-sm border rounded-xl p-4 cursor-pointer transition-all ${
                  selectedSensor?.id_capteur === sensor.id_capteur 
                    ? 'border-neo-primary shadow-[0_0_15px_rgba(59,130,246,0.2)]' 
                    : 'border-gray-800 hover:border-gray-600'
                }`}
              >
                <div className="flex justify-between items-start mb-3">
                  <div className="flex items-center gap-2">
                    <div className={`p-2 rounded-lg border bg-gray-900/80 ${getStatusColor(sensor.statut)}`}>
                      {getStatusIcon(sensor.statut)}
                    </div>
                    <div>
                      <h3 className="font-bold text-gray-200">Capteur #{sensor.id_capteur}</h3>
                      <span className="text-xs text-gray-500 uppercase tracking-wider">{sensor.type_capteur}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-1 bg-black/40 px-2 py-1 rounded border border-gray-800">
                    {getBatteryIcon(sensor.batterie_pct)}
                    <span className="text-xs font-mono text-gray-400">{sensor.batterie_pct}%</span>
                  </div>
                </div>
                
                <div className="flex justify-between items-center text-sm">
                  <div className="flex items-center gap-1 text-gray-400">
                    <MapPin className="w-3 h-3" />
                    <span>Zone {sensor.id_zone}</span>
                  </div>
                  <span className={`px-2 py-0.5 rounded text-xs font-medium border bg-black/50 ${getStatusColor(sensor.statut)}`}>
                    {sensor.statut.replace('_', ' ').toUpperCase()}
                  </span>
                </div>
              </motion.div>
            ))}
          </div>

          {/* FSM Inspector Panel */}
          <div className="lg:col-span-1 flex flex-col">
            <GlassCard className="flex-1 flex flex-col">
              {selectedSensor ? (
                <div className="flex-1 flex flex-col h-full">
                  <div className="flex justify-between items-center mb-6 border-b border-gray-800 pb-4">
                    <h2 className="text-xl font-bold text-neo-primary">FSM Inspector</h2>
                    <span className="text-xs font-mono text-gray-500">ID: {selectedSensor.id_capteur}</span>
                  </div>

                  <div className="space-y-6">
                    <div>
                      <h3 className="text-sm text-gray-400 uppercase tracking-wider mb-2">Current State</h3>
                      <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg border bg-gray-900 ${getStatusColor(selectedSensor.statut)}`}>
                        {getStatusIcon(selectedSensor.statut)}
                        <span className="font-bold">{selectedSensor.statut.toUpperCase()}</span>
                      </div>
                    </div>

                    <div>
                      <h3 className="text-sm text-gray-400 uppercase tracking-wider mb-4">State Machine (Automate)</h3>
                      <div className="relative pl-4 space-y-6 border-l-2 border-gray-800 ml-2">
                        {FSM_STATES.map((state, i) => {
                          const isActive = state === selectedSensor.statut;
                          const isPast = FSM_STATES.indexOf(selectedSensor.statut) > i;
                          return (
                            <div key={state} className="relative">
                              <div className={`absolute -left-[21px] w-4 h-4 rounded-full border-2 ${
                                isActive ? 'bg-neo-primary border-white shadow-[0_0_10px_rgba(59,130,246,0.8)]' : 
                                isPast ? 'bg-gray-600 border-gray-600' : 'bg-gray-900 border-gray-700'
                              }`}></div>
                              <div className={`ml-4 ${isActive ? 'text-white font-bold' : isPast ? 'text-gray-500' : 'text-gray-600'}`}>
                                {state.toUpperCase()}
                                {isActive && <span className="ml-2 text-xs text-neo-primary animate-pulse">← CURRENT</span>}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>

                    <div className="pt-4 border-t border-gray-800 mt-auto">
                      <h3 className="text-sm text-gray-400 uppercase tracking-wider mb-3">Trigger Transition</h3>
                      <div className="grid grid-cols-2 gap-2">
                        <button className="py-2 text-sm bg-neo-warning/10 hover:bg-neo-warning/20 text-neo-warning border border-neo-warning/30 rounded transition-colors flex justify-center items-center gap-2">
                          <AlertTriangle className="w-4 h-4" /> Signaler
                        </button>
                        <button className="py-2 text-sm bg-neo-primary/10 hover:bg-neo-primary/20 text-neo-primary border border-neo-primary/30 rounded transition-colors flex justify-center items-center gap-2">
                          <Wrench className="w-4 h-4" /> Réparer
                        </button>
                      </div>
                      <p className="text-xs text-gray-500 mt-3 text-center">Transitions are validated by the backend FSM engine.</p>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="flex-1 flex flex-col justify-center items-center text-center text-gray-500">
                  <Activity className="w-16 h-16 mb-4 text-gray-700" />
                  <p>Select a sensor to inspect its Finite State Machine (Automate)</p>
                </div>
              )}
            </GlassCard>
          </div>
        </div>
      )}
    </div>
  );
};

export default LiveSensors;
