import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Enum as SQLEnum, JSON, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel
from enum import Enum

class FailureType(str, Enum):
    NONE = "NONE"
    DELAY = "DELAY"
    DUPLICATE = "DUPLICATE"
    OUT_OF_ORDER = "OUT_OF_ORDER"
    NETWORK_INTERRUPTION = "NETWORK_INTERRUPTION"
    TIMEOUT = "TIMEOUT"
    RETRY = "RETRY"

class RecoveryStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"

class SnapshotType(str, Enum):
    BEFORE = "BEFORE"
    AFTER = "AFTER"

class FailureScenario(BaseModel):
    __tablename__ = "failure_scenarios"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000))
    failure_type: Mapped[FailureType] = mapped_column(SQLEnum(FailureType, name="failure_type_enum"), nullable=False)
    target_event_type: Mapped[Optional[str]] = mapped_column(String(100))
    target_event_id: Mapped[Optional[str]] = mapped_column(String(255))
    parameters: Mapped[dict] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False, default=dict)
    seed: Mapped[Optional[int]] = mapped_column(Integer)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class FailureExperiment(BaseModel):
    __tablename__ = "failure_experiments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scenario_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("failure_scenarios.id"), nullable=False)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exam_sessions.id", ondelete="CASCADE"), nullable=False)
    
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    initial_state: Mapped[str] = mapped_column(String(50), nullable=False)
    final_state: Mapped[Optional[str]] = mapped_column(String(50))
    
    event_count: Mapped[int] = mapped_column(Integer, default=0)
    duplicate_count: Mapped[int] = mapped_column(Integer, default=0)
    delayed_count: Mapped[int] = mapped_column(Integer, default=0)
    out_of_order_count: Mapped[int] = mapped_column(Integer, default=0)
    error_count: Mapped[int] = mapped_column(Integer, default=0)
    
    recovery_status: Mapped[RecoveryStatus] = mapped_column(SQLEnum(RecoveryStatus, name="recovery_status_enum"), nullable=False, default=RecoveryStatus.UNKNOWN)
    state_corrupted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    processing_time_ms: Mapped[Optional[float]] = mapped_column(Float)

class InjectedEvent(BaseModel):
    __tablename__ = "injected_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    experiment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("failure_experiments.id", ondelete="CASCADE"), nullable=False)
    
    original_event_id: Mapped[Optional[str]] = mapped_column(String(255))
    injected_event_id: Mapped[str] = mapped_column(String(255), nullable=False)
    
    failure_type: Mapped[FailureType] = mapped_column(SQLEnum(FailureType, name="failure_type_enum"), nullable=False)
    modification: Mapped[str] = mapped_column(String(255))
    
    original_sequence: Mapped[Optional[int]] = mapped_column(Integer)
    delivery_sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)

class StateSnapshot(BaseModel):
    __tablename__ = "state_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    experiment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("failure_experiments.id", ondelete="CASCADE"), nullable=False)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exam_sessions.id", ondelete="CASCADE"), nullable=False)
    
    snapshot_type: Mapped[SnapshotType] = mapped_column(SQLEnum(SnapshotType, name="snapshot_type_enum"), nullable=False)
    session_status: Mapped[str] = mapped_column(String(50), nullable=False)
    answer_state: Mapped[dict] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False, default=dict)
    submission_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

class IntegrityResult(BaseModel):
    __tablename__ = "integrity_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    experiment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("failure_experiments.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    status: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. RECOVERED, CORRUPTED
    state_corrupted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    
    expected_state: Mapped[str] = mapped_column(String(50), nullable=False)
    actual_state: Mapped[str] = mapped_column(String(50), nullable=False)
    submission_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    violations: Mapped[dict] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False, default=list) # List of strings stored as JSON
