from fastapi import APIRouter, Query

from app.metrics.fetcher import fetcher
from app.estimator.cost_estimator import estimate_cluster_cost

router = APIRouter(prefix="/cost", tags=["cost"])


@router.get("/summary")
async def get_cost_summary(scenario: str = Query("wasteful")):
    cluster_data = await fetcher.get_cluster_snapshot(scenario)
    cost = estimate_cluster_cost(cluster_data)
    return {
        "current_cost": f"${cost['total_current_cost']}/month",
        "optimized_cost": f"${cost['total_optimized_cost']}/month",
        "total_savings": f"${cost['total_savings']}/month",
        "total_savings_pct": cost["total_savings_pct"],
        "node_infrastructure_cost": f"${cost['total_node_infrastructure_cost']}/month",
        "current_cpu_cost": f"${cost['total_current_cpu_cost']}/month",
        "current_memory_cost": f"${cost['total_current_memory_cost']}/month",
        "optimized_cpu_cost": f"${cost['total_optimized_cpu_cost']}/month",
        "optimized_memory_cost": f"${cost['total_optimized_memory_cost']}/month",
        "raw": cost,
    }


@router.get("/by-deployment")
async def get_cost_by_deployment(scenario: str = Query("wasteful")):
    cluster_data = await fetcher.get_cluster_snapshot(scenario)
    cost = estimate_cluster_cost(cluster_data)
    return cost["by_deployment"]
