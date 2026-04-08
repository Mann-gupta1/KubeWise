"use client";

import { formatPercent } from "@/lib/format";

interface GaugeProps {
  label: string;
  value: number;
  unit?: string;
  subtitle?: string;
}

function Gauge({ label, value, unit = "%", subtitle }: GaugeProps) {
  const pct = Math.min(100, Math.max(0, value));
  const color =
    pct >= 80
      ? "text-red-400"
      : pct >= 60
        ? "text-yellow-400"
        : pct >= 40
          ? "text-green-400"
          : "text-blue-400";
  const ringColor =
    pct >= 80
      ? "stroke-red-400"
      : pct >= 60
        ? "stroke-yellow-400"
        : pct >= 40
          ? "stroke-green-400"
          : "stroke-blue-400";

  const circumference = 2 * Math.PI * 45;
  const offset = circumference - (pct / 100) * circumference;

  return (
    <div className="bg-gray-800/50 backdrop-blur border border-gray-700/50 rounded-xl p-6 flex flex-col items-center">
      <div className="relative w-28 h-28">
        <svg className="w-28 h-28 -rotate-90" viewBox="0 0 100 100">
          <circle
            cx="50"
            cy="50"
            r="45"
            fill="none"
            stroke="currentColor"
            className="text-gray-700"
            strokeWidth="8"
          />
          <circle
            cx="50"
            cy="50"
            r="45"
            fill="none"
            className={ringColor}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={`text-xl font-bold font-mono ${color}`}>
            {typeof value === "number" && unit === "%"
              ? formatPercent(value)
              : `${value}${unit}`}
          </span>
        </div>
      </div>
      <p className="mt-3 text-sm font-medium text-gray-300">{label}</p>
      {subtitle && (
        <p className="text-xs text-gray-500 mt-1">{subtitle}</p>
      )}
    </div>
  );
}

interface ClusterOverviewProps {
  cpuUtilization: number;
  memoryUtilization: number;
  activeNodes: number;
  totalNodes: number;
  estimatedSavings: string;
}

export default function ClusterOverview({
  cpuUtilization,
  memoryUtilization,
  activeNodes,
  totalNodes,
  estimatedSavings,
}: ClusterOverviewProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <Gauge
        label="CPU Utilization"
        value={cpuUtilization}
        subtitle="Cluster-wide average"
      />
      <Gauge
        label="Memory Utilization"
        value={memoryUtilization}
        subtitle="Cluster-wide average"
      />
      <Gauge
        label="Active Nodes"
        value={activeNodes}
        unit={`/${totalNodes}`}
        subtitle="Nodes in Ready state"
      />
      <div className="bg-gray-800/50 backdrop-blur border border-gray-700/50 rounded-xl p-6 flex flex-col items-center justify-center">
        <p className="text-3xl font-bold font-mono text-emerald-400">
          {estimatedSavings}
        </p>
        <p className="mt-2 text-sm font-medium text-gray-300">
          Estimated Savings
        </p>
        <p className="text-xs text-gray-500 mt-1">per month</p>
      </div>
    </div>
  );
}
