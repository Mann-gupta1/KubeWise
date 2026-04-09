"use client";

import { useEffect, useState } from "react";
import ClusterOverview from "@/components/ClusterOverview";
import PipelineOverview from "@/components/PipelineOverview";
import SavingsTable from "@/components/SavingsTable";
import { api } from "@/lib/api";
import type { ClusterMetrics, CostSummary } from "@/lib/types";

export default function DashboardHome() {
  const [clusterMetrics, setClusterMetrics] = useState<ClusterMetrics | null>(null);
  const [costSummary, setCostSummary] = useState<CostSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const [metrics, cost] = await Promise.all([
          api.getClusterMetrics() as Promise<ClusterMetrics>,
          api.getCostSummary() as Promise<CostSummary>,
        ]);
        setClusterMetrics(metrics);
        setCostSummary(cost);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load data");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-gray-400 text-lg">Loading cluster data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-red-900/20 border border-red-800 rounded-xl p-6 text-center">
          <p className="text-red-400 font-medium">Connection Error</p>
          <p className="text-red-300/70 text-sm mt-1">{error}</p>
          <p className="text-gray-500 text-xs mt-3 max-w-lg mx-auto">
            Local: run the API on port 8000. Hosted: set{" "}
            <code className="text-gray-400">NEXT_PUBLIC_API_URL</code> if needed, CORS must allow this
            Vercel origin, and Render free services sleep — open your API <code className="text-gray-400">/docs</code>{" "}
            to wake it, then retry.
          </p>
        </div>
      </div>
    );
  }

  const summary = clusterMetrics?.summary;
  const savings = costSummary?.raw?.by_deployment || [];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-100">Cluster Overview</h1>
        <p className="text-gray-400 text-sm mt-1">
          {clusterMetrics?.cluster.name} &mdash; {clusterMetrics?.cluster.provider} / {clusterMetrics?.cluster.region}
        </p>
      </div>

      <PipelineOverview />

      {clusterMetrics?.telemetry?.mock_mode || clusterMetrics?.telemetry?.live === false ? (
        <div className="rounded-lg border border-amber-700/50 bg-amber-950/30 px-4 py-3 text-sm text-amber-100/90">
          <p className="font-medium text-amber-200">Not using live Prometheus for this response</p>
          <p className="text-amber-100/70 mt-1">
            {clusterMetrics.telemetry?.hint ||
              "Synthetic or fallback data. To query a real Prometheus URL, set MOCK_MODE=false and TELEMETRY_MODE=local (or cluster) on the API, redeploy, then refresh."}
          </p>
          {clusterMetrics.telemetry?.prometheus_host ? (
            <p className="text-xs text-amber-200/60 mt-2 font-mono">
              prometheus_host: {clusterMetrics.telemetry.prometheus_host} · effective_mode:{" "}
              {clusterMetrics.telemetry.effective_mode ?? "—"}
            </p>
          ) : null}
        </div>
      ) : clusterMetrics?.telemetry?.live ? (
        <div className="rounded-lg border border-emerald-800/50 bg-emerald-950/25 px-4 py-2 text-xs text-emerald-200/90 font-mono">
          Live Prometheus · {clusterMetrics.telemetry.pipeline} ·{" "}
          {clusterMetrics.telemetry.queried_at ?? "—"}
        </div>
      ) : null}

      <ClusterOverview
        cpuUtilization={summary?.cpu_utilization_pct ?? 0}
        memoryUtilization={summary?.memory_utilization_pct ?? 0}
        activeNodes={summary?.total_nodes ?? 0}
        totalNodes={summary?.total_nodes ?? 0}
        estimatedSavings={costSummary?.total_savings ?? "$0"}
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="bg-gray-800/50 backdrop-blur border border-gray-700/50 rounded-xl p-5">
          <p className="text-xs text-gray-400 uppercase tracking-wider">Total Pods</p>
          <p className="text-2xl font-bold font-mono text-gray-100 mt-1">
            {summary?.total_pods}
          </p>
        </div>
        <div className="bg-gray-800/50 backdrop-blur border border-gray-700/50 rounded-xl p-5">
          <p className="text-xs text-gray-400 uppercase tracking-wider">Deployments</p>
          <p className="text-2xl font-bold font-mono text-gray-100 mt-1">
            {summary?.total_deployments}
          </p>
        </div>
        <div className="bg-gray-800/50 backdrop-blur border border-gray-700/50 rounded-xl p-5">
          <p className="text-xs text-gray-400 uppercase tracking-wider">Infrastructure Cost</p>
          <p className="text-2xl font-bold font-mono text-gray-100 mt-1">
            {costSummary?.node_infrastructure_cost}
          </p>
        </div>
      </div>

      <SavingsTable data={savings} />
    </div>
  );
}
