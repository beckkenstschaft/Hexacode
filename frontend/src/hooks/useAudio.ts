/** Audio recording hook for microphone capture */

import { useCallback, useEffect, useRef, useState } from "react";

interface UseAudioOptions {
  onData: (data: ArrayBuffer) => void;
  sampleRate?: number;
  chunkSize?: number;
}

export function useAudio({ onData, sampleRate = 16000, chunkSize = 4096 }: UseAudioOptions) {
  const [isRecording, setIsRecording] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const start = useCallback(async () => {
    try {
      setError(null);

      // Get user media
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });

      streamRef.current = stream;

      // Create audio context for processing
      const audioContext = new AudioContext({ sampleRate });
      audioContextRef.current = audioContext;

      // Create source from stream
      const source = audioContext.createMediaStreamSource(stream);
      sourceRef.current = source;

      // Create script processor for chunking
      const processor = audioContext.createScriptProcessor(chunkSize, 1, 1);
      processorRef.current = processor;

      processor.onaudioprocess = (event) => {
        const inputData = event.inputBuffer.getChannelData(0);
        // Convert float32 to int16
        const int16Data = new Int16Array(inputData.length);
        for (let i = 0; i < inputData.length; i++) {
          const s = Math.max(-1, Math.min(1, inputData[i]));
          int16Data[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
        }
        onData(int16Data.buffer);
      };

      // Connect
      source.connect(processor);
      processor.connect(audioContext.destination);

      setIsRecording(true);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to start recording";
      setError(message);
      console.error("Audio recording error:", err);
    }
  }, [onData, sampleRate, chunkSize]);

  const stop = useCallback(() => {
    // Disconnect audio nodes
    if (processorRef.current) {
      processorRef.current.disconnect();
      processorRef.current = null;
    }
    if (sourceRef.current) {
      sourceRef.current.disconnect();
      sourceRef.current = null;
    }
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
    // Stop media stream tracks
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }

    setIsRecording(false);
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stop();
    };
  }, [stop]);

  return {
    isRecording,
    error,
    start,
    stop,
  };
}