# KubeWise — Kubernetes Cost Intelligence Advisor

A platform that ingests Prometheus-style metrics, analyzes utilization, detects inefficiencies, estimates infrastructure cost (AWS-oriented pricing), and suggests autoscaling changes. It includes a FastAPI backend, PostgreSQL persistence, and a Next.js dashboard.

## Architecture

```
Kubernetes / VMs / mock data
        ↓
   Prometheus (optional)
        ↓
   FastAPI  →  PostgreSQL
        ↓
   Next.js dashboard
```

**Flow:** metrics collection → resource analysis → inefficiency detection → cost estimation → scaling recommendations → optional simulations. In **mock mode** (`MOCK_MODE=true`) the API uses synthetic cluster data so you can run without Prometheus.

## Features

- Cluster overview (CPU/memory, nodes, estimated savings)
- Inefficiency detection (overprovisioned resources, underutilized nodes)
- Autoscaling-style recommendations with confidence scores
- Cost comparison (current vs optimized) using static AWS list pricing
- Time-series charts, simulations (traffic spike, node failure, scale response)
- REST API with OpenAPI at `/docs`

## Tech stack

| Layer | Stack |
|-------|--------|
| API | FastAPI, SQLAlchemy 2 (async), Pydantic, Alembic |
| UI | Next.js (App Router), TypeScript, Tailwind, Recharts |
| Data | PostgreSQL 16 |
| Metrics | Prometheus + PromQL (optional; mock mode available) |
| Local / CI | Docker Compose |
| AWS (optional) | Terraform: EC2 + k3s |

## Quick start (Docker Compose)

```bash
cd kubewise
docker compose up --build
```

- Frontend: http://localhost:3000  
- API docs: http://localhost:8000/docs  
- Postgres: `localhost:5432`  

Copy [`.env.example`](.env.example) to `.env` and adjust variables. Backend defaults: `MOCK_MODE=true`, `PROMETHEUS_URL` optional until you use live metrics.

**Live Prometheus in Compose:**  
`docker compose -f docker-compose.yml -f docker-compose.live.yml --profile live up --build`

## Project layout

```
kubewise/
  backend/           # FastAPI app (app/main.py, app/api/routes/, app/metrics/, …)
  frontend/          # Next.js app
  infra/terraform/   # AWS EC2 + k3s (see below)
  infra/prometheus.yml
  docker-compose*.yml
  scripts/           # kind / seed helpers (optional)
```

## Configuration (summary)

| Variable | Purpose |
|----------|---------|
| `MOCK_MODE` | `true` = synthetic data; `false` = query `PROMETHEUS_URL` |
| `PROMETHEUS_URL` | Prometheus origin (e.g. `http://prometheus:9090` in Compose) |
| `TELEMETRY_MODE` | With `MOCK_MODE=false`: `cluster` / `local` / `hybrid` (see `backend/.env.example`) |
| `DATABASE_URL` / `DATABASE_URL_SYNC` | Async + sync Postgres URLs |

Persistence and migrations: see `backend/.env.example` and Alembic under `backend/`.

## API

Interactive documentation: **`GET /docs`** on the running API (Swagger UI). Core route groups: `/api/v1/metrics`, `/api/v1/recommendations`, `/api/v1/cost`, `/api/v1/simulations`, `/api/v1/health`, `/api/v1/telemetry`.

---

## AWS deployment (Terraform)

Terraform provisions a **single Ubuntu 22.04 EC2** instance, installs **k3s**, and attaches a security group. You use the node as a lightweight Kubernetes host for Prometheus, workloads, or experimentation.

### Prerequisites

- [Terraform](https://www.terraform.io/) ≥ 1.x  
- [AWS CLI](https://aws.amazon.com/cli/) configured (`aws configure`)  
- An **EC2 key pair** already created in the target region (for SSH)  

### Steps

1. **Change into the module**

   ```bash
   cd infra/terraform
   ```

2. **Initialize providers**

   ```bash
   terraform init
   ```

3. **Apply** (replace `your-key` with your AWS key pair **name**)

   ```bash
   terraform apply -var="key_pair_name=your-key"
   ```

   Optional: `-var="aws_region=us-east-1"` (default `us-east-1`) and `-var="instance_type=t3.micro"` (free-tier friendly).

4. **Outputs**

   After apply, Terraform prints:

   - `instance_public_ip` — public IPv4  
   - `ssh_command` — example `ssh ubuntu@<ip>`  
   - `kubeconfig_command` — how to read k3s kubeconfig from the node  

5. **SSH and k3s**

   ```bash
   ssh ubuntu@<instance_public_ip>
   sudo k3s kubectl get nodes
   ```

6. **Security note**

   The generated security group opens **22, 6443, 80, 443** from **0.0.0.0/0**. Restrict sources and ports for production.

### Destroy

```bash
cd infra/terraform
terraform destroy -var="key_pair_name=your-key"
```

---

## Scenario parameter

APIs accept `?scenario=` where applicable: `healthy`, `wasteful` (default), `spike`.
