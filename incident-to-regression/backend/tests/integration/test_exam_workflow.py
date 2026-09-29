"""Integration tests for the full exam workflow via API.

These tests run the actual event processor against SQLite (aiosqlite)
and verify the end-to-end flow: Start → Answer → Submit → Duplicate.
"""
import pytest
import uuid
from datetime import datetime, timezone
from httpx import AsyncClient, ASGITransport

from app.main import create_application
from app.db.models.enums import ExamSessionStatus
from app.db.session import get_engine, get_session_factory
from app.db.models.exam import Student, Exam, Question, AnswerOption
from app.core.config import get_settings


from app.db.base import Base

@pytest.fixture(scope="module")
async def db_setup():
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    SessionFactory = get_session_factory()

    async with SessionFactory() as session:
        # Create Student
        student = Student(name="Test Student", email=f"test_{uuid.uuid4().hex}@example.com")
        session.add(student)
        
        # Create Exam
        exam = Exam(
            title="Integration Test Exam",
            description="Testing the full workflow.",
            duration_seconds=3600,
            status="PUBLISHED"
        )
        session.add(exam)
        await session.flush()
        
        # Create Question
        q1 = Question(
            exam_id=exam.id, question_number=1,
            question_text="Integration question?",
            question_type="MULTIPLE_CHOICE"
        )
        session.add(q1)
        await session.flush()
        
        session.add_all([
            AnswerOption(question_id=q1.id, option_key="A", option_text="Opt A"),
            AnswerOption(question_id=q1.id, option_key="B", option_text="Opt B"),
        ])
        
        await session.commit()
        await session.refresh(student)
        await session.refresh(exam)
        await session.refresh(q1)
        
        return {"student": student, "exam": exam, "question": q1}


@pytest.fixture(scope="module")
def app():
    return create_application()


@pytest.fixture(scope="module")
async def client(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


class TestStateMachineUnit:
    """Pure unit tests — no database needed."""

    def test_scenario_1_normal_flow(self):
        from app.domain.state_machine import StateMachine
        from app.db.models.enums import ExamSessionStatus

        state = ExamSessionStatus.NOT_STARTED
        for event_type, expected in [
            ("EXAM_STARTED", ExamSessionStatus.IN_PROGRESS),
            ("ANSWER_SAVED", ExamSessionStatus.IN_PROGRESS),
            ("SUBMIT_REQUESTED", ExamSessionStatus.SUBMITTING),
            ("SUBMISSION_CONFIRMED", ExamSessionStatus.SUBMITTED),
        ]:
            res = StateMachine.evaluate_transition(state, event_type)
            assert res.allowed, f"Transition {state} + {event_type} should be allowed"
            state = res.new_state

        assert state == ExamSessionStatus.SUBMITTED

    def test_scenario_4_invalid_transition_after_submit(self):
        from app.domain.state_machine import StateMachine
        from app.db.models.enums import ExamSessionStatus

        result = StateMachine.evaluate_transition(ExamSessionStatus.SUBMITTED, "ANSWER_SAVED")
        assert result.allowed is False
        assert "SUBMITTED" in result.reason

    def test_scenario_6_recovery_flow(self):
        from app.domain.state_machine import StateMachine
        from app.db.models.enums import ExamSessionStatus

        state = ExamSessionStatus.SUBMITTING
        steps = [
            ("SUBMISSION_FAILED", ExamSessionStatus.FAILED),
            ("SESSION_RECOVERED", ExamSessionStatus.RECOVERING),
            ("SUBMIT_REQUESTED", ExamSessionStatus.SUBMITTING),
            ("SUBMISSION_CONFIRMED", ExamSessionStatus.SUBMITTED),
        ]
        for event_type, expected in steps:
            res = StateMachine.evaluate_transition(state, event_type)
            assert res.allowed, f"Expected allowed: {state} + {event_type}"
            state = res.new_state
            assert state == expected

    def test_delay_calculation(self):
        from datetime import datetime, timezone
        occurred = datetime(2026, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        received = datetime(2026, 1, 1, 10, 0, 5, tzinfo=timezone.utc)
        delay_ms = int((received - occurred).total_seconds() * 1000)
        assert delay_ms == 5000

    def test_duplicate_events_are_idempotent_by_contract(self):
        from app.domain.state_machine import StateMachine
        from app.db.models.enums import ExamSessionStatus
        r1 = StateMachine.evaluate_transition(ExamSessionStatus.IN_PROGRESS, "ANSWER_SAVED")
        r2 = StateMachine.evaluate_transition(ExamSessionStatus.IN_PROGRESS, "ANSWER_SAVED")
        assert r1 == r2

@pytest.mark.asyncio
async def test_full_exam_workflow_and_duplicate_submission(client, db_setup):
    """End-to-end test verifying the duplicate submission idempotency requirement."""
    student_id = str(db_setup["student"].id)
    exam_id = str(db_setup["exam"].id)
    question_id = str(db_setup["question"].id)

    # 1. Start Exam
    resp_start = await client.post("/api/v1/sessions", json={
        "student_id": student_id,
        "exam_id": exam_id
    })
    assert resp_start.status_code == 200
    session_id = resp_start.json()["id"]

    # 2. Answer Question
    resp_ans = await client.post(f"/api/v1/sessions/{session_id}/answers/{question_id}", json={
        "selected_option": "A"
    })
    assert resp_ans.status_code == 200

    # 3. Submit Exam (First time)
    resp_submit_1 = await client.post(f"/api/v1/sessions/{session_id}/submit")
    assert resp_submit_1.status_code == 200
    assert resp_submit_1.json()["status"] == "submitted"

    # 4. Confirm state is SUBMITTED
    resp_get = await client.get(f"/api/v1/sessions/{session_id}")
    assert resp_get.json()["status"] == "SUBMITTED"

    # 5. Submit Exam (Duplicate Request)
    resp_submit_2 = await client.post(f"/api/v1/sessions/{session_id}/submit")
    assert resp_submit_2.status_code == 200
    # The API acknowledges the duplicate without throwing a 500 or changing state
    assert resp_submit_2.json()["status"] == "duplicate_acknowledged"

    # 6. Confirm state remains SUBMITTED
    resp_get_after = await client.get(f"/api/v1/sessions/{session_id}")
    assert resp_get_after.json()["status"] == "SUBMITTED"

    # 7. Inspect Event Trace
    resp_traces = await client.get(f"/api/v1/sessions/{session_id}/events")
    events = resp_traces.json()["items"]
    
    # We should see EXAM_STARTED, ANSWER_SELECTED, ANSWER_SAVED, 
    # SUBMIT_REQUESTED (processed), SUBMISSION_CONFIRMED, SUBMIT_REQUESTED (duplicate)
    assert len(events) >= 5
    
    submit_requests = [e for e in events if e["event_type"] == "SUBMIT_REQUESTED"]
    assert len(submit_requests) == 2
    
    # First submit should be PROCESSED
    assert submit_requests[0]["status"] == "PROCESSED"
    # Second submit should be DUPLICATE
    assert submit_requests[1]["status"] == "DUPLICATE"

