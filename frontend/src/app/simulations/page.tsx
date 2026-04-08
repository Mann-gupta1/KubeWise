"use client";

import { useState } from "react";
import { api } from "@/lib/api";

export default function SimulationsPage() {
  const [scenario, setScenario] = useState("wasteful");
  const [loadFactor, setLoadFactor] = useState(3);
  const [nodesLost, setNodesLost] = useState(1);
  const [targetCpu, setTargetCpu] = useState(0.6);
  const [spikeResult, setSpikeResult] = useState<unknown>(null);
  const [failureResult, setFailureResult] = useState<unknown>(null);
  const [scaleResult, setScaleResult] = useState<unknown>(null);
  const [loading, setLoading] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);

  async function run(kind: "spike" | "failure" | "scale") {
    setErr(null);
    setLoading(kind);
    try {
      if (kind === "spike") {
        setSpikeResult(await api.simulateTrafficSpike(loadFactor, scenario));
      } else if (kind === "failure") {
        setFailureResult(await api.simulateNodeFailure(nodesLost, scenario));
      } else {
        setScaleResult(await api.simulateScaleResponse(targetCpu, scenario));
      }
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Request failed");
    } finally {
      setLoading(null);
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-100">Simulations</h1>
        <p className="text-gray-400 text-sm mt-1">
          Model traffic spikes, node loss, and HPA target response using the current cluster snapshot.
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <label className="text-sm text-gray-400">Scenario</label>
        <select
          value={scenario}
          onChange={(e) => setScenario(e.target.value)}
          className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-gray-200"
        >
          <option value="healthy">healthy</option>
          <option value="wasteful">wasteful</option>
          <option value="spike">spike</option>
        </select>
      </div>

      {err && (
        <div className="bg-red-900/20 border border-red-800 rounded-lg px-4 py-3 text-sm text-red-300">
          {err}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <section className="bg-gray-800/50 border border-gray-700/50 rounded-xl p-5 space-y-4">
          <h2 className="text-lg font-semibold text-gray-100">Traffic spike</h2>
          <p className="text-xs text-gray-500">
            Multiply observed load; estimate replicas, node pressure, and cost increase.
          </p>
          <label className="block text-sm text-gray-400">
            Load factor ({loadFactor}x)
            <input
              type="range"
              min={1}
              max={10}
              step={0.5}
              value={loadFactor}
              onChange={(e) => setLoadFactor(Number(e.target.value))}
              className="w-full mt-1"
            />
          </label>
          <button
            type="button"
            onClick={() => run("spike")}
            disabled={loading !== null}
            className="w-full py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium disabled:opacity-50"
          >
            {loading === "spike" ? "Running…" : "Run simulation"}
          </button>
          {spikeResult != null ? (
            <pre className="text-xs font-mono text-gray-300 bg-gray-900/80 rounded-lg p-3 overflow-x-auto max-h-80">
              {JSON.stringify(spikeResult, null, 2)}
            </pre>
          ) : null}
        </section>

        <section className="bg-gray-800/50 border border-gray-700/50 rounded-xl p-5 space-y-4">
          <h2 className="text-lg font-semibold text-gray-100">Node failure</h2>
          <p className="text-xs text-gray-500">
            Assume nodes become unavailable; see projected utilization and scheduling risk.
          </p>
          <label className="block text-sm text-gray-400">
            Nodes lost
            <input
              type="number"
              min={1}
              max={20}
              value={nodesLost}
              onChange={(e) => setNodesLost(Number(e.target.value))}
              className="mt-1 w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-1.5 text-gray-200"
            />
          </label>
          <button
            type="button"
            onClick={() => run("failure")}
            disabled={loading !== null}
            className="w-full py-2 rounded-lg bg-orange-600 hover:bg-orange-500 text-white text-sm font-medium disabled:opacity-50"
          >
            {loading === "failure" ? "Running…" : "Run simulation"}
          </button>
          {failureResult != null ? (
            <pre className="text-xs font-mono text-gray-300 bg-gray-900/80 rounded-lg p-3 overflow-x-auto max-h-80">
              {JSON.stringify(failureResult, null, 2)}
            </pre>
          ) : null}
        </section>

        <section className="bg-gray-800/50 border border-gray-700/50 rounded-xl p-5 space-y-4">
          <h2 className="text-lg font-semibold text-gray-100">Scale response</h2>
          <p className="text-xs text-gray-500">
            Replicas implied if HPA targets a CPU utilization ratio.
          </p>
          <label className="block text-sm text-gray-400">
            Target CPU util ({Math.round(targetCpu * 100)}%)
            <input
              type="range"
              min={0.3}
              max={0.9}
              step={0.05}
              value={targetCpu}
              onChange={(e) => setTargetCpu(Number(e.target.value))}
              className="w-full mt-1"
            />
          </label>
          <button
            type="button"
            onClick={() => run("scale")}
            disabled={loading !== null}
            className="w-full py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium disabled:opacity-50"
          >
            {loading === "scale" ? "Running…" : "Run simulation"}
          </button>
          {scaleResult != null ? (
            <pre className="text-xs font-mono text-gray-300 bg-gray-900/80 rounded-lg p-3 overflow-x-auto max-h-80">
              {JSON.stringify(scaleResult, null, 2)}
            </pre>
          ) : null}
        </section>
      </div>
    </div>
  );
}
