# Prometheus on Render

Minimal [Prometheus](https://prometheus.io/) for a **public HTTPS URL** you can set as `PROMETHEUS_URL` on your KubeWise API (with `MOCK_MODE=false`).

**Important**

- This instance only scrapes **itself** (`up`, build info, etc.). It does **not** include your Kubernetes cluster. For real cluster metrics you must add scrape jobs (e.g. kube-state-metrics behind a reachable endpoint) or use a different Prometheus that already scrapes your cluster.
- A public Prometheus UI + API has **no authentication** in this setup. Treat it as a demo, use Render IP restrictions if available, or keep `MOCK_MODE=true` for public demos.

## Deploy on Render

1. In [Render Dashboard](https://dashboard.render.com) → **New** → **Web Service**.
2. Connect the **KubeWise** GitHub repository.
3. Configure:
   - **Name:** e.g. `kubewise-prometheus`
   - **Region:** same region as your API if possible
   - **Branch:** `main`
   - **Root Directory:** `deploy/prometheus`
   - **Runtime:** **Docker**
   - **Dockerfile Path:** `Dockerfile` (default if root is `deploy/prometheus`)
   - **Instance type:** Free tier is fine for testing
4. **Environment:** no variables required (`PORT` is set automatically).
5. **Create Web Service** and wait for the first deploy.
6. Copy the service URL, e.g. `https://kubewise-prometheus.onrender.com`.

## Point KubeWise API at it

On your **FastAPI** Render service, set:

| Variable | Value |
|----------|--------|
| `MOCK_MODE` | `false` |
| `PROMETHEUS_URL` | `https://YOUR-PROMETHEUS-SERVICE.onrender.com` |

Use **https** and **no trailing slash**. Redeploy the API.

## Verify

Open:

`https://YOUR-PROMETHEUS-SERVICE.onrender.com/api/v1/query?query=up`

You should see JSON with `"status":"success"` and a `result` array (e.g. `up` = `1`).

### “No data” in the Prometheus web UI

The UI does **not** show a graph until you **run a query**.

1. Open `https://YOUR-PROMETHEUS-SERVICE.onrender.com/` (or `/graph`).
2. In the query box, enter **`up`** or **`prometheus_build_info`**.
3. Click **Execute**, then open the **Table** or **Graph** tab.

This minimal server only scrapes **itself**, so you only have a small set of metrics (e.g. `up`, `prometheus_*`, `go_*`). KubeWise’s live mode expects **kube-state-metrics** and **cAdvisor**-style series (`kube_*`, `container_*`). If those are missing, the API falls back to **mock** data when `PROMETHEUS_FALLBACK_MOCK=true` (default) so the UI is not all zeros. To drive the dashboard from real cluster metrics, scrape a cluster that exports those metrics (see [`backend/app/metrics/prometheus_queries.py`](../../backend/app/metrics/prometheus_queries.py)).

To confirm scraping works: **Status → Targets** — the `prometheus` job should be **UP** (green).

## Optional: custom domain

In the Prometheus service → **Settings** → **Custom Domains**, add e.g. `prometheus.kubewise.onrender.com` and follow Render’s DNS instructions. Then use that host as `PROMETHEUS_URL`.

## Local test

From the repo root:

```bash
cd deploy/prometheus
docker build -t kw-prom .
docker run --rm -p 9090:9090 -e PORT=9090 kw-prom
```

Then visit `http://localhost:9090/graph` and `http://localhost:9090/api/v1/query?query=up`.
