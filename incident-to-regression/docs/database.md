# Database Documentation

## Stack
- PostgreSQL 16
- SQLAlchemy 2.x (Async)
- Alembic (Migrations)

## Connection Configuration
Configured via `DATABASE_URL` in `.env`. The backend automatically converts standard `postgresql://` URIs to the async `postgresql+psycopg://` scheme internally.

## Migrations
Migrations are stored in `backend/alembic/versions/`.
- Apply: `make migrate`
- Create: `make migrate-create NAME="description"`

## Phase 1 Tables
- `system_events`: Proves database connectivity and provides infrastructure event logging.

## Connection Pooling
The async engine uses a connection pool (size=5, max_overflow=10) with `pool_pre_ping=True` to detect and recover from stale connections automatically.
