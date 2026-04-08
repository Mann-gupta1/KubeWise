from fastapi import APIRouter, Query

from app.metrics.fetcher import fetcher
from app.analyzer.inefficiency_detector import detect_all_inefficiencies
from app.recommender.autoscaler import generate_recommendations
from app.db.persist import run_persist_refresh

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("")
async def get_recommendations(
    scenario: str = Query("wasteful"),
    severity: str | None = Query(None),
    deployment: str | None = Query(
        None,
        description="Filter by deployment name (exact match)",
    ),
):
    cluster_data = await fetcher.get_cluster_snapshot(scenario)
    recs = generate_recommendations(cluster_data)
    if severity:
        recs = [r for r in recs if r.get("severity") == severity]
    if deployment:
        recs = [r for r in recs if r.get("deployment") == deployment]
    return recs


@router.get("/inefficiencies")
async def get_inefficiencies(scenario: str = Query("wasteful")):
    cluster_data = await fetcher.get_cluster_snapshot(scenario)
    return detect_all_inefficiencies(cluster_data)


@router.post("/refresh")
async def refresh_recommendations(scenario: str = Query("wasteful")):
    cluster_data = await fetcher.get_cluster_snapshot(scenario)
    recs = generate_recommendations(cluster_data)
    inefficiencies = detect_all_inefficiencies(cluster_data)
    await run_persist_refresh(cluster_data, recs)
    return {
        "status": "refreshed",
        "recommendations_count": len(recs),
        "inefficiencies_count": len(inefficiencies),
        "recommendations": recs,
        "inefficiencies": inefficiencies,
    }
