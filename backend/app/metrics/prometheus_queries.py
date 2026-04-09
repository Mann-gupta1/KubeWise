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

# node_exporter (hosts / VM telemetry — no Kubernetes required)
NODE_CPU_IDLE_AVG = 'avg by (instance)(rate(node_cpu_seconds_total{mode="idle"}[5m]))'
NODE_MEMORY_TOTAL = "node_memory_MemTotal_bytes"
NODE_MEMORY_AVAILABLE = "node_memory_MemAvailable_bytes"
NODE_CPU_CORES = 'count by (instance)(node_cpu_seconds_total{mode="idle"})'
# CPU busy rate per instance (for query_range charts)
NODE_CPU_NON_IDLE_RATE = 'sum by (instance)(rate(node_cpu_seconds_total{mode!="idle",mode!="iowait"}[5m]))'
