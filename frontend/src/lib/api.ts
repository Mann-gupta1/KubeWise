const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

async function fetchJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export const api = {
  getClusterMetrics: (scenario = "wasteful") =>
    fetchJSON(`/metrics/cluster?scenario=${scenario}`),

  getPodMetrics: (scenario = "wasteful") =>
    fetchJSON(`/metrics/pods?scenario=${scenario}`),

  getNodeMetrics: (scenario = "wasteful") =>
    fetchJSON(`/metrics/nodes?scenario=${scenario}`),

  getCpuTimeSeries: () =>
    fetchJSON(`/metrics/timeseries/cpu`),

  getMemoryTimeSeries: () =>
    fetchJSON(`/metrics/timeseries/memory`),

  getRecommendations: (
    scenario = "wasteful",
    severity?: string | null,
    deployment?: string | null,
  ) => {
    const q = new URLSearchParams({ scenario });
    if (severity) q.set("severity", severity);
    if (deployment) q.set("deployment", deployment);
    return fetchJSON(`/recommendations?${q.toString()}`);
  },

  getInefficiencies: (scenario = "wasteful") =>
    fetchJSON(`/recommendations/inefficiencies?scenario=${scenario}`),

  getCostSummary: (scenario = "wasteful") =>
    fetchJSON(`/cost/summary?scenario=${scenario}`),

  getCostByDeployment: (scenario = "wasteful") =>
    fetchJSON(`/cost/by-deployment?scenario=${scenario}`),

  refreshRecommendations: (scenario = "wasteful") =>
    fetchJSON(`/recommendations/refresh?scenario=${scenario}`),

  simulateTrafficSpike: (loadFactor: number, scenario = "wasteful") =>
    fetchJSON(
      `/simulations/traffic-spike?load_factor=${loadFactor}&scenario=${scenario}`,
    ),

  simulateNodeFailure: (nodesLost: number, scenario = "wasteful") =>
    fetchJSON(
      `/simulations/node-failure?nodes_lost=${nodesLost}&scenario=${scenario}`,
    ),

  simulateScaleResponse: (targetCpu: number, scenario = "wasteful") =>
    fetchJSON(
      `/simulations/scale-response?target_cpu_util=${targetCpu}&scenario=${scenario}`,
    ),
};
