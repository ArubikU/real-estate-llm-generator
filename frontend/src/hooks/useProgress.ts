import { useState, useEffect, useCallback, useRef } from 'react';

export type ProgressData = {
  progress: number;
  status: string;
  message: string;
  stage: string;
  substage?: string;
  step?: number;
  total_steps?: number;
  url?: string;
}

export type ProgressState = ProgressData & {
  isConnected: boolean;
  isComplete: boolean;
  hasError: boolean;
  errorMessage?: string;
}

interface UseProgressOptions {
  onComplete?: (data: any) => void;
  onError?: (error: string) => void;
  onProgress?: (data: ProgressData) => void;
}

export function useProgress(taskId: string | null, options: UseProgressOptions = {}) {
  const [state, setState] = useState<ProgressState>({
    progress: 0,
    status: '',
    message: '',
    stage: '',
    isConnected: false,
    isComplete: false,
    hasError: false,
  });

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;
  const optionsRef = useRef(options);
  const isCompleteRef = useRef(false);
  
  // Keep options ref updated
  useEffect(() => {
    optionsRef.current = options;
  }, [options]);
  
  // Keep isComplete ref updated
  useEffect(() => {
    isCompleteRef.current = state.isComplete;
  }, [state.isComplete]);

  const connect = useCallback(() => {
    if (!taskId || wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsHost = import.meta.env.VITE_WS_URL || 'localhost:8000';
    const wsUrl = `${wsProtocol}//${wsHost}/ws/progress/${taskId}/`;

    console.log('🔌 Connecting to WebSocket:', wsUrl);

    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('✅ WebSocket connected for task:', taskId);
        reconnectAttemptsRef.current = 0;
        setState((prev) => ({ ...prev, isConnected: true }));
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('📨 WebSocket message:', data);

          switch (data.type) {
            case 'connected':
              console.log('✅ Connection confirmed:', data.message);
              break;

            case 'progress':
              const progressData: ProgressData = {
                progress: data.progress || 0,
                status: data.status || '',
                message: data.message || '',
                stage: data.stage || '',
                substage: data.substage,
                step: data.step,
                total_steps: data.total_steps,
                url: data.url,
              };

              setState((prev) => ({
                ...prev,
                ...progressData,
              }));

              if (optionsRef.current.onProgress) {
                optionsRef.current.onProgress(progressData);
              }
              break;

            case 'complete':
              console.log('🎉 Task complete:', data.message);
              setState((prev) => ({
                ...prev,
                isComplete: true,
                progress: 100,
                message: data.message,
              }));

              if (optionsRef.current.onComplete) {
                optionsRef.current.onComplete(data.data);
              }

              // Close WebSocket after completion
              setTimeout(() => {
                ws.close();
              }, 1000);
              break;

            case 'error':
              console.error('❌ Task error:', data.message);
              setState((prev) => ({
                ...prev,
                hasError: true,
                errorMessage: data.error || data.message,
                message: data.message,
              }));

              if (optionsRef.current.onError) {
                optionsRef.current.onError(data.error || data.message);
              }
              break;

            default:
              console.warn('Unknown message type:', data.type);
          }
        } catch (error) {
          console.error('❌ Error parsing WebSocket message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        setState((prev) => ({
          ...prev,
          hasError: true,
          errorMessage: 'WebSocket connection error',
        }));
      };

      ws.onclose = (event) => {
        console.log('🔌 WebSocket closed:', event.code, event.reason);
        setState((prev) => ({ ...prev, isConnected: false }));
        wsRef.current = null;

        // Attempt to reconnect if not intentionally closed
        if (
          event.code !== 1000 &&
          !isCompleteRef.current &&
          reconnectAttemptsRef.current < maxReconnectAttempts
        ) {
          reconnectAttemptsRef.current++;
          const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 10000);
          console.log(`🔄 Reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current})...`);

          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, delay);
        }
      };
    } catch (error) {
      console.error('❌ Error creating WebSocket:', error);
      setState((prev) => ({
        ...prev,
        hasError: true,
        errorMessage: 'Failed to create WebSocket connection',
      }));
    }
  }, [taskId]); // Only depend on taskId

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    if (wsRef.current) {
      wsRef.current.close(1000, 'Client disconnect');
      wsRef.current = null;
    }

    setState((prev) => ({ ...prev, isConnected: false }));
  }, []);

  const reset = useCallback(() => {
    disconnect();
    setState({
      progress: 0,
      status: '',
      message: '',
      stage: '',
      isConnected: false,
      isComplete: false,
      hasError: false,
    });
    reconnectAttemptsRef.current = 0;
  }, [disconnect]);

  // Connect when taskId changes
  useEffect(() => {
    if (taskId) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [taskId]); // Removed connect and disconnect from dependencies

  return {
    ...state,
    connect,
    disconnect,
    reset,
  };
}
