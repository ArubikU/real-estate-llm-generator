import { useEffect, useRef, useState, useCallback } from 'react';

export interface ProgressUpdate {
  progress: number; // 0-100
  status: string;
  stage?: string;
  substage?: string;
  step?: number;
  total_steps?: number;
  data?: any;
}

interface UseProgressWebSocketProps {
  onComplete?: (data: any) => void;
  onError?: (error: string) => void;
}

export const useProgressWebSocket = ({ onComplete, onError }: UseProgressWebSocketProps = {}) => {
  const [progress, setProgress] = useState<ProgressUpdate>({
    progress: 0,
    status: 'Iniciando...',
  });
  const [isConnected, setIsConnected] = useState(false);
  const [taskId, setTaskId] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  const connect = useCallback((newTaskId: string) => {
    // Close existing connection if any
    if (wsRef.current) {
      wsRef.current.close();
    }

    setTaskId(newTaskId);
    setProgress({ progress: 0, status: 'Conectando...' });

    // Determine WebSocket URL
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    const wsBaseUrl = apiUrl
      .replace('http://', '')
      .replace('https://', '')
      .replace(/\/$/, '');
    
    const wsUrl = `${wsProtocol}//${wsBaseUrl}/ws/progress/${newTaskId}/`;
    
    console.log('🔌 Connecting to WebSocket:', wsUrl);

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('✅ WebSocket connected');
      setIsConnected(true);
      setProgress({ progress: 0, status: 'Conectado' });
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('📨 Progress update:', data);

        if (data.type === 'progress') {
          setProgress({
            progress: data.progress || 0,
            status: data.status || data.message || 'Procesando...',
            stage: data.stage,
            substage: data.substage,
            step: data.step,
            total_steps: data.total_steps,
          });
        } else if (data.type === 'complete') {
          setProgress({
            progress: 100,
            status: data.message || 'Completado',
            stage: 'Completado',
          });
          if (onComplete) {
            onComplete(data.data);
          }
          // Close connection after completion
          setTimeout(() => {
            ws.close();
          }, 1000);
        } else if (data.type === 'error') {
          setProgress({
            progress: 0,
            status: `Error: ${data.message}`,
            stage: 'Error',
          });
          if (onError) {
            onError(data.message);
          }
        }
      } catch (error) {
        console.error('❌ Error parsing WebSocket message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('❌ WebSocket error:', error);
      setIsConnected(false);
      setProgress({
        progress: 0,
        status: 'Error de conexión',
        stage: 'Error',
      });
      if (onError) {
        onError('Error de conexión WebSocket');
      }
    };

    ws.onclose = () => {
      console.log('🔌 WebSocket disconnected');
      setIsConnected(false);
    };

    return () => {
      ws.close();
    };
  }, [onComplete, onError]);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
    setTaskId(null);
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  return {
    progress,
    isConnected,
    taskId,
    connect,
    disconnect,
    reset: () => setProgress({ progress: 0, status: 'Listo' }),
  };
};
