from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func, text
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.db.models.enums import IncidentStatus, EvidenceType

# Use JSON with JSONB variant for SQLite test compatibility
_JSON = JSON().with_variant(JSONB(), "postgresql")

class IncidentGroup(Base):
    __tablename__ = "incident_groups"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()"))
    group_key = Column(String(255), unique=True, nullable=False)
    category = Column(String(50), nullable=False)
    failure_type = Column(String(50), nullable=False)
    representative_incident_id = Column(UUID(as_uuid=True), nullable=True)
    occurrence_count = Column(Integer, default=1)
    first_seen_at = Column(DateTime(timezone=True), server_default=func.now())
    last_seen_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(50), default=IncidentStatus.OPEN.value)

class Incident(Base):
    __tablename__ = "incidents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()"))
    incident_id = Column(String(50), unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(String(2000))
    status = Column(String(50), default=IncidentStatus.OPEN.value, nullable=False)
    severity = Column(String(50), nullable=False)
    category = Column(String(50), nullable=False)
    failure_type = Column(String(50))
    
    session_id = Column(UUID(as_uuid=True), nullable=False)
    experiment_id = Column(UUID(as_uuid=True), ForeignKey("failure_experiments.id"), nullable=False)
    group_id = Column(UUID(as_uuid=True), ForeignKey("incident_groups.id"), nullable=True)
    
    primary_event_id = Column(String(255))
    detected_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    occurred_at = Column(DateTime(timezone=True), nullable=False)
    resolved_at = Column(DateTime(timezone=True))
    
    reproducible = Column(Boolean, default=False)
    regression_candidate = Column(Boolean, default=False)
    state_corrupted = Column(Boolean, default=False)
    recovery_status = Column(String(50))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class IncidentEvidence(Base):
    __tablename__ = "incident_evidence"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()"))
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)
    evidence_type = Column(String(50), nullable=False)
    source_id = Column(String(255))
    event_id = Column(String(255))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    payload = Column(_JSON, nullable=False, server_default="{}")
    importance = Column(String(50), default="MEDIUM")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class IncidentTimeline(Base):
    __tablename__ = "incident_timeline"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()"))
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)
    event_id = Column(String(255))
    sequence = Column(Integer, nullable=False)
    logical_sequence = Column(Integer)
    delivery_sequence = Column(Integer)
    event_type = Column(String(100), nullable=False)
    occurred_at = Column(DateTime(timezone=True), nullable=False)
    received_at = Column(DateTime(timezone=True))
    processing_status = Column(String(50))
    state_before = Column(String(50))
    state_after = Column(String(50))
    failure_type = Column(String(50))
    is_anomalous = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class IncidentRootCause(Base):
    __tablename__ = "incident_root_causes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()"))
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)
    cause_code = Column(String(100), nullable=False)
    confidence = Column(String(50), default="HIGH")
    evidence_ids = Column(_JSON, server_default="[]")
    explanation = Column(String(2000))
    detected_by = Column(String(100), default="RULES_ENGINE")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class IncidentExpectation(Base):
    __tablename__ = "incident_expectations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()"))
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)
    expected_state = Column(_JSON, nullable=False, server_default="{}")
    actual_state = Column(_JSON, nullable=False, server_default="{}")
    differences = Column(_JSON, server_default="[]")
    invariant_violations = Column(_JSON, server_default="[]")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
