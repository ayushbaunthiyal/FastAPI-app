# Deployment Guide

## Strategies

### 1. Docker Compose (Simple)
Best for single-server deployments or testing.

**Production Command**:
```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

**Services Included**:
- `api`: FastAPI Application (Replicas: 1)
- `worker`: Celery Worker
- `beat`: Celery Scheduler
- `db`: PostgreSQL
- `redis`: Redis
- Observability Stack (Grafana, Loki, etc.)

### 2. Kubernetes (Scalable)
Best for production clusters. Manifests are located in `k8s/`.

** Apply Manifests**:
```bash
# Apply secrets (Create these manually or via vaults in real prod)
kubectl apply -f k8s/base/secrets.yaml

# Apply namespace and config
kubectl apply -f k8s/base/namespace.yaml
kubectl apply -f k8s/base/configmap.yaml

# Apply Infrastructure
kubectl apply -f k8s/base/postgres.yaml
kubectl apply -f k8s/base/redis.yaml

# Apply App Workloads
kubectl apply -f k8s/base/api.yaml
kubectl apply -f k8s/base/worker.yaml
kubectl apply -f k8s/base/beat.yaml
```

**Security Notes**:
- Ensure `secrets.yaml` is NOT committed with real values. Use a secret manager.
- The `postgres` deployment in `k8s/` uses a local Volume. For production, use a managed database (RDS, Cloud SQL) or a reliable StorageClass.

---

## Configuration

Top-level environment variables (set in `.env` or ConfigMap):

| Variable | Description | Default |
|----------|-------------|---------|
| `PROJECT_NAME` | App Name | FastAPI Production App |
| `ENVIRONMENT` | Env (`local`, `production`) | `local` |
| `DATABASE_URL` | Postgres Connection String | - |
| `REDIS_URL` | Redis Connection String | - |
| `SECRET_KEY` | Cryptographic Key | **CHANGE_ME** |
| `HTTPS_REDIRECT`| Force HTTPS | `False` |
| `POSTGRES_POOL_SIZE` | DB Connection Pool | `20` |
