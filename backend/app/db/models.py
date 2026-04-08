from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Enum as SAEnum,
)
from sqlalchemy.orm import DeclarativeBase, relationship
import enum


class Base(DeclarativeBase):
    pass


class Severity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IssueType(str, enum.Enum):
    OVERPROVISIONED_CPU = "overprovisioned_cpu"
    OVERPROVISIONED_MEMORY = "overprovisioned_memory"
    UNDERUTILIZED_NODE = "underutilized_node"
    REPLICA_MISMATCH = "replica_mismatch"


class Cluster(Base):
    __tablename__ = "clusters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    provider = Column(String, default="aws")
    region = Column(String, default="us-east-1")
    created_at = Column(DateTime, default=datetime.utcnow)

    nodes = relationship("Node", back_populates="cluster", cascade="all, delete-orphan")
    deployments = relationship("Deployment", back_populates="cluster", cascade="all, delete-orphan")


class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cluster_id = Column(Integer, ForeignKey("clusters.id"), nullable=False)
    name = Column(String, nullable=False)
    instance_type = Column(String, default="t3.medium")
    allocatable_cpu = Column(Float, nullable=False)
    allocatable_memory = Column(Float, nullable=False)
    status = Column(String, default="Ready")

    cluster = relationship("Cluster", back_populates="nodes")
    pods = relationship("Pod", back_populates="node", cascade="all, delete-orphan")
    metrics = relationship("Metric", back_populates="node", cascade="all, delete-orphan")


class Pod(Base):
    __tablename__ = "pods"

    id = Column(Integer, primary_key=True, autoincrement=True)
    node_id = Column(Integer, ForeignKey("nodes.id"), nullable=False)
    deployment_name = Column(String, nullable=False)
    namespace = Column(String, default="default")
    cpu_request = Column(Float, nullable=False)
    memory_request = Column(Float, nullable=False)
    cpu_limit = Column(Float, nullable=True)
    memory_limit = Column(Float, nullable=True)

    node = relationship("Node", back_populates="pods")
    metrics = relationship("Metric", back_populates="pod", cascade="all, delete-orphan")


class Deployment(Base):
    __tablename__ = "deployments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cluster_id = Column(Integer, ForeignKey("clusters.id"), nullable=False)
    name = Column(String, nullable=False)
    namespace = Column(String, default="default")
    replicas = Column(Integer, nullable=False)
    cpu_request = Column(Float, nullable=False)
    memory_request = Column(Float, nullable=False)

    cluster = relationship("Cluster", back_populates="deployments")
    recommendations = relationship("Recommendation", back_populates="deployment", cascade="all, delete-orphan")


class Metric(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pod_id = Column(Integer, ForeignKey("pods.id"), nullable=True)
    node_id = Column(Integer, ForeignKey("nodes.id"), nullable=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    cpu_usage = Column(Float, nullable=False)
    memory_usage = Column(Float, nullable=False)
    metric_type = Column(String, default="instant")

    pod = relationship("Pod", back_populates="metrics")
    node = relationship("Node", back_populates="metrics")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    deployment_id = Column(Integer, ForeignKey("deployments.id"), nullable=False)
    current_replicas = Column(Integer, nullable=False)
    recommended_replicas = Column(Integer, nullable=False)
    current_cpu_request = Column(Float, nullable=False)
    recommended_cpu_request = Column(Float, nullable=False)
    current_memory_request = Column(Float, nullable=False)
    recommended_memory_request = Column(Float, nullable=False)
    estimated_savings_pct = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    issue_type = Column(SAEnum(IssueType), nullable=False)
    severity = Column(SAEnum(Severity), default=Severity.MEDIUM)
    created_at = Column(DateTime, default=datetime.utcnow)

    deployment = relationship("Deployment", back_populates="recommendations")


class Simulation(Base):
    __tablename__ = "simulations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cluster_id = Column(Integer, ForeignKey("clusters.id"), nullable=True)
    simulation_type = Column(String, nullable=False)
    load_factor = Column(Float, default=1.0)
    predicted_replicas = Column(Integer, nullable=True)
    node_pressure = Column(String, nullable=True)
    cost_increase_pct = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
