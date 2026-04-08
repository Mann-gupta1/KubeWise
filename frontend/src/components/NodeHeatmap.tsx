"use client";

import { formatPercent } from "@/lib/format";
import type { NodeUtilization } from "@/lib/types";

interface NodeHeatmapProps {
  nodes: NodeUtilization[];
}

function cellColor(utilization: number): string {
  const pct = utilization * 100;
  if (pct >= 80) return "bg-red-500/80";
  if (pct >= 60) return "bg-yellow-500/80";
  if (pct >= 40) return "bg-green-500/80";
  if (pct >= 20) return "bg-blue-500/80";
  return "bg-blue-900/60";
}

export default function NodeHeatmap({ nodes }: NodeHeatmapProps) {
  return (
    <div className="bg-gray-800/50 backdrop-blur border border-gray-700/50 rounded-xl p-6">
      <h3 className="text-lg font-semibold text-gray-100 mb-4">
        Node Utilization Heatmap
      </h3>
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
        {nodes.map((node) => (
          <div key={node.node_name} className="space-y-2">
            <p className="text-xs font-medium text-gray-400 truncate">
              {node.node_name}
            </p>
            <div className="grid grid-cols-2 gap-1.5">
              <div
                className={`${cellColor(node.cpu_utilization)} rounded-lg p-3 text-center`}
              >
                <p className="text-xs text-white/70">CPU</p>
                <p className="text-sm font-mono font-bold text-white">
                  {formatPercent(node.cpu_utilization * 100)}
                </p>
              </div>
              <div
                className={`${cellColor(node.memory_utilization)} rounded-lg p-3 text-center`}
              >
                <p className="text-xs text-white/70">MEM</p>
                <p className="text-sm font-mono font-bold text-white">
                  {formatPercent(node.memory_utilization * 100)}
                </p>
              </div>
            </div>
            <p className="text-xs text-gray-500 text-center">
              {node.instance_type}
            </p>
          </div>
        ))}
      </div>
      <div className="mt-4 flex items-center gap-2 text-xs text-gray-500">
        <span>Low</span>
        <div className="flex gap-0.5">
          <div className="w-5 h-3 rounded bg-blue-900/60" />
          <div className="w-5 h-3 rounded bg-blue-500/80" />
          <div className="w-5 h-3 rounded bg-green-500/80" />
          <div className="w-5 h-3 rounded bg-yellow-500/80" />
          <div className="w-5 h-3 rounded bg-red-500/80" />
        </div>
        <span>High</span>
      </div>
    </div>
  );
}
