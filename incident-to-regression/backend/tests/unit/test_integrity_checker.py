"""Unit tests for Phase 3 IntegrityChecker."""
import pytest
from app.domain.integrity_checker import IntegrityChecker
from app.db.models.enums import ExamSessionStatus


def submitted_state(submission_count=1):
    return {"status": ExamSessionStatus.SUBMITTED.value, "submission_count": submission_count, "version": 5}

def in_progress_state():
    return {"status": ExamSessionStatus.IN_PROGRESS.value, "submission_count": 0, "version": 2}

def submit_event():
    return {"event_type": "SUBMIT_REQUESTED", "status": "PROCESSED"}


class TestIntegrityChecker:
    def test_clean_submission_passes(self):
        before = in_progress_state()
        after = submitted_state(1)
        events = [submit_event()]
        result = IntegrityChecker.verify(before, after, events)
        
        assert result["state_corrupted"] is False
        assert result["status"] == "SUCCESS"
        assert result["violations"] == []

    def test_multiple_submissions_is_violation(self):
        before = in_progress_state()
        after = submitted_state(2)  # Two submissions = corruption
        events = [submit_event()]
        result = IntegrityChecker.verify(before, after, events)
        
        assert result["state_corrupted"] is True
        assert result["status"] == "FAILED"
        assert any("Multiple confirmed submissions" in v for v in result["violations"])

    def test_state_regression_is_violation(self):
        """SUBMITTED → IN_PROGRESS is an invalid regression."""
        before = submitted_state(1)
        after = in_progress_state()  # Regressed!
        events = []
        result = IntegrityChecker.verify(before, after, events)
        
        assert result["state_corrupted"] is True
        assert any("Invalid state regression" in v for v in result["violations"])

    def test_expected_submitted_but_got_in_progress(self):
        """If we expected SUBMITTED after a submit event but got something else, flag it."""
        before = in_progress_state()
        after = in_progress_state()  # Did not transition to SUBMITTED despite submit event
        events = [submit_event()]
        result = IntegrityChecker.verify(before, after, events)
        
        assert result["state_corrupted"] is True
        assert any("Expected SUBMITTED" in v for v in result["violations"])

    def test_no_violations_returns_success(self):
        before = in_progress_state()
        after = submitted_state(1)
        result = IntegrityChecker.verify(before, after, [submit_event()])
        
        assert result["status"] == "SUCCESS"
        assert not result["state_corrupted"]

    def test_submission_count_reported(self):
        before = in_progress_state()
        after = submitted_state(1)
        result = IntegrityChecker.verify(before, after, [submit_event()])
        
        assert result["submission_count"] == 1

    def test_expected_and_actual_state_reported(self):
        before = in_progress_state()
        after = submitted_state(1)
        result = IntegrityChecker.verify(before, after, [submit_event()])
        
        assert result["expected_state"] == ExamSessionStatus.SUBMITTED.value
        assert result["actual_state"] == ExamSessionStatus.SUBMITTED.value
