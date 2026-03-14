/**
 * WebSocket Hook
 */
import { useEffect, useRef, useState, useCallback } from 'react';
import { buildWsUrl } from '../utils/fetchWithAuth';

interface WebSocketMessage {
  type: string;
  task_id?: number;
  data?: any;
  timestamp?: string;
  [key: string]: any;
}

export const useWebSocket = (url: string, clientId: string) => {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;

  const connect = useCallback(() => {
    try {
      const ws = new WebSocket(buildWsUrl(url, clientId));
      
      ws.onopen = () => {
        console.log('✅ WebSocket 连接成功');
        setIsConnected(true);
        reconnectAttempts.current = 0;
        
        // 发送心跳
        const heartbeat = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ 
              type: 'ping',
              timestamp: new Date().toISOString()
            }));
          }
        }, 30000);
        
        ws.onclose = () => {
          clearInterval(heartbeat);
        };
      };
      
      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          setLastMessage(message);
          
          if (message.type !== 'pong') {
            console.log('📨 收到消息:', message);
          }
        } catch (error) {
          console.error('❌ 解析消息失败:', error);
        }
      };
      
      ws.onerror = (error) => {
        console.error('❌ WebSocket 错误:', error);
      };
      
      ws.onclose = () => {
        console.log('🔌 WebSocket 连接关闭');
        setIsConnected(false);
        
        // 自动重连
        if (reconnectAttempts.current < maxReconnectAttempts) {
          reconnectAttempts.current++;
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000);
          console.log(`⏳ ${delay}ms 后尝试重连 (${reconnectAttempts.current}/${maxReconnectAttempts})`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, delay);
        } else {
          console.log('❌ 达到最大重连次数，停止重连');
        }
      };
      
      wsRef.current = ws;
    } catch (error) {
      console.error('❌ WebSocket 连接失败:', error);
    }
  }, [url, clientId]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('⚠️ WebSocket 未连接');
    }
  }, []);

  const subscribeTask = useCallback((taskId: number) => {
    console.log(`📡 订阅任务 ${taskId}`);
    sendMessage({ type: 'subscribe', task_id: taskId });
  }, [sendMessage]);

  const unsubscribeTask = useCallback((taskId: number) => {
    console.log(`📡 取消订阅任务 ${taskId}`);
    sendMessage({ type: 'unsubscribe', task_id: taskId });
  }, [sendMessage]);

  useEffect(() => {
    connect();
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    isConnected,
    lastMessage,
    sendMessage,
    subscribeTask,
    unsubscribeTask,
    reconnect: connect,
  };
};
