"use client";

import { useCallback, useEffect, useState } from "react";
import RecommendationCard from "@/components/RecommendationCard";
import { api } from "@/lib/api";
import type { Recommendation } from "@/lib/types";

export default function RecommendationsPage() {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterSeverity, setFilterSeverity] = useState<string>("all");
  const [deploymentFilter, setDeploymentFilter] = useState("");
  const [debouncedDeployment, setDebouncedDeployment] = useState("");
  const [sortBy, setSortBy] = useState<"savings" | "confidence">("savings");

  useEffect(() => {
    const id = setTimeout(() => setDebouncedDeployment(deploymentFilter.trim()), 350);
    return () => clearTimeout(id);
  }, [deploymentFilter]);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = (await api.getRecommendations(
        "wasteful",
        filterSeverity === "all" ? null : filterSeverity,
        debouncedDeployment || null,
      )) as Recommendation[];
      setRecommendations(data);
    } catch {
      setRecommendations([]);
    } finally {
      setLoading(false);
    }
  }, [filterSeverity, debouncedDeployment]);

  useEffect(() => {
    load();
  }, [load]);

  const sorted = [...recommendations].sort((a, b) =>
    sortBy === "savings"
      ? b.estimated_savings_pct - a.estimated_savings_pct
      : b.confidence - a.confidence,
  );

  if (loading && recommendations.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-gray-400 text-lg">Analyzing deployments...</div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-100">
            Autoscaling Recommendations
          </h1>
          <p className="text-gray-400 text-sm mt-1">
            {recommendations.length} optimization opportunities
            {deploymentFilter.trim() || filterSeverity !== "all"
              ? " (filtered)"
              : " detected"}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <input
            type="text"
            placeholder="Filter by deployment name"
            value={deploymentFilter}
            onChange={(e) => setDeploymentFilter(e.target.value)}
            className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-gray-200 placeholder:text-gray-500 min-w-[180px]"
          />
          <select
            value={filterSeverity}
            onChange={(e) => setFilterSeverity(e.target.value)}
            className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All severities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as "savings" | "confidence")}
            className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="savings">Sort by savings</option>
            <option value="confidence">Sort by confidence</option>
          </select>
        </div>
      </div>

      {sorted.length === 0 ? (
        <div className="bg-gray-800/50 border border-gray-700/50 rounded-xl p-8 text-center">
          <p className="text-gray-400">
            No recommendations match the selected filters.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {sorted.map((rec, i) => (
            <RecommendationCard key={`${rec.deployment}-${i}`} rec={rec} />
          ))}
        </div>
      )}
    </div>
  );
}
