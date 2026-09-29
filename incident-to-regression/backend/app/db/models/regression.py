from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func, text

from app.db.base import Base

_JSON = JSON().with_variant(JSONB(), "postgresql")

class ReproductionSpec(Base):
    __tablename__ = "reproduction_specs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()"))
    reproduction_id = Column(String(100), unique=True, nullable=False)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)
    
    initial_state = Column(String(50), nullable=False)
    event_sequence = Column(_JSON, nullable=False, server_default="[]")
    failure_configuration = Column(_JSON, nullable=False, server_default="{}")
    
    expected_state = Column(_JSON, nullable=False, server_default="{}")
    expected_outcome = Column(String(100))
    seed = Column(Integer)
    deterministic = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class RegressionCandidate(Base):
    __tablename__ = "regression_candidates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()"))
    candidate_id = Column(String(100), unique=True, nullable=False)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)
    reproduction_spec_id = Column(UUID(as_uuid=True), ForeignKey("reproduction_specs.id", ondelete="CASCADE"), nullable=False)
    
    name = Column(String(255), nullable=False)
    description = Column(String(2000))
    trigger_condition = Column(String(2000))
    expected_behavior = Column(String(2000))
    invariant = Column(String(2000))
    
    priority = Column(String(50), default="MEDIUM")
    status = Column(String(50), default="PENDING")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
