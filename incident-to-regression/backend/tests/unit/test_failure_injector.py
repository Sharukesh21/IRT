"""Unit tests for Phase 3 Failure Injector strategies."""
import copy
from datetime import datetime, timezone, timedelta
import uuid
import pytest

from app.domain.events import BaseDomainEvent
from app.domain.failure_injector import (
    FailureInjector, DelayStrategy, DuplicateStrategy,
    OutOfOrderStrategy, TimeoutStrategy, NormalStrategy
)
from app.db.models.failure import FailureScenario, FailureType


def make_scenario(failure_type: FailureType, target: str = "SUBMIT_REQUESTED", params: dict = None) -> FailureScenario:
    s = FailureScenario()
    s.id = uuid.uuid4()
    s.name = "Test Scenario"
    s.failure_type = failure_type
    s.target_event_type = target
    s.parameters = params or {}
    return s


def make_event(event_type: str, seq: int = 1) -> BaseDomainEvent:
    now = datetime.now(timezone.utc)
    return BaseDomainEvent(
        event_id=f"evt-{uuid.uuid4().hex}",
        event_type=event_type,
        session_id=str(uuid.uuid4()),
        sequence_number=seq,
        correlation_id=str(uuid.uuid4()),
        occurred_at=now,
        received_at=now,
        payload={}
    )


def make_exam_stream():
    """Normal stream: START → ANSWER_SAVED → SUBMIT_REQUESTED."""
    return [
        make_event("EXAM_STARTED", 1),
        make_event("ANSWER_SAVED", 2),
        make_event("SUBMIT_REQUESTED", 3),
    ]


class TestNormalStrategy:
    def test_passthrough(self):
        events = make_exam_stream()
        scenario = make_scenario(FailureType.NONE)
        result = NormalStrategy().apply(events, scenario)
        assert len(result) == len(events)
        assert [e.event_type for e in result] == [e.event_type for e in events]


class TestDelayStrategy:
    def test_delay_adds_to_received_at(self):
        events = make_exam_stream()
        scenario = make_scenario(FailureType.DELAY, "SUBMIT_REQUESTED", {"delay_ms": 3000})
        result = DelayStrategy().apply(events, scenario)
        
        # Only SUBMIT_REQUESTED should be delayed
        submit = next(e for e in result if e.event_type == "SUBMIT_REQUESTED")
        other = next(e for e in result if e.event_type == "EXAM_STARTED")
        
        delay = (submit.received_at - submit.occurred_at).total_seconds() * 1000
        assert delay == pytest.approx(3000, rel=0.01)
        
        # Non-targeted event should not be delayed
        other_delay = (other.received_at - other.occurred_at).total_seconds() * 1000
        assert other_delay == pytest.approx(0, abs=5)

    def test_delay_preserves_occurred_at(self):
        events = make_exam_stream()
        original_occurred = events[2].occurred_at
        scenario = make_scenario(FailureType.DELAY, "SUBMIT_REQUESTED", {"delay_ms": 5000})
        result = DelayStrategy().apply(events, scenario)
        
        submit = next(e for e in result if e.event_type == "SUBMIT_REQUESTED")
        assert submit.occurred_at == original_occurred  # unchanged
        assert submit.received_at > submit.occurred_at  # delayed

    def test_event_count_unchanged(self):
        events = make_exam_stream()
        scenario = make_scenario(FailureType.DELAY, "SUBMIT_REQUESTED", {"delay_ms": 1000})
        result = DelayStrategy().apply(events, scenario)
        assert len(result) == len(events)


class TestDuplicateStrategy:
    def test_duplicate_adds_events(self):
        events = make_exam_stream()
        scenario = make_scenario(FailureType.DUPLICATE, "SUBMIT_REQUESTED", {"count": 2})
        result = DuplicateStrategy().apply(events, scenario)
        
        submit_events = [e for e in result if e.event_type == "SUBMIT_REQUESTED"]
        assert len(submit_events) == 3  # 1 original + 2 duplicates

    def test_duplicate_keeps_same_event_id(self):
        """Critical: duplicates must have same event_id so idempotency catches them."""
        events = make_exam_stream()
        scenario = make_scenario(FailureType.DUPLICATE, "SUBMIT_REQUESTED", {"count": 1})
        result = DuplicateStrategy().apply(events, scenario)
        
        submit_events = [e for e in result if e.event_type == "SUBMIT_REQUESTED"]
        assert len(submit_events) == 2
        assert submit_events[0].event_id == submit_events[1].event_id

    def test_non_targeted_events_unchanged(self):
        events = make_exam_stream()
        scenario = make_scenario(FailureType.DUPLICATE, "SUBMIT_REQUESTED", {"count": 1})
        result = DuplicateStrategy().apply(events, scenario)
        
        answer_events = [e for e in result if e.event_type == "ANSWER_SAVED"]
        assert len(answer_events) == 1  # not duplicated

    def test_duplicate_received_at_offset(self):
        """Duplicates should have slightly different received_at."""
        events = make_exam_stream()
        scenario = make_scenario(FailureType.DUPLICATE, "SUBMIT_REQUESTED", {"count": 1})
        result = DuplicateStrategy().apply(events, scenario)
        
        submits = [e for e in result if e.event_type == "SUBMIT_REQUESTED"]
        assert submits[1].received_at > submits[0].received_at


class TestOutOfOrderStrategy:
    def test_target_event_swapped_with_previous(self):
        events = make_exam_stream()  # EXAM_STARTED(1), ANSWER_SAVED(2), SUBMIT_REQUESTED(3)
        scenario = make_scenario(FailureType.OUT_OF_ORDER, "ANSWER_SAVED")
        result = OutOfOrderStrategy().apply(events, scenario)
        
        # ANSWER_SAVED (index 1) should be swapped with EXAM_STARTED (index 0)
        assert result[0].event_type == "ANSWER_SAVED"
        assert result[1].event_type == "EXAM_STARTED"
        assert result[2].event_type == "SUBMIT_REQUESTED"

    def test_event_count_unchanged(self):
        events = make_exam_stream()
        scenario = make_scenario(FailureType.OUT_OF_ORDER, "ANSWER_SAVED")
        result = OutOfOrderStrategy().apply(events, scenario)
        assert len(result) == len(events)


class TestTimeoutStrategy:
    def test_timeout_creates_retry(self):
        events = make_exam_stream()
        scenario = make_scenario(FailureType.TIMEOUT, "SUBMIT_REQUESTED", {"timeout_ms": 5000})
        result = TimeoutStrategy().apply(events, scenario)
        
        submit_events = [e for e in result if e.event_type == "SUBMIT_REQUESTED"]
        assert len(submit_events) == 2  # original + retry

    def test_timeout_retry_same_event_id(self):
        """Retry must have same event_id to be caught as duplicate."""
        events = make_exam_stream()
        scenario = make_scenario(FailureType.TIMEOUT, "SUBMIT_REQUESTED", {"timeout_ms": 5000})
        result = TimeoutStrategy().apply(events, scenario)
        
        submits = [e for e in result if e.event_type == "SUBMIT_REQUESTED"]
        assert submits[0].event_id == submits[1].event_id

    def test_retry_received_at_is_delayed(self):
        events = make_exam_stream()
        scenario = make_scenario(FailureType.TIMEOUT, "SUBMIT_REQUESTED", {"timeout_ms": 5000})
        result = TimeoutStrategy().apply(events, scenario)
        
        submits = [e for e in result if e.event_type == "SUBMIT_REQUESTED"]
        delay_ms = (submits[1].received_at - submits[0].received_at).total_seconds() * 1000
        assert delay_ms == pytest.approx(5000, rel=0.01)


class TestFailureInjector:
    def test_routes_to_correct_strategy(self):
        injector = FailureInjector()
        events = make_exam_stream()
        
        # DUPLICATE should add events
        dup_scenario = make_scenario(FailureType.DUPLICATE, "SUBMIT_REQUESTED", {"count": 1})
        dup_result = injector.apply(events, dup_scenario)
        assert len(dup_result) > len(events)
        
        # NONE should pass through unchanged
        none_scenario = make_scenario(FailureType.NONE)
        none_result = injector.apply(events, none_scenario)
        assert len(none_result) == len(events)
