"""Unit tests for the health check endpoints."""

import pytest


@pytest.mark.unit
async def test_health_endpoint_returns_200(client):
    """GET /api/v1/health must return HTTP 200."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200


@pytest.mark.unit
async def test_health_endpoint_returns_ok_status(client):
    """Health endpoint must return status=ok."""
    response = await client.get("/api/v1/health")
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.unit
async def test_health_endpoint_returns_required_fields(client):
    """Health endpoint response must include all required fields."""
    response = await client.get("/api/v1/health")
    data = response.json()
    assert "status" in data
    assert "service" in data
    assert "environment" in data
    assert "version" in data


@pytest.mark.unit
async def test_health_endpoint_service_name(client):
    """Service name must match application name."""
    response = await client.get("/api/v1/health")
    data = response.json()
    assert data["service"] == "incident-to-regression"


@pytest.mark.unit
async def test_health_endpoint_environment(client):
    """Environment must be 'test' during testing."""
    response = await client.get("/api/v1/health")
    data = response.json()
    assert data["environment"] == "test"


@pytest.mark.unit
async def test_health_endpoint_version(client):
    """Version must be set."""
    response = await client.get("/api/v1/health")
    data = response.json()
    assert data["version"] == "0.1.0"


@pytest.mark.unit
async def test_unknown_route_returns_404(client):
    """Unknown routes must return 404."""
    response = await client.get("/api/v1/this-does-not-exist")
    assert response.status_code == 404


@pytest.mark.unit
async def test_404_has_error_envelope(client):
    """404 response must use the standard error envelope."""
    response = await client.get("/api/v1/nonexistent-route")
    data = response.json()
    assert "error" in data
    assert "code" in data["error"]
    assert "message" in data["error"]
    assert "request_id" in data["error"]


@pytest.mark.unit
async def test_request_id_in_response_headers(client):
    """Every response must include an X-Request-ID header."""
    response = await client.get("/api/v1/health")
    assert "x-request-id" in response.headers


@pytest.mark.unit
async def test_client_provided_request_id_is_propagated(client):
    """If client sends X-Request-ID, it must be returned in the response."""
    custom_id = "my-custom-request-id-12345"
    response = await client.get(
        "/api/v1/health",
        headers={"X-Request-ID": custom_id},
    )
    assert response.headers.get("x-request-id") == custom_id


@pytest.mark.unit
async def test_cors_headers_present(client):
    """CORS headers must be present for allowed origins."""
    response = await client.get(
        "/api/v1/health",
        headers={"Origin": "http://localhost:5173"},
    )
    assert "access-control-allow-origin" in response.headers


@pytest.mark.unit
async def test_database_health_endpoint_exists(client):
    """GET /api/v1/health/database must return a response (not 404)."""
    response = await client.get("/api/v1/health/database")
    # With SQLite, this may succeed or fail — either way it should not 404
    assert response.status_code in (200, 503)


@pytest.mark.unit
async def test_database_health_response_has_required_fields(client):
    """Database health response must include status and database fields."""
    response = await client.get("/api/v1/health/database")
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert data["database"] == "postgresql"
