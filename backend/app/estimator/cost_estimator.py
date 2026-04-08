"""Cost estimation engine using static AWS pricing data."""

from __future__ import annotations

from app.estimator.pricing_data import (
    INSTANCE_PRICING,
    HOURS_PER_MONTH,
    PRICE_PER_VCPU_HOUR,
    PRICE_PER_GIB_HOUR,
)


def estimate_node_cost(instance_type: str) -> float:
    """Monthly cost for a single node."""
    info = INSTANCE_PRICING.get(instance_type)
    if info:
        return round(info["price_per_hour"] * HOURS_PER_MONTH, 2)
    return round(0.10 * HOURS_PER_MONTH, 2)


def deployment_cpu_cost_monthly(cpu_request: float, replicas: int) -> float:
    return round(cpu_request * replicas * PRICE_PER_VCPU_HOUR * HOURS_PER_MONTH, 2)


def deployment_memory_cost_monthly(memory_request: float, replicas: int) -> float:
    return round(memory_request * replicas * PRICE_PER_GIB_HOUR * HOURS_PER_MONTH, 2)


def estimate_deployment_cost(cpu_request: float, memory_request: float, replicas: int) -> float:
    """Monthly cost of a deployment based on requested resources."""
    return round(
        deployment_cpu_cost_monthly(cpu_request, replicas)
        + deployment_memory_cost_monthly(memory_request, replicas),
        2,
    )


def estimate_cluster_cost(cluster_data: dict) -> dict:
    """Full cost breakdown: current, optimized, and savings."""
    current_costs = []
    optimized_costs = []

    for dep in cluster_data.get("deployments", []):
        replicas = dep.get("replicas", 1)
        cpu_req = dep.get("cpu_request", 0)
        mem_req = dep.get("memory_request", 0)
        total_cpu_used = dep.get("total_cpu_usage", cpu_req * replicas * 0.5)
        total_mem_used = dep.get("total_memory_usage", mem_req * replicas * 0.5)

        current = estimate_deployment_cost(cpu_req, mem_req, replicas)
        cur_cpu = deployment_cpu_cost_monthly(cpu_req, replicas)
        cur_mem = deployment_memory_cost_monthly(mem_req, replicas)

        optimized_cpu = max(0.05, total_cpu_used / max(replicas, 1)) * 1.2
        optimized_mem = max(0.05, total_mem_used / max(replicas, 1)) * 1.2
        import math
        optimized_replicas = max(1, math.ceil(total_cpu_used / (cpu_req * 0.6))) if cpu_req > 0 else replicas
        optimized = estimate_deployment_cost(optimized_cpu, optimized_mem, optimized_replicas)
        opt_cpu = deployment_cpu_cost_monthly(optimized_cpu, optimized_replicas)
        opt_mem = deployment_memory_cost_monthly(optimized_mem, optimized_replicas)

        current_costs.append({
            "deployment": dep["name"],
            "namespace": dep.get("namespace", "default"),
            "current_cost": current,
            "current_cpu_cost": cur_cpu,
            "current_memory_cost": cur_mem,
            "optimized_cost": round(optimized, 2),
            "optimized_cpu_cost": opt_cpu,
            "optimized_memory_cost": opt_mem,
            "savings": round(current - optimized, 2),
            "savings_pct": round(max(0, (current - optimized) / max(current, 0.01) * 100), 1),
            "current_cpu_request": cpu_req,
            "optimized_cpu_request": round(optimized_cpu, 4),
            "current_replicas": replicas,
            "optimized_replicas": optimized_replicas,
        })

    node_costs = []
    for node in cluster_data.get("nodes", []):
        cost = estimate_node_cost(node.get("instance_type", "t3.medium"))
        node_costs.append({
            "node": node["name"],
            "instance_type": node.get("instance_type", "unknown"),
            "monthly_cost": cost,
        })

    total_current = sum(d["current_cost"] for d in current_costs)
    total_optimized = sum(d["optimized_cost"] for d in current_costs)
    total_node_cost = sum(n["monthly_cost"] for n in node_costs)
    total_current_cpu = sum(d["current_cpu_cost"] for d in current_costs)
    total_current_mem = sum(d["current_memory_cost"] for d in current_costs)
    total_optimized_cpu = sum(d["optimized_cpu_cost"] for d in current_costs)
    total_optimized_mem = sum(d["optimized_memory_cost"] for d in current_costs)

    return {
        "total_current_cost": round(total_current, 2),
        "total_optimized_cost": round(total_optimized, 2),
        "total_savings": round(total_current - total_optimized, 2),
        "total_savings_pct": round(
            max(0, (total_current - total_optimized) / max(total_current, 0.01) * 100), 1
        ),
        "total_node_infrastructure_cost": round(total_node_cost, 2),
        "total_current_cpu_cost": round(total_current_cpu, 2),
        "total_current_memory_cost": round(total_current_mem, 2),
        "total_optimized_cpu_cost": round(total_optimized_cpu, 2),
        "total_optimized_memory_cost": round(total_optimized_mem, 2),
        "by_deployment": current_costs,
        "by_node": node_costs,
    }
