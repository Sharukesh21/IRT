import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func, text
from sqlalchemy.orm import relationship

from app.db.base import Base

_JSON = JSON().with_variant(JSONB(), "postgresql")

class ExternalIncident(Base):
    __tablename__ = "external_incidents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()"))
    external_incident_id = Column(String(255), unique=True, nullable=False)
    source = Column(String(100), nullable=False)
    raw_payload = Column(_JSON, nullable=False)
    normalized_incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id"), nullable=True)
    status = Column(String(50), nullable=False, default="RECEIVED")
    error = Column(String(1000))
    received_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class RegressionPlan(Base):
    __tablename__ = "regression_plans"
    id = Column(UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()"))
    plan_id = Column(String(50), unique=True, nullable=False)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id"), nullable=True)
    selection_strategy = Column(String(50), nullable=False)
    test_count = Column(Integer, default=0)
    estimated_duration = Column(Integer)
    status = Column(String(50), default="CREATED")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class RegressionPlanTest(Base):
    __tablename__ = "regression_plan_tests"
    id = Column(UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()"))
    plan_id = Column(UUID(as_uuid=True), ForeignKey("regression_plans.id", ondelete="CASCADE"))
    test_id = Column(UUID(as_uuid=True), ForeignKey("regression_tests.id", ondelete="CASCADE"))
    relevance_score = Column(Integer, default=0)
    selection_reason = Column(String(255))
    execution_order = Column(Integer, default=0)

class RegressionOrchestration(Base):
    __tablename__ = "regression_orchestrations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()"))
    orchestration_id = Column(String(50), unique=True, nullable=False)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id"), nullable=True)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("regression_plans.id"))
    trigger_source = Column(String(50))
    status = Column(String(50), default="CREATED")
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    total_tests = Column(Integer, default=0)
    passed = Column(Integer, default=0)
    failed = Column(Integer, default=0)
    errors = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class CIRegressionRun(Base):
    __tablename__ = "ci_regression_runs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()"))
    run_id = Column(String(50), unique=True, nullable=False)
    orchestration_id = Column(UUID(as_uuid=True), ForeignKey("regression_orchestrations.id"))
    provider = Column(String(50))
    repository = Column(String(255))
    branch = Column(String(255))
    commit_sha = Column(String(255))
    pull_request_number = Column(Integer)
    status = Column(String(50))
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class RegressionPolicy(Base):
    __tablename__ = "regression_policies"
    id = Column(UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()"))
    policy_name = Column(String(255), nullable=False)
    strategy = Column(String(50), nullable=False)
    block_on_failure = Column(Boolean, default=True)
    required_severity = Column(String(50))
    required_categories = Column(_JSON, server_default="[]")
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class RegressionEscape(Base):
    __tablename__ = "regression_escapes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()"))
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id"))
    test_id = Column(UUID(as_uuid=True), ForeignKey("regression_tests.id"))
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    test_last_status = Column(String(50))
    application_version = Column(String(100))
    explanation = Column(String(1000))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class RegressionTestTag(Base):
    __tablename__ = "regression_test_tags"
    id = Column(UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()"))
    test_id = Column(UUID(as_uuid=True), ForeignKey("regression_tests.id", ondelete="CASCADE"))
    tag = Column(String(50), nullable=False)

class IncidentTag(Base):
    __tablename__ = "incident_tags"
    id = Column(UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()"))
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id", ondelete="CASCADE"))
    tag = Column(String(50), nullable=False)
