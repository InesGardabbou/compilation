import { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Users, Mail, Phone, Wrench, CheckCircle, XCircle, ShieldCheck } from 'lucide-react';
import GlassCard from '../components/ui/GlassCard';
import { motion } from 'framer-motion';

const Technicians = () => {
  const [technicians, setTechnicians] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchTechnicians();
  }, []);

  const fetchTechnicians = async () => {
    try {
      const response = await api.get('/techniciens');
      setTechnicians(response.data);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching technicians:", error);
      setLoading(false);
    }
  };

  const filteredTechs = filter === 'all' 
    ? technicians 
    : filter === 'dispo' 
      ? technicians.filter(t => t.disponible)
      : technicians.filter(t => !t.disponible);

  return (
    <div className="flex flex-col gap-6 h-full overflow-y-auto custom-scrollbar pb-6">
      <div className="flex justify-between items-center sticky top-0 bg-gray-900/80 backdrop-blur-md p-4 rounded-xl border border-gray-800 z-10">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3 text-white">
            <Users className="text-blue-400 w-8 h-8" />
            Technician Directory
          </h1>
          <p className="text-gray-400 mt-2 text-sm">Manage city maintenance personnel and dispatching</p>
        </div>

        <div className="flex gap-2">
          <button 
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-lg text-sm transition-colors ${filter === 'all' ? 'bg-blue-500 text-white' : 'bg-gray-800 text-gray-400'}`}
          >
            All Staff
          </button>
          <button 
            onClick={() => setFilter('dispo')}
            className={`px-4 py-2 rounded-lg text-sm transition-colors ${filter === 'dispo' ? 'bg-neo-success text-white' : 'bg-gray-800 text-gray-400'}`}
          >
            Available
          </button>
          <button 
            onClick={() => setFilter('busy')}
            className={`px-4 py-2 rounded-lg text-sm transition-colors ${filter === 'busy' ? 'bg-neo-warning text-white' : 'bg-gray-800 text-gray-400'}`}
          >
            In Intervention
          </button>
        </div>
      </div>

      {loading ? (
        <div className="flex-1 flex justify-center items-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredTechs.map((tech, i) => (
            <motion.div 
              key={tech.id_technicien}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              whileHover={{ y: -5 }}
            >
              <GlassCard className="h-full flex flex-col relative overflow-hidden group">
                {/* Decorative background element */}
                <div className={`absolute -right-10 -top-10 w-32 h-32 rounded-full blur-3xl opacity-20 ${tech.disponible ? 'bg-neo-success' : 'bg-neo-warning'}`}></div>
                
                <div className="flex items-start justify-between mb-4 relative z-10">
                  <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-gray-800 to-gray-900 border border-gray-700 flex items-center justify-center shadow-lg">
                    <span className="text-2xl font-bold text-gray-300">
                      {tech.prenom[0]}{tech.nom[0]}
                    </span>
                  </div>
                  <div className={`px-3 py-1 rounded-full border flex items-center gap-1 text-xs font-medium ${
                    tech.disponible 
                      ? 'bg-neo-success/10 border-neo-success/30 text-neo-success' 
                      : 'bg-neo-warning/10 border-neo-warning/30 text-neo-warning'
                  }`}>
                    {tech.disponible ? <CheckCircle className="w-3 h-3" /> : <XCircle className="w-3 h-3" />}
                    {tech.disponible ? 'Disponible' : 'Occupé'}
                  </div>
                </div>

                <div className="relative z-10">
                  <h3 className="text-xl font-bold text-white tracking-wide">{tech.prenom} {tech.nom}</h3>
                  <p className="text-blue-400 text-sm mt-1 mb-4 flex items-center gap-1">
                    <ShieldCheck className="w-4 h-4" /> {tech.specialite}
                  </p>
                </div>

                <div className="space-y-3 mt-auto relative z-10 pt-4 border-t border-gray-800/50">
                  <div className="flex items-center gap-3 text-sm text-gray-400">
                    <Mail className="w-4 h-4 text-gray-500" />
                    <span className="truncate">{tech.email}</span>
                  </div>
                  <div className="flex items-center gap-3 text-sm text-gray-400">
                    <Phone className="w-4 h-4 text-gray-500" />
                    <span>{tech.telephone}</span>
                  </div>
                </div>

                <div className="mt-6 pt-4 relative z-10 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button className="w-full py-2 bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 border border-blue-500/30 rounded-lg transition-colors flex justify-center items-center gap-2">
                    <Wrench className="w-4 h-4" /> Dispatch Task
                  </button>
                </div>
              </GlassCard>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Technicians;
