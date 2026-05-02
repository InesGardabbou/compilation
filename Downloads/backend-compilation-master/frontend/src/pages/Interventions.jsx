import { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Wrench, Clock, User, CheckCircle, Brain, AlertOctagon, Activity } from 'lucide-react';
import { motion } from 'framer-motion';

const Interventions = () => {
  const [interventions, setInterventions] = useState([]);
  const [loading, setLoading] = useState(true);

  // Define the FSM states exactly as specified in the project requirements
  const columns = [
    { id: 'demande', title: 'Demande Initiale', icon: <AlertOctagon className="w-5 h-5 text-gray-400" />, color: 'border-gray-500' },
    { id: 'tech1_assigne', title: 'Tech 1 Assigné', icon: <User className="w-5 h-5 text-neo-warning" />, color: 'border-neo-warning' },
    { id: 'tech2_valide', title: 'Tech 2 Validé', icon: <CheckCircle className="w-5 h-5 text-neo-primary" />, color: 'border-neo-primary' },
    { id: 'ia_valide', title: 'IA Validé', icon: <Brain className="w-5 h-5 text-neo-purple" />, color: 'border-neo-purple' },
    { id: 'termine', title: 'Terminé', icon: <CheckCircle className="w-5 h-5 text-neo-success" />, color: 'border-neo-success' }
  ];

  useEffect(() => {
    fetchInterventions();
  }, []);

  const fetchInterventions = async () => {
    try {
      const response = await api.get('/interventions');
      setInterventions(response.data);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching interventions:", error);
      setLoading(false);
    }
  };

  const getPriorityColor = (priorite) => {
    switch(priorite) {
      case 'basse': return 'bg-gray-800 text-gray-300 border-gray-700';
      case 'moyenne': return 'bg-neo-primary/20 text-neo-primary border-neo-primary/30';
      case 'haute': return 'bg-neo-warning/20 text-neo-warning border-neo-warning/30';
      case 'critique': return 'bg-neo-danger/20 text-neo-danger border-neo-danger/30';
      default: return 'bg-gray-800 text-gray-300 border-gray-700';
    }
  };

  const formatDate = (dateStr) => {
    const d = new Date(dateStr);
    return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
  };

  return (
    <div className="flex flex-col gap-6 h-full">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3 text-white">
            <Wrench className="text-neo-warning w-8 h-8" />
            Maintenance FSM Kanban
          </h1>
          <p className="text-gray-400 mt-2">Track the Multi-Agent (Techs + AI) Validation Finite State Machine</p>
        </div>
      </div>

      {loading ? (
        <div className="flex-1 flex justify-center items-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-neo-warning"></div>
        </div>
      ) : (
        <div className="flex-1 flex gap-4 overflow-x-auto pb-4 custom-scrollbar">
          {columns.map(col => {
            const colInterventions = interventions.filter(i => i.statut === col.id);
            return (
              <div key={col.id} className="min-w-[320px] max-w-[320px] flex flex-col gap-4">
                {/* Column Header */}
                <div className={`bg-gray-900/60 p-4 rounded-xl border-t-4 ${col.color} border-l border-r border-b border-gray-800 flex items-center justify-between shadow-lg`}>
                  <div className="flex items-center gap-2">
                    {col.icon}
                    <h2 className="font-bold text-gray-200">{col.title}</h2>
                  </div>
                  <span className="bg-gray-800 text-gray-400 text-xs font-bold px-2 py-1 rounded-full">
                    {colInterventions.length}
                  </span>
                </div>

                {/* Column Cards */}
                <div className="flex-1 flex flex-col gap-3 overflow-y-auto custom-scrollbar pr-1">
                  {colInterventions.map(ticket => (
                    <motion.div 
                      key={ticket.id_intervention}
                      whileHover={{ scale: 1.02 }}
                      className="bg-gray-900/40 backdrop-blur-sm p-4 rounded-xl border border-gray-800 hover:border-gray-600 transition-colors cursor-pointer group shadow-md"
                    >
                      <div className="flex justify-between items-start mb-3">
                        <span className="text-xs font-mono text-gray-500">TICKET-{ticket.id_intervention}</span>
                        <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded border ${getPriorityColor(ticket.priorite)}`}>
                          {ticket.priorite}
                        </span>
                      </div>
                      
                      <p className="text-sm text-gray-300 font-medium mb-4 line-clamp-3">
                        {ticket.description}
                      </p>

                      <div className="flex items-center justify-between text-xs text-gray-500">
                        <div className="flex items-center gap-1">
                          <Activity className="w-3 h-3" />
                          <span>Capteur #{ticket.id_capteur}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          <span>{formatDate(ticket.date_demande)}</span>
                        </div>
                      </div>

                      {/* Transition button (visual only) */}
                      <div className="mt-4 pt-3 border-t border-gray-800 opacity-0 group-hover:opacity-100 transition-opacity flex justify-end">
                        <button className="text-xs flex items-center gap-1 text-neo-warning hover:text-yellow-400">
                          Force Transition <span className="text-lg leading-none">→</span>
                        </button>
                      </div>
                    </motion.div>
                  ))}
                  {colInterventions.length === 0 && (
                    <div className="h-24 border-2 border-dashed border-gray-800/50 rounded-xl flex items-center justify-center text-gray-600 text-sm">
                      No tickets
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default Interventions;
