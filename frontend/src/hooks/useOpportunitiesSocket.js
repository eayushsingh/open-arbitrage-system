import { useEffect, useRef, useState, useCallback } from 'react';

// WebSocket hook for subscribing to opportunities stream.
// Keeps a robust reconnect strategy with exponential backoff and exposes connection state.

export default function useOpportunitiesSocket(url) {
  const wsRef = useRef(null);
  const reconnectRef = useRef(0);
  const heartbeatRef = useRef(null);
  const [status, setStatus] = useState('connecting'); // connecting | open | closed | error | reconnecting
  const [data, setData] = useState([]);
  const [lastMessageAt, setLastMessageAt] = useState(null);

  const connect = useCallback(() => {
    setStatus(prev => (prev === 'open' ? prev : 'connecting'));
    wsRef.current = new WebSocket(url);

    wsRef.current.onopen = () => {
      reconnectRef.current = 0;
      setStatus('open');
      // start heartbeat to detect dead connections
      heartbeatRef.current = setInterval(() => {
        try {
          wsRef.current.send(JSON.stringify({ type: 'ping' }));
        } catch (err) {
          // ignore
        }
      }, 25000);
    };

    wsRef.current.onmessage = (evt) => {
      setLastMessageAt(new Date());
      try {
        const parsed = JSON.parse(evt.data);
        // Expecting array or single object
        if (Array.isArray(parsed)) {
          setData(parsed);
        } else if (parsed && parsed.type === 'update' && parsed.payload) {
          // merge single updates by id
          setData(prev => {
            const idx = prev.findIndex(i => i.id === parsed.payload.id);
            if (idx === -1) return [parsed.payload, ...prev];
            const copy = [...prev];
            copy[idx] = { ...copy[idx], ...parsed.payload };
            return copy;
          });
        } else {
          // fallback: replace
          setData(typeof parsed === 'object' ? parsed : []);
        }
      } catch (err) {
        console.error('ws parse error', err);
      }
    };

    wsRef.current.onclose = () => {
      setStatus('closed');
      clearInterval(heartbeatRef.current);
      // attempt reconnect
      const timeout = Math.min(30000, 1000 * 2 ** reconnectRef.current);
      reconnectRef.current += 1;
      setStatus('reconnecting');
      setTimeout(() => connect(), timeout);
    };

    wsRef.current.onerror = (e) => {
      console.error('ws error', e);
      setStatus('error');
      try { wsRef.current.close(); } catch (err) {}
    };
  }, [url]);

  useEffect(() => {
    connect();
    return () => {
      clearInterval(heartbeatRef.current);
      try { wsRef.current && wsRef.current.close(); } catch (err) {}
    };
  }, [connect]);

  // manual reconnect
  const reconnect = useCallback(() => {
    try { wsRef.current && wsRef.current.close(); } catch (err) {}
    reconnectRef.current = 0;
    connect();
  }, [connect]);

  return { data, status, lastMessageAt, reconnect };
}
