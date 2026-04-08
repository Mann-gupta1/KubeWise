"""Detect resource inefficiencies in cluster workloads."""

from __future__ import annotations

import math

from app.analyzer.resource_analyzer import (
    compute_deployment_utilization,
    compute_node_utilization,
)


OVERPROVISIONED_THRESHOLD = 0.5  # usage < 50% of request
UNDERUTILIZED_NODE_THRESHOLD = 0.20  # node < 20% utilization
TARGET_CPU_UTILIZATION = 0.60


def detect_all_inefficiencies(cluster_data: dict) -> list[dict]:
    """Run all detection rules and return a list of findings."""
    findings: list[dict] = []

    for dep in cluster_data.get("deployments", []):
        util = compute_deployment_utilization(dep)
        findings.extend(_check_overprovisioned_cpu(dep, util))
        findings.extend(_check_overprovisioned_memory(dep, util))
        findings.extend(_check_replica_mismatch(dep, util))

    for node in cluster_data.get("nodes", []):
        util = compute_node_utilization(node)
        findings.extend(_check_underutilized_node(node, util))

    return findings


def _check_overprovisioned_cpu(dep: dict, util: dict) -> list[dict]:
    if util["cpu_utilization"] < OVERPROVISIONED_THRESHOLD:
        waste_pct = round((1 - util["cpu_utilization"]) * 100, 1)
        severity = _severity_from_waste(waste_pct)
        return [{
            "deployment": dep["name"],
            "namespace": dep.get("namespace", "default"),
            "issue_type": "overprovisioned_cpu",
            "severity": severity,
            "current_request": dep["cpu_request"],
            "actual_usage_per_replica": round(util["total_used_cpu"] / max(dep.get("replicas", 1), 1), 4),
            "recommended_request": round(util["total_used_cpu"] / max(dep.get("replicas", 1), 1) * 1.2, 4),
            "utilization_pct": round(util["cpu_utilization"] * 100, 1),
            "waste_pct": waste_pct,
        }]
    return []


def _check_overprovisioned_memory(dep: dict, util: dict) -> list[dict]:
    if util["memory_utilization"] < OVERPROVISIONED_THRESHOLD:
        waste_pct = round((1 - util["memory_utilization"]) * 100, 1)
        severity = _severity_from_waste(waste_pct)
        return [{
            "deployment": dep["name"],
            "namespace": dep.get("namespace", "default"),
            "issue_type": "overprovisioned_memory",
            "severity": severity,
            "current_request": dep["memory_request"],
            "actual_usage_per_replica": round(util["total_used_memory"] / max(dep.get("replicas", 1), 1), 4),
            "recommended_request": round(util["total_used_memory"] / max(dep.get("replicas", 1), 1) * 1.2, 4),
            "utilization_pct": round(util["memory_utilization"] * 100, 1),
            "waste_pct": waste_pct,
        }]
    return []


def _check_replica_mismatch(dep: dict, util: dict) -> list[dict]:
    avg_cpu_per_replica = util["total_used_cpu"] / max(dep.get("replicas", 1), 1)
    recommended = max(1, math.ceil(util["total_used_cpu"] / (dep["cpu_request"] * TARGET_CPU_UTILIZATION)))
    current = dep.get("replicas", 1)

    if current > recommended and current - recommended >= 1:
        savings_pct = round((current - recommended) / current * 100, 1)
        return [{
            "deployment": dep["name"],
            "namespace": dep.get("namespace", "default"),
            "issue_type": "replica_mismatch",
            "severity": "medium" if savings_pct < 40 else "high",
            "current_replicas": current,
            "recommended_replicas": recommended,
            "avg_cpu_per_replica": round(avg_cpu_per_replica, 4),
            "savings_pct": savings_pct,
        }]
    return []


def _check_underutilized_node(node: dict, util: dict) -> list[dict]:
    if (util["cpu_utilization"] < UNDERUTILIZED_NODE_THRESHOLD
            and util["memory_utilization"] < UNDERUTILIZED_NODE_THRESHOLD):
        return [{
            "node": node["name"],
            "issue_type": "underutilized_node",
            "severity": "high",
            "instance_type": node.get("instance_type", "unknown"),
            "cpu_utilization_pct": round(util["cpu_utilization"] * 100, 1),
            "memory_utilization_pct": round(util["memory_utilization"] * 100, 1),
        }]
    return []


def _severity_from_waste(waste_pct: float) -> str:
    if waste_pct >= 80:
        return "critical"
    if waste_pct >= 60:
        return "high"
    if waste_pct >= 40:
        return "medium"
    return "low"
