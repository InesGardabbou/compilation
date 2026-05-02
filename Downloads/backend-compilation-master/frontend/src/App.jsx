import { useState } from 'react';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import AIInsights from './pages/AIInsights';
import NLQuery from './pages/NLQuery';
import LiveSensors from './pages/LiveSensors';
import Vehicles from './pages/Vehicles';
import Interventions from './pages/Interventions';
import Technicians from './pages/Technicians';
import MapDashboard from './pages/MapDashboard';
import DataExplorer from './pages/DataExplorer';
import Automata from './pages/Automata';
import TestScenarios from './pages/TestScenarios';

function App() {
  const [currentRoute, setCurrentRoute] = useState('dashboard');

  return (
    <Layout currentRoute={currentRoute} setCurrentRoute={setCurrentRoute}>
      {({ wsMessages, isConnected }) => (
        <>
          {currentRoute === 'dashboard' && (
            <Dashboard wsMessages={wsMessages} isConnected={isConnected} />
          )}
          {currentRoute === 'ai-insights' && <AIInsights />}
          {currentRoute === 'nl-query' && <NLQuery />}
          {currentRoute === 'sensors' && <LiveSensors wsMessages={wsMessages} />}
          {currentRoute === 'vehicles' && <Vehicles />}
          {currentRoute === 'technicians' && <Technicians />}
          {currentRoute === 'map' && <MapDashboard wsMessages={wsMessages} />}
          {currentRoute === 'data-explorer' && <DataExplorer />}
          {currentRoute === 'automata' && <Automata />}
          {currentRoute === 'test-scenarios' && <TestScenarios />}
          
          {/* Fallback for empty routes */}
          {[''].includes(currentRoute) && (
            <div className="flex-1 flex flex-col items-center justify-center h-[calc(100vh-120px)] border-2 border-dashed border-gray-800 rounded-xl bg-gray-900/20">
              <div className="w-16 h-16 mb-4 text-gray-700 animate-pulse">
                <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
              </div>
              <h2 className="text-xl font-medium text-gray-500">Module in Development</h2>
              <p className="text-gray-600 text-sm mt-2">The {currentRoute} module is currently being integrated with the backend.</p>
            </div>
          )}
        </>
      )}
    </Layout>
  );
}

export default App;
