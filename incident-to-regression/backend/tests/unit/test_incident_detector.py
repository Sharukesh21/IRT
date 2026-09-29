"""Unit tests for Phase 4 IncidentDetector."""
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
import pytest

from app.domain.incident_detector import IncidentDetector
from app.db.models.enums import IncidentSeverity, IncidentCategory


def _make_experiment(state_corrupted: bool = True):
    exp = MagicMock()
    exp.id = uuid.uuid4()
    exp.scenario_id = uuid.uuid4()
    exp.session_id = uuid.uuid4()
    exp.started_at = datetime.now(timezone.utc)
    exp.completed_at = datetime.now(timezone.utc)
    exp.initial_state = "IN_PROGRESS"
    exp.final_state = "IN_PROGRESS" if state_corrupted else "SUBMITTED"
    exp.state_corrupted = state_corrupted
    exp.event_count = 3
    exp.recovery_status.name = "FAILED" if state_corrupted else "SUCCESS"
    return exp


def _make_integrity(status: str = "FAILED", violations=None):
    ir = MagicMock()
    ir.status = status
    ir.state_corrupted = status == "FAILED"
    ir.expected_state = "SUBMITTED"
    ir.actual_state = "IN_PROGRESS"
    ir.submission_count = 2 if status == "FAILED" else 1
    ir.violations = violations if violations is not None else ["Multiple confirmed submissions detected."]
    return ir


def _make_scenario(failure_type_name: str = "DUPLICATE"):
    sc = MagicMock()
    sc.id = uuid.uuid4()
    sc.failure_type.name = failure_type_name
    sc.target_event_type = "SUBMIT_REQUESTED"
    sc.parameters = {"count": 2}
    return sc


def _make_db(exp, ir, sc):
    """Build a fake async db that returns exp, ir, sc in order."""
    db = AsyncMock()
    calls = [exp, ir, sc]
    idx = [0]

    async def fake_execute(_stmt):
        result = MagicMock()
        obj = calls[idx[0]] if idx[0] < len(calls) else None
        idx[0] += 1
        result.scalars.return_value.first.return_value = obj
        return result

    db.execute = AsyncMock(side_effect=fake_execute)
    return db


class TestIncidentDetector:

    @pytest.mark.asyncio
    async def test_state_corruption_creates_detection(self):
        exp = _make_experiment(state_corrupted=True)
        ir = _make_integrity("FAILED", ["Multiple confirmed submissions detected."])
        sc = _make_scenario("DUPLICATE")
        db = _make_db(exp, ir, sc)

        detection = await IncidentDetector(db).detect_from_experiment(exp.id)
        assert detection is not None

    @pytest.mark.asyncio
    async def test_recovered_failure_returns_none(self):
        """Recovered failure must NOT auto-create an incident."""
        exp = _make_experiment(state_corrupted=False)
        ir = _make_integrity("SUCCESS", [])
        sc = _make_scenario("DUPLICATE")
        db = _make_db(exp, ir, sc)

        detection = await IncidentDetector(db).detect_from_experiment(exp.id)
        assert detection is None

    @pytest.mark.asyncio
    async def test_missing_experiment_returns_none(self):
        db = _make_db(None, None, None)
        detection = await IncidentDetector(db).detect_from_experiment(uuid.uuid4())
        assert detection is None

    @pytest.mark.asyncio
    async def test_critical_severity_for_multiple_submissions(self):
        exp = _make_experiment(state_corrupted=True)
        ir = _make_integrity("FAILED", ["Multiple confirmed submissions detected."])
        sc = _make_scenario("DUPLICATE")
        db = _make_db(exp, ir, sc)

        detection = await IncidentDetector(db).detect_from_experiment(exp.id)
        assert detection["severity"] == IncidentSeverity.CRITICAL
        assert detection["category"] == IncidentCategory.DATA_INTEGRITY

    @pytest.mark.asyncio
    async def test_duplicate_failure_maps_duplication_category(self):
        exp = _make_experiment(state_corrupted=True)
        ir = _make_integrity("FAILED", ["Generic violation."])
        sc = _make_scenario("DUPLICATE")
        db = _make_db(exp, ir, sc)

        detection = await IncidentDetector(db).detect_from_experiment(exp.id)
        assert detection["category"] == IncidentCategory.DUPLICATION

    @pytest.mark.asyncio
    async def test_out_of_order_failure_maps_ordering_category(self):
        exp = _make_experiment(state_corrupted=True)
        ir = _make_integrity("FAILED", ["Generic violation."])
        sc = _make_scenario("OUT_OF_ORDER")
        db = _make_db(exp, ir, sc)

        detection = await IncidentDetector(db).detect_from_experiment(exp.id)
        assert detection["category"] == IncidentCategory.EVENT_ORDERING

    @pytest.mark.asyncio
    async def test_timeout_failure_maps_timeout_category(self):
        exp = _make_experiment(state_corrupted=True)
        ir = _make_integrity("FAILED", ["Generic violation."])
        sc = _make_scenario("TIMEOUT")
        db = _make_db(exp, ir, sc)

        detection = await IncidentDetector(db).detect_from_experiment(exp.id)
        assert detection["category"] == IncidentCategory.TIMEOUT
