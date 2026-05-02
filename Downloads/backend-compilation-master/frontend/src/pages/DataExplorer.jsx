import { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Database, Search, Filter, ChevronLeft, ChevronRight, Activity, Wrench, Radio, Car, Users } from 'lucide-react';
import GlassCard from '../components/ui/GlassCard';
import { motion } from 'framer-motion';

const DataExplorer = () => {
  const [activeTab, setActiveTab] = useState('mesures');
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 15;

  // Fetch data
  useEffect(() => {
    fetchData();
  }, [activeTab]);

  const fetchData = async () => {
    setLoading(true);
    try {
      let response;
      if (activeTab === 'mesures') {
        response = await api.get('/mesures?limit=100');
      } else if (activeTab === 'capteurs') {
        response = await api.get('/capteurs');
      } else if (activeTab === 'interventions') {
        response = await api.get('/interventions/all'); // Use /all to get more than 5
      } else if (activeTab === 'vehicules') {
        response = await api.get('/vehicules');
      } else if (activeTab === 'techniciens') {
        response = await api.get('/techniciens');
      }
      setData(response.data);
      setCurrentPage(1); 
    } catch (error) {
      console.error(`Error fetching ${activeTab}:`, error);
      setData([]);
    } finally {
      setLoading(false);
    }
  };

  const totalPages = Math.ceil(data.length / itemsPerPage);
  const paginatedData = data.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const getStatusColor = (status) => {
    if (!status) return 'text-gray-400 bg-gray-800 border-gray-600';
    const s = status.toLowerCase();
    if (s.includes('actif') || s.includes('termine') || s.includes('disponible') || s === 'true') 
      return 'text-neo-success bg-neo-success/10 border-neo-success/30';
    if (s.includes('maintenance') || s.includes('signale') || s.includes('cours') || s.includes('planif')) 
      return 'text-neo-warning bg-neo-warning/10 border-neo-warning/30';
    if (s.includes('service') || s.includes('critique') || s.includes('annul')) 
      return 'text-neo-danger bg-neo-danger/10 border-neo-danger/30';
    return 'text-gray-400 bg-gray-800 border-gray-600';
  };

  const renderTableHeaders = () => {
    switch (activeTab) {
      case 'mesures':
        return (
          <tr>
            <th className="px-4 py-3 text-left">ID</th>
            <th className="px-4 py-3 text-left">Capteur ID</th>
            <th className="px-4 py-3 text-left">Pollution (AQI)</th>
            <th className="px-4 py-3 text-left">Temperature (°C)</th>
            <th className="px-4 py-3 text-left">Timestamp</th>
          </tr>
        );
      case 'capteurs':
        return (
          <tr>
            <th className="px-4 py-3 text-left">ID</th>
            <th className="px-4 py-3 text-left">Type</th>
            <th className="px-4 py-3 text-left">Zone ID</th>
            <th className="px-4 py-3 text-left">Battery</th>
            <th className="px-4 py-3 text-left">Status</th>
          </tr>
        );
      case 'interventions':
        return (
          <tr>
            <th className="px-4 py-3 text-left">ID</th>
            <th className="px-4 py-3 text-left">Zone ID</th>
            <th className="px-4 py-3 text-left">Nature</th>
            <th className="px-4 py-3 text-left">Priority</th>
            <th className="px-4 py-3 text-left">Status</th>
          </tr>
        );
      case 'vehicules':
        return (
          <tr>
            <th className="px-4 py-3 text-left">ID</th>
            <th className="px-4 py-3 text-left">Model</th>
            <th className="px-4 py-3 text-left">Type</th>
            <th className="px-4 py-3 text-left">Battery</th>
            <th className="px-4 py-3 text-left">Status</th>
          </tr>
        );
      case 'techniciens':
        return (
          <tr>
            <th className="px-4 py-3 text-left">ID</th>
            <th className="px-4 py-3 text-left">Name</th>
            <th className="px-4 py-3 text-left">Specialty</th>
            <th className="px-4 py-3 text-left">Certification</th>
            <th className="px-4 py-3 text-left">Available</th>
          </tr>
        );
      default: return null;
    }
  };

  const renderTableRow = (item) => {
    switch (activeTab) {
      case 'mesures':
        return (
          <tr key={item.id_mesure} className="border-b border-gray-800/50 hover:bg-white/5 transition-colors">
            <td className="px-4 py-3 font-mono text-xs text-gray-500">{item.id_mesure}</td>
            <td className="px-4 py-3 font-mono">{item.id_capteur}</td>
            <td className={`px-4 py-3 font-bold ${item.pollution > 80 ? 'text-neo-danger' : item.pollution > 50 ? 'text-neo-warning' : 'text-neo-success'}`}>
              {item.pollution?.toFixed(1) || 0}
            </td>
            <td className="px-4 py-3 text-gray-300">{item.temperature?.toFixed(1) || 0}°</td>
            <td className="px-4 py-3 text-sm text-gray-500">{new Date(item.timestamp).toLocaleString()}</td>
          </tr>
        );
      case 'capteurs':
        return (
          <tr key={item.id_capteur} className="border-b border-gray-800/50 hover:bg-white/5 transition-colors">
            <td className="px-4 py-3 font-mono text-xs text-gray-500">{item.id_capteur}</td>
            <td className="px-4 py-3 uppercase text-xs tracking-wider text-blue-400">{item.type_capteur}</td>
            <td className="px-4 py-3">Zone {item.id_zone}</td>
            <td className="px-4 py-3">
              <div className="flex items-center gap-2">
                <div className="w-16 h-1.5 bg-gray-800 rounded-full overflow-hidden">
                  <div className={`h-full ${item.batterie_pct > 20 ? 'bg-neo-success' : 'bg-neo-danger'}`} style={{ width: `${item.batterie_pct}%` }}></div>
                </div>
                <span className="text-xs font-mono">{item.batterie_pct}%</span>
              </div>
            </td>
            <td className="px-4 py-3">
              <span className={`px-2 py-1 rounded text-[10px] font-bold uppercase border ${getStatusColor(item.statut)}`}>
                {item.statut}
              </span>
            </td>
          </tr>
        );
      case 'interventions':
        return (
          <tr key={item.id_intervention} className="border-b border-gray-800/50 hover:bg-white/5 transition-colors">
            <td className="px-4 py-3 font-mono text-xs text-gray-500">INT-{item.id_intervention}</td>
            <td className="px-4 py-3">Zone {item.id_zone}</td>
            <td className="px-4 py-3 text-sm text-gray-300">{item.nature_intervention || 'Maintenance'}</td>
            <td className="px-4 py-3">
              <span className={`px-2 py-1 rounded text-[10px] font-bold uppercase border ${getStatusColor(item.priorite)}`}>
                {item.priorite}
              </span>
            </td>
            <td className="px-4 py-3">
              <span className={`px-2 py-1 rounded text-[10px] font-bold uppercase border ${getStatusColor(item.statut)}`}>
                {item.statut?.replace('_', ' ')}
              </span>
            </td>
          </tr>
        );
      case 'vehicules':
        return (
          <tr key={item.id_vehicule} className="border-b border-gray-800/50 hover:bg-white/5 transition-colors">
            <td className="px-4 py-3 font-mono text-xs text-gray-500">{item.id_vehicule}</td>
            <td className="px-4 py-3 font-medium text-white">{item.modele}</td>
            <td className="px-4 py-3 text-xs text-blue-400 uppercase tracking-wider">{item.type_vehicule}</td>
            <td className="px-4 py-3 text-sm">{item.batterie_pct}%</td>
            <td className="px-4 py-3">
              <span className={`px-2 py-1 rounded text-[10px] font-bold uppercase border ${getStatusColor(item.statut)}`}>
                {item.statut}
              </span>
            </td>
          </tr>
        );
      case 'techniciens':
        return (
          <tr key={item.id_technicien} className="border-b border-gray-800/50 hover:bg-white/5 transition-colors">
            <td className="px-4 py-3 font-mono text-xs text-gray-500">{item.id_technicien}</td>
            <td className="px-4 py-3 font-medium text-white">{item.prenom} {item.nom}</td>
            <td className="px-4 py-3 text-sm text-gray-300">{item.specialite}</td>
            <td className="px-4 py-3 text-xs text-gray-500 italic">{item.certification}</td>
            <td className="px-4 py-3">
              <span className={`px-2 py-1 rounded text-[10px] font-bold uppercase border ${getStatusColor(String(item.disponible))}`}>
                {item.disponible ? 'Available' : 'Busy'}
              </span>
            </td>
          </tr>
        );
      default: return null;
    }
  };

  const tabs = [
    { id: 'mesures', label: 'Mesures', icon: Activity },
    { id: 'capteurs', label: 'Capteurs', icon: Radio },
    { id: 'interventions', label: 'Interventions', icon: Wrench },
    { id: 'vehicules', label: 'Véhicules', icon: Car },
    { id: 'techniciens', label: 'Techniciens', icon: Users },
  ];

  return (
    <div className="flex flex-col gap-6 h-full">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3 text-white">
            <Database className="text-blue-500 w-8 h-8" />
            Data Explorer
          </h1>
          <p className="text-gray-400 mt-2 text-sm">Browse, filter, and inspect core database entities</p>
        </div>
        
        <div className="flex bg-gray-900/50 p-1 rounded-lg border border-gray-800 overflow-x-auto">
          {tabs.map(tab => (
            <button 
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-2 whitespace-nowrap ${activeTab === tab.id ? 'bg-blue-500 text-white shadow-lg' : 'text-gray-400 hover:text-white hover:bg-gray-800'}`}
            >
              <tab.icon className="w-4 h-4" /> {tab.label}
            </button>
          ))}
        </div>
      </div>

      <GlassCard className="flex-1 flex flex-col p-0 overflow-hidden">
        {/* Toolbar */}
        <div className="p-4 border-b border-gray-800 flex justify-between items-center bg-black/20">
          <div className="flex items-center gap-4">
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
              <input 
                type="text" 
                placeholder={`Search ${activeTab}...`} 
                className="bg-gray-900 border border-gray-700 rounded-lg pl-9 pr-4 py-2 text-sm text-white focus:outline-none focus:border-blue-500 w-64"
              />
            </div>
            <button className="flex items-center gap-2 px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-sm text-gray-300 hover:bg-gray-800 transition-colors">
              <Filter className="w-4 h-4" /> Filters
            </button>
          </div>
          <div className="text-sm text-gray-500 font-mono">
            {data.length} total records found
          </div>
        </div>

        {/* Table Area */}
        <div className="flex-1 overflow-auto custom-scrollbar relative">
          {loading ? (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            </div>
          ) : (
            <table className="w-full whitespace-nowrap text-sm text-gray-300">
              <thead className="bg-gray-900/80 sticky top-0 z-10 text-gray-400 border-b border-gray-800 backdrop-blur-md">
                {renderTableHeaders()}
              </thead>
              <tbody>
                {paginatedData.map(renderTableRow)}
              </tbody>
            </table>
          )}
        </div>

        {/* Pagination */}
        <div className="p-4 border-t border-gray-800 flex justify-between items-center bg-black/20">
          <span className="text-sm text-gray-500">
            Showing {data.length > 0 ? ((currentPage - 1) * itemsPerPage) + 1 : 0} to {Math.min(currentPage * itemsPerPage, data.length)} of {data.length}
          </span>
          <div className="flex items-center gap-2">
            <button 
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="p-1 rounded-md border border-gray-700 text-gray-400 hover:bg-gray-800 disabled:opacity-50 transition-colors"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <span className="text-sm font-mono px-2">Page {currentPage} / {totalPages || 1}</span>
            <button 
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages || totalPages === 0}
              className="p-1 rounded-md border border-gray-700 text-gray-400 hover:bg-gray-800 disabled:opacity-50 transition-colors"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      </GlassCard>
    </div>
  );
};

export default DataExplorer;
