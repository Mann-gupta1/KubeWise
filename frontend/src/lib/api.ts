/** Used when the app is opened on Vercel but `NEXT_PUBLIC_API_URL` was not baked into the build. */
const DEFAULT_API_ON_VERCEL = "https://kubewise.onrender.com/api/v1";

function getApiBase(): string {
  let fromEnv = process.env.NEXT_PUBLIC_API_URL?.trim();
  // Ignore a mis-set Vercel env that still points at localhost when the app runs on Vercel.
  if (fromEnv && typeof window !== "undefined") {
    const host = window.location.hostname;
    const onVercel = host === "kubewise.vercel.app" || host.endsWith(".vercel.app");
    if (onVercel && (fromEnv.includes("localhost") || fromEnv.includes("127.0.0.1"))) {
      fromEnv = "";
    }
  }
  if (fromEnv) return fromEnv.replace(/\/$/, "");

  if (typeof window !== "undefined") {
    const host = window.location.hostname;
    if (host === "kubewise.vercel.app" || host.endsWith(".vercel.app")) {
      return DEFAULT_API_ON_VERCEL;
    }
  }

  return "http://localhost:8000/api/v1";
}

const FETCH_TIMEOUT_MS = 120_000;

async function fetchJSON<T>(path: string): Promise<T> {
  const url = `${getApiBase()}${path}`;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);
  let res: Response;
  try {
    res = await fetch(url, { cache: "no-store", signal: controller.signal });
  } catch (e) {
    if (e instanceof Error) {
      if (e.name === "AbortError") {
        throw new Error(
          `Request timed out after ${FETCH_TIMEOUT_MS / 1000}s. Render free tier cold starts can take 60s+ — try again, or open your API /docs once to wake the service.`,
        );
      }
      if (e.message === "Failed to fetch" || e.name === "TypeError") {
        throw new Error(
          "Could not reach the API (network). Wake the Render service (visit its /docs), confirm it is not sleeping, and check CORS allows your Vercel origin.",
        );
      }
    }
    throw e;
  } finally {
    clearTimeout(timeoutId);
  }
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
