"""Periodic metrics collection (APScheduler)."""

from __future__ import annotations

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings

logger = logging.getLogger("kubewise")

scheduler = AsyncIOScheduler()


def start_metrics_scheduler() -> None:
    if not settings.ENABLE_METRICS_SCHEDULER:
        logger.info("Metrics scheduler disabled (ENABLE_METRICS_SCHEDULER=false)")
        return

    async def collect_job() -> None:
        from app.metrics import cache as snapshot_cache

        try:
            await snapshot_cache.refresh_snapshot(settings.METRICS_COLLECTION_SCENARIO)
            logger.debug("Scheduled metrics collection OK")
        except Exception as exc:
            logger.warning("Scheduled metrics collection failed: %s", exc)

    scheduler.add_job(
        collect_job,
        "interval",
        minutes=settings.METRICS_COLLECTION_INTERVAL_MINUTES,
        id="kubewise_metrics_collect",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(
        "Metrics scheduler: every %s min, scenario=%s",
        settings.METRICS_COLLECTION_INTERVAL_MINUTES,
        settings.METRICS_COLLECTION_SCENARIO,
    )


def shutdown_metrics_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Metrics scheduler stopped")
