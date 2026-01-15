# Phase 4: Authentication & Authorization

## Goal Description
Implement secure authentication using OAuth2 with Password Flow and JWT (JSON Web Tokens). This includes password hashing, token generation, and protecting API endpoints.

## Implemented Changes

### Security Utilities
- **`app/core/security.py`**:
    - Password hashing using `bcrypt` (via `passlib`).
    - JWT generation and verification using `python-jose`.

### Schemas
- **`app/schemas/token.py`**: `Token` and `TokenPayload` schemas.

### Service Layer Update
- **`app/services/user_service.py`**:
    - `create_user`: Hashes password before storage.
    - `authenticate`: Verifies credentials.

### API Dependencies
- **`app/api/deps.py`**:
    - `get_current_user`: Validates JWT and retrieves user.
    - `get_current_active_user`: Ensures user is active.
    - `get_current_superuser`: Ensures user is admin.

### Endpoints
- **`app/api/v1/endpoints/login.py`**:
    - `POST /login/access-token`: OAuth2 compliant login endpoint.
- **`app/api/v1/endpoints/users.py`**:
    - `POST /users/`: Open user registration endpoint.

### Wiring
- **`app/main.py`**: Mounted `api_router` with prefix `/api/v1`.

## Verification
### Static Analysis
- `ruff` and `mypy` checks passed (strict mode).

### Runtime Verification (Pending Docker)
- **Login Tests**: `pytest tests/api/test_login.py` (Blocked: Requires running DB).
- **Registration Tests**: `pytest tests/api/test_users.py` (Blocked: Requires running DB).
- **Manual Verification**: Can be tested via `/docs` (Swagger UI) once the app is running.

## Next Steps
Proceed to Phase 5: Containerization & Deployment verification (Integration Testing).
