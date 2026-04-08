"use client";

import { useEffect, useState } from "react";
import CostComparison from "@/components/CostComparison";
import { api } from "@/lib/api";
import { formatCurrency, formatPercent } from "@/lib/format";
import type { CostSummary, DeploymentCost } from "@/lib/types";

export default function CostPage() {
  const [costSummary, setCostSummary] = useState<CostSummary | null>(null);
  const [deploymentCosts, setDeploymentCosts] = useState<DeploymentCost[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [summary, byDep] = await Promise.all([
          api.getCostSummary() as Promise<CostSummary>,
          api.getCostByDeployment() as Promise<DeploymentCost[]>,
        ]);
        setCostSummary(summary);
        setDeploymentCosts(byDep);
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
        <div className="text-gray-400 text-lg">Calculating costs...</div>
      </div>
    );
  }

  const raw = costSummary?.raw;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-100">Cost Analysis</h1>
        <p className="text-gray-400 text-sm mt-1">
          Resource cost breakdown and optimization potential
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-gray-800/50 backdrop-blur border border-gray-700/50 rounded-xl p-5">
          <p className="text-xs text-gray-400 uppercase tracking-wider">
            Current Cost
          </p>
          <p className="text-2xl font-bold font-mono text-red-400 mt-1">
            {costSummary?.current_cost}
          </p>
        </div>
        <div className="bg-gray-800/50 backdrop-blur border border-gray-700/50 rounded-xl p-5">
          <p className="text-xs text-gray-400 uppercase tracking-wider">
            Optimized Cost
          </p>
          <p className="text-2xl font-bold font-mono text-emerald-400 mt-1">
            {costSummary?.optimized_cost}
          </p>
        </div>
        <div className="bg-gray-800/50 backdrop-blur border border-gray-700/50 rounded-xl p-5">
          <p className="text-xs text-gray-400 uppercase tracking-wider">
            Total Savings
          </p>
          <p className="text-2xl font-bold font-mono text-emerald-400 mt-1">
            {costSummary?.total_savings}
          </p>
        </div>
        <div className="bg-gray-800/50 backdrop-blur border border-gray-700/50 rounded-xl p-5">
          <p className="text-xs text-gray-400 uppercase tracking-wider">
            Savings Rate
          </p>
          <p className="text-2xl font-bold font-mono text-emerald-400 mt-1">
            {formatPercent(costSummary?.total_savings_pct ?? 0)}
          </p>
        </div>
      </div>

      {(costSummary?.current_cpu_cost || raw) && (
        <div>
          <h2 className="text-sm font-semibold text-gray-300 mb-3">
            Workload cost split (CPU vs memory)
          </h2>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-gray-800/50 backdrop-blur border border-gray-700/50 rounded-xl p-4">
              <p className="text-xs text-gray-500 uppercase">Current CPU</p>
              <p className="text-lg font-mono text-sky-400 mt-1">
                {costSummary?.current_cpu_cost ??
                  (raw
                    ? `$${raw.total_current_cpu_cost.toFixed(2)}/mo`
                    : "—")}
              </p>
            </div>
            <div className="bg-gray-800/50 backdrop-blur border border-gray-700/50 rounded-xl p-4">
              <p className="text-xs text-gray-500 uppercase">Current memory</p>
              <p className="text-lg font-mono text-violet-400 mt-1">
                {costSummary?.current_memory_cost ??
                  (raw
                    ? `$${raw.total_current_memory_cost.toFixed(2)}/mo`
                    : "—")}
              </p>
            </div>
            <div className="bg-gray-800/50 backdrop-blur border border-gray-700/50 rounded-xl p-4">
              <p className="text-xs text-gray-500 uppercase">Optimized CPU</p>
              <p className="text-lg font-mono text-sky-300 mt-1">
                {costSummary?.optimized_cpu_cost ??
                  (raw
                    ? `$${raw.total_optimized_cpu_cost.toFixed(2)}/mo`
                    : "—")}
              </p>
            </div>
            <div className="bg-gray-800/50 backdrop-blur border border-gray-700/50 rounded-xl p-4">
              <p className="text-xs text-gray-500 uppercase">Optimized memory</p>
              <p className="text-lg font-mono text-violet-300 mt-1">
                {costSummary?.optimized_memory_cost ??
                  (raw
                    ? `$${raw.total_optimized_memory_cost.toFixed(2)}/mo`
                    : "—")}
              </p>
            </div>
          </div>
        </div>
      )}

      <CostComparison data={deploymentCosts} />

      <div className="bg-gray-800/50 backdrop-blur border border-gray-700/50 rounded-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-700/50">
          <h3 className="text-lg font-semibold text-gray-100">
            Per-Deployment Breakdown
          </h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                <th className="px-6 py-3">Deployment</th>
                <th className="px-6 py-3">Current Replicas</th>
                <th className="px-6 py-3">Optimized Replicas</th>
                <th className="px-6 py-3">CPU (curr)</th>
                <th className="px-6 py-3">Mem (curr)</th>
                <th className="px-6 py-3">Current</th>
                <th className="px-6 py-3">Optimized</th>
                <th className="px-6 py-3">Savings</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700/30">
              {deploymentCosts.map((d) => (
                <tr
                  key={d.deployment}
                  className="hover:bg-gray-700/20 transition-colors"
                >
                  <td className="px-6 py-4 text-sm text-gray-200 font-medium">
                    {d.deployment}
                  </td>
                  <td className="px-6 py-4 font-mono text-sm text-gray-300">
                    {d.current_replicas}
                  </td>
                  <td className="px-6 py-4 font-mono text-sm text-emerald-400">
                    {d.optimized_replicas}
                  </td>
                  <td className="px-6 py-4 font-mono text-xs text-sky-400/90">
                    {formatCurrency(d.current_cpu_cost)}
                  </td>
                  <td className="px-6 py-4 font-mono text-xs text-violet-400/90">
                    {formatCurrency(d.current_memory_cost)}
                  </td>
                  <td className="px-6 py-4 font-mono text-sm text-gray-300">
                    {formatCurrency(d.current_cost)}/mo
                  </td>
                  <td className="px-6 py-4 font-mono text-sm text-emerald-400">
                    {formatCurrency(d.optimized_cost)}/mo
                  </td>
                  <td className="px-6 py-4 font-mono text-sm text-emerald-400">
                    {formatCurrency(d.savings)} ({formatPercent(d.savings_pct)})
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {raw && raw.by_node.length > 0 && (
        <div className="bg-gray-800/50 backdrop-blur border border-gray-700/50 rounded-xl overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-700/50">
            <h3 className="text-lg font-semibold text-gray-100">
              Node Infrastructure Costs
            </h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  <th className="px-6 py-3">Node</th>
                  <th className="px-6 py-3">Instance Type</th>
                  <th className="px-6 py-3">Monthly Cost</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700/30">
                {raw.by_node.map((n) => (
                  <tr
                    key={n.node}
                    className="hover:bg-gray-700/20 transition-colors"
                  >
                    <td className="px-6 py-4 text-sm text-gray-200">
                      {n.node}
                    </td>
                    <td className="px-6 py-4 font-mono text-sm text-gray-300">
                      {n.instance_type}
                    </td>
                    <td className="px-6 py-4 font-mono text-sm text-gray-300">
                      {formatCurrency(n.monthly_cost)}/mo
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
