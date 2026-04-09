"""Optional OpenCost API — typically deployed in-cluster. https://github.com/opencost/opencost"""

from __future__ import annotations

import logging

import httpx

from app.config import settings

logger = logging.getLogger("kubewise.opencost")


async def opencost_health() -> dict[str, object]:
    """Best-effort check; OpenCost serves allocation/assets APIs (not a public dataset)."""
    base = (settings.OPENCOST_URL or "").strip().rstrip("/")
    if not base:
        return {"reachable": False, "detail": "OPENCOST_URL unset"}
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{base}/allocation",
                params={"window": "today", "aggregate": "namespace"},
                timeout=8.0,
            )
            ok = r.status_code < 500
            return {"reachable": ok, "status_code": r.status_code}
    except Exception as e:
        logger.debug("OpenCost check failed: %s", e)
        return {"reachable": False, "detail": str(e)[:200]}
