/** Typed API client using fetch */

import type {
  Session,
  SessionDetail,
  SessionCreate,
  SessionUpdate,
  TranscriptSegment,
  Summary,
  SummaryCreate,
  SystemCapabilities,
  BenchmarkRun,
  BenchmarkRunDetail,
  BenchmarkRunCreate,
  HealthResponse,
  ErrorResponse,
} from "../types/api";

const API_BASE = import.meta.env.VITE_API_BASE || "/api/v1";

class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    public details: Record<string, unknown>,
    message: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorData: ErrorResponse | null = null;
    try {
      errorData = await response.json();
    } catch {
      // Ignore JSON parse errors
    }

    const message = errorData?.error?.message || response.statusText;
    const code = errorData?.error?.code || "UNKNOWN_ERROR";
    const details = errorData?.error?.details || {};

    throw new ApiError(response.status, code, details, message);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  return handleResponse<T>(response);
}

// Session API
export const sessionsApi = {
  list: (params?: { limit?: number; offset?: number; status?: string }) => {
    const searchParams = new URLSearchParams();
    if (params?.limit) searchParams.set("limit", params.limit.toString());
    if (params?.offset) searchParams.set("offset", params.offset.toString());
    if (params?.status) searchParams.set("status", params.status);
    return request<Session[]>(`/sessions?${searchParams}`);
  },

  create: (data: SessionCreate) =>
    request<Session>("/sessions", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  get: (id: string) =>
    request<SessionDetail>(`/sessions/${id}`),

  update: (id: string, data: SessionUpdate) =>
    request<Session>(`/sessions/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  delete: (id: string) =>
    request<void>(`/sessions/${id}`, {
      method: "DELETE",
    }),

  generateSummary: (id: string) =>
    request<Summary>(`/sessions/${id}/summary`, {
      method: "POST",
    }),
};

// Benchmark API
export const benchmarksApi = {
  list: (params?: { limit?: number; offset?: number }) => {
    const searchParams = new URLSearchParams();
    if (params?.limit) searchParams.set("limit", params.limit.toString());
    if (params?.offset) searchParams.set("offset", params.offset.toString());
    return request<BenchmarkRun[]>(`/benchmarks?${searchParams}`);
  },

  create: (data: BenchmarkRunCreate) =>
    request<BenchmarkRunDetail>("/benchmarks", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  get: (id: string) =>
    request<BenchmarkRunDetail>(`/benchmarks/${id}`),
};

// System API
export const systemApi = {
  health: () => request<HealthResponse>("/health"),
  ready: () => request<HealthResponse>("/ready"),
  capabilities: () => request<SystemCapabilities>("/system/capabilities"),
};

// WebSocket helper
export function createWebSocket(sessionId: string): WebSocket {
  const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsHost = import.meta.env.VITE_WS_HOST || window.location.host;
  return new WebSocket(`${wsProtocol}//${wsHost}/api/v1/sessions/${sessionId}/stream`);
}

export { ApiError };