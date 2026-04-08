"use client";

import { formatCurrency, formatPercent } from "@/lib/format";
import StatusBadge from "./StatusBadge";

interface SavingsRow {
  deployment: string;
  namespace: string;
  current_cost: number;
  optimized_cost: number;
  savings: number;
  savings_pct: number;
}

interface SavingsTableProps {
  data: SavingsRow[];
}

export default function SavingsTable({ data }: SavingsTableProps) {
  const sorted = [...data].sort((a, b) => b.savings_pct - a.savings_pct);

  return (
    <div className="bg-gray-800/50 backdrop-blur border border-gray-700/50 rounded-xl overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-700/50">
        <h3 className="text-lg font-semibold text-gray-100">
          Savings Opportunities
        </h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
              <th className="px-6 py-3">Deployment</th>
              <th className="px-6 py-3">Current</th>
              <th className="px-6 py-3">Optimized</th>
              <th className="px-6 py-3">Savings</th>
              <th className="px-6 py-3">Impact</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-700/30">
            {sorted.map((row) => (
              <tr key={row.deployment} className="hover:bg-gray-700/20 transition-colors">
                <td className="px-6 py-4">
                  <div className="text-sm font-medium text-gray-200">
                    {row.deployment}
                  </div>
                  <div className="text-xs text-gray-500">{row.namespace}</div>
                </td>
                <td className="px-6 py-4 font-mono text-sm text-gray-300">
                  {formatCurrency(row.current_cost)}/mo
                </td>
                <td className="px-6 py-4 font-mono text-sm text-emerald-400">
                  {formatCurrency(row.optimized_cost)}/mo
                </td>
                <td className="px-6 py-4 font-mono text-sm text-emerald-400">
                  {formatCurrency(row.savings)}
                </td>
                <td className="px-6 py-4">
                  <StatusBadge
                    severity={row.savings_pct >= 40 ? "high" : row.savings_pct >= 20 ? "medium" : "low"}
                    label={formatPercent(row.savings_pct)}
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
