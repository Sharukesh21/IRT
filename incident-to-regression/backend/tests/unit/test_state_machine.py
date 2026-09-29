"""Unit tests for the exam state machine."""
import pytest
from app.db.models.enums import ExamSessionStatus
from app.domain.state_machine import StateMachine


class TestStateMachineNormalFlow:
    def test_not_started_to_in_progress(self):
        result = StateMachine.evaluate_transition(ExamSessionStatus.NOT_STARTED, "EXAM_STARTED")
        assert result.allowed is True
        assert result.new_state == ExamSessionStatus.IN_PROGRESS

    def test_in_progress_answer_stays_in_progress(self):
        result = StateMachine.evaluate_transition(ExamSessionStatus.IN_PROGRESS, "ANSWER_SAVED")
        assert result.allowed is True
        assert result.new_state == ExamSessionStatus.IN_PROGRESS

    def test_in_progress_to_submitting(self):
        result = StateMachine.evaluate_transition(ExamSessionStatus.IN_PROGRESS, "SUBMIT_REQUESTED")
        assert result.allowed is True
        assert result.new_state == ExamSessionStatus.SUBMITTING

    def test_submitting_to_submitted(self):
        result = StateMachine.evaluate_transition(ExamSessionStatus.SUBMITTING, "SUBMISSION_CONFIRMED")
        assert result.allowed is True
        assert result.new_state == ExamSessionStatus.SUBMITTED

    def test_submitting_to_failed(self):
        result = StateMachine.evaluate_transition(ExamSessionStatus.SUBMITTING, "SUBMISSION_FAILED")
        assert result.allowed is True
        assert result.new_state == ExamSessionStatus.FAILED

    def test_failed_to_recovering(self):
        result = StateMachine.evaluate_transition(ExamSessionStatus.FAILED, "SESSION_RECOVERED")
        assert result.allowed is True
        assert result.new_state == ExamSessionStatus.RECOVERING

    def test_recovering_to_submitting(self):
        result = StateMachine.evaluate_transition(ExamSessionStatus.RECOVERING, "SUBMIT_REQUESTED")
        assert result.allowed is True
        assert result.new_state == ExamSessionStatus.SUBMITTING


class TestStateMachineInvalidTransitions:
    def test_submitted_cannot_accept_answers(self):
        result = StateMachine.evaluate_transition(ExamSessionStatus.SUBMITTED, "ANSWER_SAVED")
        assert result.allowed is False
        assert result.reason is not None
        assert "SUBMITTED" in result.reason

    def test_submitted_cannot_resubmit_directly(self):
        result = StateMachine.evaluate_transition(ExamSessionStatus.SUBMITTED, "SUBMIT_REQUESTED")
        assert result.allowed is False

    def test_not_started_cannot_submit(self):
        result = StateMachine.evaluate_transition(ExamSessionStatus.NOT_STARTED, "SUBMIT_REQUESTED")
        assert result.allowed is False

    def test_not_started_cannot_save_answer(self):
        result = StateMachine.evaluate_transition(ExamSessionStatus.NOT_STARTED, "ANSWER_SAVED")
        assert result.allowed is False

    def test_transition_result_has_reason_on_failure(self):
        result = StateMachine.evaluate_transition(ExamSessionStatus.SUBMITTED, "EXAM_STARTED")
        assert result.allowed is False
        assert isinstance(result.reason, str)
        assert len(result.reason) > 0
