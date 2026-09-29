"""System event model for Phase 1 infrastructure logging."""

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column
import uuid

from app.db.base import Base


class SystemEvent(Base):
    """Records infrastructure-level events (startup, shutdown, migrations, etc.).

    Phase 1 table that proves database connectivity and provides a foundation
    for future audit/event logging throughout the pipeline.
    """

    __tablename__ = "system_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_: Mapped[dict[str, Any] | None] = mapped_column(
        "metadata",
        JSON,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        return f"<SystemEvent id={self.id} type={self.event_type}>"
