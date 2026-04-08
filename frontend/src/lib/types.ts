export interface ClusterSummary {
  total_nodes: number;
  total_pods: number;
  total_deployments: number;
  total_cpu_allocatable: number;
  total_memory_allocatable: number;
  total_cpu_usage: number;
  total_memory_usage: number;
  cpu_utilization_pct: number;
  memory_utilization_pct: number;
}

export interface ClusterInfo {
  name: string;
  provider: string;
  region: string;
  description?: string;
}

export interface ClusterMetrics {
  cluster: ClusterInfo;
  summary: ClusterSummary;
}

export interface PodUtilization {
  pod_name: string;
  deployment_name: string;
  cpu_utilization: number;
  memory_utilization: number;
  cpu_waste: number;
  memory_waste: number;
}

export interface NodeUtilization {
  node_name: string;
  instance_type: string;
  cpu_utilization: number;
  memory_utilization: number;
  cpu_available: number;
  memory_available: number;
}

export interface ConfidenceBreakdown {
  metrics_consistency_score: number;
  traffic_pattern_stability: number;
  node_pressure_score: number;
  raw_node_pressure: number;
}

export interface Recommendation {
  deployment: string;
  namespace: string;
  issue_type: string;
  severity: string;
  current_replicas: number;
  recommended_replicas: number;
  current_cpu_request: number;
  recommended_cpu_request: number;
  current_memory_request: number;
  recommended_memory_request: number;
  estimated_savings_pct: number;
  confidence: number;
  confidence_breakdown?: ConfidenceBreakdown;
  traffic_pattern: string;
}

export interface DeploymentCost {
  deployment: string;
  namespace: string;
  current_cost: number;
  current_cpu_cost: number;
  current_memory_cost: number;
  optimized_cost: number;
  optimized_cpu_cost: number;
  optimized_memory_cost: number;
  savings: number;
  savings_pct: number;
  current_cpu_request: number;
  optimized_cpu_request: number;
  current_replicas: number;
  optimized_replicas: number;
}

export interface CostSummary {
  current_cost: string;
  optimized_cost: string;
  total_savings: string;
  total_savings_pct: number;
  node_infrastructure_cost: string;
  current_cpu_cost?: string;
  current_memory_cost?: string;
  optimized_cpu_cost?: string;
  optimized_memory_cost?: string;
  raw: {
    total_current_cost: number;
    total_optimized_cost: number;
    total_savings: number;
    total_savings_pct: number;
    total_node_infrastructure_cost: number;
    total_current_cpu_cost: number;
    total_current_memory_cost: number;
    total_optimized_cpu_cost: number;
    total_optimized_memory_cost: number;
    by_deployment: DeploymentCost[];
    by_node: { node: string; instance_type: string; monthly_cost: number }[];
  };
}

export interface TimeSeriesPoint {
  timestamp: string;
  value: number;
}

export interface Inefficiency {
  deployment?: string;
  node?: string;
  issue_type: string;
  severity: string;
  [key: string]: unknown;
}
