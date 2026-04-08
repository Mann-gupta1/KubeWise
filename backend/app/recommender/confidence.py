"""Recommendation confidence scoring — basic and advanced (multi-factor)."""

from __future__ import annotations


def compute_confidence(
    utilization_ratio: float,
    sample_count: int = 60,
    variance: float = 0.05,
) -> float:
    """Weighted score: consistency, sample window, utilization gap."""
    consistency_score = max(0, 1.0 - variance * 5)

    sample_score = min(1.0, sample_count / 60)

    gap = abs(1.0 - utilization_ratio)
    gap_score = min(1.0, gap * 2)

    weights = {"consistency": 0.35, "sample_size": 0.25, "gap": 0.40}
    raw = (
        consistency_score * weights["consistency"]
        + sample_score * weights["sample_size"]
        + gap_score * weights["gap"]
    )
    return round(min(0.99, max(0.10, raw)), 2)


def compute_confidence_advanced(
    utilization_ratio: float,
    *,
    sample_count: int = 60,
    variance: float = 0.05,
    traffic_pattern: str = "stable",
    avg_node_cpu_util: float = 0.5,
    avg_node_mem_util: float = 0.5,
) -> tuple[float, dict[str, float]]:
    """Multi-factor confidence: metrics consistency, traffic stability, node pressure.

    - traffic_pattern: classified workload stability (stable → higher confidence).
    - node pressure: average node utilization; hot clusters reduce confidence in aggressive changes.
    """
    traffic_stability_map = {
        "low": 0.78,
        "stable": 0.95,
        "moderate": 0.82,
        "high": 0.68,
        "spiky": 0.52,
    }
    traffic_stability = traffic_stability_map.get(traffic_pattern, 0.85)

    node_pressure = (avg_node_cpu_util + avg_node_mem_util) / 2.0
    node_pressure_score = max(0.2, 1.0 - node_pressure * 0.45)

    metrics_consistency_score = compute_confidence(utilization_ratio, sample_count, variance)

    weights = {
        "metrics_consistency": 0.40,
        "traffic_stability": 0.30,
        "node_pressure": 0.30,
    }
    combined = (
        metrics_consistency_score * weights["metrics_consistency"]
        + traffic_stability * weights["traffic_stability"]
        + node_pressure_score * weights["node_pressure"]
    )
    score = round(min(0.99, max(0.10, combined)), 2)
    breakdown = {
        "metrics_consistency_score": round(metrics_consistency_score, 3),
        "traffic_pattern_stability": round(traffic_stability, 3),
        "node_pressure_score": round(node_pressure_score, 3),
        "raw_node_pressure": round(node_pressure, 3),
    }
    return score, breakdown
