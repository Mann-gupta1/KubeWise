"""Predefined cluster scenarios for mock data generation."""

from dataclasses import dataclass, field


@dataclass
class DeploymentSpec:
    name: str
    namespace: str
    replicas: int
    cpu_request: float  # vCPU cores
    memory_request: float  # GiB
    cpu_usage_ratio: float  # actual/request ratio
    memory_usage_ratio: float  # actual/request ratio
    usage_variance: float = 0.05  # noise in utilization


@dataclass
class NodeSpec:
    name: str
    instance_type: str
    allocatable_cpu: float  # vCPU cores
    allocatable_memory: float  # GiB


@dataclass
class ClusterScenario:
    name: str
    description: str
    provider: str
    region: str
    nodes: list[NodeSpec]
    deployments: list[DeploymentSpec]


HEALTHY_CLUSTER = ClusterScenario(
    name="production-healthy",
    description="Well-optimized cluster with efficient resource usage",
    provider="aws",
    region="us-east-1",
    nodes=[
        NodeSpec("node-1", "t3.large", 2.0, 8.0),
        NodeSpec("node-2", "t3.large", 2.0, 8.0),
        NodeSpec("node-3", "t3.large", 2.0, 8.0),
    ],
    deployments=[
        DeploymentSpec("api-gateway", "default", 2, 0.25, 0.5, 0.70, 0.65, 0.08),
        DeploymentSpec("user-service", "default", 2, 0.20, 0.4, 0.60, 0.55, 0.06),
        DeploymentSpec("order-service", "default", 2, 0.30, 0.6, 0.65, 0.60, 0.07),
        DeploymentSpec("notification-svc", "default", 1, 0.10, 0.2, 0.50, 0.45, 0.05),
    ],
)

WASTEFUL_CLUSTER = ClusterScenario(
    name="staging-wasteful",
    description="Overprovisioned cluster with significant waste",
    provider="aws",
    region="us-west-2",
    nodes=[
        NodeSpec("node-1", "m5.xlarge", 4.0, 16.0),
        NodeSpec("node-2", "m5.xlarge", 4.0, 16.0),
        NodeSpec("node-3", "m5.xlarge", 4.0, 16.0),
        NodeSpec("node-4", "m5.xlarge", 4.0, 16.0),  # largely idle
    ],
    deployments=[
        DeploymentSpec("recommendation-svc", "default", 4, 0.50, 1.0, 0.20, 0.25, 0.04),
        DeploymentSpec("auth-service", "default", 3, 0.40, 0.8, 0.15, 0.18, 0.03),
        DeploymentSpec("search-service", "default", 4, 0.60, 1.2, 0.22, 0.20, 0.05),
        DeploymentSpec("analytics-worker", "default", 3, 0.50, 1.0, 0.10, 0.12, 0.02),
        DeploymentSpec("cache-service", "default", 2, 0.30, 2.0, 0.30, 0.15, 0.04),
        DeploymentSpec("logging-agent", "kube-system", 4, 0.20, 0.4, 0.08, 0.10, 0.02),
    ],
)

SPIKE_CLUSTER = ClusterScenario(
    name="production-spiky",
    description="Cluster with traffic-spike patterns and scaling challenges",
    provider="aws",
    region="eu-west-1",
    nodes=[
        NodeSpec("node-1", "c5.xlarge", 4.0, 8.0),
        NodeSpec("node-2", "c5.xlarge", 4.0, 8.0),
        NodeSpec("node-3", "c5.xlarge", 4.0, 8.0),
    ],
    deployments=[
        DeploymentSpec("web-frontend", "default", 3, 0.40, 0.5, 0.45, 0.40, 0.25),
        DeploymentSpec("payment-service", "default", 2, 0.30, 0.6, 0.35, 0.30, 0.20),
        DeploymentSpec("inventory-svc", "default", 3, 0.50, 0.8, 0.55, 0.50, 0.30),
        DeploymentSpec("email-worker", "default", 2, 0.20, 0.3, 0.40, 0.35, 0.15),
    ],
)

ALL_SCENARIOS = {
    "healthy": HEALTHY_CLUSTER,
    "wasteful": WASTEFUL_CLUSTER,
    "spike": SPIKE_CLUSTER,
}
