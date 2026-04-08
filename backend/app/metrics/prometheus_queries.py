"""PromQL query constants for Prometheus metrics collection."""

CPU_USAGE_BY_POD = 'sum(rate(container_cpu_usage_seconds_total{container!=""}[5m])) by (pod)'
MEMORY_USAGE_BY_POD = 'sum(container_memory_usage_bytes{container!=""}) by (pod)'
CPU_USAGE_BY_NODE = 'sum(rate(container_cpu_usage_seconds_total{container!=""}[5m])) by (node)'
MEMORY_USAGE_BY_NODE = 'sum(container_memory_usage_bytes{container!=""}) by (node)'
DEPLOYMENT_REPLICAS = "kube_deployment_status_replicas"
DEPLOYMENT_REPLICAS_AVAILABLE = "kube_deployment_status_replicas_available"
NODE_ALLOCATABLE_CPU = 'kube_node_status_allocatable{resource="cpu"}'
NODE_ALLOCATABLE_MEMORY = 'kube_node_status_allocatable{resource="memory"}'
CPU_REQUESTS_BY_POD = 'sum(kube_pod_container_resource_requests{resource="cpu"}) by (pod)'
MEMORY_REQUESTS_BY_POD = 'sum(kube_pod_container_resource_requests{resource="memory"}) by (pod)'
