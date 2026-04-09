from fastapi import APIRouter

from app.config import effective_telemetry_mode, settings
from app.integrations.opencost import opencost_health

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "kubewise"}


@router.get("/telemetry")
async def telemetry_info():
    """Effective telemetry pipeline mode (demo / cluster / local / hybrid)."""
    return {
        "effective_mode": effective_telemetry_mode(),
        "telemetry_mode": settings.TELEMETRY_MODE,
        "mock_mode": settings.MOCK_MODE,
        "opencost_configured": bool((settings.OPENCOST_URL or "").strip()),
        "prometheus_required": not settings.MOCK_MODE,
        "live_prometheus_queries": not settings.MOCK_MODE,
        "note": "When mock_mode is true, all metrics are synthetic; PROMETHEUS_URL is not used.",
    }


@router.get("/integrations/opencost/health")
async def opencost_probe():
    """Live probe to OpenCost (only if OPENCOST_URL is set)."""
    return await opencost_health()
