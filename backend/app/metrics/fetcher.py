"""Metrics fetcher with Prometheus live mode and mock fallback."""

from __future__ import annotations

import logging

import httpx

from app.config import settings

logger = logging.getLogger("kubewise.metrics")
from app.mock.generator import generate_cluster_data, generate_time_series
from app.metrics import prometheus_queries as pq


class MetricsFetcher:
    def __init__(self):
        self.mock_mode = settings.MOCK_MODE
        self.prom_url = settings.PROMETHEUS_URL

    async def get_cluster_snapshot(self, scenario: str = "wasteful") -> dict:
        if self.mock_mode:
            return generate_cluster_data(scenario)
        try:
            snap = await self._fetch_live_cluster()
            # Minimal Prometheus (only self-scrape `up`) has no kube_* / container_* series — queries return empty → UI all zeros.
            if settings.PROMETHEUS_FALLBACK_MOCK and self._live_snapshot_has_no_kubernetes_metrics(snap):
                logger.warning(
                    "Prometheus has no Kubernetes/cAdvisor metrics; using mock cluster (scenario=%s)",
                    scenario,
                )
                return generate_cluster_data(scenario)
            return snap
        except Exception as e:
            if settings.PROMETHEUS_FALLBACK_MOCK:
                logger.warning(
                    "Prometheus unavailable (%s); returning mock cluster (scenario=%s)",
                    e,
                    scenario,
                )
                return generate_cluster_data(scenario)
            raise

    @staticmethod
    def _live_snapshot_has_no_kubernetes_metrics(snap: dict) -> bool:
        summary = snap.get("summary") or {}
        return summary.get("total_nodes", 0) == 0 and summary.get("total_pods", 0) == 0

    async def get_cpu_time_series(self, pod_name: str | None = None) -> list[dict]:
        if self.mock_mode:
            return generate_time_series(base_value=0.15, variance=0.1)
        try:
            series = await self._query_range(pq.CPU_USAGE_BY_POD)
            if settings.PROMETHEUS_FALLBACK_MOCK and not series:
                logger.warning("Prometheus returned no CPU time series; using synthetic series")
                return generate_time_series(base_value=0.15, variance=0.1)
            return series
        except Exception as e:
            if settings.PROMETHEUS_FALLBACK_MOCK:
                logger.warning("Prometheus unavailable for CPU series (%s); using synthetic series", e)
                return generate_time_series(base_value=0.15, variance=0.1)
            raise

    async def get_memory_time_series(self, pod_name: str | None = None) -> list[dict]:
        if self.mock_mode:
            return generate_time_series(base_value=256_000_000, variance=0.08)
        try:
            series = await self._query_range(pq.MEMORY_USAGE_BY_POD)
            if settings.PROMETHEUS_FALLBACK_MOCK and not series:
                logger.warning("Prometheus returned no memory time series; using synthetic series")
                return generate_time_series(base_value=256_000_000, variance=0.08)
            return series
        except Exception as e:
            if settings.PROMETHEUS_FALLBACK_MOCK:
                logger.warning("Prometheus unavailable for memory series (%s); using synthetic series", e)
                return generate_time_series(base_value=256_000_000, variance=0.08)
            raise

    async def _fetch_live_cluster(self) -> dict:
        pods_cpu = await self._query_instant(pq.CPU_USAGE_BY_POD)
        pods_mem = await self._query_instant(pq.MEMORY_USAGE_BY_POD)
        nodes_cpu = await self._query_instant(pq.CPU_USAGE_BY_NODE)
        nodes_mem = await self._query_instant(pq.MEMORY_USAGE_BY_NODE)
        node_alloc_cpu = await self._query_instant(pq.NODE_ALLOCATABLE_CPU)
        node_alloc_mem = await self._query_instant(pq.NODE_ALLOCATABLE_MEMORY)
        replicas = await self._query_instant(pq.DEPLOYMENT_REPLICAS)
        cpu_requests = await self._query_instant(pq.CPU_REQUESTS_BY_POD)
        mem_requests = await self._query_instant(pq.MEMORY_REQUESTS_BY_POD)

        nodes_data = self._build_nodes(nodes_cpu, nodes_mem, node_alloc_cpu, node_alloc_mem)
        pods_data = self._build_pods(pods_cpu, pods_mem, cpu_requests, mem_requests)
        deployments_data = self._build_deployments(pods_data, replicas)

        total_cpu_alloc = sum(n["allocatable_cpu"] for n in nodes_data)
        total_mem_alloc = sum(n["allocatable_memory"] for n in nodes_data)
        total_cpu_used = sum(p["cpu_usage"] for p in pods_data)
        total_mem_used = sum(p["memory_usage"] for p in pods_data)

        return {
            "cluster": {"name": "live-cluster", "provider": "aws", "region": "unknown"},
            "summary": {
                "total_nodes": len(nodes_data),
                "total_pods": len(pods_data),
                "total_deployments": len(deployments_data),
                "total_cpu_allocatable": total_cpu_alloc,
                "total_memory_allocatable": total_mem_alloc,
                "total_cpu_usage": round(total_cpu_used, 4),
                "total_memory_usage": round(total_mem_used, 4),
                "cpu_utilization_pct": round(total_cpu_used / max(total_cpu_alloc, 0.01) * 100, 1),
                "memory_utilization_pct": round(total_mem_used / max(total_mem_alloc, 0.01) * 100, 1),
            },
            "nodes": nodes_data,
            "deployments": deployments_data,
            "pods": pods_data,
        }

    async def _query_instant(self, query: str) -> list[dict]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.prom_url}/api/v1/query",
                params={"query": query},
                timeout=10.0,
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("data", {}).get("result", [])

    async def _query_range(self, query: str, duration_hours: int = 6) -> list[dict]:
        import time

        end = time.time()
        start = end - duration_hours * 3600
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.prom_url}/api/v1/query_range",
                params={"query": query, "start": start, "end": end, "step": "300"},
                timeout=10.0,
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("data", {}).get("result", [])

    def _build_nodes(self, cpu_data, mem_data, alloc_cpu, alloc_mem) -> list[dict]:
        cpu_map = {r["metric"].get("node", ""): float(r["value"][1]) for r in cpu_data}
        mem_map = {r["metric"].get("node", ""): float(r["value"][1]) for r in mem_data}
        alloc_cpu_map = {r["metric"].get("node", ""): float(r["value"][1]) for r in alloc_cpu}
        alloc_mem_map = {r["metric"].get("node", ""): float(r["value"][1]) / (1024**3) for r in alloc_mem}

        nodes = []
        for name in alloc_cpu_map:
            ac = alloc_cpu_map.get(name, 1)
            am = alloc_mem_map.get(name, 1)
            cu = cpu_map.get(name, 0)
            mu = mem_map.get(name, 0) / (1024**3)
            nodes.append({
                "name": name,
                "instance_type": "unknown",
                "allocatable_cpu": ac,
                "allocatable_memory": round(am, 2),
                "cpu_usage": round(cu, 4),
                "memory_usage": round(mu, 4),
                "cpu_utilization_pct": round(cu / max(ac, 0.01) * 100, 1),
                "memory_utilization_pct": round(mu / max(am, 0.01) * 100, 1),
                "status": "Ready",
            })
        return nodes

    def _build_pods(self, cpu_data, mem_data, req_cpu, req_mem) -> list[dict]:
        cpu_map = {r["metric"].get("pod", ""): float(r["value"][1]) for r in cpu_data}
        mem_map = {r["metric"].get("pod", ""): float(r["value"][1]) / (1024**3) for r in mem_data}
        req_cpu_map = {r["metric"].get("pod", ""): float(r["value"][1]) for r in req_cpu}
        req_mem_map = {r["metric"].get("pod", ""): float(r["value"][1]) / (1024**3) for r in req_mem}

        pods = []
        for name in cpu_map:
            cu = cpu_map.get(name, 0)
            mu = mem_map.get(name, 0)
            rc = req_cpu_map.get(name, cu)
            rm = req_mem_map.get(name, mu)
            parts = name.rsplit("-", 2)
            dep_name = parts[0] if len(parts) >= 3 else name
            pods.append({
                "name": name,
                "deployment_name": dep_name,
                "namespace": "default",
                "node_name": "unknown",
                "cpu_request": round(rc, 4),
                "memory_request": round(rm, 4),
                "cpu_usage": round(cu, 4),
                "memory_usage": round(mu, 4),
                "cpu_utilization_pct": round(cu / max(rc, 0.001) * 100, 1),
                "memory_utilization_pct": round(mu / max(rm, 0.001) * 100, 1),
            })
        return pods

    def _build_deployments(self, pods_data, replicas_data) -> list[dict]:
        replica_map = {r["metric"].get("deployment", ""): int(float(r["value"][1])) for r in replicas_data}
        dep_pods: dict[str, list] = {}
        for p in pods_data:
            dep_pods.setdefault(p["deployment_name"], []).append(p)

        deployments = []
        for dep_name, pods in dep_pods.items():
            total_cpu = sum(p["cpu_usage"] for p in pods)
            total_mem = sum(p["memory_usage"] for p in pods)
            deployments.append({
                "name": dep_name,
                "namespace": pods[0]["namespace"],
                "replicas": replica_map.get(dep_name, len(pods)),
                "cpu_request": pods[0]["cpu_request"],
                "memory_request": pods[0]["memory_request"],
                "total_cpu_usage": round(total_cpu, 4),
                "total_memory_usage": round(total_mem, 4),
            })
        return deployments


fetcher = MetricsFetcher()
