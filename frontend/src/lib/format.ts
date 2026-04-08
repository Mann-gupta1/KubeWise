export function formatCurrency(value: number): string {
  return `$${value.toFixed(2)}`;
}

export function formatPercent(value: number): string {
  return `${value.toFixed(1)}%`;
}

export function formatCPU(cores: number): string {
  if (cores < 1) {
    return `${Math.round(cores * 1000)}m`;
  }
  return `${cores.toFixed(2)} cores`;
}

export function formatMemory(gib: number): string {
  if (gib < 1) {
    return `${Math.round(gib * 1024)} MiB`;
  }
  return `${gib.toFixed(1)} GiB`;
}

export function severityColor(severity: string): string {
  switch (severity) {
    case "critical":
      return "text-red-400 bg-red-400/10 border-red-400/20";
    case "high":
      return "text-orange-400 bg-orange-400/10 border-orange-400/20";
    case "medium":
      return "text-yellow-400 bg-yellow-400/10 border-yellow-400/20";
    case "low":
      return "text-green-400 bg-green-400/10 border-green-400/20";
    default:
      return "text-gray-400 bg-gray-400/10 border-gray-400/20";
  }
}

export function utilizationColor(pct: number): string {
  if (pct >= 80) return "bg-red-500";
  if (pct >= 60) return "bg-yellow-500";
  if (pct >= 40) return "bg-green-500";
  return "bg-blue-500";
}
