/** API Type Definitions - matched to backend OpenAPI schema */

export interface Session {
  id: string;
  title: string;
  language: string;
  started_at: string;
  ended_at: string | null;
  status: "active" | "completed" | "archived";
}

export interface SessionDetail extends Session {
  transcript_segments: TranscriptSegment[];
  summaries: Summary[];
}

export interface TranscriptSegment {
  id: string;
  session_id: string;
  start_ms: number;
  end_ms: number;
  text: string;
  language: string;
  provider: string;
  simulated: boolean;
}

export interface Summary {
  id: string;
  session_id: string;
  key_points: string[];
  action_items: string[];
  provider: string;
  simulated: boolean;
  created_at: string;
}

export interface SystemCapabilities {
  product_name: string;
  providers: {
    npu_available: boolean;
    gpu_available: boolean;
    cpu_available: boolean;
    available_providers: string[];
    selected_providers: string[];
  };
  models_loaded: {
    vad: { provider: string; simulated: boolean };
    asr: { provider: string; simulated: boolean };
    summarizer: { provider: string; simulated: boolean };
  };
  simulated_mode: boolean;
}

export interface HealthResponse {
  status: string;
  timestamp: string;
}

export interface BenchmarkRun {
  id: string;
  audio_name: string;
  audio_duration_s: number;
  started_at: string;
  finished_at: string | null;
  device_info: Record<string, unknown>;
}

export interface BenchmarkResult {
  id: string;
  run_id: string;
  provider: string;
  stage: string;
  latency_ms: number;
  real_time_factor: number;
  cpu_percent: number;
  npu_percent: number | null;
  battery_delta_percent: number | null;
  simulated: boolean;
}

export interface BenchmarkRunDetail extends BenchmarkRun {
  results: BenchmarkResult[];
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

// Request types
export interface SessionCreate {
  title: string;
  language: string;
}

export interface SessionUpdate {
  title?: string;
  status?: "active" | "completed" | "archived";
}

export interface TranscriptSegmentCreate {
  start_ms: number;
  end_ms: number;
  text: string;
  language: string;
  provider: string;
  simulated: boolean;
}

export interface SummaryCreate {
  key_points: string[];
  action_items: string[];
  provider: string;
  simulated: boolean;
}

export interface BenchmarkRunCreate {
  audio_name: string;
  audio_duration_s: number;
  device_info?: Record<string, unknown>;
}

// WebSocket message types
export type WSMessageType = "audio" | "caption" | "error" | "end";

export interface WSMessage {
  type: WSMessageType;
  payload: Record<string, unknown>;
}

export interface WSCaptionPayload {
  text: string;
  provider: string;
  simulated: boolean;
  latency_ms: number;
}

export interface WSErrorPayload {
  message: string;
}

// Error types
export interface ErrorDetail {
  code: string;
  message: string;
  details: Record<string, unknown>;
}

export interface ErrorResponse {
  error: ErrorDetail;
}