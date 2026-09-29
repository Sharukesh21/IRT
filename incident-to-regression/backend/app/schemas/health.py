"""Pydantic schemas for health check endpoints."""

from typing import Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Response schema for GET /api/v1/health."""

    status: str = Field(..., description="Service status", examples=["ok"])
    service: str = Field(..., description="Service name", examples=["incident-to-regression"])
    environment: str = Field(..., description="Deployment environment", examples=["development"])
    version: str = Field(..., description="API version", examples=["0.1.0"])


class DatabaseHealthResponse(BaseModel):
    """Response schema for GET /api/v1/health/database."""

    status: str = Field(..., description="Database status", examples=["ok", "unavailable"])
    database: str = Field(..., description="Database type", examples=["postgresql"])
    latency_ms: Optional[float] = Field(
        None,
        description="Query round-trip latency in milliseconds",
        examples=[2.5],
    )
    error: Optional[str] = Field(
        None,
        description="Error message when database is unavailable",
        examples=["Connection refused"],
    )
