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

### Telemetry modes (multi-environment pipeline)

`MOCK_MODE=true` (default) forces **demo** mode: synthetic cluster data only — no Prometheus required.

When **`MOCK_MODE=false`**, set **`TELEMETRY_MODE`**:

| Mode | Behavior |
|------|----------|
| **`demo`** | Same as above — synthetic data (rarely needed if you already set `MOCK_MODE=false`; use `MOCK_MODE=true` instead). |
| **`cluster`** | Kubernetes-style metrics from Prometheus (`kube_*`, `container_*`) — needs kube-state-metrics / cAdvisor scraping. |
| **`local`** | **node_exporter** metrics only (`node_cpu_seconds_total`, `node_memory_*`) — valid **host/VM telemetry** pipeline without Kubernetes. Point `PROMETHEUS_URL` at a Prometheus that scrapes node_exporter. |
| **`hybrid`** | Try **cluster** first; if empty or errors, use **node_exporter**; if still nothing, honor **`PROMETHEUS_FALLBACK_MOCK`**. |

Example **local** stack: `node_exporter` → Prometheus → FastAPI (`TELEMETRY_MODE=local`) → dashboard.

**OpenCost** ([`opencost/opencost`](https://github.com/opencost/opencost)) exposes allocation APIs when deployed in-cluster; there is **no** global public dataset URL. Set **`OPENCOST_URL`** to your OpenCost service (e.g. `http://opencost.opencost:9003`) and probe **`GET /api/v1/integrations/opencost/health`**. Effective mode and flags: **`GET /api/v1/telemetry`**.

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

## For reviewers (portfolio evidence)

The **home page** is a cluster overview; the **intelligence pipeline** is visible across **Recommendations**, **Cost Analysis**, **Metrics**, and **Simulations** (navbar), and in **OpenAPI** at `/docs`. The backend is not “mock-only”: it implements PromQL-backed fetchers, detection rules, a recommender, pricing-based cost estimation, and simulations.

| Concern | Where it lives |
|---------|----------------|
| **Prometheus / PromQL** | [`backend/app/metrics/prometheus_queries.py`](backend/app/metrics/prometheus_queries.py), [`fetcher.py`](backend/app/metrics/fetcher.py) (`/api/v1/query` + `query_range`) |
| **Inefficiency detection** | [`backend/app/analyzer/inefficiency_detector.py`](backend/app/analyzer/inefficiency_detector.py) — e.g. overprovisioned CPU/memory, underutilized nodes (`GET /api/v1/recommendations/inefficiencies`) |
| **Autoscaling recommendations** | [`backend/app/recommender/autoscaler.py`](backend/app/recommender/autoscaler.py) — replica and request suggestions, confidence (`GET /api/v1/recommendations`) |
| **Cost engine** | [`backend/app/estimator/cost_estimator.py`](backend/app/estimator/cost_estimator.py) — vCPU / GiB-hour style math (`GET /api/v1/cost/summary`, `/cost/by-deployment`) |
| **Simulations** | [`backend/app/api/routes/simulations.py`](backend/app/api/routes/simulations.py) — traffic spike, node failure, scale response |
| **Telemetry mode** | `GET /api/v1/telemetry` — `demo` / `cluster` / `local` / `hybrid` |

**Try live public Prometheus (no Kubernetes required):** point `PROMETHEUS_URL` at a **working** community demo with **`MOCK_MODE=false`** and **`TELEMETRY_MODE=local`** (node_exporter path) or **`TELEMETRY_MODE=cluster`** if the demo exposes `kube_*` / `container_*` metrics.

Verified examples (use **exactly** these hosts — `prometheus.demo.do.prometheus.io` does **not** resolve):

```text
# PromLabs demo (node, cAdvisor, demo jobs — good for local + charts)
PROMETHEUS_URL=https://demo.promlabs.com

# Official Prometheus project demo
PROMETHEUS_URL=https://prometheus.demo.prometheus.io

MOCK_MODE=false
TELEMETRY_MODE=local
```

**Critical:** If **`MOCK_MODE=true`** (the default in `.env.example`), the API **never** calls Prometheus — `PROMETHEUS_URL` is ignored and you always get **synthetic** data. You must set **`MOCK_MODE=false`** on the server (e.g. Render) and redeploy. Check **`GET /api/v1/telemetry`** (`live_prometheus_queries` should be `true`) and **`GET /api/v1/metrics/cluster`** — the JSON includes a **`telemetry`** object with `live: true` when PromQL ran.

Then open `/docs` and call `GET /api/v1/metrics/cluster` or use the dashboard **Metrics** tab.

**Quick curls** (replace host with your API):

```bash
curl -s "https://YOUR-API/api/v1/telemetry"
curl -s "https://YOUR-API/api/v1/recommendations?scenario=wasteful" | head -c 800
curl -s "https://YOUR-API/api/v1/cost/summary?scenario=wasteful"
curl -s "https://YOUR-API/api/v1/simulations/traffic-spike?load_factor=2&scenario=wasteful"
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/telemetry` | Effective telemetry mode (`demo` / `cluster` / `local` / `hybrid`) |
| GET | `/api/v1/metrics/cluster?scenario=wasteful` | Cluster-wide utilization summary + **`telemetry`** (synthetic vs live Prometheus) |
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

## Production deployment (Neon + Render/Railway + Vercel)

Use this path when you want a **live URL** without AWS billing. The **AWS Terraform** code under [`infra/terraform/`](infra/terraform/) stays in the repo for later (EKS, EC2, credits); you do not need it for this stack.

**Architecture:** Neon (Postgres) → Render or Railway (FastAPI) → Vercel (Next.js). The API uses **mock cluster data** by default (`MOCK_MODE=true`), so no Kubernetes or Prometheus is required in the cloud.

---

### 1. Neon (Postgres) — database only

1. Sign up at [https://neon.tech](https://neon.tech) and create a **project** (pick a region close to your API region).
2. Create a **database** (default `neondb` is fine).
3. Open **Connection details** and copy the connection string (role: use a user that can create tables, usually the default).
4. You need **two** URLs for this app:
   - **Async (FastAPI / SQLAlchemy):** take Neon’s URI and change the scheme to `postgresql+asyncpg://` (keep host, user, password, database name).
   - **Sync (Alembic / migrations):** keep `postgresql://` (psycopg2).

Example (values are illustrative):

```text
# Async — app runtime
DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@ep-xxxxx.us-east-2.aws.neon.tech/neondb?ssl=require

# Sync — alembic from Dockerfile / local
DATABASE_URL_SYNC=postgresql://USER:PASSWORD@ep-xxxxx.us-east-2.aws.neon.tech/neondb?sslmode=require
```

If the app fails to connect, check Neon’s docs for **SQLAlchemy** / **asyncpg** and ensure `ssl=require` or `sslmode=require` matches what Neon shows.

---

### 2. Backend — Render (recommended) or Railway

**Common environment variables** (set these in the service dashboard):

| Variable | Example / notes |
|----------|-------------------|
| `DATABASE_URL` | Async URL above (`postgresql+asyncpg://...`) |
| `DATABASE_URL_SYNC` | Sync URL above (`postgresql://...?sslmode=require`) |
| `MOCK_MODE` | `true` (demo without a real cluster) |
| `ENABLE_DB_PERSISTENCE` | `true` if you want writes to Neon |
| `CORS_ORIGINS` | JSON array of **frontend** origins (where the browser loads the UI), e.g. `["https://kubewise.vercel.app"]`. Do **not** put your Render API URL here — CORS is about the page origin, not the API host. Add `http://localhost:3000` only if you need local dev against prod API |
| `PROMETHEUS_URL` | `http://localhost:9090` (unused when `MOCK_MODE=true`) |

**Render (Web Service)**

1. New **Web Service** → connect the **KubeWise** GitHub repo.
2. **Root directory:** `backend`
3. **Runtime:** Python 3
4. **Build command:** `pip install -r requirements.txt`
5. **Start command:**  
   `sh -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT"`
6. **Instance type:** Free tier is OK for demos; **services spin down after idle** (cold start ~30–60s on first request). Open `/docs` if the UI times out. Set `PROMETHEUS_FALLBACK_MOCK=true` (default) so a sleeping Prometheus does not take down the API when `MOCK_MODE=false`.
7. Copy the service URL (e.g. `https://kubewise-api.onrender.com`).

**Railway**

1. New project → **Deploy from GitHub** → select repo, set **root directory** to `backend`.
2. Railway detects Python; set **Start command** to the same `sh -c "alembic upgrade head && ..."` as above (use `$PORT` if Railway injects it).
3. Add the same env vars in **Variables**.

**Health check:** open `https://YOUR-API-HOST/docs` — you should see FastAPI Swagger.

**Optional — Prometheus URL on Render (live mode):** To obtain a public `PROMETHEUS_URL` for `MOCK_MODE=false`, deploy a second Render **Web Service** using Docker from [`deploy/prometheus/`](deploy/prometheus/) and follow [`deploy/prometheus/README.md`](deploy/prometheus/README.md). That stack exposes the Prometheus HTTP API; it does not scrape a real cluster until you add scrape targets. For a public demo, `MOCK_MODE=true` is usually simpler.

---

### 3. Frontend — Vercel

1. Import the repo in [Vercel](https://vercel.com) → set **Root Directory** to `frontend`.
2. Framework: **Next.js** (default).
3. **Environment variable:**
   - `NEXT_PUBLIC_API_URL` = `https://YOUR-API-HOST/api/v1`  
     (no trailing slash; use your Render/Railway URL from step 2).
4. Deploy. Open the Vercel URL; the dashboard should load data from the API.
5. **Auto-refresh:** Overview, Metrics, Cost, and Recommendations pages **poll the API every 30s** by default (no manual refresh needed). Override with **`NEXT_PUBLIC_POLL_INTERVAL_MS`** (milliseconds, 10000–300000) if you rebuild the frontend.

If the UI shows CORS errors, your `CORS_ORIGINS` on the backend must include the **exact** Vercel origin (scheme + host, no path), e.g. `https://kubewise-xxxxx.vercel.app`.

**Troubleshooting: “Connection Error” / “Failed to fetch” / message about port 8000**

That message appears when the browser is still using the **default** API base (`http://localhost:8000/api/v1`) because **`NEXT_PUBLIC_API_URL` was not set when the Next.js app was built**.

**Preview works but Production (`kubewise.vercel.app`) does not:** Vercel stores env vars **per environment** (Production, Preview, Development). If you only added `NEXT_PUBLIC_API_URL` under **Preview**, production builds still bake in localhost. Either add the same variable for **Production**, or rely on the default in [`frontend/next.config.ts`](frontend/next.config.ts) (Render URL when `VERCEL_ENV=production`) and **redeploy** Production once.

1. In **Vercel** → Project → **Settings** → **Environment Variables**, set  
   `NEXT_PUBLIC_API_URL` = `https://YOUR-RENDER-HOST/api/v1`  
   (example: `https://kubewise.onrender.com/api/v1`) for **Production** (and Preview if you want).
2. **Redeploy** the **Production** deployment. `NEXT_PUBLIC_*` is inlined at **build** time; a hard refresh does not change the bundle.
3. On **Render**, set **`CORS_ORIGINS`** to a JSON array that includes your Vercel origin, e.g.  
   `["https://kubewise.vercel.app"]`  
   (add `http://localhost:3000` in the same array if you still hit the prod API from local dev).
4. Confirm the API is up: open `https://YOUR-RENDER-HOST/docs` in the browser.

---

### 4. Order of operations

1. Create **Neon** → copy both connection strings.
2. Deploy **backend** (Render/Railway) with env vars → confirm `/docs` works.
3. Set **`CORS_ORIGINS`** to your future Vercel URL (you can add/edit after first deploy).
4. Deploy **Vercel** with `NEXT_PUBLIC_API_URL` pointing at the API.
5. Update **`CORS_ORIGINS`** again if Vercel assigned a different production domain.

---

### 5. Optional AWS / Terraform (keep for later)

The [`infra/terraform/`](infra/terraform/) module is **optional**. It is useful when you want a cheap EC2 + k3s node or later EKS work; it is **not** required for Neon + Render + Vercel. No payment method is needed for the serverless path above.

```bash
cd infra/terraform
terraform init
terraform apply -var="key_pair_name=your-key"
```

## Mock Scenarios

| Scenario | Description |
|----------|-------------|
| `healthy` | Well-optimized cluster with efficient resource usage |
| `wasteful` | Overprovisioned cluster with significant waste (default) |
| `spike` | Cluster with traffic-spike patterns and scaling challenges |

Switch scenarios via the `?scenario=` query parameter on any API endpoint.
