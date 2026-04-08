"""Static AWS EC2 on-demand pricing (USD/hour). No API key needed.

Prices are approximate us-east-1 on-demand rates as of 2024.
"""

INSTANCE_PRICING: dict[str, dict] = {
    "t3.micro":   {"vcpu": 2,  "memory_gib": 1,   "price_per_hour": 0.0104},
    "t3.small":   {"vcpu": 2,  "memory_gib": 2,   "price_per_hour": 0.0208},
    "t3.medium":  {"vcpu": 2,  "memory_gib": 4,   "price_per_hour": 0.0416},
    "t3.large":   {"vcpu": 2,  "memory_gib": 8,   "price_per_hour": 0.0832},
    "t3.xlarge":  {"vcpu": 4,  "memory_gib": 16,  "price_per_hour": 0.1664},
    "t3.2xlarge": {"vcpu": 8,  "memory_gib": 32,  "price_per_hour": 0.3328},
    "m5.large":   {"vcpu": 2,  "memory_gib": 8,   "price_per_hour": 0.096},
    "m5.xlarge":  {"vcpu": 4,  "memory_gib": 16,  "price_per_hour": 0.192},
    "m5.2xlarge": {"vcpu": 8,  "memory_gib": 32,  "price_per_hour": 0.384},
    "m5.4xlarge": {"vcpu": 16, "memory_gib": 64,  "price_per_hour": 0.768},
    "c5.large":   {"vcpu": 2,  "memory_gib": 4,   "price_per_hour": 0.085},
    "c5.xlarge":  {"vcpu": 4,  "memory_gib": 8,   "price_per_hour": 0.170},
    "c5.2xlarge": {"vcpu": 8,  "memory_gib": 16,  "price_per_hour": 0.340},
    "r5.large":   {"vcpu": 2,  "memory_gib": 16,  "price_per_hour": 0.126},
    "r5.xlarge":  {"vcpu": 4,  "memory_gib": 32,  "price_per_hour": 0.252},
    "r5.2xlarge": {"vcpu": 8,  "memory_gib": 64,  "price_per_hour": 0.504},
}

HOURS_PER_MONTH = 730

# Derived per-resource rates (blended average across instance families)
PRICE_PER_VCPU_HOUR = 0.035
PRICE_PER_GIB_HOUR = 0.005
