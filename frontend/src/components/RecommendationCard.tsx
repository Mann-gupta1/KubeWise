"use client";

import StatusBadge from "./StatusBadge";
import { formatPercent, formatCPU } from "@/lib/format";
import type { Recommendation } from "@/lib/types";

interface RecommendationCardProps {
  rec: Recommendation;
}

export default function RecommendationCard({ rec }: RecommendationCardProps) {
  return (
    <div className="bg-gray-800/50 backdrop-blur border border-gray-700/50 rounded-xl p-5 hover:border-gray-600/50 transition-colors">
      <div className="flex items-start justify-between mb-3">
        <div>
          <h4 className="text-sm font-semibold text-gray-100">
            {rec.deployment}
          </h4>
          <p className="text-xs text-gray-500 mt-0.5">{rec.namespace}</p>
        </div>
        <StatusBadge severity={rec.severity} />
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-400">Replicas</span>
          <span className="font-mono">
            <span className="text-gray-300">{rec.current_replicas}</span>
            <span className="text-gray-500 mx-1.5">&rarr;</span>
            <span className="text-emerald-400">{rec.recommended_replicas}</span>
          </span>
        </div>

        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-400">CPU Request</span>
          <span className="font-mono">
            <span className="text-gray-300">{formatCPU(rec.current_cpu_request)}</span>
            <span className="text-gray-500 mx-1.5">&rarr;</span>
            <span className="text-emerald-400">{formatCPU(rec.recommended_cpu_request)}</span>
          </span>
        </div>

        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-400">Est. Savings</span>
          <span className="font-mono text-emerald-400 font-semibold">
            {formatPercent(rec.estimated_savings_pct)}
          </span>
        </div>

        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-400">Confidence</span>
          <div className="flex items-center gap-2">
            <div className="w-16 h-1.5 bg-gray-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-400 rounded-full"
                style={{ width: `${rec.confidence * 100}%` }}
              />
            </div>
            <span className="font-mono text-gray-300 text-xs">
              {formatPercent(rec.confidence * 100)}
            </span>
          </div>
        </div>

        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-400">Traffic</span>
          <span className="text-gray-300 text-xs capitalize">
            {rec.traffic_pattern}
          </span>
        </div>

        {rec.confidence_breakdown && (
          <div className="pt-2 text-[10px] text-gray-500 font-mono space-y-0.5 border-t border-gray-700/20 mt-2">
            <div className="flex justify-between">
              <span>metrics consistency</span>
              <span>{rec.confidence_breakdown.metrics_consistency_score.toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span>traffic stability</span>
              <span>{rec.confidence_breakdown.traffic_pattern_stability.toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span>node pressure</span>
              <span>{rec.confidence_breakdown.node_pressure_score.toFixed(2)}</span>
            </div>
          </div>
        )}
      </div>

      <div className="mt-3 pt-3 border-t border-gray-700/30">
        <span className="text-xs text-gray-500">
          {rec.issue_type.replace(/_/g, " ")}
        </span>
      </div>
    </div>
  );
}
