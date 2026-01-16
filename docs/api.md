# API Documentation

## Authentication

The API uses **OAuth2 Password Bearer** flow with JWT (JSON Web Tokens).

### 1. Get Access Token
**Endpoint**: `POST /api/v1/login/access-token`

**Request Body** (Form Data):
- `username`: Email address
- `password`: User password

**Response**:
```json
{
  "access_token": "eyJhbG...",
  "token_type": "bearer"
}
```

### 2. Using the Token
Include the token in the `Authorization` header of subsequent requests:
```
Authorization: Bearer <your_access_token>
```

---

## Key Endpoints

### Users
- `POST /api/v1/users/open`: Register a new user (public).
- `GET /api/v1/users/me`: Get current user profile (auth required).
- `PATCH /api/v1/users/me`: Update profile (auth required).

### Tasks
- `POST /api/v1/tasks/test-email`: Trigger a test email background task.
- `POST /api/v1/tasks/test-celery/{word}`: Trigger a simple celery task.

### Health & Metrics
- `GET /health/live`: Liveness probe (Kubernetes).
- `GET /health/ready`: Readiness probe (Kubernetes).
- `GET /metrics`: Prometheus metrics.

---

## Error Handling

Errors follow a standard structure:

```json
{
  "detail": "Error message description"
}
```

Common HTTP Codes:
- `400 Bad Request`: Validation error or invalid input.
- `401 Unauthorized`: Missing or invalid token.
- `403 Forbidden`: Valid token but insufficient permissions.
- `404 Not Found`: Resource does not exist.
- `429 Too Many Requests`: Rate limit exceeded.
- `500 Internal Server Error`: Server-side issue.
