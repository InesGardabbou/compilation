import { motion } from 'framer-motion';
import { TrendingUp } from 'lucide-react';

const KpiCard = ({ title, value, unit, icon: Icon, colorClass, delay = 0, change = null, isPositive = true }) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9, y: 20 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      whileHover={{ y: -5, shadow: '0 20px 40px rgba(59, 130, 246, 0.2)' }}
      className="relative overflow-hidden group rounded-2xl backdrop-blur-xl bg-gradient-to-br from-gray-800/40 to-gray-900/40 border border-gray-700/50 hover:border-neo-primary/30 transition-all duration-300 p-6"
    >
      {/* Animated background gradient */}
      <div className={`absolute top-0 right-0 w-40 h-40 bg-gradient-to-br ${colorClass} opacity-5 rounded-full blur-3xl -mr-20 -mt-20 group-hover:opacity-15 transition-opacity duration-500`}></div>
      <div className="absolute inset-0 bg-gradient-to-br from-neo-primary/0 to-transparent opacity-0 group-hover:opacity-5 transition-opacity duration-300 pointer-events-none"></div>
      
      <div className="relative z-10">
        <div className="flex justify-between items-start mb-4">
          <div className="flex-1">
            <p className="text-gray-400 text-xs font-semibold uppercase tracking-widest mb-3">{title}</p>
            <div className="flex items-baseline gap-2">
              <span className="text-4xl font-bold text-white">{value}</span>
              {unit && <span className="text-gray-400 text-sm font-medium">{unit}</span>}
            </div>
          </div>
          <motion.div
            whileHover={{ scale: 1.1, rotate: 5 }}
            className={`p-3 rounded-xl bg-gradient-to-br ${colorClass} opacity-80 group-hover:opacity-100 transition-all duration-300 border border-gray-600/30`}
          >
            <Icon className="w-6 h-6 text-white" />
          </motion.div>
        </div>

        {/* Change indicator */}
        {change && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className={`flex items-center gap-1 text-xs font-semibold mt-4 pt-4 border-t border-gray-700/30 ${isPositive ? 'text-green-400' : 'text-red-400'}`}
          >
            <TrendingUp className={`w-3 h-3 ${isPositive ? '' : 'rotate-180'}`} />
            <span>{isPositive ? '+' : '-'}{change}% from yesterday</span>
          </motion.div>
        )}
      </div>

      {/* Decorative corner accent */}
      <div className="absolute top-0 left-0 w-0.5 h-12 bg-gradient-to-b from-neo-primary to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
    </motion.div>
  );
};

export default KpiCard;
