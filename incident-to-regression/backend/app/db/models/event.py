import uuid
from datetime import datetime
from typing import Optional, Any

from sqlalchemy import String, Integer, DateTime, ForeignKey, Enum as SQLEnum, JSON, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel
from app.db.models.enums import EventStatus

class Event(BaseModel):
    __tablename__ = "events"

    # event_id is the unique identifier for the event itself, not the PK for this table.
    event_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exam_sessions.id", ondelete="CASCADE"), index=True)
    student_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("students.id"), index=True)
    exam_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("exams.id"), index=True)
    
    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False)
    correlation_id: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    causation_id: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    status: Mapped[EventStatus] = mapped_column(SQLEnum(EventStatus, name="event_status_enum"), nullable=False, index=True)
    payload: Mapped[dict] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=dict,
        server_default="{}"
    )
    
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    error_code: Mapped[Optional[str]] = mapped_column(String(100))
    error_message: Mapped[Optional[str]] = mapped_column(String(1000))

    session = relationship("ExamSession", back_populates="events")

    __table_args__ = (
        UniqueConstraint("session_id", "sequence_number", name="uix_session_sequence"),
    )
