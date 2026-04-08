from fastapi import APIRouter, Query

from app.metrics.fetcher import fetcher
from app.metrics import cache as snapshot_cache
from app.db.persist import run_persist_snapshot
from app.analyzer.resource_analyzer import (
    compute_pod_utilization,
    compute_node_utilization,
)

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/cluster")
async def get_cluster_metrics(scenario: str = Query("wasteful")):
    snap = await snapshot_cache.refresh_snapshot(scenario)
    return {
        "cluster": snap["cluster"],
        "summary": snap["summary"],
    }


@router.get("/pods")
async def get_pod_metrics(scenario: str = Query("wasteful")):
    snap = await snapshot_cache.refresh_snapshot(scenario)
    pods = snap.get("pods", [])
    return [compute_pod_utilization(p) for p in pods]


@router.get("/nodes")
async def get_node_metrics(scenario: str = Query("wasteful")):
    snap = await snapshot_cache.refresh_snapshot(scenario)
    nodes = snap.get("nodes", [])
    return [compute_node_utilization(n) for n in nodes]


@router.get("/timeseries/cpu")
async def get_cpu_timeseries():
    return await fetcher.get_cpu_time_series()


@router.get("/timeseries/memory")
async def get_memory_timeseries():
    return await fetcher.get_memory_time_series()


@router.post("/collect")
async def collect_metrics(scenario: str = Query("wasteful")):
    snap = await snapshot_cache.refresh_snapshot(scenario)
    await run_persist_snapshot(snap)
    return {
        "status": "collected",
        "pods": len(snap.get("pods", [])),
        "nodes": len(snap.get("nodes", [])),
        "deployments": len(snap.get("deployments", [])),
    }
