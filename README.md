# FastAPI Production App

A production-ready, async FastAPI application featuring comprehensive security, observability, and performance optimizations.

## 🚀 Features

- **Authentication**: JWT-based auth with refresh tokens and Redis blocklisting.
- **User Management**: Complete CRUD with email verification and role-based access.
- **Async Tasks**: Celery with Redis for background processing (emails, reports).
- **Security**:
  - HSTS, Security Headers, and CORS configuration.
  - Redis-based Rate Limiting.
  - Container Security Contexts (non-root, read-only fs).
- **Observability**:
  - Prometheus Metrics & Grafana Dashboards.
  - Loki for centralized logging.
  - Tempo for distributed tracing.
- **Performance**:
  - Database connection pooling.
  - Redis caching for high-read endpoints.
  - Pagination safeguards.

## 🛠️ Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.12+ (for local dev)

### Run with Docker Compose
The easiest way to run the entire stack (App, DB, Redis, Grafana, Prometheus, Loki, Tempo):

```bash
# Start production stack
./scripts/run_prod.ps1
# OR
docker-compose -f docker-compose.prod.yml up -d --build
```

Access the application:
- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Grafana**: [http://localhost:3000](http://localhost:3000) (admin/admin)
- **Prometheus**: [http://localhost:9090](http://localhost:9090)

## 💻 Local Development

### Setup
We use `uv` for fast dependency management.

```bash
# Install dependencies
uv sync

# Activate virtual environment
.venv\Scripts\activate
```

### Run Locally
```bash
# Start infrastructure (DB, Redis)
docker-compose up -d db redis

# Run migrations
alembic upgrade head

# Start App
uvicorn app.main:app --reload
```

## 🧪 Testing

Run the comprehensive test suite with Docker:

```bash
# Run integration tests
docker-compose -f docker-compose.test.yml up --build --exit-code-from app-test
```

## 📂 Project Structure

- `app/`: Application source code
  - `api/`: Route handlers
  - `core/`: Config, Security, DB, Cache
  - `models/`: SQLAlchemy models
  - `schemas/`: Pydantic models
- `k8s/`: Kubernetes manifests
- `tests/`: Pytest suite & Locust load tests
- `docker-compose.prod.yml`: Production stack definition
