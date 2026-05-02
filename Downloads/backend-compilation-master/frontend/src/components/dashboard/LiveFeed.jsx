import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, AlertTriangle, Info, ChevronLeft, ChevronRight } from 'lucide-react';
import GlassCard from '../ui/GlassCard';

const LiveFeed = ({ messages }) => {
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 8;
  
  const totalPages = Math.ceil(messages.length / itemsPerPage);
  
  const currentMessages = messages.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const nextPage = () => {
    if (currentPage < totalPages) setCurrentPage(currentPage + 1);
  };

  const prevPage = () => {
    if (currentPage > 1) setCurrentPage(currentPage - 1);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.4 }}
      className="h-full"
    >
      <GlassCard className="h-full flex flex-col">
        {/* Header — mirrors AdvancedChart's p-6 + title block */}
        <div className="p-6 pb-0">
          <div className="mb-6">
            <h3 className="text-xl font-bold text-white mb-1 flex items-center gap-2">
              <Activity className="w-5 h-5 text-neo-primary" />
              Live Event Feed
            </h3>
            <p className="text-gray-400 text-sm">Real-time sensor updates</p>
          </div>
        </div>

        {/* Scrollable feed — fixed to h-[300px] to match chart height */}
        <div className="px-6 overflow-y-auto custom-scrollbar space-y-3 h-[300px]">
          <AnimatePresence initial={false}>
            {messages.length === 0 && (
              <div className="text-center text-gray-500 text-sm mt-10">
                Waiting for incoming data...
              </div>
            )}

            {currentMessages.map((msg, idx) => {
              const isAlert = msg.data && msg.data.pollution > 80;
              const globalIdx = idx + (currentPage - 1) * itemsPerPage;

              return (
                <motion.div
                  key={globalIdx}
                  initial={{ opacity: 0, x: -20, height: 0 }}
                  animate={{ opacity: 1, x: 0, height: 'auto' }}
                  exit={{ opacity: 0 }}
                  className={`p-3 rounded-lg border ${
                    isAlert
                      ? 'bg-neo-danger/10 border-neo-danger/30'
                      : 'bg-gray-800/40 border-gray-700/50'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <div className="mt-0.5">
                      {isAlert ? (
                        <AlertTriangle className="w-4 h-4 text-neo-danger" />
                      ) : (
                        <Info className="w-4 h-4 text-neo-primary" />
                      )}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between gap-4">
                        <span className="text-sm font-medium text-gray-200">
                          {msg.type || 'EVENT'}
                        </span>
                        <span className="text-xs text-gray-500 font-mono">
                          {new Date().toLocaleTimeString()}
                        </span>
                      </div>
                      {msg.data && (
                        <div className="mt-1 text-xs text-gray-400">
                          Zone {msg.data.id_zone}: Pol: {msg.data.pollution} | Tmp: {msg.data.temperature}°C
                        </div>
                      )}
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </AnimatePresence>
        </div>

        {/* Footer — pagination + WebSocket badge */}
        <div className="px-6 pb-6 mt-4">
          <div className="flex items-center justify-between pt-4 border-t border-gray-700/50">
            {totalPages > 1 ? (
              <>
                <button
                  onClick={prevPage}
                  disabled={currentPage === 1}
                  className="p-1 rounded bg-gray-800 text-gray-400 hover:text-white disabled:opacity-50 transition-colors"
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>
                <span className="text-xs text-gray-400 font-mono">
                  Page {currentPage} / {totalPages}
                </span>
                <button
                  onClick={nextPage}
                  disabled={currentPage === totalPages}
                  className="p-1 rounded bg-gray-800 text-gray-400 hover:text-white disabled:opacity-50 transition-colors"
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
              </>
            ) : (
              <span className="text-xs font-mono bg-neo-primary/10 text-neo-primary px-2 py-1 rounded-md border border-neo-primary/30 ml-auto">
                WebSocket
              </span>
            )}
          </div>
        </div>
      </GlassCard>
    </motion.div>
  );
};

export default LiveFeed;