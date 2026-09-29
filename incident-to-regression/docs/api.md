# API Documentation

## Base URL
Development: `http://localhost:8000/api/v1`

## Interactive Documentation
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Request Tracing
Every request accepts and returns an `X-Request-ID` header. If not provided, a UUIDv4 is generated.

## Error Format
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "request_id": "uuid-here"
  }
}
```

## Endpoints

### `GET /api/v1/health`
Returns service liveness status.
**Response (200 OK):**
```json
{
  "status": "ok",
  "service": "incident-to-regression",
  "environment": "development",
  "version": "0.1.0"
}
```

### `GET /api/v1/health/database`
Performs a real `SELECT 1` against PostgreSQL.
**Response (200 OK):**
```json
{
  "status": "ok",
  "database": "postgresql",
  "latency_ms": 1.5
}
```
**Response (503 Unavailable):**
```json
{
  "status": "unavailable",
  "database": "postgresql",
  "error": "Connection failed"
}
```
