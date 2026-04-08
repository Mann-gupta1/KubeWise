# KubeWise - Kubernetes Cost Intelligence Advisor

A production-grade platform that analyzes Kubernetes cluster utilization using Prometheus metrics, detects resource inefficiencies, and generates autoscaling recommendations with projected infrastructure savings.

## Architecture

```
Kubernetes Cluster (kind / minikube / EKS)
        |
        v
Prometheus Metrics Scraper
        |
        v
+---------------------------+
|   FastAPI Backend         |
|  +---------------------+ |
|  | Metrics Fetcher      | |
|  | Resource Analyzer    | |
|  | Inefficiency Detector| |
|  | Cost Estimator       | |
|  | Scaling Recommender  | |
|  +---------------------+ |
+---------------------------+
        |
        v
   PostgreSQL
        |
        v
  Next.js Dashboard
```

### Data Flow

1. **Metrics Collection** -- Fetches CPU, memory, pod, and node metrics from Prometheus (or generates synthetic data in mock mode)
2. **Resource Analysis** -- Computes per-pod, per-node, and per-deployment utilization ratios
3. **Inefficiency Detection** -- Identifies overprovisioned pods, underutilized nodes, replica mismatches, and resource waste
4. **Cost Estimation** -- Calculates current and optimized monthly costs using static AWS pricing data
5. **Scaling Recommendations** -- Generates HPA tuning suggestions, resource right-sizing, and replica optimization with confidence scores
6. **Dashboard** -- Visualizes all insights through an interactive Next.js interface

## Features

- **Cluster Overview** -- CPU/memory utilization gauges, node status, estimated monthly savings
- **Inefficiency Detection** -- Overprovisioned CPU/memory, underutilized nodes, replica mismatch detection
- **Autoscaling Recommendations** -- HPA tuning, right-sizing with confidence scoring, traffic pattern classification
- **Cost Analysis** -- Current vs optimized cost comparison per deployment, node infrastructure costs
- **Metrics Visualization** -- Time-series charts, node utilization heatmap, pod resource allocation tables
- **Mock Mode** -- Full demo mode with synthetic data (no live cluster required)

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, SQLAlchemy 2.0 (async), Pydantic |
| Frontend | Next.js 14+ (App Router), TypeScript, Tailwind CSS, Recharts |
| Database | PostgreSQL 16 |
| Metrics | Prometheus, kube-state-metrics |
| Infrastructure | Docker Compose, Terraform (optional) |
| Local K8s | kind (optional, for live mode) |

## Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone and start all services (mock mode, no cluster needed)
cd kubewise
docker compose up --build

# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
# Postgres: localhost:5432
```

### Option 2: Local Development

**Backend:**

```bash
cd kubewise/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Start the backend (requires Postgres running)
uvicorn app.main:app --reload --port 8000
```

**Frontend:**

```bash
cd kubewise/frontend
npm install
npm run dev
```

### Option 3: Live Cluster Mode (Prometheus)

Default Compose uses **mock data** (`MOCK_MODE=true`). To point the API at the Prometheus container and disable mocks:

```bash
# Optional: create a kind cluster + kube-prometheus (see scripts/setup-kind.sh)
# Port-forward Prometheus on the host if it runs inside the cluster:
#   kubectl port-forward svc/prometheus-kube-prometheus-prometheus 9090:9090

docker compose -f docker-compose.yml -f docker-compose.live.yml --profile live up --build
```

The override file sets `MOCK_MODE=false` and `PROMETHEUS_URL=http://prometheus:9090`. For Prometheus only on your host (not in Compose), set `PROMETHEUS_URL` to `http://host.docker.internal:9090` (Docker Desktop) or your LAN IP.

Copy [.env.example](.env.example) to `.env` and adjust variables as needed.

### Seed mock data (warm API cache)

```bash
# Bash (Git Bash / WSL / macOS / Linux)
./scripts/seed-mock-data.sh

# PowerShell
./scripts/seed-mock-data.ps1
```

### Phase 3 checklist (local dev)

| Item | Notes |
|------|--------|
| `docker-compose.yml` | Backend + Postgres + frontend; optional Prometheus with `--profile live` |
| `docker-compose.dev.yml` | Backend hot-reload + Postgres |
| `docker-compose.live.yml` | Sets live Prometheus URL + `MOCK_MODE=false` |
| `infra/prometheus.yml` | Self-scrape + kube targets (when running in-cluster) |
| `scripts/setup-kind.sh` | kind + Helm Prometheus |
| `scripts/seed-mock-data.sh` / `.ps1` | POST collect + refresh |

### Phase 4 features

| Feature | Implementation |
|---------|------------------|
| **Simulation engine** | `POST/GET /api/v1/simulations/traffic-spike`, `.../node-failure`, `.../scale-response` — UI: `/simulations` |
| **Advanced confidence** | `compute_confidence_advanced()` blends metrics consistency, traffic stability, node pressure; breakdown returned on recommendations |
| **Scheduled collection** | Set `ENABLE_METRICS_SCHEDULER=true` — APScheduler refreshes the metrics snapshot every `METRICS_COLLECTION_INTERVAL_MINUTES` |
| **Terraform (optional)** | `infra/terraform/` — requires your AWS credentials + `key_pair_name` |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/metrics/cluster?scenario=wasteful` | Cluster-wide utilization summary |
| GET | `/api/v1/metrics/pods?scenario=wasteful` | Per-pod utilization |
| GET | `/api/v1/metrics/nodes?scenario=wasteful` | Per-node utilization |
| GET | `/api/v1/metrics/timeseries/cpu` | CPU time-series data |
| GET | `/api/v1/metrics/timeseries/memory` | Memory time-series data |
| POST | `/api/v1/metrics/collect` | Trigger metrics collection |
| GET | `/api/v1/recommendations?scenario=wasteful` | Autoscaling recommendations |
| GET | `/api/v1/recommendations/inefficiencies` | Detected inefficiencies |
| POST | `/api/v1/recommendations/refresh` | Re-run analysis pipeline |
| GET | `/api/v1/cost/summary?scenario=wasteful` | Cost summary |
| GET | `/api/v1/cost/by-deployment` | Per-deployment cost breakdown |
| GET/POST | `/api/v1/simulations/traffic-spike?load_factor=3&scenario=wasteful` | Traffic spike simulation |
| GET/POST | `/api/v1/simulations/node-failure?nodes_lost=1&scenario=wasteful` | Node failure simulation |
| GET/POST | `/api/v1/simulations/scale-response?target_cpu_util=0.6&scenario=wasteful` | HPA target replica estimate |

Scenarios: `healthy`, `wasteful`, `spike`

**Scheduler:** set `ENABLE_METRICS_SCHEDULER=true` in the environment (see `.env.example`) to periodically refresh cached metrics.

## Example API Output

**Recommendation:**

```json
{
  "deployment": "recommendation-svc",
  "issue_type": "replica_mismatch",
  "severity": "high",
  "current_replicas": 4,
  "recommended_replicas": 1,
  "current_cpu_request": 0.5,
  "recommended_cpu_request": 0.12,
  "estimated_savings_pct": 52.0,
  "confidence": 0.87,
  "traffic_pattern": "low"
}
```

**Cost Summary:**

```json
{
  "current_cost": "$42.34/month",
  "optimized_cost": "$27.12/month",
  "total_savings": "$15.22/month",
  "total_savings_pct": 35.9
}
```

## Project Structure

```
kubewise/
  backend/
    app/
      main.py               # FastAPI entry point
      config.py              # Pydantic settings
      api/routes/            # REST endpoints
      metrics/               # Prometheus fetcher + PromQL queries
      analyzer/              # Resource analysis + inefficiency detection
      estimator/             # AWS cost estimation
      recommender/           # Autoscaling recommendations + confidence
      simulator/             # Traffic spike / node failure / scale simulations
      scheduler_service.py   # APScheduler periodic metrics refresh
      mock/                  # Synthetic data generator + scenarios
      db/                    # SQLAlchemy models + session
    requirements.txt
    Dockerfile

  frontend/
    src/
      app/                   # Next.js pages (+ simulations)
      components/            # Reusable UI components
      lib/                   # API client, types, formatters
    Dockerfile

  docker-compose.yml         # Production setup
  docker-compose.dev.yml     # Dev with hot reload
  infra/
    terraform/               # Optional AWS EC2 + k3s provisioning
    prometheus.yml           # Prometheus scrape config
  scripts/
    setup-kind.sh            # Local k8s cluster setup
    seed-mock-data.sh        # Warm API (collect + refresh)
    seed-mock-data.ps1
  docker-compose.live.yml    # MOCK_MODE=false + Prometheus URL
  .env.example               # Compose / backend env template
```

## Database schema & persistence

- **Alembic:** revisions live under `backend/app/db/migrations/versions/`. From `backend/`: `alembic upgrade head` (the Docker image runs this before Uvicorn).
- **ORM bootstrap:** the app still calls `create_all` on startup when the DB is reachable (handy for local dev without Alembic).
- **Persistence:** when `ENABLE_DB_PERSISTENCE=true` (default), `POST /metrics/collect`, `POST /recommendations/refresh`, and `POST /simulations/*` write topology, recommendations, and simulation rows to Postgres. Set `ENABLE_DB_PERSISTENCE=false` to disable writes (API-only).

## What you need to provide (optional)

| Goal | You supply |
|------|------------|
| **Terraform / AWS k3s** | AWS credentials, an EC2 key pair name, and `terraform apply` |
| **Live Prometheus not in Docker** | Correct `PROMETHEUS_URL` (host port-forward or LAN IP) and `MOCK_MODE=false` |
| **Nothing else** | Mock mode + Docker Compose runs fully offline for demos |

## AWS Deployment (Optional, Free Tier)

Provision a t3.micro EC2 instance with k3s:

```bash
cd infra/terraform
terraform init
terraform apply -var="key_pair_name=your-key"
```

Or deploy the application to free-tier services:

- **Backend**: Render / Railway
- **Frontend**: Vercel
- **Database**: Neon Postgres (free tier)

The deployed version runs in mock mode by default.

## Mock Scenarios

| Scenario | Description |
|----------|-------------|
| `healthy` | Well-optimized cluster with efficient resource usage |
| `wasteful` | Overprovisioned cluster with significant waste (default) |
| `spike` | Cluster with traffic-spike patterns and scaling challenges |

Switch scenarios via the `?scenario=` query parameter on any API endpoint.
