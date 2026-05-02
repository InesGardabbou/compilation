import { motion, AnimatePresence } from 'framer-motion';
import { AlertCircle, CheckCircle, Info, Zap } from 'lucide-react';

const AlertPanel = ({ alerts = [] }) => {
  const defaultAlerts = [
    { id: 1, type: 'critical', title: 'High AQI Detected', message: 'Pollution levels exceed safe limits in Zone 3', time: '2 min ago', value: '156 AQI' },
    { id: 2, type: 'warning', title: 'Sensor Malfunction', message: 'Sensor 47 in Downtown requires maintenance', time: '15 min ago', value: 'Sensor 47' },
    { id: 3, type: 'info', title: 'System Update', message: 'Dashboard upgraded with new analytics', time: '1 hour ago', value: 'v2.4.0' },
  ];

  const displayAlerts = alerts.length > 0 ? alerts : defaultAlerts;

  const getAlertIcon = (type) => {
    switch (type) {
      case 'critical': return <AlertCircle className="w-5 h-5" />;
      case 'warning': return <Zap className="w-5 h-5" />;
      case 'success': return <CheckCircle className="w-5 h-5" />;
      default: return <Info className="w-5 h-5" />;
    }
  };

  const getAlertColor = (type) => {
    switch (type) {
      case 'critical': return 'from-red-500/20 to-red-600/10 border-red-500/30 text-red-400';
      case 'warning': return 'from-yellow-500/20 to-yellow-600/10 border-yellow-500/30 text-yellow-400';
      case 'success': return 'from-green-500/20 to-green-600/10 border-green-500/30 text-green-400';
      default: return 'from-blue-500/20 to-blue-600/10 border-blue-500/30 text-blue-400';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.4 }}
      className="rounded-2xl backdrop-blur-xl bg-gradient-to-br from-gray-800/40 to-gray-900/40 border border-gray-700/50 overflow-hidden"
    >
      <div className="p-6 border-b border-gray-700/30">
        <h3 className="text-lg font-bold text-white flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-neo-primary" />
          Active Alerts
        </h3>
      </div>
      
      <div className="max-h-72 overflow-y-auto">
        <AnimatePresence>
          {displayAlerts.map((alert, index) => (
            <motion.div
              key={alert.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
              className={`p-4 border-b border-gray-700/20 last:border-b-0 bg-gradient-to-r ${getAlertColor(alert.type)} border-l-4 hover:bg-opacity-100 transition-all duration-200 cursor-pointer group`}
            >
              <div className="flex gap-3">
                <div className="flex-shrink-0 mt-0.5">
                  {getAlertIcon(alert.type)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="font-semibold text-white group-hover:text-opacity-100 transition-all">{alert.title}</p>
                      <p className="text-sm text-gray-300 mt-1">{alert.message}</p>
                    </div>
                    <span className="text-xs font-mono bg-black/20 px-2 py-1 rounded whitespace-nowrap ml-2">{alert.value}</span>
                  </div>
                  <p className="text-xs text-gray-400 mt-2">{alert.time}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

export default AlertPanel;
