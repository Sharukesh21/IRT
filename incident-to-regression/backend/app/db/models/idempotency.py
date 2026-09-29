import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel

class IdempotencyKey(BaseModel):
    __tablename__ = "idempotency_keys"

    idempotency_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    tenant_id: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    operation: Mapped[str] = mapped_column(String(100), nullable=False)
    request_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    response_status: Mapped[Optional[int]] = mapped_column(Integer)
    response_body: Mapped[Optional[dict]] = mapped_column(JSON().with_variant(JSONB, "postgresql"))
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
