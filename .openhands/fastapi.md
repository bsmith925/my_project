# .openhands/fastapi.md
## Purpose
Opinionated checklist for building consistent FastAPI services in OpenHands.

### 1 – Project structure
```
app/
├── main.py          # FastAPI() instance
├── api/             # routers
│   └── v1/
│       └── users.py
├── models/          # Pydantic models & ORMs
├── services/        # business logic
└── dependencies/    # Depends() callables
```
Follow *one module per concern*; keep route handlers thin.  
Use **snake_case** for files and folders, *PascalCase* for classes.

### 2 – Router guidelines
* Mount routers under a clear prefix (`/api/v1/users`).
* Tag groups (`tags=["users"]`) for automatic docs.
* Keep handlers small; delegate heavy work to **services**.

### 3 – Pydantic & validation
* One request and one response model per endpoint.
* Use `Field(..., examples=…)` for richer docs.
* Validate with `constr`, `conlist`, etc., instead of manual checks.

### 4 – Dependency injection
* Keep shared objects (DB session, settings) behind `Depends()`.
* Scope heavy resources with `@asynccontextmanager` or `yield` fixtures.

### 5 – Settings & environment
* Centralise configuration with `pydantic.BaseSettings`.
* Separate `prod`, `staging`, `local`, and `test` env files.

### 6 – Testing reminders
* Reuse the layout and patterns in **tests.md**; leverage `TestClient`.

### 7 – Observability
* Add JSON structured logging (e.g., `structlog`).
* Expose `/healthz` and `/metrics` for readiness & Prometheus scraping.
