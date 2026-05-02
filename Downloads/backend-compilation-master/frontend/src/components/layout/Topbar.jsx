import { Bell, Search, User, Zap } from 'lucide-react';

const Topbar = ({ isConnected }) => {
  return (
    <div className="h-20 glass-panel fixed top-0 right-0 left-64 z-40 flex items-center justify-between px-8 border-b border-gray-800/50">
      <div className="flex items-center gap-4 w-96">
        <div className="relative w-full">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input 
            type="text" 
            placeholder="Search zones, sensors, technicians..." 
            className="w-full bg-gray-900/50 border border-gray-700 rounded-full py-2 pl-10 pr-4 text-sm focus:outline-none focus:border-neo-primary/50 focus:ring-1 focus:ring-neo-primary/50 transition-all text-white placeholder-gray-500"
          />
        </div>
      </div>

      <div className="flex items-center gap-6">
        {/* System Status */}
        <div className="flex items-center gap-2 bg-gray-900/50 px-4 py-1.5 rounded-full border border-gray-800">
          <div className="relative flex h-3 w-3">
            {isConnected ? (
              <>
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-neo-success opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-neo-success"></span>
              </>
            ) : (
              <span className="relative inline-flex rounded-full h-3 w-3 bg-neo-danger"></span>
            )}
          </div>
          <span className="text-xs font-medium tracking-wide text-gray-300">
            {isConnected ? 'LIVE FEED ACTIVE' : 'DISCONNECTED'}
          </span>
        </div>

        {/* Action Icons */}
        <div className="flex items-center gap-4">
          <button className="relative p-2 text-gray-400 hover:text-white transition-colors">
            <Bell className="w-5 h-5" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-neo-danger rounded-full shadow-[0_0_8px_rgba(239,68,68,0.8)]"></span>
          </button>
          <button className="p-2 text-gray-400 hover:text-white transition-colors">
            <Zap className="w-5 h-5" />
          </button>
          <div className="w-px h-6 bg-gray-700 mx-2"></div>
          <button className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-neo-primary to-neo-purple p-0.5">
              <div className="w-full h-full bg-gray-900 rounded-full flex items-center justify-center">
                <User className="w-5 h-5 text-gray-300" />
              </div>
            </div>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Topbar;
