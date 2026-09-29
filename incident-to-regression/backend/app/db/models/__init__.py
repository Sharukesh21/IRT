"""Database models package.

Import all models here so that Alembic can discover them via Base.metadata.
"""

from app.db.models.health import SystemEvent
from app.db.models.exam import Student, Exam, Question, AnswerOption
from app.db.models.session import ExamSession, StudentAnswer, Submission
from app.db.models.event import Event
from app.db.models.failure import FailureScenario, FailureExperiment, InjectedEvent, StateSnapshot, IntegrityResult
from app.db.models.incident import (
    IncidentGroup, Incident, IncidentEvidence, IncidentTimeline, IncidentRootCause, IncidentExpectation
)
from app.db.models.regression import (
    RegressionCandidate, ReproductionSpec
)
from app.db.models.regression_test import (
    RegressionTest, RegressionTestVersion, RegressionTestRun, RegressionAssertionResult, RegressionProof, RegressionSuiteRun
)
from app.db.models.ci import (
    ExternalIncident, RegressionPlan, RegressionPlanTest, RegressionOrchestration, 
    CIRegressionRun, RegressionPolicy, RegressionEscape, RegressionTestTag, IncidentTag
)
from app.db.models.evaluation import (
    EvaluationBenchmark, EvaluationExperiment, EvaluationEvidence, EvaluationBaseline, TargetedRegressionEvaluation
)

__all__ = [
    "Exam", "Question", "Student", 
    "ExamSession", "StudentAnswer", "Submission", "Event",
    "FailureExperiment", "StateSnapshot",
    "IncidentGroup", "Incident", "IncidentEvidence", "IncidentTimeline", "IncidentRootCause", "IncidentExpectation",
    "RegressionCandidate", "ReproductionSpec",
    "RegressionTest", "RegressionTestVersion", "RegressionTestRun", "RegressionAssertionResult", "RegressionProof", "RegressionSuiteRun",
    "ExternalIncident", "RegressionPlan", "RegressionPlanTest", "RegressionOrchestration", "CIRegressionRun", "RegressionPolicy", "RegressionEscape", "RegressionTestTag", "IncidentTag",
    "EvaluationBenchmark", "EvaluationExperiment", "EvaluationEvidence", "EvaluationBaseline", "TargetedRegressionEvaluation"
]
