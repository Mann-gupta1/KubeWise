"""Autoscaling recommendation engine for HPA tuning and resource right-sizing."""

from __future__ import annotations

import math

from app.recommender.confidence import compute_confidence_advanced


TARGET_CPU_UTILIZATION = 0.60
HEADROOM_FACTOR = 1.20  # 20% buffer above p95


def generate_recommendations(cluster_data: dict) -> list[dict]:
    """Produce scaling recommendations for every deployment in the cluster."""
    recommendations = []
    for dep in cluster_data.get("deployments", []):
        rec = _recommend_for_deployment(dep)
        if rec:
            recommendations.append(rec)
    return recommendations


def _recommend_for_deployment(dep: dict) -> dict | None:
    replicas = dep.get("replicas", 1)
    cpu_request = dep.get("cpu_request", 0)
    mem_request = dep.get("memory_request", 0)
    total_cpu_used = dep.get("total_cpu_usage", 0)
    total_mem_used = dep.get("total_memory_usage", 0)

    if cpu_request <= 0 or replicas <= 0:
        return None

    avg_cpu_per_replica = total_cpu_used / replicas
    avg_mem_per_replica = total_mem_used / replicas

    recommended_replicas = max(1, math.ceil(
        total_cpu_used / (cpu_request * TARGET_CPU_UTILIZATION)
    ))

    recommended_cpu = round(avg_cpu_per_replica * HEADROOM_FACTOR, 4)
    recommended_mem = round(avg_mem_per_replica * HEADROOM_FACTOR, 4)
    recommended_cpu = max(0.05, recommended_cpu)
    recommended_mem = max(0.05, recommended_mem)

    cpu_util_ratio = avg_cpu_per_replica / cpu_request

    traffic_pattern = _classify_traffic(cpu_util_ratio)
    # Node-level pressure not available per-deployment; use neutral defaults (see confidence.py).
    confidence, confidence_breakdown = compute_confidence_advanced(
        cpu_util_ratio,
        traffic_pattern=traffic_pattern,
        avg_node_cpu_util=0.5,
        avg_node_mem_util=0.5,
    )

    current_total_cpu = cpu_request * replicas
    optimized_total_cpu = recommended_cpu * recommended_replicas
    estimated_savings = round(
        max(0, (current_total_cpu - optimized_total_cpu) / max(current_total_cpu, 0.001) * 100), 1
    )

    has_change = (
        recommended_replicas != replicas
        or abs(recommended_cpu - cpu_request) > 0.01
    )
    if not has_change:
        return None

    issue_type = "replica_mismatch"
    if recommended_replicas == replicas and recommended_cpu < cpu_request:
        issue_type = "overprovisioned_cpu"
    elif recommended_replicas < replicas:
        issue_type = "replica_mismatch"

    severity = "low"
    if estimated_savings >= 40:
        severity = "high"
    elif estimated_savings >= 20:
        severity = "medium"

    return {
        "deployment": dep["name"],
        "namespace": dep.get("namespace", "default"),
        "issue_type": issue_type,
        "severity": severity,
        "current_replicas": replicas,
        "recommended_replicas": recommended_replicas,
        "current_cpu_request": cpu_request,
        "recommended_cpu_request": recommended_cpu,
        "current_memory_request": mem_request,
        "recommended_memory_request": recommended_mem,
        "estimated_savings_pct": estimated_savings,
        "confidence": confidence,
        "confidence_breakdown": confidence_breakdown,
        "traffic_pattern": traffic_pattern,
    }


def _classify_traffic(util_ratio: float) -> str:
    if util_ratio < 0.3:
        return "low"
    if util_ratio < 0.6:
        return "stable"
    if util_ratio < 0.85:
        return "moderate"
    return "high"
