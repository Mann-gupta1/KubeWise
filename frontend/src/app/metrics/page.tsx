"use client";

import { useEffect, useState } from "react";
import MetricsChart from "@/components/MetricsChart";
import NodeHeatmap from "@/components/NodeHeatmap";
import { api } from "@/lib/api";
import { formatPercent, formatCPU, formatMemory } from "@/lib/format";
import type {
  NodeUtilization,
  PodUtilization,
  TimeSeriesPoint,
} from "@/lib/types";

export default function MetricsPage() {
  const [nodes, setNodes] = useState<NodeUtilization[]>([]);
  const [pods, setPods] = useState<PodUtilization[]>([]);
  const [cpuTS, setCpuTS] = useState<TimeSeriesPoint[]>([]);
  const [memTS, setMemTS] = useState<TimeSeriesPoint[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [n, p, cpu, mem] = await Promise.all([
          api.getNodeMetrics() as Promise<NodeUtilization[]>,
          api.getPodMetrics() as Promise<PodUtilization[]>,
          api.getCpuTimeSeries() as Promise<TimeSeriesPoint[]>,
          api.getMemoryTimeSeries() as Promise<TimeSeriesPoint[]>,
        ]);
        setNodes(n);
        setPods(p);
        setCpuTS(cpu);
        setMemTS(mem);
      } catch {
        /* backend not reachable */
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-gray-400 text-lg">Loading metrics...</div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-100">Cluster Metrics</h1>
        <p className="text-gray-400 text-sm mt-1">
          Real-time resource utilization and time-series data
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <MetricsChart
          data={cpuTS}
          title="CPU Usage (vCPU cores)"
          color="#3B82F6"
        />
        <MetricsChart
          data={memTS}
          title="Memory Usage"
          color="#8B5CF6"
          yAxisFormatter={(v) => {
            if (v >= 1e9) return `${(v / 1e9).toFixed(1)}G`;
            if (v >= 1e6) return `${(v / 1e6).toFixed(0)}M`;
            return v.toFixed(3);
          }}
        />
      </div>

      <NodeHeatmap nodes={nodes} />

      <div className="bg-gray-800/50 backdrop-blur border border-gray-700/50 rounded-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-700/50">
          <h3 className="text-lg font-semibold text-gray-100">
            Pod Resource Allocation
          </h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                <th className="px-6 py-3">Pod</th>
                <th className="px-6 py-3">Deployment</th>
                <th className="px-6 py-3">CPU Utilization</th>
                <th className="px-6 py-3">Memory Utilization</th>
                <th className="px-6 py-3">CPU Waste</th>
                <th className="px-6 py-3">Memory Waste</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700/30">
              {pods.map((pod) => (
                <tr
                  key={pod.pod_name}
                  className="hover:bg-gray-700/20 transition-colors"
                >
                  <td className="px-6 py-3 text-sm text-gray-200 font-mono truncate max-w-[200px]">
                    {pod.pod_name}
                  </td>
                  <td className="px-6 py-3 text-sm text-gray-300">
                    {pod.deployment_name}
                  </td>
                  <td className="px-6 py-3">
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-1.5 bg-gray-700 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${
                            pod.cpu_utilization > 0.8
                              ? "bg-red-400"
                              : pod.cpu_utilization > 0.6
                                ? "bg-yellow-400"
                                : "bg-green-400"
                          }`}
                          style={{
                            width: `${Math.min(100, pod.cpu_utilization * 100)}%`,
                          }}
                        />
                      </div>
                      <span className="font-mono text-xs text-gray-300">
                        {formatPercent(pod.cpu_utilization * 100)}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-3">
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-1.5 bg-gray-700 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${
                            pod.memory_utilization > 0.8
                              ? "bg-red-400"
                              : pod.memory_utilization > 0.6
                                ? "bg-yellow-400"
                                : "bg-green-400"
                          }`}
                          style={{
                            width: `${Math.min(100, pod.memory_utilization * 100)}%`,
                          }}
                        />
                      </div>
                      <span className="font-mono text-xs text-gray-300">
                        {formatPercent(pod.memory_utilization * 100)}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-3 font-mono text-xs text-orange-400">
                    {formatCPU(pod.cpu_waste)}
                  </td>
                  <td className="px-6 py-3 font-mono text-xs text-orange-400">
                    {formatMemory(pod.memory_waste)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
