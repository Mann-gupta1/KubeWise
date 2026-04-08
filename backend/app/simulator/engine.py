"""Traffic spike, node failure, and scale-response simulations."""

from __future__ import annotations

import math

from app.estimator.cost_estimator import estimate_deployment_cost


def _avg_node_utilization(cluster_data: dict) -> tuple[float, float]:
    nodes = cluster_data.get("nodes") or []
    if not nodes:
        return 0.35, 0.35
    cpu_pcts = [n.get("cpu_utilization_pct", 0) / 100.0 for n in nodes]
    mem_pcts = [n.get("memory_utilization_pct", 0) / 100.0 for n in nodes]
    return sum(cpu_pcts) / len(cpu_pcts), sum(mem_pcts) / len(mem_pcts)


def simulate_traffic_spike(cluster_data: dict, load_factor: float = 3.0) -> dict:
    """Scale load; estimate replicas, node pressure, and cost delta."""
    load_factor = max(1.0, min(load_factor, 10.0))
    summary = cluster_data.get("summary") or {}
    deployments = cluster_data.get("deployments") or []

    total_current_cost = 0.0
    total_predicted_cost = 0.0
    per_dep = []

    for dep in deployments:
        r = dep.get("replicas", 1)
        cpu_req = dep.get("cpu_request", 0.1)
        mem_req = dep.get("memory_request", 0.1)
        total_cpu_used = dep.get("total_cpu_usage", cpu_req * r * 0.5)
        scaled_cpu = total_cpu_used * load_factor
        needed = max(1, math.ceil(scaled_cpu / (cpu_req * 0.6)))
        predicted = max(r, needed)
        cur = estimate_deployment_cost(cpu_req, mem_req, r)
        pred = estimate_deployment_cost(cpu_req, mem_req, predicted)
        total_current_cost += cur
        total_predicted_cost += pred
        per_dep.append({
            "deployment": dep["name"],
            "current_replicas": r,
            "predicted_replicas": predicted,
            "load_factor": load_factor,
        })

    avg_cpu, avg_mem = _avg_node_utilization(cluster_data)
    stressed_cpu = min(0.99, avg_cpu * load_factor / max(summary.get("total_nodes", 3), 1) ** 0.5)
    stressed_mem = min(0.99, avg_mem * load_factor / max(summary.get("total_nodes", 3), 1) ** 0.5)
    pressure_score = (stressed_cpu + stressed_mem) / 2
    if pressure_score >= 0.85:
        node_pressure = "critical"
    elif pressure_score >= 0.65:
        node_pressure = "high"
    elif pressure_score >= 0.45:
        node_pressure = "medium"
    else:
        node_pressure = "low"

    cost_increase_pct = 0.0
    if total_current_cost > 0:
        cost_increase_pct = round(
            (total_predicted_cost - total_current_cost) / total_current_cost * 100, 1
        )

    return {
        "simulation_type": "traffic_spike",
        "load_factor": load_factor,
        "node_pressure": node_pressure,
        "pressure_score": round(pressure_score, 3),
        "cost_increase_pct": cost_increase_pct,
        "estimated_monthly_cost_before": round(total_current_cost, 2),
        "estimated_monthly_cost_after": round(total_predicted_cost, 2),
        "deployments": per_dep,
        "latency_risk": "high" if node_pressure in ("high", "critical") else "moderate",
    }


def simulate_node_failure(cluster_data: dict, nodes_lost: int = 1) -> dict:
    """Assume N nodes become unavailable; remaining nodes absorb load."""
    nodes = cluster_data.get("nodes") or []
    n = len(nodes)
    nodes_lost = max(1, min(nodes_lost, max(1, n - 1)))
    remaining = max(1, n - nodes_lost)
    summary = cluster_data.get("summary") or {}
    cpu_util = (summary.get("cpu_utilization_pct") or 50) / 100.0
    mem_util = (summary.get("memory_utilization_pct") or 50) / 100.0
    # Load concentrates on fewer nodes
    concentration = n / remaining
    new_cpu = min(0.99, cpu_util * concentration)
    new_mem = min(0.99, mem_util * concentration)
    pressure = (new_cpu + new_mem) / 2
    predicted_extra_replicas = max(0, math.ceil((pressure - 0.75) * 10)) if pressure > 0.75 else 0

    return {
        "simulation_type": "node_failure",
        "nodes_total": n,
        "nodes_lost": nodes_lost,
        "nodes_remaining": remaining,
        "projected_cpu_utilization": round(new_cpu * 100, 1),
        "projected_memory_utilization": round(new_mem * 100, 1),
        "node_pressure": "critical" if pressure > 0.9 else "high" if pressure > 0.75 else "medium",
        "predicted_extra_replicas_needed": predicted_extra_replicas,
        "scheduling_risk": "high" if new_cpu > 0.85 or new_mem > 0.85 else "low",
    }


def simulate_scale_response(cluster_data: dict, target_cpu_util: float = 0.6) -> dict:
    """How many replicas are needed if HPA targets target_cpu_util across workloads."""
    target_cpu_util = max(0.3, min(0.9, target_cpu_util))
    deployments = cluster_data.get("deployments") or []
    out = []
    for dep in deployments:
        r = dep.get("replicas", 1)
        cpu_req = dep.get("cpu_request", 0.1)
        total_used = dep.get("total_cpu_usage", cpu_req * r * 0.5)
        if cpu_req <= 0:
            continue
        # desired replicas ~= total_used / (cpu_req * target)
        desired = max(1, math.ceil(total_used / (cpu_req * target_cpu_util)))
        out.append({
            "deployment": dep["name"],
            "current_replicas": r,
            "replicas_for_target": desired,
            "delta": desired - r,
        })
    return {
        "simulation_type": "scale_response",
        "target_cpu_utilization": target_cpu_util,
        "deployments": out,
    }
