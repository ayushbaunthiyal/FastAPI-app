# Phase 12: Observability Stack

## Goal
Implement a comprehensive observability stack including metrics (Prometheus), visualization (Grafana), and logging (Loki/Promtail) for the FastAPI application.

## Changes Implemented

### 1. Application Instrumentation
- Added `prometheus-fastapi-instrumentator` to `pyproject.toml` and installed it in the Docker container.
- Updated `app/main.py` to instrument the application and expose metrics at `/metrics`.
    - Note: Moved instrumentation to module scope to avoid "middleware added after startup" error.

### 2. Infrastructure (Docker Compose)
- Added the following services to `docker-compose.prod.yml`:
    - **Prometheus**: Scrapes metrics from `api:8000`.
    - **Grafana**: Visualization dashboard (Port 3000).
    - **Loki**: Log aggregation.
    - **Promtail**: Log collector shipping Docker logs to Loki.

### 3. Configuration
- Created `deploy/` directory with:
    - `prometheus.yml`: Configured to scrape `fastapi` job.
    - `loki-config.yml`: Basic Loki configuration.
    - `promtail-config.yml`: Scrapes Docker container logs.
    - `grafana/provisioning/datasources/datasources.yml`: Auto-provisions Prometheus and Loki datasources in Grafana.

### 4. Build System Updates
- Updated `Dockerfile` to:
    - Remove `uv.lock` from `COPY` instruction to prevent stale lock file from host interfering with build.
    - Remove `--frozen` flag from `uv sync` to allow fresh dependency resolution.
    - Add `uv.lock` to `.dockerignore`.

## Verification
- **Metrics Endpoint**: verified `curl http://localhost:8000/metrics` returns Prometheus metrics.
- **Services**: All services (Prometheus, Grafana, Loki, Promtail, API, DB, Redis, Worker, Beat) are running and healthy.
- **Grafana**: Accessible at `http://localhost:3000` (default login `admin/admin`), with Datasources for Prometheus and Loki pre-configured.

## Next Steps
- Phase 13: CI/CD Pipeline.
