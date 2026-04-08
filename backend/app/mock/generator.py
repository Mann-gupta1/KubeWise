"""Synthetic cluster metrics generator for mock/demo mode."""

from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np

from app.mock.scenarios import ClusterScenario, ALL_SCENARIOS


def generate_time_series(
    base_value: float,
    variance: float,
    points: int = 60,
    interval_minutes: int = 5,
) -> list[dict]:
    """Generate a realistic time-series with noise around a base value."""
    now = datetime.utcnow()
    rng = np.random.default_rng()
    noise = rng.normal(0, variance * base_value, points)
    values = np.clip(base_value + noise, 0.01, None)
    return [
        {
            "timestamp": (now - timedelta(minutes=interval_minutes * (points - i))).isoformat(),
            "value": round(float(v), 4),
        }
        for i, v in enumerate(values)
    ]


def generate_cluster_data(scenario_name: str = "wasteful") -> dict:
    """Generate a full snapshot of cluster data for the given scenario."""
    scenario = ALL_SCENARIOS.get(scenario_name, ALL_SCENARIOS["wasteful"])
    return _build_cluster_snapshot(scenario)


def _build_cluster_snapshot(scenario: ClusterScenario) -> dict:
    rng = np.random.default_rng()

    nodes_data = []
    for node in scenario.nodes:
        node_cpu_used = 0.0
        node_mem_used = 0.0
        for dep in scenario.deployments:
            per_node_fraction = 1.0 / len(scenario.nodes)
            node_cpu_used += dep.cpu_request * dep.cpu_usage_ratio * dep.replicas * per_node_fraction
            node_mem_used += dep.memory_request * dep.memory_usage_ratio * dep.replicas * per_node_fraction

        node_cpu_used *= (1 + rng.normal(0, 0.05))
        node_mem_used *= (1 + rng.normal(0, 0.05))

        nodes_data.append({
            "name": node.name,
            "instance_type": node.instance_type,
            "allocatable_cpu": node.allocatable_cpu,
            "allocatable_memory": node.allocatable_memory,
            "cpu_usage": round(max(0.01, node_cpu_used), 4),
            "memory_usage": round(max(0.01, node_mem_used), 4),
            "cpu_utilization_pct": round(min(99, max(1, node_cpu_used / node.allocatable_cpu * 100)), 1),
            "memory_utilization_pct": round(min(99, max(1, node_mem_used / node.allocatable_memory * 100)), 1),
            "status": "Ready",
        })

    deployments_data = []
    pods_data = []
    for dep in scenario.deployments:
        actual_cpu = dep.cpu_request * dep.cpu_usage_ratio
        actual_mem = dep.memory_request * dep.memory_usage_ratio

        deployments_data.append({
            "name": dep.name,
            "namespace": dep.namespace,
            "replicas": dep.replicas,
            "cpu_request": dep.cpu_request,
            "memory_request": dep.memory_request,
            "total_cpu_usage": round(actual_cpu * dep.replicas, 4),
            "total_memory_usage": round(actual_mem * dep.replicas, 4),
        })

        for i in range(dep.replicas):
            pod_cpu = actual_cpu * (1 + rng.normal(0, dep.usage_variance))
            pod_mem = actual_mem * (1 + rng.normal(0, dep.usage_variance))
            pods_data.append({
                "name": f"{dep.name}-{_pod_hash()}-{_pod_suffix()}",
                "deployment_name": dep.name,
                "namespace": dep.namespace,
                "node_name": scenario.nodes[i % len(scenario.nodes)].name,
                "cpu_request": dep.cpu_request,
                "memory_request": dep.memory_request,
                "cpu_usage": round(max(0.001, pod_cpu), 4),
                "memory_usage": round(max(0.001, pod_mem), 4),
                "cpu_utilization_pct": round(min(99, max(1, pod_cpu / dep.cpu_request * 100)), 1),
                "memory_utilization_pct": round(min(99, max(1, pod_mem / dep.memory_request * 100)), 1),
            })

    total_cpu_allocatable = sum(n.allocatable_cpu for n in scenario.nodes)
    total_mem_allocatable = sum(n.allocatable_memory for n in scenario.nodes)
    total_cpu_used = sum(p["cpu_usage"] for p in pods_data)
    total_mem_used = sum(p["memory_usage"] for p in pods_data)

    return {
        "cluster": {
            "name": scenario.name,
            "provider": scenario.provider,
            "region": scenario.region,
            "description": scenario.description,
        },
        "summary": {
            "total_nodes": len(scenario.nodes),
            "total_pods": len(pods_data),
            "total_deployments": len(scenario.deployments),
            "total_cpu_allocatable": total_cpu_allocatable,
            "total_memory_allocatable": total_mem_allocatable,
            "total_cpu_usage": round(total_cpu_used, 4),
            "total_memory_usage": round(total_mem_used, 4),
            "cpu_utilization_pct": round(total_cpu_used / total_cpu_allocatable * 100, 1),
            "memory_utilization_pct": round(total_mem_used / total_mem_allocatable * 100, 1),
        },
        "nodes": nodes_data,
        "deployments": deployments_data,
        "pods": pods_data,
    }


def _pod_hash() -> str:
    return "".join(np.random.choice(list("abcdef0123456789"), 9))


def _pod_suffix() -> str:
    return "".join(np.random.choice(list("abcdefghijklmnopqrstuvwxyz0123456789"), 5))
