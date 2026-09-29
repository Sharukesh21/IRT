"""Unit tests for domain event models."""
import pytest
from datetime import datetime, timezone
from app.domain.events import BaseDomainEvent, ExamStartedEvent, SubmitRequestedEvent


class TestDomainEvents:
    def test_exam_started_event_type_literal(self):
        ev = ExamStartedEvent(
            event_id="evt_001",
            session_id="session_001",
            sequence_number=1,
            correlation_id="corr_001",
            occurred_at=datetime.now(timezone.utc),
        )
        assert ev.event_type == "EXAM_STARTED"

    def test_submit_requested_event_type_literal(self):
        ev = SubmitRequestedEvent(
            event_id="evt_002",
            session_id="session_001",
            sequence_number=5,
            correlation_id="corr_001",
            occurred_at=datetime.now(timezone.utc),
        )
        assert ev.event_type == "SUBMIT_REQUESTED"

    def test_event_delay_calculation(self):
        occurred = datetime(2026, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        received = datetime(2026, 1, 1, 10, 0, 5, tzinfo=timezone.utc)
        delay_ms = int((received - occurred).total_seconds() * 1000)
        assert delay_ms == 5000  # 5 seconds

    def test_occurred_at_received_at_distinction(self):
        """The system must distinguish occurred_at from received_at for future delay analysis."""
        occurred = datetime(2026, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        received = datetime(2026, 1, 1, 10, 0, 3, tzinfo=timezone.utc)

        ev = BaseDomainEvent(
            event_id="evt_003",
            event_type="ANSWER_SAVED",
            session_id="session_001",
            sequence_number=2,
            correlation_id="corr_001",
            occurred_at=occurred,
            received_at=received,
        )

        assert ev.occurred_at == occurred
        assert ev.received_at == received
        delay = (ev.received_at - ev.occurred_at).total_seconds()
        assert delay == 3.0

    def test_event_payload_defaults_empty(self):
        ev = ExamStartedEvent(
            event_id="evt_004",
            session_id="session_001",
            sequence_number=1,
            correlation_id="corr_001",
            occurred_at=datetime.now(timezone.utc),
        )
        assert ev.payload == {}

    def test_event_with_payload(self):
        ev = BaseDomainEvent(
            event_id="evt_005",
            event_type="ANSWER_SAVED",
            session_id="session_001",
            sequence_number=3,
            correlation_id="corr_001",
            occurred_at=datetime.now(timezone.utc),
            payload={"question_id": "q1", "selected_option": "A"},
        )
        assert ev.payload["selected_option"] == "A"
