from sqlalchemy import Column, String, Boolean, DateTime, Integer, Float, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func, text

from app.db.base import Base

_JSON = JSON().with_variant(JSONB(), "postgresql")


class RegressionTest(Base):
    __tablename__ = "regression_tests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()"))
    test_id = Column(String(50), unique=True, nullable=False)   # REG-000001
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("regression_candidates.id"), nullable=False)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id"), nullable=False)

    name = Column(String(255), nullable=False)
    description = Column(String(2000))
    category = Column(String(50))
    failure_type = Column(String(50))
    priority = Column(String(50), default="MEDIUM")
    status = Column(String(50), default="DRAFT")      # DRAFT|READY|ACTIVE|DISABLED|DEPRECATED
    version = Column(Integer, default=1)

    test_definition = Column(_JSON, nullable=False, server_default="{}")
    deterministic = Column(Boolean, default=True)
    enabled = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class RegressionTestVersion(Base):
    __tablename__ = "regression_test_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()"))
    test_id = Column(UUID(as_uuid=True), ForeignKey("regression_tests.id", ondelete="CASCADE"), nullable=False)
    version = Column(Integer, nullable=False)
    definition = Column(_JSON, nullable=False, server_default="{}")
    change_reason = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class RegressionTestRun(Base):
    __tablename__ = "regression_test_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()"))
    run_id = Column(String(50), unique=True, nullable=False)
    test_id = Column(UUID(as_uuid=True), ForeignKey("regression_tests.id"), nullable=False)
    incident_id = Column(UUID(as_uuid=True), nullable=True)

    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    duration_ms = Column(Float)
    status = Column(String(50), default="QUEUED")     # QUEUED|RUNNING|PASSED|FAILED|ERROR|CANCELLED
    environment = Column(String(100), default="test")
    session_id = Column(String(255))

    assertions_total = Column(Integer, default=0)
    assertions_passed = Column(Integer, default=0)
    assertions_failed = Column(Integer, default=0)
    error_type = Column(String(100))
    error_message = Column(String(2000))
    execution_trace = Column(_JSON, server_default="[]")

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class RegressionAssertionResult(Base):
    __tablename__ = "regression_assertion_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()"))
    run_id = Column(UUID(as_uuid=True), ForeignKey("regression_test_runs.id", ondelete="CASCADE"), nullable=False)
    assertion_index = Column(Integer, nullable=False)
    path = Column(String(255), nullable=False)
    operator = Column(String(50), nullable=False)
    expected_value = Column(String(500))
    actual_value = Column(String(500))
    status = Column(String(50), nullable=False)       # PASS|FAIL
    message = Column(String(1000))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class RegressionProof(Base):
    __tablename__ = "regression_proofs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()"))
    test_id = Column(UUID(as_uuid=True), ForeignKey("regression_tests.id"), nullable=False)
    incident_id = Column(UUID(as_uuid=True), nullable=True)
    before_run_id = Column(UUID(as_uuid=True), ForeignKey("regression_test_runs.id"), nullable=True)
    after_run_id = Column(UUID(as_uuid=True), ForeignKey("regression_test_runs.id"), nullable=True)
    before_status = Column(String(50))
    after_status = Column(String(50))
    protected = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class RegressionSuiteRun(Base):
    __tablename__ = "regression_suite_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()"))
    suite_run_id = Column(String(50), unique=True, nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    total_tests = Column(Integer, default=0)
    passed = Column(Integer, default=0)
    failed = Column(Integer, default=0)
    errors = Column(Integer, default=0)
    skipped = Column(Integer, default=0)
    pass_rate = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
