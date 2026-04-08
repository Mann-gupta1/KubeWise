"use client";

import { severityColor } from "@/lib/format";

interface StatusBadgeProps {
  severity: string;
  label?: string;
}

export default function StatusBadge({ severity, label }: StatusBadgeProps) {
  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${severityColor(severity)}`}
    >
      {label || severity}
    </span>
  );
}
