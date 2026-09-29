"""Evaluation DB Models — Phase 7"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Float, ForeignKey, JSON, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func, text

from app.db.base import Base

_JSON = JSON().with_variant(JSONB(), "postgresql")


class EvaluationBenchmark(Base):
    __tablename__ = "evaluation_benchmarks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()"))
    benchmark_id = Column(String(50), unique=True, nullable=False)
    scenario_name = Column(String(255), nullable=False)
    description = Column(Text)
    failure_type = Column(String(50), nullable=False)
    category = Column(String(50), nullable=False)
    severity = Column(String(50), nullable=False)
    tags = Column(_JSON, server_default="[]")
    # The DSL-based scenario config
    scenario_config = Column(_JSON, nullable=False)
    # Expected outcomes
    expected_detection = Column(Boolean, default=True)
    expected_reproduction = Column(Boolean, default=True)
    expected_regression = Column(Boolean, default=True)
    expected_ci_status = Column(String(50), default="PASSED")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class EvaluationExperiment(Base):
    __tablename__ = "evaluation_experiments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()"))
    experiment_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    benchmark_id = Column(UUID(as_uuid=True), ForeignKey("evaluation_benchmarks.id"))
    experiment_type = Column(String(50), nullable=False)
    status = Column(String(50), default="CREATED")
    environment = Column(String(100), default="test")
    seed = Column(Integer)
    reproducible = Column(Boolean, default=False)
    # Results — collected during experiment
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id"), nullable=True)
    regression_test_id = Column(UUID(as_uuid=True), ForeignKey("regression_tests.id"), nullable=True)
    orchestration_id = Column(UUID(as_uuid=True), ForeignKey("regression_orchestrations.id"), nullable=True)
    # Outcome
    incident_detected = Column(Boolean)
    incident_reproduced = Column(Boolean)
    regression_generated = Column(Boolean)
    regression_passed = Column(Boolean)
    ci_status = Column(String(50))
    # Timing
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    duration_ms = Column(Float)
    full_suite_duration_ms = Column(Float)
    targeted_suite_duration_ms = Column(Float)
    full_suite_test_count = Column(Integer)
    targeted_suite_test_count = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class EvaluationEvidence(Base):
    __tablename__ = "evaluation_evidence"

    id = Column(UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()"))
    evidence_id = Column(String(50), unique=True, nullable=False)
    experiment_id = Column(UUID(as_uuid=True), ForeignKey("evaluation_experiments.id"))
    evidence_type = Column(String(50), nullable=False)
    title = Column(String(255))
    description = Column(Text)
    expected_value = Column(String(500))
    actual_value = Column(String(500))
    status = Column(String(50))  # PASS / FAIL / SKIP / ERROR
    artifact_data = Column(_JSON, server_default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class EvaluationBaseline(Base):
    __tablename__ = "evaluation_baselines"

    id = Column(UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()"))
    baseline_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    methodology = Column(String(100))       # MANUAL_PROCESS, FULL_REGRESSION, etc.
    measurement_source = Column(String(100))  # OBSERVED, CALCULATED, ESTIMATED, ASSUMED
    assumptions = Column(Text)
    # Baseline measurements
    incident_detection_time_s = Column(Float)
    reproduction_time_s = Column(Float)
    test_creation_time_s = Column(Float)
    test_execution_time_s = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TargetedRegressionEvaluation(Base):
    __tablename__ = "targeted_regression_evaluations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()"))
    evaluation_id = Column(String(50), unique=True, nullable=False)
    experiment_id = Column(UUID(as_uuid=True), ForeignKey("evaluation_experiments.id"))
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id"))
    full_test_count = Column(Integer, default=0)
    targeted_test_count = Column(Integer, default=0)
    full_duration_ms = Column(Float, default=0)
    targeted_duration_ms = Column(Float, default=0)
    full_status = Column(String(50))
    targeted_status = Column(String(50))
    relevant_test_count = Column(Integer, default=0)
    selected_relevant_count = Column(Integer, default=0)
    missed_relevant_count = Column(Integer, default=0)
    test_reduction_percent = Column(Float)
    execution_reduction_percent = Column(Float)
    protection_preserved = Column(Boolean)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
