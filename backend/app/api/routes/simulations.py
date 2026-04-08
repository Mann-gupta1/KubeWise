from fastapi import APIRouter, Query

from app.metrics import cache as snapshot_cache
from app.metrics.fetcher import fetcher
from app.simulator.engine import (
    simulate_node_failure,
    simulate_scale_response,
    simulate_traffic_spike,
)
from app.db.persist import run_persist_simulation

router = APIRouter(prefix="/simulations", tags=["simulations"])


async def _cluster_data(scenario: str) -> dict:
    snap = snapshot_cache.get_cached_snapshot()
    if snap is not None:
        return snap
    return await snapshot_cache.refresh_snapshot(scenario)


@router.post("/traffic-spike")
async def post_traffic_spike(
    load_factor: float = Query(3.0, ge=1.0, le=10.0),
    scenario: str = Query("wasteful"),
):
    """Simulate load multiplier; returns predicted replicas, node pressure, cost delta."""
    data = await fetcher.get_cluster_snapshot(scenario)
    result = simulate_traffic_spike(data, load_factor)
    await run_persist_simulation(data, "traffic_spike", result, load_factor)
    return result


@router.post("/node-failure")
async def post_node_failure(
    nodes_lost: int = Query(1, ge=1, le=50),
    scenario: str = Query("wasteful"),
):
    """Simulate loss of N nodes; returns projected utilization and scheduling risk."""
    data = await fetcher.get_cluster_snapshot(scenario)
    result = simulate_node_failure(data, nodes_lost)
    await run_persist_simulation(data, "node_failure", result, float(nodes_lost))
    return result


@router.post("/scale-response")
async def post_scale_response(
    target_cpu_util: float = Query(0.6, ge=0.3, le=0.9),
    scenario: str = Query("wasteful"),
):
    """Replicas needed if HPA targets the given CPU utilization."""
    data = await fetcher.get_cluster_snapshot(scenario)
    result = simulate_scale_response(data, target_cpu_util)
    await run_persist_simulation(data, "scale_response", result, target_cpu_util)
    return result


@router.get("/traffic-spike")
async def get_traffic_spike(
    load_factor: float = Query(3.0, ge=1.0, le=10.0),
    scenario: str = Query("wasteful"),
):
    data = await _cluster_data(scenario)
    return simulate_traffic_spike(data, load_factor)


@router.get("/node-failure")
async def get_node_failure(
    nodes_lost: int = Query(1, ge=1, le=50),
    scenario: str = Query("wasteful"),
):
    data = await _cluster_data(scenario)
    return simulate_node_failure(data, nodes_lost)


@router.get("/scale-response")
async def get_scale_response(
    target_cpu_util: float = Query(0.6, ge=0.3, le=0.9),
    scenario: str = Query("wasteful"),
):
    data = await _cluster_data(scenario)
    return simulate_scale_response(data, target_cpu_util)
