/** NPU Advantage Dashboard page */

import { useEffect, useState } from "react";
import { clsx } from "clsx";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { PROVIDER_LABELS, STAGE_LABELS } from "../utils/constants";
import { useCapabilities, useRunBenchmark, useBenchmarks, useBenchmark } from "../hooks/useApi";
import {
  Button,
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  Badge,
  Select,
  Loading,
  EmptyState,
  ErrorState,
  PageHeader,
} from "../components";
import type { SystemCapabilities, BenchmarkRunDetail, BenchmarkResult, BenchmarkRunCreate } from "../types/api";

const STAGE_COLORS = {
  vad: "#3253DC",
  asr: "#0B1A4F",
  summarization: "#2843B8",
};

const PROVIDER_COLORS: Record<string, string> = {
  QNNExecutionProvider: "#3253DC",
  CUDAExecutionProvider: "#0B1A4F",
  DmlExecutionProvider: "#2843B8",
  CPUExecutionProvider: "#64748B",
  Mock: "#A855F7",
};

export function DashboardPage() {
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
  const [benchmarkAudio, setBenchmarkAudio] = useState<BenchmarkRunCreate>({
    audio_name: "benchmark_audio.wav",
    audio_duration_s: 30,
    device_info: {},
  });

  const { data: capabilities, isLoading: capsLoading } = useCapabilities();
  const { data: runs, isLoading: runsLoading, refetch: refetchRuns } = useBenchmarks({ limit: 20 });
  const runBenchmark = useRunBenchmark();
  const { data: selectedRun, isLoading: runLoading } = useBenchmark(selectedRunId!);

  const handleRunBenchmark = async () => {
    try {
      const result = await runBenchmark.mutateAsync(benchmarkAudio);
      setSelectedRunId(result.id);
      refetchRuns();
    } catch (e) {
      console.error("Benchmark failed:", e);
    }
  };

  const handleRunSelect = (runId: string) => {
    setSelectedRunId(runId);
  };

  // Process benchmark data for charts
  const chartData = selectedRun?.results || [];

  // Group by provider for latency chart
  const latencyByProvider = chartData.reduce((acc, result) => {
    const key = result.provider;
    if (!acc[key]) acc[key] = { provider: key, vad: 0, asr: 0, summarization: 0, count: 0 };
    acc[key][result.stage as keyof typeof acc[key]] = (acc[key][result.stage as keyof typeof acc[key]] as number) + result.latency_ms;
    acc[key].count++;
    return acc;
  }, {} as Record<string, { provider: string; vad: number; asl: number; summarization: number; count: number }>);

  const latencyChartData = Object.values(latencyByProvider).map((d) => ({
    provider: PROVIDER_LABELS[d.provider] || d.provider,
    VAD: d.vad / (d.count || 1),
    ASR: d.asr / (d.count || 1),
    Summarization: d.summarization / (d.count || 1),
  }));

  // RTF chart data
  const rtfByProvider = chartData.reduce((acc, result) => {
    const key = result.provider;
    if (!acc[key]) acc[key] = { provider: key, values: [] as number[] };
    acc[key].values.push(result.real_time_factor);
    return acc;
  }, {} as Record<string, { provider: string; values: number[] }>);

  const rtfChartData = Object.values(rtfByProvider).map((d) => ({
    provider: PROVIDER_LABELS[d.provider] || d.provider,
    rtf: d.values.reduce((a, b) => a + b, 0) / d.values.length,
  }));

  // Battery chart data
  const batteryByProvider = chartData
    .filter((r) => r.battery_delta_percent !== null)
    .reduce((acc, result) => {
      const key = result.provider;
      if (!acc[key]) acc[key] = { provider: key, total: 0, count: 0 };
      acc[key].total += result.battery_delta_percent || 0;
      acc[key].count++;
      return acc;
    }, {} as Record<string, { provider: string; total: number; count: number }>);

  const batteryChartData = Object.values(batteryByProvider).map((d) => ({
    provider: PROVIDER_LABELS[d.provider] || d.provider,
    battery: d.total / (d.count || 1),
  }));

  // Stage processor table data
  const stageProcessorData = chartData.reduce((acc, result) => {
    const key = `${result.stage}-${result.provider}`;
    if (!acc[key] || result.latency_ms < acc[key].latency_ms) {
      acc[key] = {
        stage: STAGE_LABELS[result.stage] || result.stage,
        provider: PROVIDER_LABELS[result.provider] || result.provider,
        latency_ms: result.latency_ms,
        rtf: result.real_time_factor,
        simulated: result.simulated,
      };
    }
    return acc;
  }, {} as Record<string, { stage: string; provider: string; latency_ms: number; rtf: number; simulated: boolean }>);

  const stageTableData = Object.values(stageProcessorData);

  if (capsLoading) {
    return (
      <div>
        <PageHeader title="NPU Advantage Dashboard" subtitle="Compare NPU, CPU, and GPU performance" />
        <Loading text="Loading system capabilities..." />
      </div>
    );
  }

  return (
    <div>
      <PageHeader
        title="NPU Advantage Dashboard"
        subtitle="Run benchmarks to compare NPU, CPU, and GPU performance on the same audio"
        action={
          <Button
            onClick={handleRunBenchmark}
            disabled={runBenchmark.isPending}
            size="lg"
          >
            {runBenchmark.isPending ? "Running Benchmark..." : "Run Benchmark"}
          </Button>
        }
      />

      {/* Capabilities Panel */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>System Capabilities</CardTitle>
        </CardHeader>
        <CardContent>
          {capabilities && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 rounded-lg bg-gray-50">
                <h4 className="font-medium text-snapdragon-navy mb-2">NPU (QNN)</h4>
                <Badge variant={capabilities.providers.npu_available ? "success" : "danger"} dot>
                  {capabilities.providers.npu_available ? "Available" : "Not Available"}
                </Badge>
              </div>
              <div className="p-4 rounded-lg bg-gray-50">
                <h4 className="font-medium text-snapdragon-navy mb-2">GPU</h4>
                <Badge variant={capabilities.providers.gpu_available ? "success" : "danger"} dot>
                  {capabilities.providers.gpu_available ? "Available" : "Not Available"}
                </Badge>
              </div>
              <div className="p-4 rounded-lg bg-gray-50">
                <h4 className="font-medium text-snapdragon-navy mb-2">CPU</h4>
                <Badge variant={capabilities.providers.cpu_available ? "success" : "danger"} dot>
                  {capabilities.providers.cpu_available ? "Available" : "Not Available"}
                </Badge>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Models Status */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Models Status</CardTitle>
        </CardHeader>
        <CardContent>
          {capabilities && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {["vad", "asr", "summarizer"].map((model) => {
                const info = capabilities.models_loaded[model as keyof typeof capabilities.models_loaded];
                return (
                  <div key={model} className="p-4 rounded-lg bg-gray-50">
                    <h4 className="font-medium text-snapdragon-navy mb-1 capitalize">{model}</h4>
                    <div className="flex items-center gap-2">
                      <Badge variant={info.simulated ? "simulated" : "info"} size="sm">
                        {PROVIDER_LABELS[info.provider] || info.provider}
                      </Badge>
                      {info.simulated && <span className="text-xs text-purple-600">Simulated</span>}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Benchmark History */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Benchmark History</CardTitle>
        </CardHeader>
        <CardContent>
          {runsLoading ? (
            <Loading text="Loading benchmark history..." />
          ) : runs && runs.length > 0 ? (
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {runs.map((run) => (
                <div
                  key={run.id}
                  className={clsx(
                    "p-3 rounded-lg border cursor-pointer transition-colors",
                    selectedRunId === run.id
                      ? "border-snapdragon-blue bg-snapdragon-blue-light"
                      : "border-gray-200 hover:bg-gray-50"
                  )}
                  onClick={() => handleRunSelect(run.id)}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-snapdragon-navy">{run.audio_name}</p>
                      <p className="text-sm text-gray-500">
                        {run.audio_duration_s}s • {new Date(run.started_at).toLocaleString()}
                        {run.finished_at && ` • Completed in ${Math.round((new Date(run.finished_at).getTime() - new Date(run.started_at).getTime()) / 1000)}s`}
                      </p>
                    </div>
                    <Badge variant={run.finished_at ? "success" : "warning"} size="sm">
                      {run.finished_at ? "Completed" : "Running"}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState
              title="No benchmarks run yet"
              description="Click 'Run Benchmark' to start comparing processor performance"
            />
          )}
        </CardContent>
      </Card>

      {/* Charts - only show if we have a selected run */}
      {selectedRun && (
        <>
          {/* Latency Chart */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Average Latency by Stage</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={latencyChartData} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" />
                    <YAxis dataKey="provider" type="category" width={100} />
                    <Tooltip
                      formatter={(value: number) => [value.toFixed(1), "ms"]}
                      labelFormatter={(label) => label}
                    />
                    <Bar dataKey="VAD" fill={STAGE_COLORS.vad} name="VAD" radius={[0, 4, 4, 0]} />
                    <Bar dataKey="ASR" fill={STAGE_COLORS.asr} name="ASR" radius={[0, 4, 4, 0]} />
                    <Bar dataKey="Summarization" fill={STAGE_COLORS.summarization} name="Summarization" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          {/* Real-time Factor Chart */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Real-Time Factor (Lower is Better)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={rtfChartData} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" />
                    <YAxis dataKey="provider" type="category" width={100} />
                    <Tooltip formatter={(value: number) => [value.toFixed(2), "x real-time"]} />
                    <Bar dataKey="rtf" fill="#3253DC" name="RTF" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <p className="text-sm text-gray-500 mt-2">Values < 1.0 indicate faster-than-real-time processing</p>
            </CardContent>
          </Card>

          {/* Battery Chart */}
          {batteryChartData.length > 0 && (
            <Card className="mb-6">
              <CardHeader>
                <CardTitle>Battery Impact (Estimated)</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={batteryChartData} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis type="number" />
                      <YAxis dataKey="provider" type="category" width={100} />
                      <Tooltip formatter={(value: number) => [value.toFixed(2), "%"]} />
                      <Bar dataKey="battery" fill="#0B1A4F" name="Battery Δ%" radius={[0, 4, 4, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                <p className="text-sm text-gray-500 mt-2">Estimated battery drain percentage per benchmark run</p>
              </CardContent>
            </Card>
          )}

          {/* Stage Processor Table */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Processor Used Per Stage</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-200 text-left text-gray-500">
                      <th className="pb-2 font-medium">Stage</th>
                      <th className="pb-2 font-medium">Processor</th>
                      <th className="pb-2 font-medium text-right">Latency (ms)</th>
                      <th className="pb-2 font-medium text-right">Real-Time Factor</th>
                      <th className="pb-2 font-medium">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {stageTableData.map((row, i) => (
                      <tr key={i} className="border-b border-gray-100">
                        <td className="py-2">{row.stage}</td>
                        <td className="py-2">
                          <Badge
                            variant={row.simulated ? "simulated" : "default"}
                            size="sm"
                          >
                            {row.provider}
                          </Badge>
                        </td>
                        <td className="py-2 text-right font-mono">{row.latency_ms}</td>
                        <td className="py-2 text-right font-mono">{row.rtf.toFixed(2)}x</td>
                        <td className="py-2">
                          {row.simulated ? (
                            <Badge variant="simulated" size="sm">Simulated</Badge>
                          ) : (
                            <Badge variant="success" size="sm">Real</Badge>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          {/* Raw Results Table */}
          <Card>
            <CardHeader>
              <CardTitle>Detailed Results</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-200 text-left text-gray-500">
                      <th className="pb-2 font-medium">Provider</th>
                      <th className="pb-2 font-medium">Stage</th>
                      <th className="pb-2 font-medium text-right">Latency (ms)</th>
                      <th className="pb-2 font-medium text-right">RTF</th>
                      <th className="pb-2 font-medium text-right">CPU %</th>
                      <th className="pb-2 font-medium text-right">NPU %</th>
                      <th className="pb-2 font-medium text-right">Battery Δ%</th>
                      <th className="pb-2 font-medium">Type</th>
                    </tr>
                  </thead>
                  <tbody>
                    {chartData.map((result, i) => (
                      <tr key={i} className="border-b border-gray-100">
                        <td className="py-2">
                          <Badge
                            variant={result.simulated ? "simulated" : "default"}
                            size="sm"
                          >
                            {PROVIDER_LABELS[result.provider] || result.provider}
                          </Badge>
                        </td>
                        <td className="py-2">{STAGE_LABELS[result.stage] || result.stage}</td>
                        <td className="py-2 text-right font-mono">{result.latency_ms}</td>
                        <td className="py-2 text-right font-mono">{result.real_time_factor.toFixed(2)}x</td>
                        <td className="py-2 text-right font-mono">{result.cpu_percent.toFixed(1)}%</td>
                        <td className="py-2 text-right font-mono">
                          {result.npu_percent !== null ? result.npu_percent.toFixed(1) + "%" : "N/A"}
                        </td>
                        <td className="py-2 text-right font-mono">
                          {result.battery_delta_percent !== null ? result.battery_delta_percent.toFixed(2) + "%" : "N/A"}
                        </td>
                        <td className="py-2">
                          <Badge variant={result.simulated ? "simulated" : "success"} size="sm">
                            {result.simulated ? "Simulated" : "Real"}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}