/** WebSocket hook for live captions */

import { useCallback, useEffect, useRef, useState } from "react";
import { createWebSocket, type WSMessage, type WSCaptionPayload } from "../api";

interface UseWebSocketOptions {
  sessionId: string | null;
  onCaption?: (caption: WSCaptionPayload) => void;
  onError?: (error: string) => void;
  onClose?: () => void;
}

interface UseWebSocketReturn {
  isConnected: boolean;
  sendAudio: (audioData: ArrayBuffer) => void;
  close: () => void;
  lastMessage: WSMessage | null;
}

export function useWebSocket({
  sessionId,
  onCaption,
  onError,
  onClose,
}: UseWebSocketOptions): UseWebSocketReturn {
  const wsRef = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WSMessage | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);

  const connect = useCallback(() => {
    if (!sessionId) return;

    const ws = createWebSocket(sessionId);
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
      console.log("WebSocket connected");
    };

    ws.onmessage = (event) => {
      try {
        const message: WSMessage = JSON.parse(event.data);
        setLastMessage(message);

        if (message.type === "caption" && onCaption) {
          onCaption(message.payload as WSCaptionPayload);
        } else if (message.type === "error" && onError) {
          onError((message.payload as { message: string }).message);
        }
      } catch (e) {
        console.error("Failed to parse WebSocket message:", e);
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
      if (onError) onError("WebSocket connection error");
    };

    ws.onclose = () => {
      setIsConnected(false);
      wsRef.current = null;
      if (onClose) onClose();

      // Attempt reconnect for active sessions
      if (sessionId) {
        reconnectTimeoutRef.current = window.setTimeout(() => {
          connect();
        }, 2000);
      }
    };
  }, [sessionId, onCaption, onError, onClose]);

  const sendAudio = useCallback((audioData: ArrayBuffer) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(audioData);
    }
  }, []);

  const close = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
  }, []);

  useEffect(() => {
    connect();
    return () => {
      close();
    };
  }, [connect, close]);

  return {
    isConnected,
    sendAudio,
    close,
    lastMessage,
  };
}