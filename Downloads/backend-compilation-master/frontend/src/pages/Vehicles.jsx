import { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Truck, Battery, BatteryCharging, BatteryWarning, Zap, MapPin, Activity, CheckCircle, AlertTriangle, Navigation, PauseCircle } from 'lucide-react';
import GlassCard from '../components/ui/GlassCard';
import { motion } from 'framer-motion';

const Vehicles = () => {
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedVehicle, setSelectedVehicle] = useState(null);

  useEffect(() => {
    fetchVehicles();
  }, []);

  const fetchVehicles = async () => {
    try {
      const response = await api.get('/vehicules');
      setVehicles(response.data);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching vehicles:", error);
      setLoading(false);
    }
  };

  const getStatusColor = (statut) => {
    switch(statut) {
      case 'en_route': return 'text-neo-primary border-neo-primary bg-neo-primary/10 shadow-[0_0_10px_rgba(59,130,246,0.3)]';
      case 'stationné': return 'text-gray-400 border-gray-600 bg-gray-800/50';
      case 'arrivé': return 'text-neo-success border-neo-success bg-neo-success/10 shadow-[0_0_10px_rgba(16,185,129,0.3)]';
      case 'en_panne': return 'text-neo-danger border-neo-danger bg-neo-danger/10 shadow-[0_0_10px_rgba(239,68,68,0.3)]';
      default: return 'text-gray-400 border-gray-600';
    }
  };

  const getStatusIcon = (statut) => {
    switch(statut) {
      case 'en_route': return <Navigation className="w-4 h-4" />;
      case 'stationné': return <PauseCircle className="w-4 h-4" />;
      case 'arrivé': return <CheckCircle className="w-4 h-4" />;
      case 'en_panne': return <AlertTriangle className="w-4 h-4" />;
      default: return <Activity className="w-4 h-4" />;
    }
  };

  // Automata states for Vehicles
  const FSM_STATES = ['stationné', 'en_route', 'en_panne', 'arrivé'];

  return (
    <div className="flex flex-col gap-6 h-full">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Truck className="text-neo-purple w-8 h-8" />
            Autonomous Fleet & Route FSM
          </h1>
          <p className="text-gray-400 mt-2">Manage smart city electric vehicles and monitor automated routing states</p>
        </div>
      </div>

      {loading ? (
        <div className="flex-1 flex justify-center items-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-neo-purple"></div>
        </div>
      ) : (
        <div className="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-6 overflow-hidden">
          
          {/* Vehicles List */}
          <div className="lg:col-span-2 overflow-y-auto custom-scrollbar pr-2 grid grid-cols-1 md:grid-cols-2 gap-4 content-start">
            {vehicles.map(vehicle => (
              <motion.div 
                whileHover={{ scale: 1.02 }}
                key={vehicle.id_vehicule}
                onClick={() => setSelectedVehicle(vehicle)}
                className={`bg-gray-900/40 backdrop-blur-sm border rounded-xl p-4 cursor-pointer transition-all ${
                  selectedVehicle?.id_vehicule === vehicle.id_vehicule 
                    ? 'border-neo-purple shadow-[0_0_15px_rgba(139,92,246,0.3)]' 
                    : 'border-gray-800 hover:border-gray-600'
                }`}
              >
                <div className="flex justify-between items-start mb-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-gray-800 border border-gray-700">
                      <Truck className="w-6 h-6 text-neo-purple" />
                    </div>
                    <div>
                      <h3 className="font-bold text-white tracking-wide">{vehicle.modele}</h3>
                      <span className="text-xs text-neo-primary bg-neo-primary/10 px-2 py-0.5 rounded border border-neo-primary/30 uppercase tracking-wider">
                        {vehicle.type_vehicule.replace('_', ' ')}
                      </span>
                    </div>
                  </div>
                  <div className={`flex items-center gap-2 px-3 py-1 rounded-full border ${getStatusColor(vehicle.statut)}`}>
                    {getStatusIcon(vehicle.statut)}
                    <span className="text-xs font-bold uppercase">{vehicle.statut.replace('_', ' ')}</span>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4 mt-4">
                  <div className="bg-black/30 p-2 rounded border border-gray-800/50 flex flex-col gap-1">
                    <span className="text-xs text-gray-500 uppercase flex items-center gap-1"><Battery className="w-3 h-3"/> Battery</span>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 h-1.5 bg-gray-800 rounded-full overflow-hidden">
                        <div 
                          className={`h-full ${vehicle.batterie_pct > 20 ? 'bg-neo-success' : 'bg-neo-danger'}`} 
                          style={{ width: `${vehicle.batterie_pct}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-mono text-gray-300">{vehicle.batterie_pct}%</span>
                    </div>
                  </div>
                  <div className="bg-black/30 p-2 rounded border border-gray-800/50 flex flex-col gap-1">
                    <span className="text-xs text-gray-500 uppercase flex items-center gap-1"><Activity className="w-3 h-3"/> Speed</span>
                    <span className="text-sm font-mono text-gray-300">{vehicle.statut === 'en_route' ? vehicle.vitesse_kmh : 0} km/h</span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          {/* FSM Inspector Panel */}
          <div className="lg:col-span-1 flex flex-col">
            <GlassCard className="flex-1 flex flex-col border-t-4 border-t-neo-purple">
              {selectedVehicle ? (
                <div className="flex-1 flex flex-col h-full">
                  <div className="flex justify-between items-center mb-6 border-b border-gray-800 pb-4">
                    <div>
                      <h2 className="text-xl font-bold text-white">{selectedVehicle.modele}</h2>
                      <p className="text-sm text-neo-purple">Vehicle Routing FSM</p>
                    </div>
                    <span className="text-xs font-mono bg-gray-800 px-2 py-1 rounded text-gray-400">ID: {selectedVehicle.id_vehicule}</span>
                  </div>

                  <div className="space-y-8">
                    <div>
                      <h3 className="text-sm text-gray-400 uppercase tracking-wider mb-5">Route State Machine</h3>
                      
                      {/* Vertical Timeline FSM */}
                      <div className="relative pl-6 space-y-8 border-l-2 border-gray-800 ml-4">
                        {FSM_STATES.map((state, i) => {
                          const isActive = state === selectedVehicle.statut;
                          const isPast = FSM_STATES.indexOf(selectedVehicle.statut) > i && selectedVehicle.statut !== 'en_panne';
                          const isError = state === 'en_panne' && isActive;
                          
                          let nodeColor = 'bg-gray-900 border-gray-700';
                          if (isActive) nodeColor = isError ? 'bg-neo-danger border-white shadow-[0_0_15px_rgba(239,68,68,0.8)]' : 'bg-neo-purple border-white shadow-[0_0_15px_rgba(139,92,246,0.8)]';
                          else if (isPast) nodeColor = 'bg-gray-600 border-gray-600';

                          return (
                            <div key={state} className="relative">
                              <div className={`absolute -left-[31px] w-5 h-5 rounded-full border-2 flex items-center justify-center ${nodeColor}`}>
                                {isPast && <CheckCircle className="w-3 h-3 text-white" />}
                              </div>
                              <div className={`ml-4 ${isActive ? (isError ? 'text-neo-danger font-bold' : 'text-white font-bold') : isPast ? 'text-gray-400' : 'text-gray-600'}`}>
                                <div className="flex flex-col">
                                  <span className="uppercase tracking-wider">{state.replace('_', ' ')}</span>
                                  {isActive && <span className="text-xs font-normal mt-1 opacity-80">Current execution state</span>}
                                </div>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>

                    <div className="bg-gray-900/50 p-4 rounded-xl border border-gray-800">
                      <h4 className="text-sm font-semibold text-gray-300 mb-2">Vehicle Telemetry</h4>
                      <div className="grid grid-cols-2 gap-y-2 text-sm">
                        <span className="text-gray-500">Energy Source</span>
                        <span className="text-right text-gray-300 flex items-center justify-end gap-1"><Zap className="w-3 h-3 text-yellow-500"/> {selectedVehicle.energie_utilisee}</span>
                        
                        <span className="text-gray-500">Max Speed</span>
                        <span className="text-right text-gray-300">{selectedVehicle.vitesse_kmh} km/h</span>
                        
                        <span className="text-gray-500">Fleet Class</span>
                        <span className="text-right text-gray-300 uppercase">{selectedVehicle.type_vehicule.replace('_', ' ')}</span>
                      </div>
                    </div>

                    <div className="pt-4 border-t border-gray-800 mt-auto">
                      <h3 className="text-sm text-gray-400 uppercase tracking-wider mb-3">Dispatch Controls</h3>
                      <div className="grid grid-cols-2 gap-2">
                        <button 
                          className="py-2 text-sm bg-neo-purple/10 hover:bg-neo-purple/20 text-neo-purple border border-neo-purple/30 rounded transition-colors flex justify-center items-center gap-2"
                          disabled={selectedVehicle.statut === 'en_route'}
                        >
                          <Navigation className="w-4 h-4" /> Dispatch
                        </button>
                        <button className="py-2 text-sm bg-gray-800 hover:bg-gray-700 text-gray-300 border border-gray-700 rounded transition-colors flex justify-center items-center gap-2">
                          <AlertTriangle className="w-4 h-4" /> Report Issue
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="flex-1 flex flex-col justify-center items-center text-center text-gray-500">
                  <Truck className="w-16 h-16 mb-4 text-gray-800" />
                  <p>Select a vehicle to inspect its Autonomous FSM</p>
                </div>
              )}
            </GlassCard>
          </div>
        </div>
      )}
    </div>
  );
};

export default Vehicles;
