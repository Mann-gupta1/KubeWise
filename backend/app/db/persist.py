"""Persist cluster snapshots, recommendations, and simulation runs to PostgreSQL."""

from __future__ import annotations

import logging
from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.models import (
    Cluster,
    Deployment,
    IssueType,
    Metric,
    Node,
    Pod,
    Recommendation,
    Severity,
    Simulation,
)

logger = logging.getLogger("kubewise")

ISSUE_TYPE_MAP = {
    "replica_mismatch": IssueType.REPLICA_MISMATCH,
    "overprovisioned_cpu": IssueType.OVERPROVISIONED_CPU,
    "overprovisioned_memory": IssueType.OVERPROVISIONED_MEMORY,
    "underutilized_node": IssueType.UNDERUTILIZED_NODE,
}

SEVERITY_MAP = {
    "low": Severity.LOW,
    "medium": Severity.MEDIUM,
    "high": Severity.HIGH,
    "critical": Severity.CRITICAL,
}


def _issue_type(s: str) -> IssueType:
    return ISSUE_TYPE_MAP.get(s, IssueType.REPLICA_MISMATCH)


def _severity(s: str) -> Severity:
    return SEVERITY_MAP.get(s, Severity.MEDIUM)


async def _clear_cluster_children(session: AsyncSession, cluster_id: int) -> None:
    pod_ids = list(
        (
            await session.scalars(
                select(Pod.id).join(Node, Pod.node_id == Node.id).where(Node.cluster_id == cluster_id)
            )
        ).all()
    )
    if pod_ids:
        await session.execute(delete(Metric).where(Metric.pod_id.in_(pod_ids)))
    node_ids = list(
        (await session.scalars(select(Node.id).where(Node.cluster_id == cluster_id))).all()
    )
    if node_ids:
        await session.execute(delete(Metric).where(Metric.node_id.in_(node_ids)))
    if pod_ids:
        await session.execute(delete(Pod).where(Pod.id.in_(pod_ids)))
    dep_ids = list(
        (
            await session.scalars(
                select(Deployment.id).where(Deployment.cluster_id == cluster_id)
            )
        ).all()
    )
    if dep_ids:
        await session.execute(delete(Recommendation).where(Recommendation.deployment_id.in_(dep_ids)))
        await session.execute(delete(Deployment).where(Deployment.id.in_(dep_ids)))
    if node_ids:
        await session.execute(delete(Node).where(Node.id.in_(node_ids)))


async def _ensure_cluster(session: AsyncSession, snapshot: dict) -> Cluster:
    meta = snapshot.get("cluster") or {}
    name = meta.get("name") or "default-cluster"
    r = await session.execute(select(Cluster).where(Cluster.name == name))
    row = r.scalar_one_or_none()
    if row:
        row.provider = meta.get("provider", row.provider)
        row.region = meta.get("region", row.region)
        return row
    c = Cluster(
        name=name,
        provider=meta.get("provider", "aws"),
        region=meta.get("region", "us-east-1"),
    )
    session.add(c)
    await session.flush()
    return c


async def persist_cluster_snapshot(session: AsyncSession, snapshot: dict) -> int:
    """Replace topology for this cluster name and insert fresh nodes, deployments, pods, metrics."""
    cluster = await _ensure_cluster(session, snapshot)
    await _clear_cluster_children(session, cluster.id)

    node_by_name: dict[str, int] = {}
    for n in snapshot.get("nodes") or []:
        node = Node(
            cluster_id=cluster.id,
            name=n["name"],
            instance_type=n.get("instance_type", "unknown"),
            allocatable_cpu=float(n.get("allocatable_cpu", 1)),
            allocatable_memory=float(n.get("allocatable_memory", 1)),
            status=n.get("status", "Ready"),
        )
        session.add(node)
        await session.flush()
        node_by_name[n["name"]] = node.id
        m = Metric(
            pod_id=None,
            node_id=node.id,
            timestamp=datetime.utcnow(),
            cpu_usage=float(n.get("cpu_usage", 0)),
            memory_usage=float(n.get("memory_usage", 0)),
            metric_type="node_instant",
        )
        session.add(m)

    for d in snapshot.get("deployments") or []:
        dep = Deployment(
            cluster_id=cluster.id,
            name=d["name"],
            namespace=d.get("namespace", "default"),
            replicas=int(d.get("replicas", 1)),
            cpu_request=float(d.get("cpu_request", 0)),
            memory_request=float(d.get("memory_request", 0)),
        )
        session.add(dep)
        await session.flush()

    for p in snapshot.get("pods") or []:
        nid = node_by_name.get(p.get("node_name") or "")
        if not nid:
            continue
        pod = Pod(
            node_id=nid,
            deployment_name=p.get("deployment_name", ""),
            namespace=p.get("namespace", "default"),
            cpu_request=float(p.get("cpu_request", 0)),
            memory_request=float(p.get("memory_request", 0)),
            cpu_limit=p.get("cpu_limit"),
            memory_limit=p.get("memory_limit"),
        )
        session.add(pod)
        await session.flush()
        session.add(
            Metric(
                pod_id=pod.id,
                node_id=None,
                timestamp=datetime.utcnow(),
                cpu_usage=float(p.get("cpu_usage", 0)),
                memory_usage=float(p.get("memory_usage", 0)),
                metric_type="pod_instant",
            )
        )

    await session.flush()
    return cluster.id


async def persist_recommendations(
    session: AsyncSession,
    cluster_id: int,
    recommendations: list[dict],
) -> None:
    r = await session.execute(select(Deployment).where(Deployment.cluster_id == cluster_id))
    deps = {(d.name, d.namespace): d for d in r.scalars().all()}
    for rec in recommendations:
        key = (rec.get("deployment"), rec.get("namespace", "default"))
        dep = deps.get(key)
        if not dep:
            continue
        session.add(
            Recommendation(
                deployment_id=dep.id,
                current_replicas=int(rec["current_replicas"]),
                recommended_replicas=int(rec["recommended_replicas"]),
                current_cpu_request=float(rec["current_cpu_request"]),
                recommended_cpu_request=float(rec["recommended_cpu_request"]),
                current_memory_request=float(rec["current_memory_request"]),
                recommended_memory_request=float(rec["recommended_memory_request"]),
                estimated_savings_pct=float(rec["estimated_savings_pct"]),
                confidence=float(rec["confidence"]),
                issue_type=_issue_type(str(rec.get("issue_type", "replica_mismatch"))),
                severity=_severity(str(rec.get("severity", "medium"))),
            )
        )
    await session.flush()


async def persist_simulation_run(
    session: AsyncSession,
    cluster_id: int,
    simulation_type: str,
    result: dict,
    load_factor: float = 1.0,
) -> None:
    predicted = None
    if simulation_type == "traffic_spike":
        ds = result.get("deployments") or []
        if ds:
            predicted = max(int(d.get("predicted_replicas", 0)) for d in ds)
        row = Simulation(
            cluster_id=cluster_id,
            simulation_type=simulation_type,
            load_factor=load_factor,
            predicted_replicas=predicted,
            node_pressure=result.get("node_pressure"),
            cost_increase_pct=result.get("cost_increase_pct"),
        )
    elif simulation_type == "node_failure":
        row = Simulation(
            cluster_id=cluster_id,
            simulation_type=simulation_type,
            load_factor=float(result.get("nodes_lost", 1)),
            predicted_replicas=result.get("predicted_extra_replicas_needed"),
            node_pressure=result.get("node_pressure"),
            cost_increase_pct=None,
        )
    elif simulation_type == "scale_response":
        row = Simulation(
            cluster_id=cluster_id,
            simulation_type=simulation_type,
            load_factor=load_factor,
            predicted_replicas=None,
            node_pressure=None,
            cost_increase_pct=None,
        )
    else:
        row = Simulation(
            cluster_id=cluster_id,
            simulation_type=simulation_type,
            load_factor=load_factor,
            predicted_replicas=None,
            node_pressure=None,
            cost_increase_pct=None,
        )
    session.add(row)
    await session.flush()


async def run_persist_snapshot(snapshot: dict) -> None:
    if not settings.ENABLE_DB_PERSISTENCE:
        return
    from app.db.session import async_session

    try:
        async with async_session() as session:
            async with session.begin():
                await persist_cluster_snapshot(session, snapshot)
    except Exception:
        logger.exception("persist_cluster_snapshot failed")


async def run_persist_refresh(snapshot: dict, recommendations: list[dict]) -> None:
    if not settings.ENABLE_DB_PERSISTENCE:
        return
    from app.db.session import async_session

    try:
        async with async_session() as session:
            async with session.begin():
                cid = await persist_cluster_snapshot(session, snapshot)
                await persist_recommendations(session, cid, recommendations)
    except Exception:
        logger.exception("persist_refresh failed")


async def run_persist_simulation(
    snapshot: dict,
    simulation_type: str,
    result: dict,
    load_factor: float = 1.0,
) -> None:
    if not settings.ENABLE_DB_PERSISTENCE:
        return
    from app.db.session import async_session

    try:
        async with async_session() as session:
            async with session.begin():
                cluster = await _ensure_cluster(session, snapshot)
                await session.flush()
                await persist_simulation_run(session, cluster.id, simulation_type, result, load_factor)
    except Exception:
        logger.exception("persist_simulation failed")
