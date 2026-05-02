import { useState } from 'react';
import Sidebar from './Sidebar';
import Topbar from './Topbar';
import { useWebSocket } from '../../hooks/useWebSocket';

const Layout = ({ children, currentRoute, setCurrentRoute }) => {
  const { isConnected, messages } = useWebSocket();

  return (
    <div className="min-h-screen bg-neo-bg text-gray-100 flex">
      <Sidebar currentRoute={currentRoute} setCurrentRoute={setCurrentRoute} />
      
      <div className="flex-1 ml-64 relative">
        <Topbar isConnected={isConnected} />
        
        <main className="pt-24 p-8 min-h-screen">
          {children({ wsMessages: messages, isConnected })}
        </main>
      </div>
    </div>
  );
};

export default Layout;
