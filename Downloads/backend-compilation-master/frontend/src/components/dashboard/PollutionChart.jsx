import { useState, useEffect } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import GlassCard from '../ui/GlassCard';

const PollutionChart = ({ data }) => {
  const [chartData, setChartData] = useState([]);

  // Generate some initial mock data if no real data
  useEffect(() => {
    if (chartData.length === 0) {
      const initial = Array.from({ length: 20 }).map((_, i) => ({
        time: new Date(Date.now() - (20 - i) * 60000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        pollution: Math.floor(Math.random() * 40) + 30
      }));
      setChartData(initial);
    }
  }, []);

  // Update with live WS data
  useEffect(() => {
    if (data && data.length > 0) {
      const latest = data[0];
      if (latest && latest.data && latest.data.pollution) {
        setChartData(prev => {
          const newData = [...prev.slice(1), {
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
            pollution: latest.data.pollution
          }];
          return newData;
        });
      }
    }
  }, [data]);

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="glass-panel p-3 rounded border border-gray-700/50">
          <p className="text-gray-400 text-xs mb-1">{label}</p>
          <p className="text-neo-primary font-bold">
            AQI: {payload[0].value}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <GlassCard delay={0.3} className="h-full">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-200">Average Pollution Level</h3>
        <p className="text-xs text-gray-500">Real-time Air Quality Index (AQI)</p>
      </div>
      
      <div className="h-[250px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="colorPollution" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4}/>
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
            <XAxis 
              dataKey="time" 
              stroke="#6b7280" 
              fontSize={10} 
              tickMargin={10}
              tickLine={false}
              axisLine={false}
            />
            <YAxis 
              stroke="#6b7280" 
              fontSize={10}
              tickLine={false}
              axisLine={false}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ stroke: '#3b82f6', strokeWidth: 1, strokeDasharray: '4 4' }} />
            <Area 
              type="monotone" 
              dataKey="pollution" 
              stroke="#00f0ff" 
              strokeWidth={2}
              fillOpacity={1} 
              fill="url(#colorPollution)" 
              isAnimationActive={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </GlassCard>
  );
};

export default PollutionChart;
