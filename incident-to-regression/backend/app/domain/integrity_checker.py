from typing import List, Dict, Any

from app.db.models.enums import ExamSessionStatus
from app.db.models.failure import RecoveryStatus

class IntegrityChecker:
    @staticmethod
    def verify(state_before: dict, state_after: dict, events_processed: List[dict]) -> dict:
        """
        Verify state invariants after a failure scenario has run.
        Returns a dict representing the IntegrityResult.
        """
        violations = []
        
        expected_status = state_before.get("status")
        actual_status = state_after.get("status")
        
        # Calculate expected status based on normal processing of events
        for ev in events_processed:
            if ev.get("event_type") == "SUBMIT_REQUESTED":
                expected_status = ExamSessionStatus.SUBMITTED.value
                break
                
        # Invariant 1: A session cannot have more than one confirmed submission.
        submission_count = state_after.get("submission_count", 0)
        if submission_count > 1:
            violations.append("Multiple confirmed submissions detected.")

        # Invariant 2: Duplicate events cannot create duplicate domain side effects.
        # Handled by submission_count check and checking final status.
        
        # Invariant 4: Out-of-order events cannot silently overwrite valid state.
        # If the state changed in an invalid way (e.g. going from SUBMITTED back to IN_PROGRESS)
        if state_before.get("status") == ExamSessionStatus.SUBMITTED.value and actual_status != ExamSessionStatus.SUBMITTED.value:
            violations.append(f"Invalid state regression: {state_before.get('status')} -> {actual_status}")

        if expected_status == ExamSessionStatus.SUBMITTED.value and actual_status != ExamSessionStatus.SUBMITTED.value:
            violations.append(f"Expected SUBMITTED state but actual is {actual_status}")
            
        state_corrupted = len(violations) > 0
        recovery_status = RecoveryStatus.FAILED if state_corrupted else RecoveryStatus.SUCCESS
        
        return {
            "status": recovery_status.value,
            "state_corrupted": state_corrupted,
            "expected_state": expected_status,
            "actual_state": actual_status,
            "submission_count": submission_count,
            "violations": violations
        }
