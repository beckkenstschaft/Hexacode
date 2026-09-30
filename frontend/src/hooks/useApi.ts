/** React Query hooks for API */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  sessionsApi,
  benchmarksApi,
  systemApi,
  type Session,
  type SessionDetail,
  type SessionCreate,
  type SessionUpdate,
  type Summary,
  type BenchmarkRun,
  type BenchmarkRunDetail,
  type BenchmarkRunCreate,
  type SystemCapabilities,
  type HealthResponse,
} from "../api";

// Query keys
export const queryKeys = {
  sessions: (params?: { limit?: number; offset?: number; status?: string }) => [
    "sessions",
    params,
  ],
  session: (id: string) => ["session", id],
  benchmarks: (params?: { limit?: number; offset?: number }) => [
    "benchmarks",
    params,
  ],
  benchmark: (id: string) => ["benchmark", id],
  capabilities: () => ["capabilities"],
  health: () => ["health"],
};

// Session hooks
export function useSessions(params?: { limit?: number; offset?: number; status?: string }) {
  return useQuery({
    queryKey: queryKeys.sessions(params),
    queryFn: () => sessionsApi.list(params),
  });
}

export function useSession(id: string) {
  return useQuery({
    queryKey: queryKeys.session(id),
    queryFn: () => sessionsApi.get(id),
    enabled: !!id,
  });
}

export function useCreateSession() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: SessionCreate) => sessionsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["sessions"] });
    },
  });
}

export function useUpdateSession() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: SessionUpdate }) =>
      sessionsApi.update(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ["sessions"] });
      queryClient.invalidateQueries({ queryKey: ["session", id] });
    },
  });
}

export function useDeleteSession() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => sessionsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["sessions"] });
    },
  });
}

export function useGenerateSummary() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (sessionId: string) => sessionsApi.generateSummary(sessionId),
    onSuccess: (_, sessionId) => {
      queryClient.invalidateQueries({ queryKey: ["session", sessionId] });
    },
  });
}

// Benchmark hooks
export function useBenchmarks(params?: { limit?: number; offset?: number }) {
  return useQuery({
    queryKey: queryKeys.benchmarks(params),
    queryFn: () => benchmarksApi.list(params),
  });
}

export function useBenchmark(id: string) {
  return useQuery({
    queryKey: queryKeys.benchmark(id),
    queryFn: () => benchmarksApi.get(id),
    enabled: !!id,
  });
}

export function useRunBenchmark() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: BenchmarkRunCreate) => benchmarksApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["benchmarks"] });
    },
  });
}

// System hooks
export function useCapabilities() {
  return useQuery({
    queryKey: queryKeys.capabilities(),
    queryFn: () => systemApi.capabilities(),
    refetchInterval: 30000, // Refresh every 30 seconds
  });
}

export function useHealth() {
  return useQuery({
    queryKey: queryKeys.health(),
    queryFn: () => systemApi.health(),
    refetchInterval: 60000,
  });
}

export function useReadiness() {
  return useQuery({
    queryKey: ["ready"],
    queryFn: () => systemApi.ready(),
    refetchInterval: 30000,
  });
}