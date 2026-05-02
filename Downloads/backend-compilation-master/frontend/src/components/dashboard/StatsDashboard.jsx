import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Activity } from 'lucide-react';

const StatCard = ({ title, value, change, isPositive, icon: Icon, delay }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      className="group relative p-6 rounded-2xl backdrop-blur-xl bg-gradient-to-br from-gray-800/40 to-gray-900/40 border border-gray-700/50 hover:border-neo-primary/30 transition-all duration-300 overflow-hidden"
    >
      {/* Background gradient effect */}
      <div className="absolute inset-0 bg-gradient-to-br from-neo-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
      
      {/* Content */}
      <div className="relative z-10">
        <div className="flex items-start justify-between mb-4">
          <div>
            <p className="text-gray-400 text-sm font-medium uppercase tracking-wider mb-2">{title}</p>
            <div className="flex items-baseline gap-2">
              <span className="text-4xl font-bold text-white">{value}</span>
              <div className={`flex items-center gap-1 px-2 py-1 rounded-lg ${isPositive ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'}`}>
                {isPositive ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                <span className="text-xs font-semibold">{change}%</span>
              </div>
            </div>
          </div>
          <div className="p-3 rounded-xl bg-gradient-to-br from-neo-primary/20 to-blue-600/20 border border-neo-primary/30">
            <Icon className="w-6 h-6 text-neo-primary" />
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default StatCard;
