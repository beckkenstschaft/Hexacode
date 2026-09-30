/** Live captions page */

import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { clsx } from "clsx";
import { PRODUCT_NAME, LANGUAGES, PROVIDER_LABELS } from "../utils/constants";
import {
  useCreateSession,
  useSession,
  useGenerateSummary,
} from "../hooks/useApi";
import { useWebSocket } from "../hooks/useWebSocket";
import { useAudio } from "../hooks/useAudio";
import { useSettings } from "../hooks/useSettings";
import {
  Button,
  Card,
  CardContent,
  Badge,
  Select,
  Toggle,
  Loading,
  EmptyState,
  PageHeader,
} from "../components";
import type { TranscriptSegment } from "../types/api";

export function LivePage() {
  const navigate = useNavigate();
  const { settings } = useSettings();
  const createSession = useCreateSession();
  const generateSummary = useGenerateSummary();

  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [captions, setCaptions] = useState<TranscriptSegment[]>([]);
  const [currentCaption, setCurrentCaption] = useState<string>("");
  const [selectedLanguage, setSelectedLanguage] = useState(settings.defaultLanguage);
  const [providerInfo, setProviderInfo] = useState<{ provider: string; simulated: boolean } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const captionsEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom when new captions arrive
  useEffect(() => {
    captionsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [captions]);

  const handleStartSession = useCallback(async () => {
    try {
      setError(null);
      const session = await createSession.mutateAsync({
        title: `${PRODUCT_NAME} Session - ${new Date().toLocaleString()}`,
        language: selectedLanguage,
      });
      setSessionId(session.id);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create session");
    }
  }, [createSession, selectedLanguage]);

  const handleEndSession = useCallback(async () => {
    if (!sessionId) return;
    try {
      await generateSummary.mutateAsync(sessionId);
      navigate(`/sessions/${sessionId}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to generate summary");
    }
  }, [sessionId, generateSummary, navigate]);

  const { isConnected, sendAudio, lastMessage } = useWebSocket({
    sessionId,
    onCaption: (caption) => {
      setCurrentCaption(caption.text);
      setProviderInfo({ provider: caption.provider, simulated: caption.simulated });

      const newSegment: TranscriptSegment = {
        id: crypto.randomUUID(),
        session_id: sessionId!,
        start_ms: Date.now() - caption.latency_ms,
        end_ms: Date.now(),
        text: caption.text,
        language: selectedLanguage,
        provider: caption.provider,
        simulated: caption.simulated,
      };
      setCaptions((prev) => [...prev, newSegment]);
    },
    onError: setError,
  });

  const { start, stop } = useAudio({
    onData: sendAudio,
    sampleRate: 16000,
    chunkSize: 4096,
  });

  const handleToggleRecording = useCallback(() => {
    if (isRecording) {
      stop();
      setIsRecording(false);
    } else {
      if (!sessionId) {
        handleStartSession();
      } else {
        start();
        setIsRecording(true);
      }
    }
  }, [isRecording, sessionId, start, stop, handleStartSession]);

  // Reset current caption when it changes
  useEffect(() => {
    if (lastMessage?.type === "caption") {
      setCurrentCaption((lastMessage.payload as { text: string }).text);
    }
  }, [lastMessage]);

  if (!sessionId) {
    return (
      <div>
        <PageHeader
          title="Live Captions"
          subtitle="Start a new session to begin real-time transcription"
        />
        <Card className="max-w-2xl">
          <CardContent className="flex flex-col items-center gap-6 py-12">
            <div className="text-snapdragon-blue">
              <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h10m-5 0v3" />
              </svg>
            </div>
            <div className="text-center">
              <h2 className="text-xl font-semibold text-snapdragon-navy mb-2">Start a Session</h2>
              <p className="text-gray-500 mb-6">Click below to create a new live caption session</p>
            </div>
            <Select
              label="Language"
              value={selectedLanguage}
              onChange={(e) => setSelectedLanguage(e.target.value)}
              options={LANGUAGES.map((l) => ({ value: l.code, label: `${l.name} (${l.nativeName})` }))}
            />
            <Button size="lg" onClick={handleStartSession} disabled={createSession.isPending}>
              {createSession.isPending ? "Creating..." : "Start Session"}
            </Button>
            {error && <p className="text-red-600 text-sm" role="alert">{error}</p>}
          </CardContent>
        </Card>
      </div>
    );
  }

  // Fetch session details for existing captions
  const { data: session } = useSession(sessionId);

  return (
    <div>
      <PageHeader
        title="Live Captions"
        subtitle={session ? `Session: ${session.title}` : "Active session"}
        action={
          <div className="flex items-center gap-3">
            <Select
              label="Language"
              value={selectedLanguage}
              onChange={(e) => setSelectedLanguage(e.target.value)}
              options={LANGUAGES.map((l) => ({ value: l.code, label: `${l.name} (${l.nativeName})` }))}
              className="w-48"
            />
            <Badge variant={isRecording ? "success" : "default"} dot>
              {isRecording ? "Recording" : "Stopped"}
            </Badge>
            <Badge variant={providerInfo?.simulated ? "simulated" : "info"} dot>
              {PROVIDER_LABELS[providerInfo?.provider] || providerInfo?.provider || "Connecting..."}
            </Badge>
            <Button
              variant={isRecording ? "danger" : "primary"}
              size="lg"
              onClick={handleToggleRecording}
              disabled={!isConnected}
            >
              {isRecording ? "Stop Recording" : "Start Recording"}
            </Button>
            {!isRecording && session?.status === "active" && (
              <Button variant="secondary" onClick={handleEndSession} disabled={generateSummary.isPending}>
                {generateSummary.isPending ? "Saving..." : "End & Summarize"}
              </Button>
            )}
          </div>
        }
      />

      {/* Connection status */}
      <div className="mb-4 flex items-center gap-2 text-sm">
        <span className={clsx("w-2 h-2 rounded-full", isConnected ? "bg-green-500" : "bg-red-500")} aria-hidden="true" />
        <span className="text-gray-600">
          {isConnected ? "Connected" : "Disconnected"}
        </span>
      </div>

      {/* Caption display */}
      <Card className="mb-6">
        <CardContent className="p-0">
          <div
            className={clsx(
              "h-64 md:h-80 overflow-y-auto p-6",
              settings.highContrast && "bg-black text-white",
              !settings.highContrast && "bg-white"
            )}
            style={{ fontSize: `${settings.captionSize}px` }}
            role="log"
            aria-live="polite"
            aria-label="Live captions"
          >
            {captions.length === 0 && !isRecording && (
              <EmptyState
                icon={
                  <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h10m-5 0v3" />
                  </svg>
                }
                title="No captions yet"
                description="Start recording to see live captions appear here"
              />
            )}
            <div className="space-y-4">
              {captions.map((segment) => (
                <div
                  key={segment.id}
                  className={clsx(
                    "p-3 rounded-lg border-l-4 transition-colors",
                    settings.highContrast
                      ? "bg-gray-900 border-white text-white"
                      : "bg-gray-50 border-snapdragon-blue-light text-snapdragon-navy"
                  )}
                >
                  <p className="whitespace-pre-wrap">{segment.text}</p>
                  <div className="flex items-center gap-2 mt-1 text-xs text-gray-500">
                    <Badge variant={segment.simulated ? "simulated" : "default"} size="sm">
                      {PROVIDER_LABELS[segment.provider] || segment.provider}
                    </Badge>
                    <span>{new Date(segment.start_ms).toLocaleTimeString()}</span>
                  </div>
                </div>
              ))}
              {currentCaption && captions.length > 0 && (
                <div className={clsx("p-3 rounded-lg bg-snapdragon-blue-light border-l-4 border-snapdragon-blue animate-pulse")}>
                  <p className="whitespace-pre-wrap text-snapdragon-navy">{currentCaption}</p>
                  <div className="flex items-center gap-2 mt-1 text-xs text-snapdragon-blue">
                    <Badge variant={providerInfo?.simulated ? "simulated" : "info"} size="sm">
                      {PROVIDER_LABELS[providerInfo?.provider] || providerInfo?.provider || "Processing..."}
                    </Badge>
                    <span>Live</span>
                  </div>
                </div>
              )}
              <div ref={captionsEndRef} />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Settings panel */}
      <Card>
        <CardContent className="pt-0">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-snapdragon-navy mb-2">Caption Size</label>
              <input
                type="range"
                min="14"
                max="32"
                value={settings.captionSize}
                onChange={(e) => settings.updateSetting("captionSize", parseInt(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-snapdragon-blue"
                aria-label="Caption font size"
              />
              <p className="text-sm text-gray-500 mt-1">{settings.captionSize}px</p>
            </div>
            <div>
              <Toggle
                checked={settings.highContrast}
                onChange={(e) => settings.updateSetting("highContrast", e.target.checked)}
                label="High Contrast"
                description="Increase contrast for better readability"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700" role="alert">
          {error}
        </div>
      )}
    </div>
  );
}