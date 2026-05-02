import { useState, useEffect } from 'react';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ComposedChart, Bar } from 'recharts';
import { motion } from 'framer-motion';
import GlassCard from '../ui/GlassCard';

const AdvancedChart = ({ data, chartType = 'area' }) => {
  const [chartData, setChartData] = useState([]);

  // Generate comprehensive mock data
  useEffect(() => {
    const initial = Array.from({ length: 24 }).map((_, i) => ({
      time: `${i}:00`,
      aqi: Math.floor(Math.random() * 80) + 20,
      temperature: Math.floor(Math.random() * 15) + 15,
      humidity: Math.floor(Math.random() * 40) + 40,
      pm25: Math.floor(Math.random() * 60) + 10,
    }));
    setChartData(initial);
  }, []);

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="glass-panel p-4 rounded-lg border border-gray-600/30 backdrop-blur-md"
        >
          <p className="text-gray-300 text-xs font-semibold mb-2">{payload[0].payload.time}</p>
          {payload.map((entry, index) => (
            <p key={index} className="text-sm font-semibold" style={{ color: entry.color }}>
              {entry.name}: {entry.value} {entry.name === 'AQI' ? 'µg/m³' : entry.name === 'Temperature' ? '°C' : '%'}
            </p>
          ))}
        </motion.div>
      );
    }
    return null;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
    >
      <GlassCard>
        <div className="p-6">
          <div className="mb-6">
            <h3 className="text-xl font-bold text-white mb-1">Air Quality Metrics</h3>
            <p className="text-gray-400 text-sm">24-hour trend analysis</p>
          </div>
          
          <ResponsiveContainer width="100%" height={300}>
            <ComposedChart data={chartData}>
              <defs>
                <linearGradient id="colorAqi" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="colorTemp" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(107,114,128,0.1)" />
              <XAxis dataKey="time" stroke="#6b7280" style={{ fontSize: '12px' }} />
              <YAxis stroke="#6b7280" style={{ fontSize: '12px' }} />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ paddingTop: '20px' }} />
              <Area type="monotone" dataKey="aqi" stroke="#3b82f6" fillOpacity={1} fill="url(#colorAqi)" name="AQI" />
              <Area type="monotone" dataKey="pm25" stroke="#ef4444" fillOpacity={0.6} fill="#ef4444" name="PM2.5" />
              <Line type="monotone" dataKey="temperature" stroke="#f59e0b" strokeWidth={2} dot={false} name="Temperature" />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </GlassCard>
    </motion.div>
  );
};

export default AdvancedChart;
