"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import type { DeploymentCost } from "@/lib/types";

interface CostComparisonProps {
  data: DeploymentCost[];
}

export default function CostComparison({ data }: CostComparisonProps) {
  const chartData = data.map((d) => ({
    name: d.deployment,
    Current: d.current_cost,
    Optimized: d.optimized_cost,
  }));

  return (
    <div className="bg-gray-800/50 backdrop-blur border border-gray-700/50 rounded-xl p-6">
      <h3 className="text-lg font-semibold text-gray-100 mb-4">
        Cost Comparison by Deployment
      </h3>
      <ResponsiveContainer width="100%" height={350}>
        <BarChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis
            dataKey="name"
            tick={{ fill: "#9CA3AF", fontSize: 12 }}
            axisLine={{ stroke: "#4B5563" }}
          />
          <YAxis
            tick={{ fill: "#9CA3AF", fontSize: 12 }}
            axisLine={{ stroke: "#4B5563" }}
            tickFormatter={(v) => `$${v}`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#1F2937",
              border: "1px solid #374151",
              borderRadius: "8px",
              color: "#F3F4F6",
            }}
            formatter={(value) => [`$${Number(value).toFixed(2)}/mo`]}
          />
          <Legend wrapperStyle={{ color: "#9CA3AF" }} />
          <Bar dataKey="Current" fill="#EF4444" radius={[4, 4, 0, 0]} />
          <Bar dataKey="Optimized" fill="#10B981" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
