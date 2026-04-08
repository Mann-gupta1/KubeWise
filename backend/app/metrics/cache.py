"""In-memory cache for the latest cluster snapshot (used by API + scheduler)."""

from __future__ import annotations

from app.metrics.fetcher import fetcher

_cached_snapshot: dict | None = None


def get_cached_snapshot() -> dict | None:
    return _cached_snapshot


async def refresh_snapshot(scenario: str = "wasteful") -> dict:
    global _cached_snapshot
    _cached_snapshot = await fetcher.get_cluster_snapshot(scenario)
    return _cached_snapshot
