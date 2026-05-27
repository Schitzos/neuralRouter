import { useState, useEffect, useRef } from 'react';

interface RouterEvent {
  id: string;
  session_id: string;
  request_id: string;
  event_type: string;
  timestamp: string;
  data: Record<string, any>;
}

const STORAGE_KEY = 'schitzo_events';

function loadEvents(): RouterEvent[] {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? JSON.parse(stored) : [];
  } catch { return []; }
}

export const useWebSocket = (url: string) => {
  const [events, setEvents] = useState<RouterEvent[]>(loadEvents);
  const [isConnected, setIsConnected] = useState(false);
  const [lastEvent, setLastEvent] = useState<RouterEvent | null>(null);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(events.slice(-100)));
  }, [events]);

  useEffect(() => {
    const connect = () => {
      try {
        ws.current = new WebSocket(url);
        
        ws.current.onopen = () => {
          setIsConnected(true);
          console.log('WebSocket connected');
        };
        
        ws.current.onmessage = (event) => {
          try {
            const routerEvent: RouterEvent = JSON.parse(event.data);
            setLastEvent(routerEvent);
            setEvents(prev => [...prev.slice(-99), routerEvent]);
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
          }
        };
        
        ws.current.onclose = () => {
          setIsConnected(false);
          console.log('WebSocket disconnected, reconnecting...');
          setTimeout(connect, 3000);
        };
        
        ws.current.onerror = (error) => {
          console.error('WebSocket error:', error);
        };
      } catch (error) {
        console.error('Failed to connect WebSocket:', error);
        setTimeout(connect, 3000);
      }
    };

    connect();

    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [url]);

  const clearEvents = () => {
    setEvents([]);
    localStorage.removeItem(STORAGE_KEY);
  };

  return { events, isConnected, lastEvent, clearEvents };
};
