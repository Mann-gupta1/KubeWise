from urllib.parse import urlparse

from fastapi import APIRouter, Query

from app.config import effective_telemetry_mode, settings
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
    tel = dict(snap.get("telemetry") or {})
    prom_host = ""
    if settings.PROMETHEUS_URL:
        try:
            prom_host = urlparse(settings.PROMETHEUS_URL).netloc or settings.PROMETHEUS_URL
        except Exception:
            prom_host = settings.PROMETHEUS_URL
    live = bool(tel.get("live"))
    return {
        "cluster": snap["cluster"],
        "summary": snap["summary"],
        "telemetry": {
            **tel,
            "effective_mode": effective_telemetry_mode(),
            "mock_mode": settings.MOCK_MODE,
            "prometheus_host": prom_host if not settings.MOCK_MODE else None,
            "live_queries_enabled": not settings.MOCK_MODE,
            "hint": None
            if (not settings.MOCK_MODE and live)
            else (
                "API has MOCK_MODE=true — Prometheus URL is ignored. Set MOCK_MODE=false and "
                "TELEMETRY_MODE=local (or cluster/hybrid) on the server, then redeploy."
                if settings.MOCK_MODE
                else (
                    "Snapshot is synthetic (fallback) or Prometheus returned no series; "
                    "check TELEMETRY_MODE and PROMETHEUS_URL."
                    if not live
                    else None
                )
            ),
        },
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
