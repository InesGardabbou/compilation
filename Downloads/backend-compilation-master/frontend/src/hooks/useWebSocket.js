import { useState, useEffect, useCallback, useRef } from 'react';

const WS_URL = 'ws://localhost:8000/ws/dashboard';

export const useWebSocket = () => {
  const [messages, setMessages] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const ws = useRef(null);

  const connect = useCallback(() => {
    ws.current = new WebSocket(WS_URL);

    ws.current.onopen = () => {
      setIsConnected(true);
      console.log('WebSocket Connected to Neo-Sousse Dashboard');
    };

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setMessages((prev) => [data, ...prev].slice(0, 100)); // Keep last 100 messages
    };

    ws.current.onclose = () => {
      setIsConnected(false);
      console.log('WebSocket Disconnected. Reconnecting in 3s...');
      setTimeout(connect, 3000);
    };

    ws.current.onerror = (error) => {
      console.error('WebSocket Error:', error);
      ws.current.close();
    };
  }, []);

  useEffect(() => {
    connect();
    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [connect]);

  return { messages, isConnected };
};
