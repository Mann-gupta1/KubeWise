"""CPU/memory utilization calculations for cluster resources."""

from __future__ import annotations


def compute_pod_utilization(pod: dict) -> dict:
    """Calculate utilization percentages for a single pod."""
    cpu_req = pod.get("cpu_request", 0) or 0.001
    mem_req = pod.get("memory_request", 0) or 0.001
    cpu_use = pod.get("cpu_usage", 0)
    mem_use = pod.get("memory_usage", 0)
    return {
        "pod_name": pod["name"],
        "deployment_name": pod.get("deployment_name", ""),
        "cpu_utilization": round(cpu_use / cpu_req, 4),
        "memory_utilization": round(mem_use / mem_req, 4),
        "cpu_waste": round(max(0, cpu_req - cpu_use), 4),
        "memory_waste": round(max(0, mem_req - mem_use), 4),
    }


def compute_node_utilization(node: dict) -> dict:
    """Calculate utilization percentages for a single node."""
    alloc_cpu = node.get("allocatable_cpu", 1)
    alloc_mem = node.get("allocatable_memory", 1)
    cpu_use = node.get("cpu_usage", 0)
    mem_use = node.get("memory_usage", 0)
    return {
        "node_name": node["name"],
        "instance_type": node.get("instance_type", "unknown"),
        "cpu_utilization": round(cpu_use / max(alloc_cpu, 0.001), 4),
        "memory_utilization": round(mem_use / max(alloc_mem, 0.001), 4),
        "cpu_available": round(alloc_cpu - cpu_use, 4),
        "memory_available": round(alloc_mem - mem_use, 4),
    }


def compute_deployment_utilization(deployment: dict) -> dict:
    """Calculate per-deployment aggregate utilization."""
    replicas = deployment.get("replicas", 1)
    total_requested_cpu = deployment["cpu_request"] * replicas
    total_requested_mem = deployment["memory_request"] * replicas
    total_used_cpu = deployment.get("total_cpu_usage", 0)
    total_used_mem = deployment.get("total_memory_usage", 0)
    return {
        "deployment_name": deployment["name"],
        "namespace": deployment.get("namespace", "default"),
        "replicas": replicas,
        "total_requested_cpu": round(total_requested_cpu, 4),
        "total_requested_memory": round(total_requested_mem, 4),
        "total_used_cpu": round(total_used_cpu, 4),
        "total_used_memory": round(total_used_mem, 4),
        "cpu_utilization": round(total_used_cpu / max(total_requested_cpu, 0.001), 4),
        "memory_utilization": round(total_used_mem / max(total_requested_mem, 0.001), 4),
    }
