import { Home, MessageSquare, Share2, Brain, Database, ShieldAlert, Activity, Car, Wrench, Users, Radio, Map } from 'lucide-react';
import { motion } from 'framer-motion';

const Sidebar = ({ currentRoute, setCurrentRoute }) => {
  const navItems = [
    { id: 'dashboard', icon: Home, label: 'Dashboard' },
    { id: 'map', icon: Map, label: 'Map' },
    { id: 'automata', icon: Share2, label: 'Automata' },
    { id: 'ai-insights', icon: Brain, label: 'AI Reports' },
    { id: 'data-explorer', icon: Database, label: 'Data Explorer' },
    { id: 'test-scenarios', icon: ShieldAlert, label: 'Test Scenarios' },
    { id: 'sensors', icon: Radio, label: 'Live Sensors' },
    { id: 'vehicles', icon: Car, label: 'Vehicles' },
    { id: 'technicians', icon: Users, label: 'Technicians' },
    { id: 'nl-query', icon: MessageSquare, label: 'NLP Compiler' },
  ];

  return (
    <div className="w-64 h-screen glass-panel flex flex-col fixed left-0 top-0 z-50">
      <div className="p-6 flex items-center gap-3 border-b border-gray-800">
        <div className="w-10 h-10 rounded-xl bg-neo-primary/20 flex items-center justify-center border border-neo-primary/50 shadow-[0_0_15px_rgba(59,130,246,0.5)]">
          <Activity className="text-neo-primary w-6 h-6" />
        </div>
        <h1 className="text-xl font-bold tracking-wider text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500 neon-text">
          NEO-SOUSSE
        </h1>
      </div>

      <div className="flex-1 overflow-y-auto py-6 px-4 flex flex-col gap-2 custom-scrollbar">
        {navItems.map((item) => {
          const isActive = currentRoute === item.id;
          const Icon = item.icon;

          return (
            <motion.button
              key={item.id}
              whileHover={{ x: 5 }}
              onClick={() => setCurrentRoute(item.id)}
              className={`w-full flex items-center gap-4 px-4 py-3 rounded-lg transition-all duration-300 ${isActive
                ? 'bg-gradient-to-r from-neo-primary/20 to-transparent border-l-4 border-neo-primary text-white shadow-[inset_0_0_20px_rgba(59,130,246,0.1)]'
                : 'text-gray-400 hover:text-gray-200 hover:bg-white/5'
                }`}
            >
              <Icon className={`w-5 h-5 ${isActive ? 'text-neo-primary' : ''}`} />
              <span className="font-medium">{item.label}</span>
            </motion.button>
          );
        })}
      </div>

      <div className="p-4 border-t border-gray-800 text-xs text-center text-gray-500">
        v2.4.0 • System Online
      </div>
    </div>
  );
};

export default Sidebar;