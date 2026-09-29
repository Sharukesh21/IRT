from typing import Optional
from pydantic import BaseModel

from app.db.models.enums import ExamSessionStatus

class StateTransitionResult(BaseModel):
    allowed: bool
    new_state: Optional[ExamSessionStatus] = None
    reason: Optional[str] = None

class StateMachine:
    """Deterministic state machine for ExamSessions."""

    # current_state: { event_type: new_state }
    _transitions = {
        ExamSessionStatus.NOT_STARTED: {
            "EXAM_STARTED": ExamSessionStatus.IN_PROGRESS,
        },
        ExamSessionStatus.IN_PROGRESS: {
            "QUESTION_VIEWED": ExamSessionStatus.IN_PROGRESS,
            "ANSWER_SELECTED": ExamSessionStatus.IN_PROGRESS,
            "ANSWER_SAVED": ExamSessionStatus.IN_PROGRESS,
            "ANSWER_UPDATED": ExamSessionStatus.IN_PROGRESS,
            "SUBMIT_REQUESTED": ExamSessionStatus.SUBMITTING,
            "SESSION_TIMEOUT": ExamSessionStatus.FAILED,
        },
        ExamSessionStatus.SUBMITTING: {
            "SUBMISSION_PROCESSING": ExamSessionStatus.SUBMITTING,
            "SUBMISSION_CONFIRMED": ExamSessionStatus.SUBMITTED,
            "SUBMISSION_FAILED": ExamSessionStatus.FAILED,
        },
        ExamSessionStatus.FAILED: {
            "SESSION_RECOVERED": ExamSessionStatus.RECOVERING,
        },
        ExamSessionStatus.RECOVERING: {
            "SUBMIT_REQUESTED": ExamSessionStatus.SUBMITTING,
            "ANSWER_SAVED": ExamSessionStatus.IN_PROGRESS, # E.g. recovering network
        },
        ExamSessionStatus.SUBMITTED: {
            # Terminal state, no outbound transitions normally expected
        }
    }

    @classmethod
    def evaluate_transition(
        cls, current_state: ExamSessionStatus, event_type: str
    ) -> StateTransitionResult:
        
        # Safe duplicate handling: if we receive an event that implies we are already 
        # in the target state, or is safe to ignore (e.g., duplicated IN_PROGRESS events)
        # That logic is handled by the Processor, but here we strictly evaluate state edges.
        
        valid_exits = cls._transitions.get(current_state, {})
        
        if event_type in valid_exits:
            return StateTransitionResult(
                allowed=True, 
                new_state=valid_exits[event_type],
            )
            
        return StateTransitionResult(
            allowed=False,
            reason=f"Transition from {current_state} via {event_type} is not allowed."
        )
